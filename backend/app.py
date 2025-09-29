"""
Flask API server for AI To-Do List Manager
Provides REST endpoints for task processing and management
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, current_user
import sqlite3
import json
from datetime import datetime
from ai_processor import TaskProcessor
from auth import (
    login_manager, User, verify_google_token, get_or_create_user, 
    init_auth_database, auth_required, get_current_user_id
)
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Change this in production

# Initialize Flask-Login
login_manager.init_app(app)
login_manager.login_view = 'login'

CORS(app, supports_credentials=True, origins=['http://localhost:3000'])  # Enable CORS with credentials

# Initialize AI processor with provider selection
ai_provider = os.getenv('AI_PROVIDER', 'chatgpt')  # Default to ChatGPT
task_processor = TaskProcessor(ai_provider=ai_provider)

# Database setup
DB_PATH = 'tasks.db'

def init_database():
    """Initialize SQLite database for storing tasks."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            due_date DATE,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Add due_date column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE tasks ADD COLUMN due_date DATE')
        conn.commit()
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    # Add user_id column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE tasks ADD COLUMN user_id INTEGER')
        conn.commit()
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    conn.commit()
    conn.close()
    
    # Initialize authentication tables
    init_auth_database()

def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'AI To-Do List Manager API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Google OAuth login endpoint."""
    try:
        data = request.get_json()
        
        if not data or 'token' not in data:
            return jsonify({
                'success': False,
                'message': 'No token provided'
            }), 400
        
        # Verify Google token
        user_info = verify_google_token(data['token'])
        
        if not user_info:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401
        
        # Get or create user
        user_id = get_or_create_user(user_info)
        
        # Create user object for Flask-Login
        user = User(
            user_id=user_id,
            email=user_info['email'],
            name=user_info['name'],
            picture=user_info['picture']
        )
        
        # Log in user
        login_user(user)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user_id,
                'email': user_info['email'],
                'name': user_info['name'],
                'picture': user_info['picture']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login error: {str(e)}'
        }), 500

