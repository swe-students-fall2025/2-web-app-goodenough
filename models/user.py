# models/user.py
from db import users_collection
from datetime import datetime, timezone

# -- users
def add_user(username, email, password_hash, bio="", profile_image=""):
    user = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "bio": bio,
        "profile_image": profile_image,
        "created_at": datetime.now(timezone.utc)
    }
    return users_collection.insert_one(user)

def get_all_users():
    return list(users_collection.find())