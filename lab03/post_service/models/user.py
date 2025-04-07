from sqlalchemy import Column, Integer, String, Text
from db import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    name = Column(String(100))
    surname = Column(String(100))
    email = Column(String(100))
    age = Column(Integer)