@app.route('/api/auth/logout', methods=['POST'])
@auth_required
def logout():
    """Logout endpoint."""
    try:
        logout_user()
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Logout error: {str(e)}'
        }), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get current user info."""
    # Debug: Check if current_user is authenticated and print info
    if not current_user.is_authenticated:
        # This will cause 401 if the user is not logged in
        return jsonify({
            'success': False,
            'message': 'User not authenticated'
        }), 401

    # Optionally, print current_user info for debugging
    # print(f"Current user: {current_user}")

    return jsonify({
        'success': True,
        'user': {
            'id': current_user.id,
            'email': current_user.email,
            'name': current_user.name,
            'picture': current_user.picture
        }
    })

@app.route('/api/process-tasks', methods=['POST'])
@auth_required
def process_tasks():
    """Process raw task text and return structured tasks."""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'message': 'No text provided',
                'tasks': []
            }), 400
        
        raw_text = data['text'].strip()
        
        if not raw_text:
            return jsonify({
                'success': False,
                'message': 'Empty text provided',
                'tasks': []
            }), 400
        
        # Process tasks using AI
        result = task_processor.process_tasks(raw_text)
        
        if result['success']:
            # Save tasks to database
            conn = get_db_connection()
            cursor = conn.cursor()
            user_id = get_current_user_id()
            
            for task in result['tasks']:
                cursor.execute('''
                    INSERT INTO tasks (description, priority, category, status, due_date, user_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (task['description'], task['priority'], task['category'], task['status'], task.get('due_date'), user_id))
            
            conn.commit()
            conn.close()
            
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'tasks': []
        }), 500

@app.route('/api/tasks', methods=['GET'])
@auth_required
def get_tasks():
    """Get all tasks from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters
        status = request.args.get('status', 'all')
        priority = request.args.get('priority', 'all')
        category = request.args.get('category', 'all')
        due_date = request.args.get('due_date', 'all')  # 'today', 'tomorrow', 'this_week', 'overdue', 'all'
        
        # Build query with user filter
        user_id = get_current_user_id()
        query = 'SELECT * FROM tasks WHERE user_id = ?'
        params = [user_id]
        
        if status != 'all':
            query += ' AND status = ?'
            params.append(status)
        
        if priority != 'all':
            query += ' AND priority = ?'
            params.append(priority)
        
        if category != 'all':
            query += ' AND category = ?'
            params.append(category)
        
        # Handle date filtering
        from datetime import datetime, timedelta
        today = datetime.now().strftime("%Y-%m-%d")
        
        if due_date == 'today':
            query += ' AND due_date = ?'
            params.append(today)
        elif due_date == 'tomorrow':
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            query += ' AND due_date = ?'
            params.append(tomorrow)
        elif due_date == 'this_week':
            # Tasks due from today until end of week (Sunday)
            days_until_sunday = (6 - datetime.now().weekday()) % 7
            if days_until_sunday == 0:  # It's Sunday
                days_until_sunday = 7
            end_of_week = (datetime.now() + timedelta(days=days_until_sunday)).strftime("%Y-%m-%d")
            query += ' AND due_date BETWEEN ? AND ?'
            params.extend([today, end_of_week])
        elif due_date == 'overdue':
            query += ' AND due_date < ? AND status != "completed"'
            params.append(today)
        elif due_date == 'no_date':
            query += ' AND due_date IS NULL'
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        tasks = cursor.fetchall()
        
        conn.close()
        
        # Convert to list of dictionaries
        task_list = []
        for task in tasks:
            task_list.append({
                'id': task['id'],
                'description': task['description'],
                'priority': task['priority'],
                'category': task['category'],
                'status': task['status'],
                'due_date': task['due_date'],
                'created_at': task['created_at'],
                'updated_at': task['updated_at']
            })
        
        return jsonify({
            'success': True,
            'tasks': task_list,
            'count': len(task_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'tasks': []
        }), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@auth_required
def update_task(task_id):
    """Update a specific task."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = get_current_user_id()
        
        # Check if task exists and belongs to current user
        cursor.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
        task = cursor.fetchone()
        
        if not task:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Task not found'
            }), 404
        
        # Update task
        update_fields = []
        params = []
        
        if 'description' in data:
            update_fields.append('description = ?')
            params.append(data['description'])
        
        if 'priority' in data:
            update_fields.append('priority = ?')
            params.append(data['priority'])
        
        if 'category' in data:
            update_fields.append('category = ?')
            params.append(data['category'])
        
        if 'status' in data:
            update_fields.append('status = ?')
            params.append(data['status'])
        
        if 'due_date' in data:
            update_fields.append('due_date = ?')
            params.append(data['due_date'])
        
        if update_fields:
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            params.extend([task_id, user_id])
            
            query = f'UPDATE tasks SET {", ".join(update_fields)} WHERE id = ? AND user_id = ?'
            cursor.execute(query, params)
            
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Task updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@auth_required
def delete_task(task_id):
    """Delete a specific task."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = get_current_user_id()
        
        # Check if task exists and belongs to current user
        cursor.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
        task = cursor.fetchone()
        
        if not task:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Task not found'
            }), 404
        
        # Delete task
        cursor.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Task deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/tasks/clear-all', methods=['DELETE'])
