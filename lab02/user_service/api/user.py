from fastapi import APIRouter, HTTPException, Response, Depends, status
from models.user import User, UserCreate, UserResponse, SearchUser
from typing import List, Optional
from .dependencies import get_current_client
from .dependencies import pwd_context
import re

user_router = APIRouter()

users_db = {
    "admin": User(id=1, login="admin", password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", name="John", surname="Doe", email="admin@example.com", age=30),
    "user": User(id=2, login="user", password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", name="John", surname="Doe", email="admin@example.com", age=30)
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
async def create_user(user: UserCreate):
    if user.login in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        id=len(users_db) + 1,
        login=user.login,
        password=hashed_password,
        name=user.name,
        surname=user.surname,
        email=user.email,
        user=user.age
    )  
    users_db[user.login] = new_user    
    return UserResponse(**new_user.model_dump(exclude={"password"}))

@user_router.post(
    "/search", 
    response_model=List[UserResponse],
    responses={
        200: {"description": "Search processed"},
        401: {"description": "Invalid token"},
        404: {"description": "Users not found"},
    }
)
async def search_user(searching: SearchUser, current_user: str = Depends(get_current_client)):
    results = []
    for user in users_db.values():
        user_info = user.dict(exclude={"password"})
        for field in searching.fields:
            user_value = user_info.get(field, '')
            if isinstance(user_value, str):
                if re.search(searching.value, user_value, re.IGNORECASE):
                    results.append(UserResponse(**user_info))
                    break
            elif isinstance(user_value, int):
                if str(user_value) == searching.value:
                    results.append(UserResponse(**user_info))
                    break

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
async def get_user(user_id: int, current_user: str = Depends(get_current_client)):
    for user in users_db.values():
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@user_router.get("", response_model=List[UserResponse])
def get_users(current_user: str = Depends(get_current_client)):
    return [UserResponse(**user.model_dump(exclude={"password"})) for user in users_db.values()]

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
async def delete_user(user_id: int, current_user: str = Depends(get_current_client)):
    target_login = next((login for login, user in users_db.items() if user.id == user_id), None)
    if not target_login:
        raise HTTPException(status_code=404, detail="User wasn't found")
    users_db.pop(target_login)
    return Response(status_code=204)
