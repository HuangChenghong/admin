from fastapi import APIRouter, Depends, Query, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from database import get_db, User, Role
from routes.user import get_current_user

from routes.log import OperLogAnno, record_oper_log


router = APIRouter(prefix="/api", tags=["角色模块"])  # 统一前缀，该模块所有接口都会带上 /auth  # swagger文档分组标签


@router.get("/roles")
@record_oper_log(OperLogAnno(title="获取角色列表", log_type="操作"))
async def getRoles(
    db: Annotated[AsyncSession, Depends(get_db)],
    _req: Request,
    _bt: BackgroundTasks,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    role_name: str = Query(None, description="角色名称"),
    status: int = Query(None, description="角色状态"),
    _user: str = Depends(get_current_user),
):
    stmt = select(Role)
    if role_name:
        stmt = stmt.where(Role.role_name.contains(role_name))
    if status is not None:
        stmt = stmt.where(Role.status == status)

    offset = (page - 1) * page_size
    limit = page_size
    # 单实体查询用 scalars().all() 直接拿到 Role 对象，避免 Row 包装导致属性访问失败
    rows = (await db.execute(stmt.offset(offset).limit(limit))).scalars().all()

    # 总数要和列表用同样的条件（否则翻页总数不准）
    total_stmt = select(func.count(Role.id))
    if role_name:
        total_stmt = total_stmt.where(Role.role_name.contains(role_name))
    if status is not None:
        total_stmt = total_stmt.where(Role.status == status)
    total = await db.scalar(total_stmt)

    # 组装返回数据
    data_list = [
        {
            "id": role.id,
            "role_name": role.role_name,
            "role_code": role.role_code,
            "remark": role.remark,
            "status": role.status,
            "create_at": role.create_at,
        }
        for role in rows
    ]

    return {"code": 200, "msg": "获取角色列表成功", "data": data_list, "total": total}


class RoleCreate(BaseModel):
    role_name: str
    role_code: str
    status: int = 1
    remark: str = None


@router.post("/role")
async def createRole(
    db: Annotated[AsyncSession, Depends(get_db)],
    role: RoleCreate,
    user: str = Depends(get_current_user),
):
    print("user===========>", user, role)
    role = Role(role_name=role.role_name, role_code=role.role_code, status=role.status, remark=role.remark)
    db.add(role)
    await db.commit()
    return {"code": 200, "msg": "创建角色成功"}


@router.get("/delRole/{id}")
async def delRole(
    db: Annotated[AsyncSession, Depends(get_db)],
    id: int,
    _user: str = Depends(get_current_user),
):
    stmt = select(Role).where(Role.id == id)
    result = await db.execute(stmt)
    role = result.scalars().one_or_none()
    if not role:
        return {"code": 404, "msg": "角色不存在"}
    await db.delete(role)
    await db.commit()
    return {"code": 200, "msg": "删除角色成功"}


class UpdateRole(BaseModel):
    id: int
    role_name: str
    remark: str = None
    status: int = 1
    role_code: str


@router.post("/updateRole")
async def updateRole(
    db: Annotated[AsyncSession, Depends(get_db)],
    role: UpdateRole,
    _user: str = Depends(get_current_user),
):
    stmt = select(Role).where(Role.id == role.id)
    result = await db.execute(stmt)
    res = result.scalar_one_or_none()
    if not res:
        return {"code": 404, "msg": "角色不存在"}
    res.role_name = role.role_name
    res.remark = role.remark
    res.status = role.status
    await db.commit()
    return {"code": 200, "msg": "更新角色成功"}
