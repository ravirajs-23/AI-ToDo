"""
Test script for AI To-Do List Manager
Run this to test the AI processing functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.ai_processor import TaskProcessor
import json

def test_ai_processor():
    """Test the AI processor with sample inputs."""
    print("🤖 Testing AI To-Do List Manager")
    print("=" * 50)
    
    processor = TaskProcessor()
    
    # Test cases
    test_cases = [
        {
            "name": "Basic Task List",
            "input": "Finish PPT for client meeting tomorrow, check AWS logs for errors, call client about project update"
        },
        {
            "name": "Mixed Priorities",
            "input": "URGENT: Fix production bug ASAP, Review quarterly reports this week, Eventually clean up old files"
        },
        {
            "name": "Different Categories",
            "input": "Schedule team standup meeting, Submit expense reports, Call doctor for appointment, Review project documentation"
        },
        {
            "name": "Complex Format",
            "input": """
            • Complete presentation for board meeting (deadline: Friday)
            • Check server logs and fix any issues
            • Call Sarah about the contract
            • Update project timeline
            • Personal: Book dentist appointment
            """
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print("-" * 30)
        print(f"Input: {test_case['input'].strip()}")
        print("\nProcessing...")
        
        result = processor.process_tasks(test_case['input'])
        
        if result['success']:
            print(f"✅ {result['message']}")
            print("\n📋 Processed Tasks:")
            for task in result['tasks']:
                print(f"  • {task['description']}")
                print(f"    Priority: {task['priority']} | Category: {task['category']}")
        else:
            print(f"❌ {result['message']}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    test_ai_processor()
