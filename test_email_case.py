"""
Test the current system with the email use case
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.ai_processor import TaskProcessor
import json

def test_email_case():
    """Test the email use case to see current behavior."""
    print("🧪 Testing Email Use Case - Enhanced Version")
    print("=" * 60)
    
    processor = TaskProcessor()
    
    email_text = """Subject: URGENT – Client sandbox down
Can we restart the staging services and share a 2-line RCA by tomorrow 11am? Also, please archive old logs older than 14 days.
– Ops"""
    
    print(f"Input Email:")
    print(f'"{email_text}"')
    print("\nProcessing with enhanced email extraction...")
    
    result = processor.process_tasks(email_text)
    
    if result['success']:
        print(f"✅ {result['message']}")
        print(f"\n📋 Enhanced Output ({len(result['tasks'])} tasks):")
        for i, task in enumerate(result['tasks'], 1):
            print(f"  {i}. {task['description']}")
            print(f"     Priority: {task['priority']} | Category: {task['category']}")
    else:
        print(f"❌ {result['message']}")
    
    print("\n" + "="*60)
    print("Expected tasks should be:")
    print("1. Restart the staging services")
    print("2. Share a 2-line RCA by tomorrow 11am") 
    print("3. Archive old logs older than 14 days")
    print("="*60)
    
    # Test with additional email examples
    print("\n🧪 Testing Additional Email Patterns")
    print("-" * 40)
    
    additional_tests = [
        {
            "name": "Simple Request",
            "text": "Can you please update the documentation and deploy to staging?"
        },
        {
            "name": "Multiple Actions",
            "text": "Please restart the server, check the logs, and notify the team."
        },
        {
            "name": "Complex Deadline",
            "text": "Can we fix the bug and test it by end of day Friday?"
        }
    ]
    
    for test in additional_tests:
        print(f"\n📧 {test['name']}:")
        print(f"Input: {test['text']}")
        result = processor.process_tasks(test['text'])
        if result['success']:
            print(f"Output ({len(result['tasks'])} tasks):")
            for i, task in enumerate(result['tasks'], 1):
                print(f"  {i}. {task['description']} ({task['priority']})")
        print("-" * 40)

if __name__ == "__main__":
    test_email_case()
