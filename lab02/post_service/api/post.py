from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from uuid import uuid4
from .dependencies import get_current_client

from models.post import Post, PostCreate

post_router = APIRouter()

posts_db = {
    1: [],
    2: []
}

@post_router.post(
    "/{user_id}", 
    response_model=Post,
    responses={
        201: {"description": "The post was created successfully"},
        404: {"description": "User not found"},
        401: {"description": "Invalid token"},
    }
)
async def create_post(user_id: int, post: PostCreate, current_user: str = Depends(get_current_client)):
    if user_id not in posts_db:
        raise HTTPException(status_code=404, detail="User not found")
    post_id = str(uuid4())
    new_post = Post(id=post_id, user_id=user_id, content=post.content)    
    posts_db[user_id].append(new_post)
    
    return new_post

@post_router.get(
    "/{user_id}", 
    response_model=List[Post],
    responses={
        200: {"description": "List of posts"},
        404: {"description": "User not found"},
        401: {"description": "Invalid token"},
    }
)
async def get_posts(user_id: int, current_user: str = Depends(get_current_client)):
    if user_id not in posts_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return posts_db[user_id]