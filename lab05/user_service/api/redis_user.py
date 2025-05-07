from fastapi import APIRouter, HTTPException, Response, Depends, status
from models.user import UserModel
from sqlalchemy.orm import Session
from redis import Redis
from db import SessionLocal
from schemas.user import UserCreate, UserResponse, SearchUser
from typing import List
from .dependencies import get_current_client, get_db, pwd_context
import re
import json

redis_user_router = APIRouter()
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

@redis_user_router.post(
    "",
    summary="Create a new user",
    response_model=UserResponse,
    responses={201: {"description": "User successfully created"}, 400: {'description': 'User already exists'}},
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

    redis_client.set(f"user:{new_user.id}", json.dumps(user_to_dict(new_user)), ex=600)
    return new_user

@redis_user_router.post(
    "/cached-search",
    response_model=List[UserResponse],
    responses={
        200: {"description": "Search processed"},
        401: {"description": "Invalid token"},
        404: {"description": "Users not found"},
    }
)
async def cached_search_user(
    searching: SearchUser,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_client)
):
    # Формируем ключ кэша: например, search:login,name:user1
    fields_str = ",".join(sorted(searching.fields))
    search_value = searching.value.strip().lower()
    cache_key = f"search:{fields_str}:{search_value}"

    # Пробуем получить из кэша
    cached = redis_client.get(cache_key)
    if cached:
        print(f"[CACHE HIT] key={cache_key}")
        return json.loads(cached)

    print(f"[CACHE MISS] key={cache_key}, querying DB...")

    # Ищем в БД
    results = []
    db_users = db.query(UserModel).all()
    for user in db_users:
        user_dict = {
            "id": user.id,
            "login": user.login,
            "name": user.name,
            "surname": user.surname,
            "email": user.email,
            "age": user.age,
        }
        for field in searching.fields:
            user_value = user_dict.get(field)
            if isinstance(user_value, str) and re.search(search_value, user_value, re.IGNORECASE):
                results.append(user_dict)
                break
            elif isinstance(user_value, int) and str(user_value) == search_value:
                results.append(user_dict)
                break

    if not results:
        raise HTTPException(status_code=404, detail="No users found")

    # Сохраняем в Redis с TTL = 10 мин
    redis_client.set(cache_key, json.dumps(results), ex=600)
    print(f"[CACHE SET] key={cache_key} count={len(results)}")

    return results

@redis_user_router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={200: {"description": "User found"}, 401: {"description": "Invalid token"}, 404: {"description": "User not found"}}
)
async def get_user(user_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_client)):
    cache_key = f"user:{user_id}"

    cached_user = redis_client.get(cache_key)
    if cached_user:
        return UserResponse.parse_raw(cached_user)

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    redis_client.set(cache_key, json.dumps(user_to_dict(user)), ex=600)
    return user

@redis_user_router.get("", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: str = Depends(get_current_client)):
    users = db.query(UserModel).all()
    return users

@redis_user_router.delete(
    "/{user_id}",
    summary="Delete current user",
    response_class=Response,
    responses={204: {"description": "User deleted"}, 401: {"description": "No access"}, 404: {"description": "User not found"}}
)
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_client)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User wasn't found")

    db.delete(user)
    db.commit()

    redis_client.delete(f"user:{user_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
