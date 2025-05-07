from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    login: str
    password: str
    name: Optional[str]
    surname: Optional[str]
    email: Optional[str]
    age: Optional[int]

class UserResponse(BaseModel):
    id: int
    login: str
    name: Optional[str]
    surname: Optional[str]
    email: Optional[str]
    age: Optional[int]

    class Config:
        orm_mode = True

class SearchUser(BaseModel):
    fields: List[str]
    value: str