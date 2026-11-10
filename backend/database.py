from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Text, BigInteger
import datetime
import enum

# ===================== 数据库引擎 =====================
# MySQL 配置（如需使用 SQLite，改为下方注释的配置）
DATABASE_URL = "mysql+aiomysql://root:852456Aa@106.14.254.44:3306/blog"


engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    echo=True,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# ORM 基类
Base = declarative_base()


# ===================== 数据库依赖 =====================
async def get_db() -> AsyncSession:
    """FastAPI 依赖项：获取数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


# ===================== 数据模型 =====================
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class UserStatus(enum.IntEnum):
    DISABLED = 0
    ACTIVE = 1


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    password: Mapped[str] = mapped_column(String(200))
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    # password: Mapped[str] = mapped_column(String(200))
    avater: Mapped[str] = mapped_column(String(200))
    cname: Mapped[str] = mapped_column(String(50))
    role: Mapped[int] = mapped_column(Integer)
    status: Mapped[int] = mapped_column(Integer)
    is_delete: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    update_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    description: Mapped[str] = mapped_column(String(500), default="")
    create_user: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=True)
    create_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    update_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class ArticleStatus(enum.IntEnum):
    DRAFT = 0
    PUBLISHED = 1


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    content: Mapped[str] = mapped_column(Text, default="")
    description: Mapped[str] = mapped_column(String(500), default="")
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("category.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=True)
    status: Mapped[int] = mapped_column(Integer, default=ArticleStatus.DRAFT)
    views: Mapped[int] = mapped_column(Integer, default=0)
    thumb: Mapped[str] = mapped_column(String(200), default="")
    # likes: Mapped[int] = mapped_column(Integer, default=0)
    # comments: Mapped[int] = mapped_column(Integer, default=0)
    createdAt: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    updatedAt: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class ArticleLike(Base):
    __tablename__ = "article_like"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    article_id: Mapped[int] = mapped_column(Integer, ForeignKey("articles.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=True)
    create_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    role_name: Mapped[str] = mapped_column(String(50), nullable=True)
    role_code: Mapped[str] = mapped_column(String(50), nullable=True)
    remark: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[int] = mapped_column(Integer, default=1)
    create_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())


class SysOperLog(Base):
    __tablename__ = "sys_oper_log"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    log_type: Mapped[str] = mapped_column(String(20), nullable=False)
    log_level: Mapped[str] = mapped_column(String(20), nullable=False)
    oper_username: Mapped[str] = mapped_column(String(50), nullable=False)
    oper_content: Mapped[str] = mapped_column(String(255), nullable=False)
    oper_ip: Mapped[str] = mapped_column(String(50), nullable=False)
    cost_ms: Mapped[int] = mapped_column(Integer, default=0)
    oper_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)


# class LogType(str, enum.Enum):
#     LOGIN = "login"
#     OPERATION = "operation"
#     ERROR = "error"


# class LogLevel(str, enum.Enum):
#     INFO = "info"
#     WARNING = "warning"
#     ERROR = "error"


# class Log(Base):
#     __tablename__ = "log"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
#     type: Mapped[str] = mapped_column(String(20))
#     level: Mapped[str] = mapped_column(String(20))
#     username: Mapped[str] = mapped_column(String(50))
#     action: Mapped[str] = mapped_column(String(200))
#     ip: Mapped[str] = mapped_column(String(50))
#     params: Mapped[str] = mapped_column(Text, default="")
#     result: Mapped[str] = mapped_column(Text, default="")
#     duration: Mapped[int] = mapped_column(Integer, default=0)
#     create_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())


# ===================== 初始化表 =====================
# async def init_db():
#     """启动时自动建表（仅首次使用时调用）"""
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     print("✅ 数据库表初始化完成")
