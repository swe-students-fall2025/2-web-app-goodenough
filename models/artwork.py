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

