from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

#Import database collections
from db import users_collection, artworks_collection, comments_collection, likes_collection

#Import model functions (some not finished rn)
from models.user import add_user, get_all_users, get_user_by_email, get_user_by_id, update_user
from models.artwork import add_artwork, get_all_artworks, search_artworks, update_artwork, delete_artwork, get_artwork_by_id, get_artworks_by_artist, filter_artworks
from models.comment import add_comment, get_comments_by_artwork, delete_comment
from models.like import add_like, remove_like, get_likes_count, user_has_liked

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

#Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data['email']
        self.bio = user_data.get('bio', '')
        self.profile_image = user_data.get('profile_image', '')
        self.banner_image = user_data.get('banner_image', '')
        self.social_links = user_data.get('social_links', {})

@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(user_id)
    if user_data:
        return User(user_data)
    return None