# models/user.py
from db import users_collection

# -- users
def add_user(username, email, password_hash, bio="", profile_image=""):
    user = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "bio": bio,
        "profile_image": profile_image,
    }
    return users_collection.insert_one(user)

