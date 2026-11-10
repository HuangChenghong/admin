from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, select, and_, or_
from database import get_db, User, Article
from bcrypt import hashpw, gensalt, checkpw
from dotenv import load_dotenv
from sqlalchemy import func

from routes.log import OperLogAnno, record_oper_log
import redis

# timedelta:
from datetime import datetime, timedelta

# 自动从 HTTP 请求头 Authorization: Bearer xxxxxx 里面把 token 提取出来，配合 Depends() 使用
# 格式：Authorization: Bearer xxxxxx，格式不能改变，否则会识别失败，报401错误
from fastapi.security import OAuth2PasswordBearer
import jwt
import os

router = APIRouter(prefix="/api", tags=["登录模块"])  # 统一前缀，该模块所有接口都会带上 /auth  # swagger文档分组标签

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")  # jwt密钥

ALGORITHM = "HS256"  # 加密算法，HS256表示使用HS256算法进行加密，对称加密
ACCESS_TOKEN_EXPIRE_MINUTES = 10  # token有效期10分钟
# REFRESH_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60  # 刷新token有效期7天
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 刷新token有效期7天

# 连接Redis数据库, redis是内存数据库，用于缓存数据，提高查询速度 # TODO: 上线时要注意修改Redis host和port 配置
redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)

# 获取token，从/login接口获取，从Authorization: Bearer xxxxxx中提取token，放到Depends()中
# **自动从 HTTP 请求头 `Authorization: Bearer xxxxxx` 里面把 token 提取出来**，配合 `Depends()` 使用
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# 创建token,
# datetime → 代表某一个时间点（比如：2026‑08‑19 10:30:00）
# timedelta → 代表一段时长（比如：30 分钟、7 天）
# now = datetime.utcnow() # 当前UTC时间点,
# print(now)            # 2026‑08‑19 11:22:33.123456  人类可读时间
def create_access_token(payload: dict, expires_delta: timedelta) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # expire = expires_delta = timedelta(minutes = 5)
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_code = payload.copy()
    to_code["exp"] = expire
    token = jwt.encode(to_code, JWT_SECRET, algorithm=ALGORITHM)
    return token


# 创建长期的token
def create_refresh_token(payload: dict) -> str:
    to_code = payload.copy()
    # 如果统一用分钟的话，minutes = 7*24*60分钟, days = 7天
    to_code["exp"] = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    token = jwt.encode(to_code, JWT_SECRET, algorithm=ALGORITHM)
    return token


# 校验token, 获取用户信息payload, 失败抛异常，等价node的jwt.verify"
def verify_jwt_token(token: str) -> str:
    # 校验token是否正确
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:  # token过期,jwt自带的方法 等价于 get_token_remain_seconds 这个函数
        raise HTTPException(status_code=401, detail="令牌过期11111")
    except jwt.InvalidTokenError:  # token无效,jwt自带的方法
        raise HTTPException(status_code=401, detail="令牌无效2222222")


# 获取token剩余秒数,还有多少秒过期， 单位：秒, 负数表示已过期, 正数表示剩余秒数, 0表示过期
def get_token_remain_seconds(token: str) -> int:
    # 解析token，获取过期时间
    payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    exp = payload["exp"]
    print("exp=============?", exp)
    exp_datetime = datetime.fromtimestamp(exp)
    return (exp_datetime - datetime.now()).total_seconds()


# 保存刷新token到redis, key=user_id, value=token, ttl=7天
def save_refresh_token_to_redis(refresh_token: str, user_id: str):
    redis_client.setex(f"refresh_token:{user_id}", timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), refresh_token)
    # 下面是 等价写法 set
    # redis_client.set(f"refresh_token:{user_id}", refresh_token, ex=imedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


def get_refresh_token_from_redis(user_id: str) -> str:
    return redis_client.get(f"refresh_token:{user_id}")


def delete_refresh_token_from_redis(user_id: str):
    redis_client.delete(f"refresh_token:{user_id}")


# # 用户登出时，把未过期的 access/refresh 放入黑名单，key=token，value=1，ttl=token 剩余有效期秒
def add_access_token_to_blacklist(token: str):
    # left_seconds 剩余时间，存到redis中，redis里面过期数据会自动删除
    left_seconds = get_token_remain_seconds(token)
    # 如果没有过期，就加入黑名单， 过期了，就不用做任何处理
    if left_seconds > 0:
        # redis_client.set(token, token, ex=left_seconds)
        redis_client.setex(f"black:{token}", left_seconds, "1")


