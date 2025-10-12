from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# connecting to MongoDb ...
client = MongoClient(MONGO_URI)
db = client['enoughArt'] 

# collections
users_collection = db['users']
artworks_collection = db['artworks']



