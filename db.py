from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DBNAME = os.getenv("MONGO_DBNAME")

_client = MongoClient(MONGO_URI)
_db = _client[MONGO_DBNAME]

users_collection = _db.get_collection['users']
artworks_collection = _db.get_collection['artworks']
comments_collection = _db.get_collection['comments']
likes_collection = _db.get_collection['likes']

# Define function to return database instance
def get_db():
    return _db

# Define function to return the MongoClient instance
def get_client():
    return _client
