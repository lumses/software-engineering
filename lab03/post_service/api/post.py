from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List

from models.post import PostModel
from models.user import UserModel
from schemas.post import Post, PostCreate
from .dependencies import get_current_client, get_db

post_router = APIRouter()

@post_router.post(
    "/{user_id}",
    response_model=Post,
    status_code=201,
    responses={
        201: {"description": "The post was created successfully"},
        404: {"description": "User not found"},
        401: {"description": "Invalid token"},
    }
)
async def create_post(
    user_id: int,
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_client)
):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_post = PostModel(id=uuid4(), user_id=user_id, content=post.content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
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
async def get_posts(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_client)
):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return db.query(PostModel).filter(PostModel.user_id == user_id).all()
