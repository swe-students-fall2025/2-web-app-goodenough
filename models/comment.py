# models/comment.py
from db import comments_collection
from bson import ObjectId
from datetime import datetime, timezone

def _to_object_id(v):
    if isinstance(v, ObjectId):
        return v
    try:
        return ObjectId(v)
    except Exception:
        return v

# -- comments
def add_comment(artwork_id, user_id, text):
    """Create a comment tied to an artwork and user."""
    doc = {
        "artwork_id": _to_object_id(artwork_id),
        "user_id": _to_object_id(user_id),
        "text": text,
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
    }
    res = comments_collection.insert_one(doc)
    return {"acknowledged": res.acknowledged, "_id": res.inserted_id}

def get_comments_for_artwork(artwork_id, limit=50, skip=0, sort_asc=True):
    a_id = _to_object_id(artwork_id)
    sort_dir = 1 if sort_asc else -1
    cursor = comments_collection.find({"artwork_id": a_id}).sort("created_at", sort_dir).skip(skip).limit(limit)
    return list(cursor)

def update_comment(comment_id, user_id, new_text, admin=False):
    """Update a comment's text. Only the owner can edit unless admin=True."""
    c_id = _to_object_id(comment_id)
    u_id = _to_object_id(user_id)
    filt = {"_id": c_id}
    if not admin:
        filt["user_id"] = u_id
    update = {"$set": {"text": new_text, "updated_at": datetime.now(timezone.utc)}}
    return comments_collection.update_one(filt, update)

def delete_comment(comment_id, user_id=None, admin=False):
    """Delete a comment. Only the owner can delete unless admin=True."""
    c_id = _to_object_id(comment_id)
    filt = {"_id": c_id}
    if not admin and user_id is not None:
        filt["user_id"] = _to_object_id(user_id)
    return comments_collection.delete_one(filt)

def count_comments(artwork_id):
    a_id = _to_object_id(artwork_id)
    return comments_collection.count_documents({"artwork_id": a_id})
