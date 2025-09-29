"""
Authentication module for Google OAuth integration
"""

import os
from functools import wraps
from flask import request, jsonify, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from google.auth.transport import requests
from google.oauth2 import id_token
import sqlite3
from datetime import datetime

# Initialize login manager
login_manager = LoginManager()

class User(UserMixin):
    """User class for Flask-Login"""
    
    def __init__(self, user_id, email, name, picture=None):
        self.id = user_id
        self.email = email
        self.name = name
        self.picture = picture

@login_manager.user_loader
def load_user(user_id):
    """Load user from database"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(
            user_id=user_data[0],
            email=user_data[1],
            name=user_data[2],
            picture=user_data[3] if len(user_data) > 3 else None
        )
    return None

def verify_google_token(token):
    """Verify Google ID token and return user info"""
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            os.getenv('GOOGLE_CLIENT_ID')
        )
        
        # Check if the token is from the correct issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        return {
            'user_id': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo['name'],
            'picture': idinfo.get('picture')
        }
    except ValueError as e:
        print(f"Token verification failed: {e}")
        return None

def get_or_create_user(user_info):
    """Get existing user or create new user in database"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute('SELECT * FROM users WHERE google_id = ?', (user_info['user_id'],))
    existing_user = cursor.fetchone()
    
    if existing_user:
        # Update last login
        cursor.execute(
            'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE google_id = ?',
            (user_info['user_id'],)
        )
        conn.commit()
        conn.close()
        return existing_user[0]  # Return user ID
    else:
        # Create new user
        cursor.execute('''
            INSERT INTO users (google_id, email, name, picture, created_at, last_login)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (
            user_info['user_id'],
            user_info['email'],
            user_info['name'],
            user_info['picture']
        ))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id

def init_auth_database():
    """Initialize authentication tables"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            picture TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add user_id column to tasks table if it doesn't exist
    try:
        cursor.execute('ALTER TABLE tasks ADD COLUMN user_id INTEGER')
        cursor.execute('ALTER TABLE tasks ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id)')
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    conn.commit()
    conn.close()

def auth_required(f):
    """Decorator to require authentication for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'message': 'Authentication required',
                'error': 'UNAUTHORIZED'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_user_id():
    """Get current user ID for database operations"""
    if current_user.is_authenticated:
        return current_user.id
    return None

