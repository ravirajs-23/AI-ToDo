#!/usr/bin/env python3
"""
Screen Recording Helper for E2E Demo
Creates instructions and setup for recording the demo
"""

import os
import sys
import time
from datetime import datetime

def print_recording_instructions():
    """Print instructions for recording the demo"""
    print("🎥" + "="*78 + "🎥")
    print("🎬              SCREEN RECORDING SETUP FOR E2E DEMO                    🎬")
    print("🎥" + "="*78 + "🎥")
    print()
    
    print("📋 PRE-RECORDING CHECKLIST:")
    print("✅ 1. Backend server is running (cd backend && python app.py)")
    print("✅ 2. Terminal window is maximized")
    print("✅ 3. Font size is readable (14pt+ recommended)")
    print("✅ 4. Screen recording software is ready")
    print()
    
    print("🎬 RECORDING OPTIONS:")
    print()
    
    print("🪟 WINDOWS USERS:")
    print("   • Built-in: Windows Game Bar (Windows + G)")
    print("   • OBS Studio: https://obsproject.com/")
    print("   • Camtasia: https://www.techsmith.com/camtasia.html")
    print()
    
    print("🍎 MAC USERS:")
    print("   • Built-in: QuickTime Player (File → New Screen Recording)")
    print("   • Built-in: Screenshot app (Cmd + Shift + 5)")
    print("   • OBS Studio: https://obsproject.com/")
    print()
    
    print("🐧 LINUX USERS:")
    print("   • OBS Studio: sudo apt install obs-studio")
    print("   • SimpleScreenRecorder: sudo apt install simplescreenrecorder")
    print("   • FFmpeg command line: ffmpeg -f x11grab -s 1920x1080 -i :0.0 output.mp4")
    print()
    
    print("⚙️ RECOMMENDED SETTINGS:")
    print("   • Resolution: 1920x1080 (Full HD)")
    print("   • Frame Rate: 30 FPS")
    print("   • Format: MP4 (H.264)")
    print("   • Audio: Optional (can add voiceover later)")
    print()
    
    print("🎯 DEMO STRUCTURE (Total ~5-7 minutes):")
    print("   📊 Step 1: Health Check (30 seconds)")
    print("   📝 Step 2: Task Processing (90 seconds)")
    print("   📋 Step 3: Data Retrieval & Filtering (90 seconds)")
    print("   ✏️ Step 4: Task Management (60 seconds)")
    print("   📅 Step 5: Date Intelligence (90 seconds)")
    print("   📊 Step 6: Statistics Dashboard (30 seconds)")
    print("   🎯 Step 7: Summary (30 seconds)")
    print()
    
    print("💡 PRO TIPS:")
    print("   • Clear terminal before starting: cls (Windows) or clear (Linux/Mac)")
    print("   • Use fullscreen terminal for better visibility")
    print("   • Record in quiet environment for optional audio")
    print("   • Consider adding subtitles or annotations later")
    print()