# 判断token是否在黑名单中
def is_token_blacklist(token: str) -> bool:
    # 从redis中获取token，判断是否存在
    # return redis_client.exists(f"black:{token}") > 0
    if redis_client.get(f"black:{token}") is not None:
        return True
    return False


# 获取当前用户信息, 就是鉴权，判断token是否有效
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # 校验token是否在黑名单中
    if is_token_blacklist(token):
        raise HTTPException(status_code=401, detail="token在黑名单中")
    payload = verify_jwt_token(token)
    user_id = payload.get("user_id")
    username: str = payload.get("username")
    # role: str = payload.get("role")
    if not user_id:
        raise HTTPException(status_code=401, detail="无效凭证")
    return {"user_id": user_id, "username": username, "token_exp": payload["exp"]}


class baseData(BaseModel):
    username: str
    password: str


class loginData(baseData):
    code: str | None = None


class registerData(baseData):
    confirmPwd: str | None = None
    email: str | None = None


class UserItem(BaseModel):
    username: Annotated[str, Field(None, description="用户名")] = None
    status: Annotated[int | None, Field(None, description="状态")] = None
    page: Annotated[int, Field(1, description="页码")] = None
    pageSize: Annotated[int, Field(10, description="每页条数")] = None
    start_date: Annotated[str | None, Field(None, description="开始时间")] = None
    end_date: Annotated[str | None, Field(None, description="结束时间")] = None


class AdminCreateUser(BaseModel):
    username: str
    password: str
    email: str | None = None
    role: int = 0
    status: int = 1


class AdminUpdateUser(BaseModel):
    email: str | None = None
    password: str | None = None
    role: int | None = None
    status: int | None = None
    cname: str | None = None


