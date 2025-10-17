import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

#Models
from models.artwork import (
    add_artwork, get_all_artworks, get_artwork_by_id,
    get_artworks_by_artist, update_artwork
)
from models.comment import add_comment, get_comments_by_artwork, delete_comment
from models.like import add_like, get_likes_by_artwork
from models.user import add_user, get_all_users

#DB
from db import users_collection, artworks_collection

#Setup
load_dotenv()
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

login_manager = LoginManager(app)
login_manager.login_view = "login"

#Flask login
class User(UserMixin):
    def __init__(self, doc):
        self.doc = doc or {}
        _id = doc.get("_id")
        self.id = str(_id) if _id else None
        self.username = doc.get("username")

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    try:
        doc = users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        doc = None
    return User(doc) if doc else None

#Routes
@app.get("/")
def home():
    artworks = get_all_artworks()
    return render_template("home.html", artworks=artworks)

@app.get("/search")
def search():
    q = (request.args.get("q") or "").strip().lower()
    arts = get_all_artworks()
    if not q:
        return render_template("search.html", artworks=arts)

    def hit(a):
        title = (a.get("title") or "").lower()
        desc = (a.get("description") or "").lower()
        tags = a.get("tags") or []
        return (q in title) or (q in desc) or any(q in str(t).lower() for t in tags)

    results = [a for a in arts if hit(a)]
    return render_template("search.html", artworks=results)

@app.get("/art/<artwork_id>")
def artwork_detail(artwork_id):
    art = get_artwork_by_id(artwork_id)
    comments = get_comments_by_artwork(artwork_id)
    return render_template("artwork_detail.html", artwork=art, comments=comments)

@app.route("/art/<artwork_id>/comments", methods=["POST"])
@login_required
def add_comment_route(artwork_id):
    body = (request.form.get("body") or "").strip()
    if body:
        add_comment(artwork_id=artwork_id, author_id=current_user.id, body=body)
    return redirect(url_for("artwork_detail", artwork_id=artwork_id) + "#comments")

@app.route("/comment/<comment_id>/delete", methods=["POST"])
@login_required
def delete_comment_route(comment_id):
    delete_comment(comment_id)
    artwork_id = request.form.get("artwork_id")
    if artwork_id:
        return redirect(url_for("artwork_detail", artwork_id=artwork_id) + "#comments")
    return redirect(url_for("home"))

@app.route("/art/new", methods=["GET", "POST"])
@login_required
def add_artwork_route():
    if request.method == "POST":
        title = request.form.get("title", "")
        image_url = request.form.get("image_url", "")
        description = request.form.get("description", "")
        raw_tags = request.form.get("tags", "")
        tags = [t.strip() for t in raw_tags.split(",") if t.strip()] if raw_tags else []
        add_artwork(current_user.id, title, description, image_url, tags=tags)
        return redirect(url_for("home"))
    return render_template("add_artwork.html")

@app.route("/art/<artwork_id>/edit", methods=["GET", "POST"])
@login_required
def edit_artwork_route(artwork_id):
    art = get_artwork_by_id(artwork_id)
    if not art:
        return redirect(url_for("home"))
    if str(art.get("artist_id")) != str(current_user.id):
        flash("You can only edit your own artwork.")
        return redirect(url_for("artwork_detail", artwork_id=artwork_id))

    if request.method == "POST":
        update_data = {
            "title": request.form.get("title", ""),
            "image_url": request.form.get("image_url", ""),
            "description": request.form.get("description", ""),
            "tags": request.form.get("tags", ""),
        }
        update_artwork(artwork_id, update_data)
        return redirect(url_for("artwork_detail", artwork_id=artwork_id))
    return render_template("edit_artwork.html", artwork=art)

#likes
@app.post("/art/<artwork_id>/like")
@login_required
def like_artwork(artwork_id):
    add_like(artwork_id, current_user.id)
    likes = get_likes_by_artwork(artwork_id) or []
    return jsonify({"likes": len(likes)})

#auth
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = (request.form.get("password") or "")
        if not username or not password:
            flash("Username and password are required.")
            return render_template("signup.html")

        exists = False
        for u in get_all_users():
            if (u.get("username") or "").strip().lower() == username.lower():
                exists = True
                break
        if exists:
            flash("Username already exists.")
            return render_template("signup.html")

        password_hash = generate_password_hash(password)
        add_user(username=username, email=email, password_hash=password_hash, bio="", profile_image="")
        just = None
        for u in get_all_users():
            if (u.get("username") or "") == username:
                just = u
                break
        if just:
            login_user(User(just))
            return redirect(url_for("home"))

        flash("Signup failed.")
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "")
        target = None
        for u in get_all_users():
            if (u.get("username") or "").strip().lower() == username.lower():
                target = u
                break

        if target and check_password_hash(target.get("password_hash", ""), password):
            login_user(User(target))
            return redirect(url_for("home"))
        flash("Invalid credentials.")
    return render_template("login.html")

@app.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

#Profile
@app.get("/u/<username>")
def profile(username):
    found = None
    for u in get_all_users():
        if (u.get("username") or "").strip().lower() == (username or "").strip().lower():
            found = u
            break
    if not found:
        return redirect(url_for("home"))

    arts = get_artworks_by_artist(found.get("_id"))
    return render_template("profile.html", user=found, artworks=arts)

#Edit profile
@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        bio = request.form.get("bio", "")
        try:
            users_collection.update_one({"_id": ObjectId(current_user.id)}, {"$set": {"bio": bio}})
        except Exception:
            pass
        return redirect(url_for("profile", username=getattr(current_user, "username", "")))

    try:
        doc = users_collection.find_one({"_id": ObjectId(current_user.id)}) or {}
    except Exception:
        doc = {}
    return render_template("edit_profile.html", user=doc)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))