import time
import json
import io
from datetime import datetime
from functools import wraps
from fastapi import Request, BackgroundTasks, APIRouter, Depends, Query
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from database import SysOperLog, AsyncSessionLocal, get_db

from dataclasses import dataclass


from urllib.parse import quote
from openpyxl import Workbook
from fastapi.responses import StreamingResponse


router = APIRouter(prefix="/api", tags=["日志模块"])


# 使用方式：在接口上加 @OperLogAnno(title="新增文章", log_type="操作")
@dataclass
class OperLogAnno:
    """操作日志自定义注解"""

    title: str  # 操作内容：新增文章、删除分类
    log_type: str  # 日志类型：登录 / 操作 / 错误
    # log_level: str  # 日志等级：INFO / WARNING / ERROR


def _extract_username(user_val) -> str:
    """从 get_current_user 的返回值中提取用户名（支持 dict 或对象）"""
    if user_val is None:
        return "anonymous"
    if isinstance(user_val, dict):
        if "username" in user_val:
            return str(user_val["username"])
        if "name" in user_val:
            return str(user_val["name"])
    # 兼容对象形式
    if hasattr(user_val, "username"):
        return str(getattr(user_val, "username"))
    if hasattr(user_val, "name"):
        return str(getattr(user_val, "name"))
    return "anonymous"


def record_oper_log(anno: OperLogAnno):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            request: Request | None = None
            background_tasks: BackgroundTasks | None = None
            oper_username = "anonymous"
            req_body = ""
            cost = 0
            log_level = "INFO"
            detail = ""
            try:
                # 取出 Request、后台任务、用户对象
                for key, val in kwargs.items():
                    if isinstance(val, Request):
                        request = val
                    if isinstance(val, BackgroundTasks):
                        background_tasks = val
                    # 从 Depends(get_current_user) 的入参中提取用户名
                    if (
                        "user" in key.lower()
                        and val is not None
                        and not isinstance(val, (Request, BackgroundTasks, AsyncSession))
                    ):
                        oper_username = _extract_username(val)
                # 兜底：如果中间件写了 request.state.user
                if oper_username == "anonymous" and request and hasattr(request.state, "user"):
                    oper_username = _extract_username(request.state.user)
                # 获取请求 body（可选，存入 detail；GET 一般没有 body）
                if request and request.method in ("POST", "PUT", "PATCH"):
                    body_bytes = await request.body()
                    req_body = body_bytes.decode("utf-8")
                # 执行原始接口
                result = await func(*args, **kwargs)
                cost = int((time.time() - start) * 1000)
                log_level = "INFO"
                detail = json.dumps({"request": req_body, "response": str(result)}, ensure_ascii=False)
                return result
            except Exception as e:
                cost = int((time.time() - start) * 1000)
                log_level = "ERROR"
                import traceback

                detail = json.dumps({"request": req_body, "exception": traceback.format_exc()}, ensure_ascii=False)
                raise e
            finally:
                if request and background_tasks:
                    oper_ip = request.client.host if request.client else "0.0.0.0"
                    log_obj = SysOperLog(
                        log_type=anno.log_type,
                        log_level=log_level,
                        oper_username=oper_username,
                        oper_content=anno.title,
                        oper_ip=oper_ip,
                        cost_ms=cost,
                        oper_time=datetime.now(),
                        detail=detail,
                    )
                    # 后台异步写入数据库
                    background_tasks.add_task(save_log_db, log_obj)

        return wrapper

    return decorator


async def save_log_db(log: SysOperLog):
    """异步入库日志（直接用 AsyncSessionLocal 创建会话，不能复用 Depends 的 async generator get_db）"""
    async with AsyncSessionLocal() as db:
        db.add(log)
        await db.commit()


@router.get("/log")
async def get_log(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    log_type: str = Query("", description="日志类型"),
    log_level: str = Query("", description="日志等级"),
    oper_username: str = Query("", description="用户名"),
    start_time: str = Query("", description="开始时间"),
    end_time: str = Query("", description="结束时间"),
):
    stmt = select(SysOperLog)
    if log_type:
        stmt = stmt.where(SysOperLog.log_type == log_type)
    if log_level:
        stmt = stmt.where(SysOperLog.log_level == log_level)
    if oper_username:
        stmt = stmt.where(SysOperLog.oper_username.contains(oper_username))
    if start_time and end_time:
        stmt = stmt.where(SysOperLog.oper_time.between(start_time, end_time))

    # 总数要和列表用同样的条件
    total_stmt = select(func.count(SysOperLog.id)).select_from(stmt.subquery())
    total = await db.scalar(total_stmt)

    offset = (page - 1) * page_size
    rows = (
        (await db.execute(stmt.order_by(SysOperLog.oper_time.desc()).offset(offset).limit(page_size))).scalars().all()
    )

    # ORM 对象不能直接 JSON 序列化，先把真实表字段映射成 dict
    data_list = [{col.name: getattr(log, col.name) for col in SysOperLog.__table__.columns} for log in rows]
    return {"code": 200, "message": "获取日志成功", "data": data_list, "total": total or 0}

    # ========== 【新增：日志导出接口】 ==========


@router.post("/export", summary="导出操作日志Excel")
async def export_oper_log(
    log_type: str | None = Query(None),
    log_level: str | None = Query(None),
    oper_username: str | None = Query(None),
    start_time: datetime | None = Query(None),
    end_time: datetime | None = Query(None),
    db=Depends(get_db),
):
    # 1. 拼接筛选条件（和列表查询完全一致，筛选后导出）
    stmt = select(SysOperLog).order_by(SysOperLog.oper_time.desc())
    where_list = []
    if log_type:
        where_list.append(SysOperLog.log_type == log_type)
    if log_level:
        where_list.append(SysOperLog.log_level == log_level)
    if oper_username:
        where_list.append(SysOperLog.oper_username.like(f"%{oper_username}%"))
    if start_time and end_time:
        where_list.append(SysOperLog.oper_time.between(start_time, end_time))
    if where_list:
        stmt = stmt.where(and_(*where_list))

    res = await db.execute(stmt)
    log_list = res.scalars().all()

    # 2. 创建Excel，写入数据
    wb = Workbook()
    ws = wb.active
    ws.title = "操作日志"
    # 表头（和数据库字段一一对应，可自定义中文表头）
    headers = ["ID", "日志类型", "日志级别", "操作人", "操作描述", "操作IP", "耗时(ms)", "操作时间"]
    ws.append(headers)

    for log in log_list:
        row = [
            log.id,
            log.log_type,
            log.log_level,
            log.oper_username,
            log.oper_content,
            log.oper_ip,
            log.cost_ms,
            log.oper_time.strftime("%Y-%m-%d %H:%M:%S") if log.oper_time else "",
            # log.detail,
        ]
        ws.append(row)

    # 3. 写入内存字节流，不生成本地文件
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    # 4. 返回文件流给前端下载
    filename = quote(f"操作日志_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx")
    return StreamingResponse(
        iter([buffer.read()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
