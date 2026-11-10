from fastapi import FastAPI
from routes.user import router as user_router
from routes.articles import router as articles_router
from routes.category import router as category_router
from routes.role import router as role_router
from routes.log import router as log_router

app = FastAPI(version="1.0", title="博客管理的后台", description="一个小博客的后台")

app.include_router(user_router)
app.include_router(articles_router)
app.include_router(category_router)
app.include_router(role_router)
app.include_router(log_router)
