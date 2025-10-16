# models/like.py
from db import likes_collection
from bson import ObjectId
from datetime import datetime, timezone

def _to_object_id(v):
    if isinstance(v, ObjectId):
        return v
    try:
        return ObjectId(v)
    except Exception:
        return v

# -- likes
def add_like(artwork_id, user_id):
    """Add a like for an artwork by a user. No-op if it already exists."""
    a_id = _to_object_id(artwork_id)
    u_id = _to_object_id(user_id)
    existing = likes_collection.find_one({"artwork_id": a_id, "user_id": u_id})
    if existing:
        return {"acknowledged": True, "already_liked": True, "_id": existing.get("_id")}
    doc = {
        "artwork_id": a_id,
        "user_id": u_id,
        "created_at": datetime.now(timezone.utc),
    }
    result = likes_collection.insert_one(doc)
    return {"acknowledged": result.acknowledged, "_id": result.inserted_id}

def remove_like(artwork_id, user_id):
    a_id = _to_object_id(artwork_id)
    u_id = _to_object_id(user_id)
    return likes_collection.delete_one({"artwork_id": a_id, "user_id": u_id})

def count_likes(artwork_id):
    a_id = _to_object_id(artwork_id)
    return likes_collection.count_documents({"artwork_id": a_id})

def get_likes_for_artwork(artwork_id, limit=100, skip=0):
    a_id = _to_object_id(artwork_id)
    cursor = likes_collection.find({"artwork_id": a_id}).sort("created_at", 1).skip(skip).limit(limit)
    return list(cursor)

def has_user_liked(artwork_id, user_id):
    a_id = _to_object_id(artwork_id)
    u_id = _to_object_id(user_id)
    return likes_collection.find_one({"artwork_id": a_id, "user_id": u_id}) is not None