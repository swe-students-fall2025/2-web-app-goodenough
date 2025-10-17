from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

from db import users_collection, artworks_collection, comments_collection, likes_collection
from datetime import datetime, timezone

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data['email']
        self.bio = user_data.get('bio', '')
        self.profile_image = user_data.get('profile_image', '/static/images/profile.png')
        self.banner_image = user_data.get('banner_image', '')
        self.social_links = user_data.get('social_links', {})

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = users_collection.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data)
    except:
        pass
    return None

def get_user_by_email(email):
    return users_collection.find_one({"email": email})

def get_user_by_id(user_id):
    try:
        return users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        return None

def get_artwork_by_id(artwork_id):
    try:
        return artworks_collection.find_one({"_id": ObjectId(artwork_id)})
    except:
        return None

@app.route('/')
def index():
    artworks = list(artworks_collection.find().sort("created_at", -1))
    
    for artwork in artworks:
        artwork['artist'] = get_user_by_id(artwork['artist_id'])
        artwork['likes_count'] = likes_collection.count_documents({"artwork_id": artwork['_id']})
        artwork['comments_count'] = comments_collection.count_documents({"artwork_id": artwork['_id']})
        if current_user.is_authenticated:
            artwork['user_liked'] = likes_collection.find_one({
                "artwork_id": artwork['_id'], 
                "user_id": ObjectId(current_user.id)
            }) is not None
    
    return render_template('home.html', artworks=artworks)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('signup'))
        
        if get_user_by_email(email):
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
        
        password_hash = generate_password_hash(password)
        user_data = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "bio": "",
            "profile_image": "/static/images/profile.png",
            "banner_image": "",
            "social_links": {},
            "created_at": datetime.now(timezone.utc)
        }
        users_collection.insert_one(user_data)
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_data = get_user_by_email(email)
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data)
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/profile/<user_id>')
def profile(user_id):
    """View user profile"""
    user_data = get_user_by_id(user_id)
    if not user_data:
        flash('User not found', 'error')
        return redirect(url_for('index'))
    
    artworks = list(artworks_collection.find({"artist_id": user_id}).sort("created_at", -1))
    
    for artwork in artworks:
        artwork['likes_count'] = likes_collection.count_documents({"artwork_id": artwork['_id']})
        artwork['comments_count'] = comments_collection.count_documents({"artwork_id": artwork['_id']})
    
    return render_template('profile.html', user=user_data, artworks=artworks)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit current user's profile"""
    if request.method == 'POST':
        update_data = {
            'bio': request.form.get('bio', ''),
            'banner_image': request.form.get('banner_image', ''),
            'profile_image': request.form.get('profile_image', '/static/images/profile.png'),
            'social_links': {
                'instagram': request.form.get('instagram', ''),
                'twitter': request.form.get('twitter', ''),
                'website': request.form.get('website', '')
            }
        }
        users_collection.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": update_data}
        )
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile', user_id=current_user.id))
    
    user_data = get_user_by_id(current_user.id)
    return render_template('edit_profile.html', user=user_data)

