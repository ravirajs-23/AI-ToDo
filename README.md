# AI To-Do List Manager
## ChatGPT & Gemini API Integration

### 🎯 Overview
An AI-powered tool that automatically organizes raw task notes into structured to-do lists with priorities and categories. Uses advanced AI APIs (ChatGPT or Gemini) for intelligent task processing with fallback to rule-based processing.

### ✨ Features
- ✅ **AI-Powered Processing** - Uses ChatGPT or Gemini APIs for intelligent task extraction
- ✅ **Smart Task Extraction** - Automatically extracts tasks from raw text with context understanding
- ✅ **Priority Classification** - Assigns Highest/High/Medium/Low priorities using AI
- ✅ **Category Suggestion** - Groups tasks into Work/Admin/Meetings/Personal using AI
- ✅ **Fallback Processing** - Rule-based processing when AI APIs are unavailable
- ✅ **Clean Web Interface** - Modern, responsive React frontend
- ✅ **Task Management** - Mark complete, edit, delete tasks
- ✅ **Filtering & Search** - Filter by status, priority, category

### 🏗️ Project Structure
```
ai-todo-manager/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── ai_processor.py        # Core AI processing logic
│   └── tasks.db              # SQLite database (auto-created)
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── index.js          # React entry point
│   │   └── index.css         # Tailwind CSS styles
│   ├── package.json          # Frontend dependencies
│   └── public/
│       └── index.html        # HTML template
├── requirements.txt          # Python dependencies
├── test_ai_processor.py      # Test script
├── start_backend.bat         # Windows startup script
├── start_backend.sh          # Linux/Mac startup script
└── README.md                 # This file
```

### 🚀 Quick Start

#### Prerequisites
- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Node.js 16+** - [Download here](https://nodejs.org/)
- **Git** - [Download here](https://git-scm.com/)
- **AI API Key** (Choose one):
  - **OpenAI API Key** - [Get from OpenAI](https://platform.openai.com/api-keys) for ChatGPT
  - **Google API Key** - [Get from Google AI](https://makersuite.google.com/app/apikey) for Gemini
  - **No API Key** - System will use rule-based fallback processing

#### Installation Steps

1. **Clone/Download the project**
   ```bash
   git clone <repository-url>
   cd ai-todo-manager
   ```

2. **Set up AI API Keys** (Choose one option)
   
   **Option A: ChatGPT (OpenAI)**
   ```bash
   # Windows
   set OPENAI_API_KEY=your_openai_api_key_here
   set AI_PROVIDER=chatgpt
   
   # Linux/Mac
   export OPENAI_API_KEY="your_openai_api_key_here"
   export AI_PROVIDER="chatgpt"
   ```
   
   **Option B: Gemini (Google)**
   ```bash
   # Windows
   set GEMINI_API_KEY=your_gemini_api_key_here
   set AI_PROVIDER=gemini
   
   # Linux/Mac
   export GEMINI_API_KEY="your_gemini_api_key_here"
   export AI_PROVIDER="gemini"
   ```
   
   **Option C: No API Keys (Fallback Mode)**
   ```bash
   # The system will automatically use rule-based processing
   set AI_PROVIDER=fallback
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. **Test the AI processor**
   ```bash
   python test_ai_integration.py
   ```

6. **Start the backend server**
   ```bash
   # Windows
   start_backend.bat
   
   # Linux/Mac
   chmod +x start_backend.sh
   ./start_backend.sh
   
   # Or manually
   cd backend
   python app.py
   ```

7. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm start
   ```

8. **Open your browser**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

### 🎮 Usage

1. **Open the web interface** at http://localhost:3000
2. **Paste your raw task notes** in the text area
   ```
   Example: Finish PPT for client meeting tomorrow, check AWS logs for errors, call client about project update
   ```
3. **Click "Process Tasks"** to let AI organize them
4. **Review the results** - tasks are automatically categorized and prioritized
5. **Manage your tasks** - mark complete, edit, delete, or filter

### 🔧 API Endpoints

- `GET /api/health` - Health check
- `POST /api/process-tasks` - Process raw text into tasks
- `GET /api/tasks` - Get all tasks (with filters)
- `PUT /api/tasks/:id` - Update a task
- `DELETE /api/tasks/:id` - Delete a task
- `GET /api/stats` - Get task statistics

### 🧠 How It Works

The AI processor uses a sophisticated multi-strategy approach:
- **Email-style processing** - Handles complex email requests with multiple actions
- **Compound task splitting** - Intelligently splits "X and Y" patterns into separate tasks
- **Regex-based task extraction** - Splits text by common separators and sentence boundaries
- **Keyword-based priority classification** - Identifies urgency indicators and security tasks
- **Pattern-based categorization** - Groups tasks by context (Work/Admin/Meetings/Personal)
- **Rule-based cleaning** - Removes filler words, email headers, and normalizes text
- **Duplicate removal** - Ensures unique tasks while preserving order

### 🛠️ Customization

#### Adding New Priority Keywords
Edit `backend/ai_processor.py`:
```python
self.priority_keywords = {
    'high': ['urgent', 'asap', 'deadline', 'critical', 'your_keyword'],
    'medium': ['soon', 'this week', 'moderate', 'your_keyword'],
    'low': ['eventually', 'sometime', 'optional', 'your_keyword']
}
```

#### Adding New Categories
```python
self.category_keywords = {
    'work': ['meeting', 'client', 'project', 'your_keyword'],
    'admin': ['paperwork', 'forms', 'billing', 'your_keyword'],
    'meetings': ['meeting', 'call', 'conference', 'your_keyword'],
    'personal': ['grocery', 'doctor', 'family', 'your_keyword'],
    'your_category': ['keyword1', 'keyword2', 'keyword3']
}
```

### 🐛 Troubleshooting

**Backend won't start:**
- Check Python is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Check port 5000 is available

**Frontend won't start:**
- Check Node.js is installed: `node --version`
- Install dependencies: `cd frontend && npm install`
- Check port 3000 is available

**AI processing errors:**
- Run test script: `python test_ai_processor.py`
- Check NLTK data is downloaded (automatic on first run)

### 📈 Future Enhancements

- [ ] Train custom Hugging Face models for better accuracy
- [ ] Add due date extraction
- [ ] Implement task dependencies
- [ ] Add export functionality (CSV, PDF)
- [ ] Mobile app version
- [ ] Team collaboration features
- [ ] Integration with calendar apps

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### 📄 License

This project is open source and available under the MIT License.
