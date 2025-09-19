"""
Debug script to see exactly what's happening with the email processing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.ai_processor import TaskProcessor
import json

def debug_email_processing():
    """Debug the email processing step by step."""
    print("🔍 Debugging Email Processing - CORRECTED VERSION")
    print("=" * 70)
    
    processor = TaskProcessor()
    
    email_text = """Subject: URGENT – Client sandbox down
Can we restart the staging services and share a 2-line RCA by tomorrow 11am? Also, please archive old logs older than 14 days.
– Ops"""
    
    print(f"Original Input:")
    print(f'"{email_text}"')
    print("\n" + "="*70)
    
    # Test the cleaning step
    cleaned_text = processor._clean_input_text(email_text)
    print(f"After cleaning:")
    print(f'"{cleaned_text}"')
    print("\n" + "="*70)
    
    # Test email extraction
    email_tasks = processor._extract_email_tasks(cleaned_text)
    print(f"Email extraction result:")
    print(f"Tasks: {email_tasks}")
    print("\n" + "="*70)
    
    # Test priority classification for each task
    print("Testing priority classification:")
    for i, task in enumerate(email_tasks, 1):
        priority = processor.classify_priority(task)
        print(f"Task {i}: '{task}' → Priority: {priority}")
    print("\n" + "="*70)
    
    # Test full processing
    print("Full processing result:")
    result = processor.process_tasks(email_text)
    
    if result['success']:
        print(f"✅ {result['message']}")
        print(f"\n📋 Final Output ({len(result['tasks'])} tasks):")
        for i, task in enumerate(result['tasks'], 1):
            print(f"  {i}. {task['description']}")
            print(f"     Priority: {task['priority']} | Category: {task['category']}")
    else:
        print(f"❌ {result['message']}")
    
    print("\n" + "="*70)
    print("Expected:")
    print("1. Restart the staging services (High priority)")
    print("2. Share a 2-line RCA by tomorrow 11am (High priority)")
    print("3. Archive old logs older than 14 days (Medium priority)")
    print("="*70)

if __name__ == "__main__":
    debug_email_processing()
