from db import comments_collection
from datetime import datetime, timezone
from bson.objectid import ObjectId


def add_comment(artwork_id, user_id, content):
    comment = {
        "artwork_id": artwork_id,
        "user_id": user_id,
        "content": content,
        "created_at": datetime.now(timezone.utc)
    }
    return comments_collection.insert_one(comment)


def get_comments_by_artwork(artwork_id):
    return list(comments_collection.find({"artwork_id": artwork_id}).sort("created_at", -1))


def get_comment_by_id(comment_id):
    return comments_collection.find_one({"_id": ObjectId(comment_id)})


def delete_comment(comment_id):
    return comments_collection.delete_one({"_id": ObjectId(comment_id)})


def get_comments_by_user(user_id):
    return list(comments_collection.find({"user_id": user_id}).sort("created_at", -1))