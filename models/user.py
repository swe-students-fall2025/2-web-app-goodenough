from db import users_collection
from bson.objectid import ObjectId
from datetime import datetime, timezone

def add_user(username, email, password_hash):
    user_data = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "bio": "",
        "profile_image": "/static/images/profile.png",  #default
        "banner_image": "",   
        "social_links": {},
        "created_at": datetime.now(timezone.utc)
    }
    return users_collection.insert_one(user_data)

def get_all_users():
    return list(users_collection.find())

def get_user_by_email(email):
    return users_collection.find_one({"email": email})

def get_user_by_id(user_id):
    try:
        return users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        return None

def update_user(user_id, update_data):
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )