from db import likes_collection
from datetime import datetime, timezone
from bson.objectid import ObjectId


def add_like(artwork_id, user_id):
    existing_like = likes_collection.find_one({
        "artwork_id": artwork_id,
        "user_id": user_id
    })
    
    if existing_like:
        return None
    
    like = {
        "artwork_id": artwork_id,
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc)
    }
    return likes_collection.insert_one(like)


def remove_like(artwork_id, user_id):
    return likes_collection.delete_one({
        "artwork_id": artwork_id,
        "user_id": user_id
    })


def get_likes_count(artwork_id):
    return likes_collection.count_documents({"artwork_id": artwork_id})


def user_has_liked(artwork_id, user_id):
    like = likes_collection.find_one({
        "artwork_id": artwork_id,
        "user_id": user_id
    })
    return like is not None


def get_likes_by_user(user_id):
    return list(likes_collection.find({"user_id": user_id}).sort("created_at", -1))