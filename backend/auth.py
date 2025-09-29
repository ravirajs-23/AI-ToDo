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
import hashlib
import secrets
import re

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
        # Handle both old and new schema
        if len(user_data) >= 4:
            if len(user_data) >= 7:  # New schema with first_name, last_name
                user_id, email, name, first_name, last_name, password_hash, picture = user_data[:7]
                display_name = name or f"{first_name} {last_name}".strip()
            else:  # Old schema
                user_id, email, name, picture = user_data[:4]
                display_name = name
        else:
            return None
            
        return User(
            user_id=user_id,
            email=email,
            name=display_name,
            picture=picture
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
        # Split name into first and last name
        name_parts = user_info['name'].strip().split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Create new user
        cursor.execute('''
            INSERT INTO users (google_id, email, name, first_name, last_name, picture, auth_type, account_type, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, ?, 'google', 'Personal', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (
            user_info['user_id'],
            user_info['email'],
            user_info['name'],
            first_name,
            last_name,
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
    
    # Create users table with support for both Google OAuth and email/password
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            picture TEXT,
            password_hash TEXT,
            auth_type TEXT DEFAULT 'google',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add new columns to existing users table if they don't exist
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN password_hash TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN auth_type TEXT DEFAULT "google"')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Update existing users to have auth_type = 'google'
    cursor.execute('UPDATE users SET auth_type = "google" WHERE auth_type IS NULL')
    
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

# Email/Password Authentication Functions

def hash_password(password):
    """Hash a password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password, stored_hash):
    """Verify a password against its stored hash"""
    try:
        salt, password_hash = stored_hash.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except ValueError:
        return False

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def create_email_user(email, password, name):
    """Create a new user with email/password authentication"""
    # Validate inputs
    if not validate_email(email):
        return None, "Invalid email format"
    
    is_valid, message = validate_password(password)
    if not is_valid:
        return None, message
    
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    try:
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            return None, "User with this email already exists"
        
        # Hash password
        password_hash = hash_password(password)
        
        # Split name into first and last name
        name_parts = name.strip().split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Create user
        cursor.execute('''
            INSERT INTO users (email, name, first_name, last_name, password_hash, auth_type, account_type, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, 'email', 'Personal', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (email, name, first_name, last_name, password_hash))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        return user_id, "User created successfully"
        
    except Exception as e:
        conn.rollback()
        return None, f"Error creating user: {str(e)}"
    finally:
        conn.close()

def authenticate_email_user(email, password):
    """Authenticate user with email and password"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    try:
        # Get user by email
        cursor.execute('''
            SELECT id, email, name, first_name, last_name, password_hash, picture 
            FROM users 
            WHERE email = ? AND auth_type = 'email'
        ''', (email,))
        
        user_data = cursor.fetchone()
        if not user_data:
            return None, "Invalid email or password"
        
        user_id, user_email, name, first_name, last_name, password_hash, picture = user_data
        
        # Verify password
        if not verify_password(password, password_hash):
            return None, "Invalid email or password"
        
        # Update last login
        cursor.execute(
            'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
            (user_id,)
        )
        conn.commit()
        
        return {
            'user_id': user_id,
            'email': user_email,
            'name': name or f"{first_name} {last_name}".strip(),
            'picture': picture
        }, "Authentication successful"
        
    except Exception as e:
        return None, f"Authentication error: {str(e)}"
    finally:
        conn.close()

