from pydantic import BaseModel

class PostCreate(BaseModel):
    content: str

class Post(PostCreate):
    id: str
    user_id: int