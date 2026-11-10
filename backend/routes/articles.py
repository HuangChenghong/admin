from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, func, select
from database import get_db, Category, Article, User, ArticleLike
from routes.user import get_current_user


router = APIRouter(prefix="/api", tags=["文章模块"])  # 统一前缀，该模块所有接口都会带上 /auth  # swager文档分组标签


@router.get("/articles")
async def getArticles(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    title: str = Query(None, description="文章标题"),
    category_id: int = Query(None, description="分类ID"),
    status: int = Query(None, description="状态"),
):
    # 基础查询：同时拿 Article 实体 + User.username
    stmt = (
        select(
            Article,
            User.username,
            func.count(ArticleLike.id).label("like_count"),
        )
        .outerjoin(User, Article.user_id == User.id)
        .outerjoin(ArticleLike, ArticleLike.article_id == Article.id)
        .group_by(Article.id)
        .order_by(Article.createdAt.desc())
    )

    # 条件

    if title:
        stmt = stmt.where(Article.title.contains(title))
    if category_id is not None:
        stmt = stmt.where(Article.category_id == category_id)
    if status is not None:
        stmt = stmt.where(Article.status == status)

    offset = (page - 1) * page_size
    limit = page_size
    articles = await db.execute(stmt.offset(offset).limit(limit))
    # ⚠️ 这里不能用 .scalars()！
    # 因为 SELECT 了两列（Article 对象, username 字符串），scalars() 会只取每一行的第一列(Article)，
    # 导致后面 for article, username 无法解包，报错 "cannot unpack non-iterable Article object"
    rows = articles.all()  # [(Article, username|None), (Article, username|None), ...]

    # 总数要和列表用同样的条件（否则翻页总数不准）
    total_stmt = select(func.count(Article.id))
    if title:
        total_stmt = total_stmt.where(Article.title.contains(title))
    if category_id is not None:
        total_stmt = total_stmt.where(Article.category_id == category_id)
    if status is not None:
        total_stmt = total_stmt.where(Article.status == status)
    total = await db.scalar(total_stmt)

    data_list = []
    for article, username, like_count in rows:
        # ORM 对象本身不能直接 **article 解包（会报 not a mapping），
        # 先通过 __table__.columns 把真实表字段映射成 dict，再追加 create_user_name，
        # 写法等价于你想要的 {**article, create_user_name: username}
        item = {
            "id": article.id,
            "title": article.title,
            "description": article.description,
            "content": article.content,
            "category_id": article.category_id,
            "user_id": article.user_id,
            "status": article.status,
            "views": article.views,
            "thumb": article.thumb,
            "create_at": article.createdAt,
            "create_user_name": username or "",
            "like_count": like_count or 0,
        }
        data_list.append(item)

    return {"code": 200, "msg": "获取文章列表成功", "data": data_list, "total": total}


class ArticleCreate(BaseModel):
    title: str
    description: str | None = None
    content: str | None = None
    category_id: int | None = None
    status: int = 0
    thumb: str | None = None


@router.post("/articles")
async def createArticle(
    db: Annotated[AsyncSession, Depends(get_db)],
    article: ArticleCreate,
    current_user: dict = Depends(get_current_user),
):
    user_id: int | None = None
    if isinstance(current_user, dict):
        uid = current_user.get("user_id")
        if uid is not None:
            try:
                user_id = int(uid)
            except Exception:
                user_id = None

    new_article = Article(
        title=article.title,
        description=article.description or "",
        content=article.content or "",
        category_id=article.category_id,
        user_id=user_id,
        status=article.status,
        thumb=article.thumb or "",
    )
    db.add(new_article)
    await db.commit()
    await db.refresh(new_article)
    return {"code": 200, "msg": "创建文章成功", "data": {"id": new_article.id}}


@router.get("/delArticle/{id}")
async def delArticle(
    db: Annotated[AsyncSession, Depends(get_db)],
    id: int,
    user: str = Depends(get_current_user),
):
    stmt = Select(Article).where(Article.id == id)
    result = await db.execute(stmt)
    # category = result.scalar_or_none() 版本差异问题，没有这个方法
    exist = result.scalars().one_or_none()
    if not exist:
        return {"code": 404, "msg": "文章不存在"}
    # await db.delete(exist)
    exist.status = 2  # 删除的时候，目前只是把他改成草稿，让他重新修改在发表
    await db.commit()
    return {"code": 200, "msg": "删除文章成功"}


class UpdateArticle(BaseModel):
    id: int
    title: str | None = None
    description: str | None = None
    content: str | None = None
    category_id: int | None = None
    status: int | None = None
    thumb: str | None = None


@router.post("/update")
async def updateArticle(
    db: Annotated[AsyncSession, Depends(get_db)],
    article: UpdateArticle,
    user: str = Depends(get_current_user),
):
    stmt = Select(Article).where(Article.id == article.id)

    result = await db.execute(stmt)
    res = result.scalar()
    if not res:
        return {"code": 404, "msg": "文章不存在"}
    # res.title = article.title
    # if article.description is not None:
    #     res.description = article.description
    # if article.content is not None:
    #     res.content = article.content
    # if article.category_id is not None:
    #     res.category_id = article.category_id
    if article.status is not None:
        res.status = article.status
    # if article.thumb is not None:
    #     res.thumb = article.thumb
    await db.commit()
    return {"code": 200, "msg": "更新文章成功"}
