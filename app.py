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

#Routes
@app.route('/')
def home():
    artworks = get_all_artworks()
    return render_template('home.html', artworks=artworks)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        #Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('signup'))
        
        # Hash password and create user
        password_hash = generate_password_hash(password)
        add_user(username, email, password_hash)
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method== 'POST':
        email =request.form.get('email')
        password = request.form.get('password')
        
        user_data = get_user_by_email(email)
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data)
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/profile/<user_id>')
def profile(user_id):
    user_data = get_user_by_id(user_id)
    if not user_data:
        flash('User not found.', 'error')
        return redirect(url_for('home'))
    
    artworks = get_artworks_by_artist(user_id)
    return render_template('profile.html', user=user_data, artworks=artworks)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        update_data = {
            'bio': request.form.get('bio', ''),
            'profile_image': request.form.get('profile_image', ''),
            'banner_image': request.form.get('banner_image', ''),
            'social_links': {
                'instagram': request.form.get('instagram', ''),
                'twitter': request.form.get('twitter', ''),
                'website': request.form.get('website', '')
            }
        }
        update_user(current_user.id, update_data)
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile', user_id=current_user.id))
    
    user_data = get_user_by_id(current_user.id)
    return render_template('edit_profile.html', user=user_data)

@app.route('/artwork/add', methods=['GET', 'POST'])
@login_required
def add_artwork_route():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        tags = request.form.get('tags', '').split(',')
        tags = [tag.strip() for tag in tags if tag.strip()]
        medium = request.form.get('medium', '')
        year = request.form.get('year', '')
        price = request.form.get('price', '')
        process_images = request.form.get('process_images', '').split(',')
        process_images = [img.strip() for img in process_images if img.strip()]
        
        add_artwork(
            current_user.id, 
            title, 
            description, 
            image_url, 
            tags,
            medium,
            year,
            price,
            process_images
        )
        flash('Artwork added successfully!', 'success')
        return redirect(url_for('profile', user_id=current_user.id))
    
    return render_template('add_artwork.html')

@app.route('/artwork/<artwork_id>')
def artwork_detail(artwork_id):
    artwork = get_artwork_by_id(artwork_id)
    if not artwork:
        flash('Artwork not found.', 'error')
        return redirect(url_for('home'))
    
    artist = get_user_by_id(artwork['artist_id'])
    comments = get_comments_by_artwork(artwork_id)
    likes_count = get_likes_count(artwork_id)
    user_liked = user_has_liked(artwork_id, current_user.id) if current_user.is_authenticated else False
    
    return render_template('artwork_detail.html', 
                         artwork=artwork, 
                         artist=artist, 
                         comments=comments,
                         likes_count=likes_count,
                         user_liked=user_liked)

@app.route('/artwork/<artwork_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_artwork(artwork_id):
    artwork = get_artwork_by_id(artwork_id)
    if not artwork:
        flash('Artwork not found.', 'error')
        return redirect(url_for('home'))
    
    if artwork['artist_id'] != current_user.id:
        flash('You can only edit your own artworks.', 'error')
        return redirect(url_for('artwork_detail', artwork_id=artwork_id))
    
    if request.method == 'POST':
        update_data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'image_url': request.form.get('image_url'),
            'tags': [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()],
            'medium': request.form.get('medium', ''),
            'year': request.form.get('year', ''),
            'price': request.form.get('price', ''),
            'process_images': [img.strip() for img in request.form.get('process_images', '').split(',') if img.strip()]
        }
        update_artwork(artwork_id, update_data)
        flash('Artwork updated successfully!', 'success')
        return redirect(url_for('artwork_detail', artwork_id=artwork_id))
    
    return render_template('edit_artwork.html', artwork=artwork)

@app.route('/artwork/<artwork_id>/delete', methods=['POST'])
@login_required
def delete_artwork_route(artwork_id):
    artwork = get_artwork_by_id(artwork_id)
    if not artwork:
        flash('Artwork not found.', 'error')
        return redirect(url_for('home'))
    
    if artwork['artist_id'] != current_user.id:
        flash('You can only delete your own artworks.', 'error')
        return redirect(url_for('artwork_detail', artwork_id=artwork_id))
    
    delete_artwork(artwork_id)
    flash('Artwork deleted successfully!', 'success')
    return redirect(url_for('profile', user_id=current_user.id))

@app.route('/search')
def search():
    keyword = request.args.get('q', '')
    medium = request.args.get('medium', '')
    year = request.args.get('year', '')
    
    if keyword:
        artworks = search_artworks(keyword)
    else:
        artworks = filter_artworks(medium, year)
    
    return render_template('search.html', artworks=artworks, keyword=keyword, medium=medium, year=year)

@app.route('/artwork/<artwork_id>/comment', methods=['POST'])
@login_required
def add_comment_route(artwork_id):
    content = request.form.get('content')
    if content:
        add_comment(artwork_id, current_user.id, content)
        flash('Comment added successfully!', 'success')
    return redirect(url_for('artwork_detail', artwork_id=artwork_id))

@app.route('/comment/<comment_id>/delete', methods=['POST'])
@login_required
def delete_comment_route(comment_id):
    comment = comments_collection.find_one({'_id': ObjectId(comment_id)})
    if comment and comment['user_id'] == current_user.id:
        delete_comment(comment_id)
        flash('Comment deleted successfully!', 'success')
    return redirect(request.referrer or url_for('home'))

@app.route('/artwork/<artwork_id>/like', methods=['POST'])
@login_required
def like_artwork(artwork_id):
    if user_has_liked(artwork_id, current_user.id):
        remove_like(artwork_id, current_user.id)
        liked = False
    else:
        add_like(artwork_id, current_user.id)
        liked = True
    
    likes_count = get_likes_count(artwork_id)
    return jsonify({'liked': liked, 'likes_count': likes_count})

if __name__ == '__main__':
    app.run(debug=True)