from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List
from pymongo import MongoClient
from mongo_db import posts_collection
import os

from schemas.post import Post, PostCreate
from .dependencies import get_current_client, get_db
from models.user import UserModel

post_router = APIRouter()

def post_serializer(post) -> dict:
    post["id"] = str(post["_id"])
    del post["_id"]
    return post

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
    user_id: str,
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_client)
):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_post = {
        "user_id": user_id,
        "content": post.content,
    }
    result = posts_collection.insert_one(new_post)
    return Post(id=str(result.inserted_id), **new_post)

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
    user_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_client)
):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    posts = list(posts_collection.find({"user_id": user_id}))
    return [post_serializer(p) for p in posts]