@router.post("/login")
@record_oper_log(OperLogAnno(title="登录", log_type="登录"))
async def login(_req: Request, _bt: BackgroundTasks, data: loginData, db: AsyncSession = Depends(get_db)):
    # 1: 校验用户名是否存在
    stmt = Select(User).where(User.username == data.username)
    result = await db.execute(stmt)
    user = result.scalar()
    if user is None:
        return {"msg": "用户名不存在", "code": 400}
    # 2: 校验密码是否正确 ,bcrypt 加密密码
    checkPassword = checkpw(data.password.encode("utf-8"), user.password.encode("utf-8"))
    # True $2b$10$0qmWVt6aWKrDujtC.f3CwOwJiOH9sut37KecfN3kq64E68/vDCOdi
    print("checkPassword==============333>", checkPassword, user)
    if not checkPassword:
        return {"msg": "用户名或密码错误", "code": 400}

    # 3: 生成access_token和refresh_token
    payload = {
        "user_id": user.id,
        "username": user.username,
    }

    access_token = create_access_token(payload, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(payload)

    # 4: 将refresh_token 添加到redis：key=refresh_token, value=refresh_token, ttl=refresh_token 过期时间
    save_refresh_token_to_redis(refresh_token, user.id)

    # 校验状态是否正常
    # if user.status != User.ACTIVE:
    #     return {'msg': '用户已被禁用', 'code': 400}
    return {
        "code": 200,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "username": user.username,
        "user_id": user.id,
    }


class RefreshToken(BaseModel):
    refresh_token: str


# 刷新token, 从refresh_token中获取user_id, 生成新的access_token
# 这个token的来源是前端传的refresh_token, 用于刷新access_token, 用于后续的请求
@router.post("/refresh")
async def refresh_token(data: RefreshToken):
    if not data.refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token不能为空123")

    # 1: 校验refresh_token是否合法、过期, 同时从中获取用户信息
    payload = verify_jwt_token(data.refresh_token)
    user_id = payload.get("user_id")

    # 2: 取出redis中保存的refresh_token, 校验是否与前端传的refreshtoken是否一致
    saved_refresh_token = get_refresh_token_from_redis(user_id)
    print("saved_refresh_token==============333>", saved_refresh_token, user_id)
    print("data.refresh_token==============333>", data.refresh_token)
    if saved_refresh_token != data.refresh_token:
        raise HTTPException(status_code=401, detail="刷新令牌无效，请重新登录456")

    # 3: 生成新的access_token, 并返回给前端
    access_token = create_access_token(payload, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {
        "code": 200,
        "access_token": access_token,
        "refresh_token": data.refresh_token,
    }


@router.post("/register")
@record_oper_log(OperLogAnno(title="注册", log_type="注册"))
async def register(data: registerData, db: AsyncSession = Depends(get_db)):
    # 1: 检查用户是否存在
    stmt = Select(User).where(User.username == data.username)
    result = await db.execute(stmt)
    user = result.scalar()
    if user is not None:
        return {"msg": "用户名已存在!", "code": 400}
    # 2: 对密码进行加密
    salt = gensalt()
    hashedPwd = hashpw(data.password.encode(), salt).decode()
    user = User(
        username=data.username,
        password=hashedPwd,
        email=data.email,
        # status=User.ACTIVE
    )
    db.add(user)
    await db.commit()
    # 3: 保存用户到数据库
    return {"msg": "注册成功", "code": 200, "data": []}


# 退出的时候，删除redis里面的refresh_token, 并将access_token添加到黑名单list中, 后面的请求会立即过期
@router.get("/logout")
@record_oper_log(OperLogAnno(title="退出", log_type="退出"))
async def logout(access_token: str = Depends(oauth2_scheme), user=Depends(get_current_user)):
    delete_refresh_token_from_redis(user.id)
    add_access_token_to_blacklist(access_token)
    return {"msg": "退出成功", "code": 200, "data": []}


# ========== 新增：强制踢人下线接口（管理员用） ==========
@router.post("/admin/kick-user")
def kick_user(target_user_id: int, user_id=Depends(get_current_user)):
    """
    管理员强制把某个用户踢下线
    注意：只能废掉refresh_token；
    已经颁发出去还没过期的access_token，因为JWT无状态，无法批量作废！
    👉 解决方案：短access_token有效期（5分钟以内）， 或者维护一个用户全局黑名单集合
    """
    # if admin_user["role"] != "admin":
    #     raise HTTPException(status_code=403, detail="无权限")
    redis_client.delete(f"refresh:{user_id.id}")
    # access_token = create_access_token({"user_id": user_id.id, "username": user_id.username}, ACCESS_TOKEN_EXPIRE_MINUTES)
    # add_access_token_to_blacklist(access_token)
    return {"code": 200, "msg": f"用户{target_user_id}已被强制下线"}


# 获取用户列表， 分页查询所有用户
@router.post("/user")
@record_oper_log(OperLogAnno(title="获取用户列表", log_type="获取用户列表"))
async def getUser(user: UserItem, db: AsyncSession = Depends(get_db)):
    #    stmt = Select(User)
    stmt = (
        Select(User, func.count(Article.id).label("article_count"))
        .outerjoin(Article, Article.user_id == User.id)
        .group_by(User.id)
        .where(User.is_delete == 1)
    )

    if user.username:
        #    stmt = stmt.where(User.username.like(f"%{user.username}%"))
        stmt = stmt.where(User.username.contains(user.username))
    if user.status is not None:
        stmt = stmt.where(User.status == user.status)
    if user.page is not None and user.pageSize is not None:
        offset = (user.page - 1) * user.pageSize
        limit = user.pageSize
        stmt = stmt.offset(offset).limit(limit)
    if user.start_date and user.end_date:
        stmt = stmt.where(User.created_at.between(user.start_date, user.end_date))
    result = await db.execute(stmt)
    #    users = result.scalars().all()
    users = result.all()
    #    获取总数
    #    total = await db.execute(func.count(User.id))
    #    total = total.scalar()
    #    简写的方法，等价与上面的方法
    #    total = await db.scalar(func.count(User.id))  #没有条件查询的时候这样写
    total_stmt = select(func.count(User.id)).where(User.is_delete == 1)
    total = await db.scalar(total_stmt)
    # 删除密码，
    #    for user in users:
    #        del user.password

    # 3. 解包元组：(User对象, article_count)
    data_list = []
    for u, article_count in users:
        data_list.append(
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "avater": u.avater,
                "role": u.role,
                "cname": u.cname,
                "status": u.status,
                "created_at": u.created_at,
                "article_count": article_count,  # ← 文章数
            }
        )

    return {"msg": "获取用户列表成功", "code": 200, "data": data_list, "total": total}


# 禁用用户
@router.get("/forbidden/{id}")
@record_oper_log(OperLogAnno(title="禁用用户", log_type="禁用用户"))
async def forbiddenUser(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    user = await db.get(User, id)
    if user is None:
        return {"msg": "用户不存在", "code": 404}
    user.status = 0
    await db.commit()
    db.refresh(user)
    return {"msg": "用户已被禁用", "code": 200, "data": []}


# 启用用户
@router.get("/active/{id}")
@record_oper_log(OperLogAnno(title="启用用户", log_type="启用用户"))
async def activeUser(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    user = await db.get(User, id)
    if user is None:
        return {"msg": "用户不存在", "code": 404}
    user.status = 1
    await db.commit()
    # 刷新数据，确保获取到最新的用户状态
    db.refresh(user)
    return {"msg": "用户已被启用", "code": 200, "data": []}


# 删除用户
@router.get("/delete/{id}")
@record_oper_log(OperLogAnno(title="删除用户", log_type="删除用户"))
async def deleteUser(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    user = await db.get(User, id)
    if user is None:
        return {"msg": "用户不存在", "code": 404}
    user.is_delete = 0
    await db.commit()
    # 刷新数据，确保获取到最新的用户状态
    db.refresh(user)
    return {"msg": "用户已被删除", "code": 200, "data": []}


@router.post("/addUser")
@record_oper_log(OperLogAnno(title="新增用户", log_type="新增用户"))
async def addUser(
    data: CreateUser,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    # 1) 用户名/邮箱重复校验
    stmt = select(User).where(User.username == data.username)
    exists = await db.scalar(stmt)
    if exists is not None:
        return {"msg": "用户名已存在", "code": 400}
    if data.email:
        stmt2 = select(User).where(User.email == data.email)
        exists2 = await db.scalar(stmt2)
        if exists2 is not None:
            return {"msg": "邮箱已被注册", "code": 400}


def _normalize_role(role) -> int:
    """前端可能传字符串(如 'admin'/'user') 或数字，统一转成数字存库"""
    role_map = {
        "admin": 1,
        "super_admin": 1,
        "super": 1,
        "editor": 2,
        "auditor": 3,
        "user": 4,
        "normal": 4,
        "vip": 5,
        "maintenance": 6,
        "ops": 6,
        "finance": 7,
        "user_admin": 8,
        "guest": 9,
        "banned": 10,
        "ban": 10,
    }
    if isinstance(role, int):
        return role
    if isinstance(role, str):
        if role.isdigit():
            return int(role)
        return role_map.get(role.lower(), 4)
    return 4


# 管理员新增用户
@router.post("/createUser")
@record_oper_log(OperLogAnno(title="管理员新增用户", log_type="新增用户"))
async def admin_create_user(
    data: AdminCreateUser,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    # 1) 用户名/邮箱重复校验
    stmt = select(User).where(or_(User.username == data.username, User.email == data.email))
    exists = await db.scalar(stmt)
    if exists is not None:
        return {"msg": "用户名或邮箱已存在", "code": 400}
    salt = gensalt()
    hashed_pwd = hashpw(data.password.encode(), salt).decode()
    user = User(
        username=data.username,
        password=hashed_pwd,
        email=data.email or "",
        avater="",
        cname="",
        role=_normalize_role(data.role),
        status=data.status if data.status is not None else 1,
        is_delete=1,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"msg": "新增用户成功", "code": 200, "data": {"id": user.id}}


# 管理员编辑用户
@router.post("/updateUser/{id}")
@record_oper_log(OperLogAnno(title="管理员编辑用户", log_type="编辑用户"))
async def updateUser(
    id: int,
    data: AdminUpdateUser,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    user = await db.get(User, id)
    if user is None or user.is_delete != 1:
        return {"msg": "用户不存在", "code": 404}

    if data.email is not None and data.email != user.email:
        stmt = select(User).where(and_(User.is_delete == 1, User.email == data.email, User.id != id))
        exists = await db.scalar(stmt)
        if exists is not None:
            return {"msg": "邮箱已被其他账号使用", "code": 400}
        user.email = data.email

    if data.role is not None:
        user.role = _normalize_role(data.role)

    if data.status is not None:
        user.status = data.status

    await db.commit()
    return {"msg": "修改成功", "code": 200, "data": []}


# @router.get("/")
# async def getHome():
#     return {'msg': 'hello world'}
