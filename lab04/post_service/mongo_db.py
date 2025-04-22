from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "post_db")

client = MongoClient(MONGO_URL)
db = client[MONGO_DB_NAME]
posts_collection = db["posts"]
