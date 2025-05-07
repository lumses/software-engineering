from fastapi import FastAPI
from api.auth import auth_router
from api.user import user_router
from api.redis_user import redis_user_router

app = FastAPI(title="User Service API")

app.include_router(auth_router, prefix='/auth', tags=['auth'])
app.include_router(user_router, prefix='/users', tags=['users'])
app.include_router(redis_user_router, prefix='/users-redis', tags=['users-redis'])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)