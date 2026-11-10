from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, func
from database import get_db, Category, Article, User
from routes.user import get_current_user

router = APIRouter(prefix="/api", tags=["分类模块"])  # 统一前缀，该模块所有接口都会带上 /auth  # swagger文档分组标签


@router.get("/category")
async def getCategories(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query(None, description="分类名称"),
    user_id: str = Depends(get_current_user),
):
    print("文章分类也需要权限", user_id)
    # 模糊查询
    if name:
        stmt = (
            Select(Category, func.count(Article.id).label("article_count"), User.username.label("create_user_name"))
            .outerjoin(Article, Article.category_id == Category.id)
            .outerjoin(User, Category.create_user == User.id)
            .where(Category.name.contains(name))
            .group_by(Category.id)
        )
    else:
        # stmt = Select(Category)
        stmt = (
            Select(Category, func.count(Article.id).label("article_count"), User.username.label("create_user_name"))
            .outerjoin(Article, Article.category_id == Category.id)
            .outerjoin(User, Category.create_user == User.id)
            .group_by(Category.id)
        )

    offset = (page - 1) * page_size
    limit = page_size
    categories = await db.execute(stmt.offset(offset).limit(limit))
    rows = categories.all()
    # result.all() / result.scalars().all() 只能执行 1 次，执行完游标清空，再次调用返回空,所以要保存到变量中。
    # 所以这里只能执行一次，后续需要执行其他操作，需要重新执行查询语句。
    # rows = categories.scalars().all()
    print("--------------------------------->@@", rows, len(rows))
    total = await db.execute(func.count(Category.id))
    total = total.scalar()

    # 组装返回数据
    data_list = []
    for category, article_count, create_user_name in rows:
        data_list.append(
            {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "create_at": category.create_at,
                "article_count": article_count,
                "create_user_name": create_user_name,
            }
        )

    return {"code": 200, "msg": "获取分类列表成功", "data": data_list, "total": total}


class CategoryCreate(BaseModel):
    title: str
    description: str = None


@router.post("/category")
async def createCategory(
    db: Annotated[AsyncSession, Depends(get_db)],
    category: CategoryCreate,
    user: str = Depends(get_current_user),
):
    print("user===========>", user, category)
    category = Category(name=category.name, description=category.description, create_user=user["user_id"])
    db.add(category)
    await db.commit()
    return {"code": 200, "msg": "创建分类成功"}


@router.get("/delCategory/{id}")
async def delCategory(
    db: Annotated[AsyncSession, Depends(get_db)],
    id: int,
    user: str = Depends(get_current_user),
):
    stmt = Select(Category).where(Category.id == id)
    result = await db.execute(stmt)
    # category = result.scalar_or_none() 版本差异问题，没有这个方法
    category = result.scalars().one_or_none()
    if not category:
        return {"code": 404, "msg": "分类不存在"}
    await db.delete(category)
    await db.commit()
    return {"code": 200, "msg": "删除分类成功"}


class UpdateCategory(BaseModel):
    id: int
    title: str
    description: str = None


@router.post("/update")
async def updateCategory(
    db: Annotated[AsyncSession, Depends(get_db)],
    category: UpdateCategory,
    _user: str = Depends(get_current_user),
):
    stmt = Select(Category).where(Category.id == category.id)
    print("==========", category, category.id, category.title)

    result = await db.execute(stmt)
    # category = result.scalar_or_none() 版本差异问题，没有这个方法
    res = result.scalar()
    print("fanhuide res", res)
    if not res:
        return {"code": 404, "msg": "分类不存在"}
    res.title = category.title
    res.description = category.description
    await db.commit()
    return {"code": 200, "msg": "更新分类成功"}
