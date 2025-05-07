from pydantic import BaseModel, Field
from typing import Optional

class PostCreate(BaseModel):
    content: str

class Post(PostCreate):
    id: Optional[str] = None
    user_id: str