def create_recording_script():
    """Create a batch script for easy recording setup"""
    
    # Windows batch script
    windows_script = """@echo off
echo 🎬 Setting up AI To-Do List Manager Demo Recording...
echo.

REM Clear screen and set title
cls
title AI To-Do List Manager - E2E Demo Recording

REM Check if backend is running
echo 📊 Checking backend status...
curl -s http://localhost:5000/api/health > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Backend not running! Please start it first:
    echo    cd backend ^&^& python app.py
    pause
    exit /b 1
)

echo ✅ Backend is running!
echo.
echo 🎥 Ready to start recording!
echo    1. Start your screen recording software
echo    2. Press any key to begin demo
echo    3. Recording will auto-start the demo
pause > nul

REM Run the demo
python video_demo_e2e.py

echo.
echo 🎬 Demo completed! Stop your recording now.
pause
"""
    
    # Linux/Mac shell script  
    unix_script = """#!/bin/bash
echo "🎬 Setting up AI To-Do List Manager Demo Recording..."
echo

# Clear screen and set title
clear
echo -e "\\033]0;AI To-Do List Manager - E2E Demo Recording\\007"

# Check if backend is running
echo "📊 Checking backend status..."
if ! curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "❌ Backend not running! Please start it first:"
    echo "   cd backend && python app.py"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Backend is running!"
echo
echo "🎥 Ready to start recording!"
echo "   1. Start your screen recording software"
echo "   2. Press Enter to begin demo"
echo "   3. Recording will auto-start the demo"
read -p ""

# Run the demo
python3 video_demo_e2e.py

echo
echo "🎬 Demo completed! Stop your recording now."
read -p "Press Enter to exit..."
"""
    
    # Write scripts
    try:
        with open("record_demo.bat", "w") as f:
            f.write(windows_script)
        
        with open("record_demo.sh", "w") as f:
            f.write(unix_script)
        
        # Make shell script executable
        if os.name != 'nt':
            os.chmod("record_demo.sh", 0o755)
        
        print("📁 RECORDING SCRIPTS CREATED:")
        print("   🪟 Windows: record_demo.bat")
        print("   🐧 Linux/Mac: record_demo.sh")
        print()
        
    except Exception as e:
        print(f"❌ Failed to create recording scripts: {e}")

def create_demo_checklist():
    """Create a checklist file for the demo"""
    checklist = """AI TO-DO LIST MANAGER - E2E DEMO CHECKLIST
=============================================

PRE-RECORDING SETUP:
□ Backend server running (cd backend && python app.py)
□ Terminal font size increased (14pt+)
□ Terminal window maximized
□ Screen recording software ready
□ Audio recording setup (optional)
□ Quiet recording environment

DEMO STEPS TO RECORD:
□ Step 1: Health Check - Verify backend connectivity
□ Step 2: Task Processing - Show AI parsing different formats
□ Step 3: Data Retrieval - Demonstrate filtering capabilities  
□ Step 4: Task Management - Show CRUD operations
□ Step 5: Date Intelligence - Test smart date detection
□ Step 6: Statistics - Display dashboard analytics
□ Step 7: Summary - Highlight key achievements

POST-RECORDING:
□ Review recording quality
□ Add titles/annotations (optional)
□ Export in appropriate format
□ Share demo video

EXPECTED OUTCOMES:
□ All API endpoints working
□ AI processing demonstrates intelligence
□ Real-time updates show correctly
□ Date detection works with abbreviations
□ Filtering shows accurate results
□ Statistics display properly
□ Professional demonstration quality

TECHNICAL VALIDATION:
□ 100% E2E test pass rate
□ All HTTP requests successful
□ No error messages in demo
□ Smooth transitions between steps
□ Clear visual output

DEMO DURATION: ~5-7 minutes
RECOMMENDED EXPORT: MP4, 1920x1080, 30fps
"""
    
    try:
        with open("demo_checklist.txt", "w") as f:
            f.write(checklist)
        print("📋 Demo checklist created: demo_checklist.txt")
    except Exception as e:
        print(f"❌ Failed to create checklist: {e}")

def main():
    """Main function"""
    print_recording_instructions()
    
    print("🔧 SETUP AUTOMATION:")
    print()
    
    create_recording_script()
    create_demo_checklist()
    
    print("🚀 READY TO RECORD!")
    print()
    print("QUICK START:")
    if os.name == 'nt':
        print("   🪟 Windows: Double-click record_demo.bat")
    else:
        print("   🐧 Linux/Mac: ./record_demo.sh")
    print("   📹 Manual: python video_demo_e2e.py")
    print()
    
    print("📁 FILES CREATED:")
    print("   📋 demo_checklist.txt - Recording checklist")
    print("   🎬 record_demo.bat/sh - Automated setup scripts")
    print("   🎥 video_demo_e2e.py - Main demo script")
    print()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"💾 Session: {timestamp}")
    print("🎬 Happy recording! 🎥")

if __name__ == "__main__":
    main()
