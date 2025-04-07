from pydantic import BaseModel
from uuid import UUID

class PostCreate(BaseModel):
    content: str

class Post(PostCreate):
    id: UUID
    user_id: int

    class Config:
        orm_mode = True