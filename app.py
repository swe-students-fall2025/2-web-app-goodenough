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