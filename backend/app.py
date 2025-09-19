"""
Flask API server for AI To-Do List Manager
Provides REST endpoints for task processing and management
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
from ai_processor import TaskProcessor
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize AI processor
task_processor = TaskProcessor()

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

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

@app.route('/api/process-tasks', methods=['POST'])
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
            
            for task in result['tasks']:
                cursor.execute('''
                    INSERT INTO tasks (description, priority, category, status)
                    VALUES (?, ?, ?, ?)
                ''', (task['description'], task['priority'], task['category'], task['status']))
            
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
def get_tasks():
    """Get all tasks from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters
        status = request.args.get('status', 'all')
        priority = request.args.get('priority', 'all')
        category = request.args.get('category', 'all')
        
        # Build query
        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []
        
        if status != 'all':
            query += ' AND status = ?'
            params.append(status)
        
        if priority != 'all':
            query += ' AND priority = ?'
            params.append(priority)
        
        if category != 'all':
            query += ' AND category = ?'
            params.append(category)
        
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
        
        # Check if task exists
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
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
        
        if update_fields:
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            params.append(task_id)
            
            query = f'UPDATE tasks SET {", ".join(update_fields)} WHERE id = ?'
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
def delete_task(task_id):
    """Delete a specific task."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if task exists
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        
        if not task:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Task not found'
            }), 404
        
        # Delete task
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
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
def clear_all_tasks():
    """Clear all tasks from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get count before deletion for confirmation
        cursor.execute('SELECT COUNT(*) as count FROM tasks')
        task_count = cursor.fetchone()['count']
        
        if task_count == 0:
            conn.close()
            return jsonify({
                'success': True,
                'message': 'No tasks to clear',
                'deleted_count': 0
            })
        
        # Delete all tasks
        cursor.execute('DELETE FROM tasks')
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

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get task statistics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total tasks
        cursor.execute('SELECT COUNT(*) as total FROM tasks')
        total_tasks = cursor.fetchone()['total']
        
        # Get tasks by status
        cursor.execute('SELECT status, COUNT(*) as count FROM tasks GROUP BY status')
        status_stats = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Get tasks by priority
        cursor.execute('SELECT priority, COUNT(*) as count FROM tasks GROUP BY priority')
        priority_stats = {row['priority']: row['count'] for row in cursor.fetchall()}
        
        # Get tasks by category
        cursor.execute('SELECT category, COUNT(*) as count FROM tasks GROUP BY category')
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

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Run the app
    print("Starting AI To-Do List Manager API...")
    print("API will be available at: http://localhost:5000")
    print("Health check: http://localhost:5000/api/health")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
