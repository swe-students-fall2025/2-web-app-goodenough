from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "enoughart")

_client = MongoClient(MONGO_URI)
_db = _client[DB_NAME]

users_collection = _db.get_collection("users")
artworks_collection = _db.get_collection("artworks")
comments_collection = _db.get_collection("comments")
likes_collection = _db.get_collection("likes")

def get_db():
    return _db

def get_client():
    return _client