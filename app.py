from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
import json

#Load environment variables
load_dotenv()

#Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app, supports_credentials=True)

#MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGODB_URI)
db = client['artfolio']
artworks_collection = db['artworks']
users_collection = db['users']

#Initialize database with sample if empty
def initialize_database():
    
    #Check if admin user exists, if not create one
    if users_collection.count_documents({'username': 'admin'}) == 0:
        admin_user = {
            'username': 'admin',
            'password': generate_password_hash('admin123'),
            'email': 'admin@artfolio.com',
            'role': 'admin',
            'created_at': datetime.utcnow()
        }
        users_collection.insert_one(admin_user)
        print("Admin user created: username='admin', password='admin123'")
    
    #Check if artworks collection is empty, if so add sample data
    if artworks_collection.count_documents({}) == 0:
        sample_artworks = [
            {
                "title": "Starry Night",
                "artist": "Vincent van Gogh",
                "year": 1889,
                "medium": "Oil Painting",
                "dimensions": "73.7 cm × 92.1 cm",
                "price": 100000000,
                "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
                "description": "A swirling night sky over a French village",
                "location": "Museum of Modern Art, New York",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "title": "The Great Wave",
                "artist": "Katsushika Hokusai",
                "year": 1831,
                "medium": "Woodblock Print",
                "dimensions": "25.7 cm × 37.8 cm",
                "price": 50000000,
                "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/The_Great_Wave_off_Kanagawa.jpg/1280px-The_Great_Wave_off_Kanagawa.jpg",
                "description": "An iconic Japanese woodblock print depicting a giant wave",
                "location": "Metropolitan Museum of Art, New York",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "title": "Girl with a Pearl Earring",
                "artist": "Johannes Vermeer",
                "year": 1665,
                "medium": "Oil Painting",
                "dimensions": "44.5 cm × 39 cm",
                "price": 75000000,
                "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/1665_Girl_with_a_Pearl_Earring.jpg/800px-1665_Girl_with_a_Pearl_Earring.jpg",
                "description": "A portrait of a girl with a mysterious smile and a pearl earring",
                "location": "Mauritshuis, The Hague",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "title": "The Persistence of Memory",
                "artist": "Salvador Dalí",
                "year": 1931,
                "medium": "Oil Painting",
                "dimensions": "24 cm × 33 cm",
                "price": 80000000,
                "imageUrl": "https://upload.wikimedia.org/wikipedia/en/d/dd/The_Persistence_of_Memory.jpg",
                "description": "Surrealist masterpiece featuring melting clocks",
                "location": "Museum of Modern Art, New York",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "title": "The Kiss",
                "artist": "Gustav Klimt",
                "year": 1908,
                "medium": "Oil Painting",
                "dimensions": "180 cm × 180 cm",
                "price": 60000000,
                "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Gustav_Klimt_016.jpg/800px-Gustav_Klimt_016.jpg",
                "description": "A golden embrace between two lovers",
                "location": "Österreichische Galerie Belvedere, Vienna",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        artworks_collection.insert_many(sample_artworks)
        print(f"Inserted {len(sample_artworks)} sample artworks")

#Initialize database on startup
initialize_database()

#Helper function to convert ObjectId to string in documents
def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if doc:
        doc['_id'] = str(doc['_id'])
        if 'created_at' in doc:
            doc['created_at'] = doc['created_at'].isoformat()
        if 'updated_at' in doc:
            doc['updated_at'] = doc['updated_at'].isoformat()
    return doc

