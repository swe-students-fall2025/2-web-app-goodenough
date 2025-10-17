# models/artwork.py
from db import artworks_collection
from datetime import datetime, timezone

# -- artworks
def add_artwork(artist_id, title, description, image_url, tags=[]):
    artwork = {
        "artist_id": artist_id,
        "title": title,
        "description": description,
        "image_url": image_url,
        "tags": tags,
        "created_at": datetime.now(timezone.utc)
    }
    return artworks_collection.insert_one(artwork)

def get_all_artworks():
    return list(artworks_collection.find())

def search_artworks(keyword):
    return list(artworks_collection.find({"title": {"$regex": keyword, "$options": "i"}}))


def update_artwork(artwork_id, update_data):
    return artworks_collection.update_one({"_id": artwork_id}, {"$set": update_data})


def delete_artwork(artwork_id):
    return artworks_collection.delete_one({"_id": artwork_id})