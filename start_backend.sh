#!/bin/bash
echo "Starting AI To-Do List Manager..."
echo

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo
echo "Testing AI processor..."
python test_ai_processor.py

echo
echo "Starting Flask backend server..."
echo "Backend will be available at: http://localhost:5000"
echo
cd backend
python app.py
