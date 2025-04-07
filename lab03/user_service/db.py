from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


engine = create_engine(
    URL.create(
        drivername='postgresql',
        username='postgres',
        password='postgres',
        host='db',
        port='5432',
        database='user_db',
    )
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
