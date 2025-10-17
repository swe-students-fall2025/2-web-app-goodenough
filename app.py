import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from bson.objectid import ObjectId

#Models
from models.artwork import (
    add_artwork, get_all_artworks, get_artwork_by_id,
    get_artworks_by_artist, search_artworks, filter_artworks, update_artwork
)
import models.user as user_model
import models.comment as comment_model
import models.like as like_model

from db import get_db, artworks_collection

#app setup
load_dotenv()
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

login_manager = LoginManager(app)
login_manager.login_view = "login"


#flask login
class User(UserMixin):
    def __init__(self, doc):
        self.doc = doc or {}
        _id = doc.get("_id")
        self.id = str(_id) if _id else None
        self.username = doc.get("username")

    def get_id(self):
        return self.id


def _get_user_by_id(user_id):
    # Allow multiple possible names in user model
    for name in ("get_user_by_id", "find_user_by_id"):
        fn = getattr(user_model, name, None)
        if callable(fn):
            return fn(user_id)
    # Fallback: try by ObjectId on users collection if exposed in user model
    try:
        from db import users_collection
        return users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


@login_manager.user_loader
def load_user(user_id):
    doc = _get_user_by_id(user_id)
    return User(doc) if doc else None


#routes

@app.get("/")
def home():
    artworks = get_all_artworks()
    # Optional: enrich with author usernames if model does not embed it
    # Keep lightweight to avoid adding new features
    return render_template("home.html", artworks=artworks)


@app.get("/search")
def search():
    q = request.args.get("q", "").strip()
    if q:
        artworks = search_artworks(q)
    else:
        artworks = get_all_artworks()
    return render_template("search.html", artworks=artworks)


@app.get("/art/<artwork_id>")
def artwork_detail(artwork_id):
    art = get_artwork_by_id(artwork_id)
    # comments: allow either get_comments_by_artwork or get_comments_for_artwork function names
    comments = []
    for name in ("get_comments_by_artwork", "get_comments_for_artwork"):
        fn = getattr(comment_model, name, None)
        if callable(fn):
            comments = fn(artwork_id)
            break
    return render_template("artwork_detail.html", artwork=art, comments=comments)


@app.route("/art/<artwork_id>/comments", methods=["POST"])
@login_required
def add_comment(artwork_id):
    body = (request.form.get("body") or "").strip()
    if not body:
        return redirect(url_for("artwork_detail", artwork_id=artwork_id) + "#comments")
    # support possible function names
    added = False
    for name in ("add_comment", "create_comment"):
        fn = getattr(comment_model, name, None)
        if callable(fn):
            fn(artwork_id=artwork_id, author_id=current_user.id, body=body)
            added = True
            break
    if not added:
        # Minimal fallback through DB if no function available
        from db import comments_collection
        comments_collection.insert_one({
            "artwork_id": ObjectId(artwork_id),
            "author_id": ObjectId(current_user.id),
            "body": body,
        })
    return redirect(url_for("artwork_detail", artwork_id=artwork_id) + "#comments")


@app.route("/art/new", methods=["GET", "POST"])
@login_required
def add_artwork_route():
    if request.method == "POST":
        title = request.form.get("title", "")
        image_url = request.form.get("image_url", "")
        description = request.form.get("description", "")
        tags = request.form.get("tags", "")
        add_artwork(current_user.id, title, description, image_url, tags=tags)
        return redirect(url_for("home"))
    return render_template("add_artwork.html")


@app.route("/art/<artwork_id>/edit", methods=["GET", "POST"])
@login_required
def edit_artwork_route(artwork_id):
    art = get_artwork_by_id(artwork_id)
    if not art:
        return redirect(url_for("home"))
    # allow editing only by owner
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


#like
@app.post("/like/<artwork_id>")
@login_required
def like_artwork(artwork_id):
    # Try model's increment function or toggle; return JSON with new count
    for name in ("increment_likes", "add_like", "like_artwork"):
        fn = getattr(like_model, name, None)
        if callable(fn):
            new_count = fn(artwork_id)
            return jsonify({"likes": int(new_count) if new_count is not None else 0})
    #Fallback: simple $inc
    from db import artworks_collection
    from bson import ObjectId
    artworks_collection.update_one({"_id": ObjectId(artwork_id)}, {"$inc": {"likes": 1}})
    doc = artworks_collection.find_one({"_id": ObjectId(artwork_id)}, {"likes": 1})
    return jsonify({"likes": int(doc.get("likes", 0)) if doc else 0})


#Auth
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user_doc = None

        # 1) Try authenticate() if present
        auth_fn = getattr(user_model, "authenticate", None)
        if callable(auth_fn):
            user_doc = auth_fn(username, password)

        # 2) Try manual lookup + verify
        if user_doc is None:
            for name in ("get_user_by_username", "find_user_by_username"):
                fn = getattr(user_model, name, None)
                if callable(fn):
                    doc = fn(username)
                    if doc:
                        # verify via model if possible
                        verify = getattr(user_model, "verify_password", None)
                        if callable(verify) and verify(doc, password):
                            user_doc = doc
                    break

        if user_doc:
            login_user(User(user_doc))
            return redirect(url_for("home"))
        flash("Invalid credentials.")
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        # Prefer model's create function
        for name in ("create_user", "add_user", "register_user"):
            fn = getattr(user_model, name, None)
            if callable(fn):
                user_id = fn(username=username, password=password)
                # fetch created user for login
                fetch = getattr(user_model, "get_user_by_username", None) or getattr(user_model, "find_user_by_username", None)
                user_doc = fetch(username) if callable(fetch) else None
                if user_doc:
                    login_user(User(user_doc))
                    return redirect(url_for("home"))
                break
        flash("Sign up failed.")
    return render_template("signup.html")


@app.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# --- Profile ---
@app.get("/u/<username>")
def profile(username):
    #get user
    user_doc = None
    for name in ("get_user_by_username", "find_user_by_username"):
        fn = getattr(user_model, name, None)
        if callable(fn):
            user_doc = fn(username)
            break
    if not user_doc:
        return redirect(url_for("home"))

    arts = get_artworks_by_artist(user_doc.get("_id"))
    return render_template("profile.html", user=user_doc, artworks=arts)


@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        bio = request.form.get("bio", "")
        #Try model update
        updated = False
        for name in ("update_user", "update_profile", "update_bio"):
            fn = getattr(user_model, name, None)
            if callable(fn):
                try:
                    #Attempt common signatures
                    fn(current_user.id, {"bio": bio})
                except TypeError:
                    try:
                        fn(user_id=current_user.id, update_data={"bio": bio})
                    except TypeError:
                        fn(user_id=current_user.id, bio=bio)
                updated = True
                break
        if not updated:
            #Minimal fallback
            from db import users_collection
            users_collection.update_one({"_id": ObjectId(current_user.id)}, {"$set": {"bio": bio}})
        return redirect(url_for("profile", username=getattr(current_user, "username", "")))

    #load current user doc for form
    doc = _get_user_by_id(current_user.id)
    return render_template("edit_profile.html", user=doc or {})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
