from fastapi import FastAPI
from api.post import post_router
from init_mongo_db import init_data

app = FastAPI(title="post_service")

app.include_router(post_router, prefix='/post', tags=['post'])

@app.on_event("startup")
def on_startup():
    init_data()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)