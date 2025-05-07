from fastapi import APIRouter, HTTPException, Response, Depends, status
from models.user import UserModel
from sqlalchemy.orm import Session
from redis import Redis
from db import SessionLocal
from schemas.user import UserCreate, UserResponse, SearchUser
from typing import List, Optional
from .dependencies import get_current_client, get_db
from .dependencies import pwd_context
import re
import json

user_router = APIRouter()
redis_client = Redis(host='redis', port=6379, decode_responses=True)

def user_to_dict(user: UserModel) -> dict:
    return {
        "id": user.id,
        "login": user.login,
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "age": user.age,
    }

@user_router.post(
    "",
    summary="Create a new user",
    response_model=UserResponse,
    responses={
        201: {"description": "User successfully created"},
        400: {'description': 'User already exists'},
    },
    status_code=201
)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.login == user.login).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = UserModel(**user.dict())
    new_user.password = hashed_password

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@user_router.post(
    "/search",
    response_model=List[UserResponse],
    responses={
        200: {"description": "Search processed"},
        401: {"description": "Invalid token"},
        404: {"description": "Users not found"},
    }
)
async def search_user(
    searching: SearchUser,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_client)
):
    query = db.query(UserModel)
    users = query.all()

    results = []
    for user in users:
        for field in searching.fields:
            user_value = getattr(user, field, None)
            if isinstance(user_value, str):
                if re.search(searching.value, user_value, re.IGNORECASE):
                    results.append(user)
                    break
            elif isinstance(user_value, int):
                if str(user_value) == searching.value:
                    results.append(user)
                    break

    if not results:
        raise HTTPException(status_code=404, detail="No users found")

    return results

@user_router.post(
    "/search-redis",
    response_model=List[UserResponse],
    responses={
        200: {"description": "Search processed"},
        401: {"description": "Invalid token"},
        404: {"description": "Users not found"},
    }
)
async def search_user_redis(
    searching: SearchUser,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_client)
):
    results = []

    for key in redis_client.scan_iter("user:*"):
        cached_user_json = redis_client.get(key)
        if not cached_user_json:
            continue

        user_data = json.loads(cached_user_json)

        for field in searching.fields:
            user_value = user_data.get(field)
            if isinstance(user_value, str) and re.search(searching.value, user_value, re.IGNORECASE):
                results.append(user_data)
                break
            elif isinstance(user_value, int) and str(user_value) == searching.value:
                results.append(user_data)
                break

    if results:
        return results

    db_users = db.query(UserModel).all()
    for user in db_users:
        user_dict = user_to_dict(user)
        for field in searching.fields:
            user_value = user_dict.get(field)
            if isinstance(user_value, str) and re.search(searching.value, user_value, re.IGNORECASE):
                results.append(user_dict)
                break
            elif isinstance(user_value, int) and str(user_value) == searching.value:
                results.append(user_dict)
                break

        redis_client.set(f"user:{user.id}", json.dumps(user_dict), ex=600)

    if not results:
        raise HTTPException(status_code=404, detail="No users found")

    return results

@user_router.get(
    '/{user_id}',
    response_model=UserResponse,
    responses={
        200: {"description": "User found"},
        401: {"description": "Invalid token"},
        404: {"description": "User not found"},
    }
)
async def get_user(user_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_client)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_router.get("", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: str = Depends(get_current_client)):
    users = db.query(UserModel).all()
    return users

@user_router.delete(
    '/{user_id}',
    summary='Delete current user',
    response_class=Response,
    responses={
        204: {"description": "User deleted"},
        401: {"description": "No access"},
        404: {"description": "User not found"},
    }
)
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_client)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User wasn't found")

    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