@app.route('/artwork/add', methods=['GET', 'POST'])
@login_required
def add_artwork_route():
    """Add new artwork"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        tags = [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]
        medium = request.form.get('medium')
        year = request.form.get('year', type=int)
        price = request.form.get('price', type=float)
        process_images = [img.strip() for img in request.form.get('process_images', '').split(',') if img.strip()]
        
        artwork_data = {
            "artist_id": current_user.id,
            "title": title,
            "description": description,
            "image_url": image_url,
            "tags": tags,
            "medium": medium,
            "year": year,
            "price": price,
            "process_images": process_images,
            "created_at": datetime.now(timezone.utc)
        }
        artworks_collection.insert_one(artwork_data)
        
        flash('Artwork added successfully!', 'success')
        return redirect(url_for('profile', user_id=current_user.id))
    
    return render_template('add_artwork.html')

@app.route('/artwork/<artwork_id>')
def artwork_detail(artwork_id):
    """View artwork details"""
    artwork = get_artwork_by_id(artwork_id)
    if not artwork:
        flash('Artwork not found', 'error')
        return redirect(url_for('index'))
    
    artist = get_user_by_id(artwork['artist_id'])
    comments = list(comments_collection.find({"artwork_id": ObjectId(artwork_id)}).sort("created_at", 1))
    
    for comment in comments:
        comment['user'] = get_user_by_id(str(comment['user_id']))
    
    likes_count = likes_collection.count_documents({"artwork_id": ObjectId(artwork_id)})
    user_liked = False
    if current_user.is_authenticated:
        user_liked = likes_collection.find_one({
            "artwork_id": ObjectId(artwork_id),
            "user_id": ObjectId(current_user.id)
        }) is not None
    
    return render_template('artwork_detail.html', 
                         artwork=artwork, 
                         artist=artist, 
                         comments=comments,
                         likes_count=likes_count,
                         user_liked=user_liked)

@app.route('/artwork/<artwork_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_artwork(artwork_id):
    """Edit artwork"""
    artwork = get_artwork_by_id(artwork_id)
    
    if not artwork or str(artwork['artist_id']) != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        update_data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'image_url': request.form.get('image_url'),
            'tags': [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()],
            'medium': request.form.get('medium'),
            'year': request.form.get('year', type=int),
            'price': request.form.get('price', type=float),
            'process_images': [img.strip() for img in request.form.get('process_images', '').split(',') if img.strip()]
        }
        artworks_collection.update_one(
            {"_id": ObjectId(artwork_id)},
            {"$set": update_data}
        )
        flash('Artwork updated successfully!', 'success')
        return redirect(url_for('artwork_detail', artwork_id=artwork_id))
    
    return render_template('edit_artwork.html', artwork=artwork)

@app.route('/artwork/<artwork_id>/delete', methods=['POST'])
@login_required
def delete_artwork_route(artwork_id):
    """Delete artwork"""
    artwork = get_artwork_by_id(artwork_id)
    
    if not artwork or str(artwork['artist_id']) != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    
    artworks_collection.delete_one({"_id": ObjectId(artwork_id)})
    flash('Artwork deleted successfully!', 'success')
    return redirect(url_for('profile', user_id=current_user.id))

@app.route('/search')
def search():
    """Search artworks"""
    keyword = request.args.get('q', '')
    medium = request.args.get('medium', '')
    year = request.args.get('year', type=int)
    
    query = {}
    
    if keyword:
        query = {"$or": [
            {"title": {"$regex": keyword, "$options": "i"}},
            {"description": {"$regex": keyword, "$options": "i"}},
            {"tags": {"$regex": keyword, "$options": "i"}}
        ]}
    
    if medium:
        query["medium"] = medium
    if year:
        query["year"] = year
    
    artworks = list(artworks_collection.find(query))
    
    for artwork in artworks:
        artwork['artist'] = get_user_by_id(artwork['artist_id'])
        artwork['likes_count'] = likes_collection.count_documents({"artwork_id": artwork['_id']})
    
    return render_template('search_results.html', artworks=artworks, query=keyword)

@app.route('/api/artwork/<artwork_id>/like', methods=['POST'])
@login_required
def toggle_like(artwork_id):
    """Toggle like on artwork"""
    try:
        artwork_obj_id = ObjectId(artwork_id)
        user_obj_id = ObjectId(current_user.id)
        
        existing_like = likes_collection.find_one({
            "artwork_id": artwork_obj_id,
            "user_id": user_obj_id
        })
        
        if existing_like:
            likes_collection.delete_one({"_id": existing_like['_id']})
            liked = False
        else:
            likes_collection.insert_one({
                "artwork_id": artwork_obj_id,
                "user_id": user_obj_id,
                "created_at": datetime.now(timezone.utc)
            })
            liked = True
        
        likes_count = likes_collection.count_documents({"artwork_id": artwork_obj_id})
        return jsonify({'success': True, 'liked': liked, 'likes_count': likes_count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/artwork/<artwork_id>/comment', methods=['POST'])
@login_required
def add_comment_route(artwork_id):
    """Add comment to artwork"""
    try:
        text = request.json.get('text')
        
        if not text:
            return jsonify({'success': False, 'error': 'Comment text required'}), 400
        
        comment_data = {
            "artwork_id": ObjectId(artwork_id),
            "user_id": ObjectId(current_user.id),
            "text": text,
            "created_at": datetime.now(timezone.utc),
            "updated_at": None
        }
        result = comments_collection.insert_one(comment_data)
        return jsonify({'success': True, 'comment_id': str(result.inserted_id)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/comment/<comment_id>/edit', methods=['PUT'])
@login_required
def edit_comment(comment_id):
    """Edit comment"""
    try:
        new_text = request.json.get('text')
        
        if not new_text:
            return jsonify({'success': False, 'error': 'Comment text required'}), 400
        
        result = comments_collection.update_one(
            {"_id": ObjectId(comment_id), "user_id": ObjectId(current_user.id)},
            {"$set": {"text": new_text, "updated_at": datetime.now(timezone.utc)}}
        )
        
        if result.modified_count > 0:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Unauthorized or comment not found'}), 403
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/comment/<comment_id>/delete', methods=['DELETE'])
@login_required
def delete_comment_route(comment_id):
    """Delete comment"""
    try:
        result = comments_collection.delete_one({
            "_id": ObjectId(comment_id),
            "user_id": ObjectId(current_user.id)
        })
        
        if result.deleted_count > 0:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Unauthorized or comment not found'}), 403
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)