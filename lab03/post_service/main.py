from fastapi import FastAPI
from api.post import post_router

app = FastAPI(title="post_service")

app.include_router(post_router, prefix='/post', tags=['post'])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)