@auth_required
def clear_all_tasks():
    """Clear all tasks from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = get_current_user_id()
        
        # Get count before deletion for confirmation
        cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id = ?', (user_id,))
        task_count = cursor.fetchone()['count']
        
        if task_count == 0:
            conn.close()
            return jsonify({
                'success': True,
                'message': 'No tasks to clear',
                'deleted_count': 0
            })
        
        # Delete all tasks for current user
        cursor.execute('DELETE FROM tasks WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Successfully cleared {task_count} tasks',
            'deleted_count': task_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/analyze-priority', methods=['POST'])
@auth_required
def analyze_priority():
    """Get detailed priority analysis for a single task."""
    try:
        data = request.get_json()
        
        if not data or 'task' not in data:
            return jsonify({
                'success': False,
                'message': 'No task provided'
            }), 400
        
        task = data['task'].strip()
        
        if not task:
            return jsonify({
                'success': False,
                'message': 'Empty task provided'
            }), 400
        
        # Get detailed priority analysis
        analysis = task_processor.get_priority_analysis(task)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/stats', methods=['GET'])
@auth_required
def get_stats():
    """Get task statistics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = get_current_user_id()
        
        # Get total tasks
        cursor.execute('SELECT COUNT(*) as total FROM tasks WHERE user_id = ?', (user_id,))
        total_tasks = cursor.fetchone()['total']
        
        # Get tasks by status
        cursor.execute('SELECT status, COUNT(*) as count FROM tasks WHERE user_id = ? GROUP BY status', (user_id,))
        status_stats = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Get tasks by priority
        cursor.execute('SELECT priority, COUNT(*) as count FROM tasks WHERE user_id = ? GROUP BY priority', (user_id,))
        priority_stats = {row['priority']: row['count'] for row in cursor.fetchall()}
        
        # Get tasks by category
        cursor.execute('SELECT category, COUNT(*) as count FROM tasks WHERE user_id = ? GROUP BY category', (user_id,))
        category_stats = {row['category']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_tasks': total_tasks,
                'by_status': status_stats,
                'by_priority': priority_stats,
                'by_category': category_stats
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/tasks/today', methods=['GET'])
@auth_required
def get_today_tasks():
    """Get tasks due today."""
    try:
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = get_current_user_id()
        cursor.execute('SELECT * FROM tasks WHERE due_date = ? AND user_id = ? ORDER BY priority DESC, created_at ASC', (today, user_id))
        tasks = cursor.fetchall()
        conn.close()
        
        task_list = []
        for task in tasks:
            task_list.append({
                'id': task['id'],
                'description': task['description'],
                'priority': task['priority'],
                'category': task['category'],
                'status': task['status'],
                'due_date': task['due_date'],
                'created_at': task['created_at'],
                'updated_at': task['updated_at']
            })
        
        return jsonify({
            'success': True,
            'tasks': task_list,
            'count': len(task_list),
            'date': today
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'tasks': []
        }), 500

@app.route('/api/tasks/tomorrow', methods=['GET'])
@auth_required
def get_tomorrow_tasks():
    """Get tasks due tomorrow."""
    try:
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = get_current_user_id()
        cursor.execute('SELECT * FROM tasks WHERE due_date = ? AND user_id = ? ORDER BY priority DESC, created_at ASC', (tomorrow, user_id))
        tasks = cursor.fetchall()
        conn.close()
        
        task_list = []
        for task in tasks:
            task_list.append({
                'id': task['id'],
                'description': task['description'],
                'priority': task['priority'],
                'category': task['category'],
                'status': task['status'],
                'due_date': task['due_date'],
                'created_at': task['created_at'],
                'updated_at': task['updated_at']
            })
        
        return jsonify({
            'success': True,
            'tasks': task_list,
            'count': len(task_list),
            'date': tomorrow
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'tasks': []
        }), 500

@app.route('/api/tasks/overdue', methods=['GET'])
@auth_required
def get_overdue_tasks():
    """Get overdue tasks."""
    try:
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = get_current_user_id()
        cursor.execute('SELECT * FROM tasks WHERE due_date < ? AND status != "completed" AND user_id = ? ORDER BY due_date ASC', (today, user_id))
        tasks = cursor.fetchall()
        conn.close()
        
        task_list = []
        for task in tasks:
            task_list.append({
                'id': task['id'],
                'description': task['description'],
                'priority': task['priority'],
                'category': task['category'],
                'status': task['status'],
                'due_date': task['due_date'],
                'created_at': task['created_at'],
                'updated_at': task['updated_at']
            })
        
        return jsonify({
            'success': True,
            'tasks': task_list,
            'count': len(task_list),
            'message': f'Found {len(task_list)} overdue tasks'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'tasks': []
        }), 500

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Run the app
    print("Starting AI To-Do List Manager API...")
    print("API will be available at: http://localhost:5000")
    print("Health check: http://localhost:5000/api/health")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
