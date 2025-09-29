import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  CheckCircle, 
  Circle, 
  Clock, 
  AlertCircle, 
  Calendar,
  Filter,
  Trash2,
  Edit3,
  Plus,
  Loader2,
  Trash,
  User,
  LogOut
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const API_BASE_URL = 'http://localhost:5000/api';

const TodoApp = () => {
  const { user, logout } = useAuth();
  const [rawText, setRawText] = useState('');
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [aiProvider, setAiProvider] = useState('');
  const [filter, setFilter] = useState({
    status: 'all',
    priority: 'all',
    category: 'all',
    due_date: 'all'
  });

  // Load tasks on component mount
  useEffect(() => {
    loadTasks();
  }, [filter]);

  const loadTasks = async () => {
    try {
      const params = new URLSearchParams();
      if (filter.status !== 'all') params.append('status', filter.status);
      if (filter.priority !== 'all') params.append('priority', filter.priority);
      if (filter.category !== 'all') params.append('category', filter.category);
      if (filter.due_date !== 'all') params.append('due_date', filter.due_date);

      const response = await axios.get(`${API_BASE_URL}/tasks?${params}`, {
        withCredentials: true
      });
      if (response.data.success) {
        setTasks(response.data.tasks);
      }
    } catch (error) {
      console.error('Error loading tasks:', error);
      setMessage('Error loading tasks');
    }
  };

  const processTasks = async () => {
    if (!rawText.trim()) {
      setMessage('Please enter some tasks to process');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const response = await axios.post(`${API_BASE_URL}/process-tasks`, {
        text: rawText
      }, {
        withCredentials: true
      });

      if (response.data.success) {
        const provider = response.data.ai_provider || 'Unknown';
        setMessage(`Successfully processed ${response.data.tasks.length} tasks using ${provider}!`);
        setAiProvider(provider);
        setRawText('');
        loadTasks(); // Reload tasks to show new ones
      } else {
        setMessage(response.data.message || 'Error processing tasks');
        setAiProvider('');
      }
    } catch (error) {
      console.error('Error processing tasks:', error);
      setMessage('Error processing tasks. Make sure the backend is running.');
      setAiProvider('');
    } finally {
      setLoading(false);
    }
  };

  const updateTaskStatus = async (taskId, newStatus) => {
    try {
      await axios.put(`${API_BASE_URL}/tasks/${taskId}`, {
        status: newStatus
      }, {
        withCredentials: true
      });
      loadTasks(); // Reload tasks
    } catch (error) {
      console.error('Error updating task:', error);
      setMessage('Error updating task');
    }
  };

  const deleteTask = async (taskId) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await axios.delete(`${API_BASE_URL}/tasks/${taskId}`, {
          withCredentials: true
        });
        loadTasks(); // Reload tasks
        setMessage('Task deleted successfully');
      } catch (error) {
        console.error('Error deleting task:', error);
        setMessage('Error deleting task');
      }
    }
  };

  const clearAllTasks = async () => {
    if (tasks.length === 0) {
      setMessage('No tasks to clear');
      return;
    }

    const confirmMessage = `Are you sure you want to delete all ${tasks.length} tasks? This action cannot be undone.`;
    if (window.confirm(confirmMessage)) {
      try {
        const response = await axios.delete(`${API_BASE_URL}/tasks/clear-all`, {
          withCredentials: true
        });
        if (response.data.success) {
          setMessage(`Successfully cleared ${response.data.deleted_count} tasks`);
          loadTasks(); // Reload tasks
        } else {
          setMessage(response.data.message || 'Error clearing tasks');
        }
      } catch (error) {
        console.error('Error clearing tasks:', error);
        setMessage('Error clearing tasks');
      }
    }
  };

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to logout?')) {
      await logout();
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'High':
        return <AlertCircle className="w-4 h-4" />;
      case 'Medium':
        return <Clock className="w-4 h-4" />;
      case 'Low':
        return <Calendar className="w-4 h-4" />;
      default:
        return <Circle className="w-4 h-4" />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'High':
        return 'priority-high';
      case 'Medium':
        return 'priority-medium';
      case 'Low':
        return 'priority-low';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryColor = (category) => {
    switch (category.toLowerCase()) {
      case 'work':
        return 'category-work';
      case 'admin':
        return 'category-admin';
      case 'meetings':
        return 'category-meetings';
      case 'personal':
        return 'category-personal';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDueDate = (dueDate) => {
    if (!dueDate) return '';
    
    const today = new Date();
    const due = new Date(dueDate);
    const diffTime = due - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    if (diffDays === -1) return 'Yesterday';
    if (diffDays < -1) return `${Math.abs(diffDays)} days overdue`;
    if (diffDays <= 7) return `In ${diffDays} days`;
    
    return due.toLocaleDateString();
  };

  const getDueDateColor = (dueDate) => {
    if (!dueDate) return 'bg-gray-100 text-gray-800';
    
    const today = new Date();
    const due = new Date(dueDate);
    const diffTime = due - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'bg-red-100 text-red-800 border border-red-200'; // Overdue
    if (diffDays === 0) return 'bg-orange-100 text-orange-800 border border-orange-200'; // Today
    if (diffDays === 1) return 'bg-yellow-100 text-yellow-800 border border-yellow-200'; // Tomorrow
    if (diffDays <= 7) return 'bg-blue-100 text-blue-800 border border-blue-200'; // This week
    
    return 'bg-green-100 text-green-800 border border-green-200'; // Future
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                AI To-Do List Manager
              </h1>
              <p className="text-gray-600 mt-1">
                Welcome back, {user?.name}! Paste your raw task notes and let AI organize them for you
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <User className="w-4 h-4" />
                <span>{user?.name}</span>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                  {user?.email}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Process Your Tasks
          </h2>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="rawText" className="block text-sm font-medium text-gray-700 mb-2">
                Paste your raw task notes here:
              </label>
              <textarea
                id="rawText"
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                placeholder="Example: Finish PPT for client meeting tomorrow, check AWS logs for errors, call client about project update..."
                className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              />
            </div>
            
            <button
              onClick={processTasks}
              disabled={loading || !rawText.trim()}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4 mr-2" />
                  Process Tasks
                </>
              )}
            </button>
          </div>

          {message && (
            <div className={`mt-4 p-3 rounded-md ${
              message.includes('Error') || message.includes('error') 
                ? 'bg-red-100 text-red-700 border border-red-200' 
                : 'bg-green-100 text-green-700 border border-green-200'
            }`}>
              <div className="flex items-center justify-between">
                <span>{message}</span>
                {aiProvider && !message.includes('Error') && (
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full font-medium">
                    🤖 {aiProvider.toUpperCase()}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Filter className="w-5 h-5 mr-2" />
            Filter Tasks
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={filter.status}
                onChange={(e) => setFilter({...filter, status: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <select
                value={filter.priority}
                onChange={(e) => setFilter({...filter, priority: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Priorities</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                value={filter.category}
                onChange={(e) => setFilter({...filter, category: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Categories</option>
                <option value="Work">Work</option>
                <option value="Admin">Admin</option>
                <option value="Meetings">Meetings</option>
                <option value="Personal">Personal</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Due Date
              </label>
              <select
                value={filter.due_date}
                onChange={(e) => setFilter({...filter, due_date: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Dates</option>
                <option value="today">Today</option>
                <option value="tomorrow">Tomorrow</option>
                <option value="this_week">This Week</option>
                <option value="overdue">Overdue</option>
                <option value="no_date">No Date Set</option>
              </select>
            </div>
          </div>
        </div>

        {/* Quick Date Filters */}
        <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Quick Filters</h4>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setFilter({...filter, due_date: 'today'})}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                filter.due_date === 'today'
                  ? 'bg-blue-100 text-blue-700 border border-blue-200'
                  : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
              }`}
            >
              📅 Today
            </button>
            <button
              onClick={() => setFilter({...filter, due_date: 'tomorrow'})}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                filter.due_date === 'tomorrow'
                  ? 'bg-green-100 text-green-700 border border-green-200'
                  : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
              }`}
            >
              🌅 Tomorrow
            </button>
            <button
              onClick={() => setFilter({...filter, due_date: 'this_week'})}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                filter.due_date === 'this_week'
                  ? 'bg-purple-100 text-purple-700 border border-purple-200'
                  : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
              }`}
            >
              📆 This Week
            </button>
            <button
              onClick={() => setFilter({...filter, due_date: 'overdue'})}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                filter.due_date === 'overdue'
                  ? 'bg-red-100 text-red-700 border border-red-200'
                  : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
              }`}
            >
              ⚠️ Overdue
            </button>
            <button
              onClick={() => setFilter({status: 'all', priority: 'all', category: 'all', due_date: 'all'})}
              className="px-3 py-2 text-sm font-medium bg-gray-100 text-gray-700 border border-gray-200 rounded-md hover:bg-gray-200 transition-colors"
            >
              🔄 Clear Filters
            </button>
          </div>
        </div>

        {/* Tasks List */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="px-6 py-4 border-b flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">
              Your Tasks ({tasks.length})
            </h3>
            {tasks.length > 0 && (
              <button
                onClick={clearAllTasks}
                className="inline-flex items-center px-3 py-2 text-sm font-medium text-red-700 bg-red-100 border border-red-200 rounded-md hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
                title="Clear all tasks"
              >
                <Trash className="w-4 h-4 mr-1" />
                Clear All
              </button>
            )}
          </div>
          
          <div className="p-6">
            {tasks.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Circle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No tasks found. Process some tasks to get started!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    className={`border rounded-lg p-4 transition-all duration-200 ${
                      task.status === 'completed' 
                        ? 'bg-gray-50 opacity-75' 
                        : 'bg-white hover:shadow-md'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        <button
                          onClick={() => updateTaskStatus(
                            task.id, 
                            task.status === 'completed' ? 'pending' : 'completed'
                          )}
                          className="mt-1 text-gray-400 hover:text-green-600 transition-colors"
                        >
                          {task.status === 'completed' ? (
                            <CheckCircle className="w-5 h-5 text-green-600" />
                          ) : (
                            <Circle className="w-5 h-5" />
                          )}
                        </button>
                        
                        <div className="flex-1">
                          <p className={`text-gray-900 ${
                            task.status === 'completed' ? 'line-through' : ''
                          }`}>
                            {task.description}
                          </p>
                          
                          <div className="flex items-center space-x-4 mt-2">
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getPriorityColor(task.priority)}`}>
                              {getPriorityIcon(task.priority)}
                              <span className="ml-1">{task.priority}</span>
                            </span>
                            
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(task.category)}`}>
                              {task.category}
                            </span>
                            
                            {task.due_date && (
                              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getDueDateColor(task.due_date)}`}>
                                📅 {formatDueDate(task.due_date)}
                              </span>
                            )}
                            
                            <span className="text-xs text-gray-500">
                              {new Date(task.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <button
                        onClick={() => deleteTask(task.id)}
                        className="text-gray-400 hover:text-red-600 transition-colors p-1"
                        title="Delete task"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TodoApp;
