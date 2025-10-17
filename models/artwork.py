# In models/artwork.py

from db import artworks_collection
from bson.objectid import ObjectId
from datetime import datetime, timezone

def add_artwork(artist_id, title, description, image_url, tags, medium, year, price, process_images):
    artwork_data = {
        "artist_id": artist_id,
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
    return artworks_collection.insert_one(artwork_data)

def get_all_artworks():
    return list(artworks_collection.find().sort("created_at", -1))

def get_artwork_by_id(artwork_id):
    try:
        return artworks_collection.find_one({"_id": ObjectId(artwork_id)})
    except:
        return None

def get_artworks_by_artist(artist_id):
    return list(artworks_collection.find({"artist_id": artist_id}).sort("created_at", -1))

def update_artwork(artwork_id, update_data):
    artworks_collection.update_one(
        {"_id": ObjectId(artwork_id)},
        {"$set": update_data}
    )

def delete_artwork(artwork_id):
    artworks_collection.delete_one({"_id": ObjectId(artwork_id)})

def search_artworks(keyword):
    query = {"$or": [
        {"title": {"$regex": keyword, "$options": "i"}},
        {"description": {"$regex": keyword, "$options": "i"}},
        {"tags": {"$regex": keyword, "$options": "i"}}
    ]}
    return list(artworks_collection.find(query))

def filter_artworks(medium=None, year=None):
    query = {}
    if medium:
        query["medium"] = medium
    if year:
        query["year"] = year
    return list(artworks_collection.find(query))