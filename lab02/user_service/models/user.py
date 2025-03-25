from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    id: int
    login: str
    password: str
    name: str
    surname: str
    email: str
    age: Optional[int] = None

class UserCreate(BaseModel):
    login: str
    password: str
    name: str
    surname: str
    email: str
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    login: str
    name: str
    surname: str
    email: str
    age: Optional[int] = None

class SearchUser(BaseModel):
    fields: List[str]
    value: str      