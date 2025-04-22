from pymongo import MongoClient, ASCENDING
from mongo_db import posts_collection
import os

sample_posts = [
    {"user_id": "1", "content": "Тестовый пост для лабораторной"},
    {"user_id": "1", "content": "Еще один тестовый пост для лабораторной"},
    {"user_id": "2", "content": "И третий тестовый"},
]

def init_data():
    posts_collection.create_index([("user_id", ASCENDING)])
    if posts_collection.count_documents({}) == 0:
        posts_collection.insert_many(sample_posts)
