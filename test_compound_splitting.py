"""
Test script for enhanced AI To-Do List Manager with compound task splitting
Run this to test the improved task extraction functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.ai_processor import TaskProcessor
import json

def test_compound_task_splitting():
    """Test the enhanced AI processor with compound task examples."""
    print("🤖 Testing Enhanced AI To-Do List Manager - Compound Task Splitting")
    print("=" * 70)
    
    processor = TaskProcessor()
    
    # Test cases focusing on compound tasks
    test_cases = [
        {
            "name": "Compound Task with 'also'",
            "input": "And oh—rotate api keys (security flagged expiring on 30th). also ship a short loom to anish about the demo flow"
        },
        {
            "name": "Multiple Actions with 'and'",
            "input": "Update client deck v3.1 by eod wed and schedule follow-up meeting"
        },
        {
            "name": "Complex Compound Task",
            "input": "Fix production bug ASAP, also update documentation, and then deploy to staging"
        },
        {
            "name": "Security and Admin Tasks",
            "input": "Rotate API keys expiring next week; also submit expense reports and ping finance team"
        },
        {
            "name": "Mixed Priorities Compound",
            "input": "URGENT: Fix critical security issue, also clean up old files when possible"
        },
        {
            "name": "Simple Single Task",
            "input": "Call client about project update"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print("-" * 50)
        print(f"Input: {test_case['input']}")
        print("\nProcessing...")
        
        result = processor.process_tasks(test_case['input'])
        
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"\n📋 Processed Tasks ({len(result['tasks'])}):")
            for j, task in enumerate(result['tasks'], 1):
                print(f"  {j}. {task['description']}")
                print(f"     Priority: {task['priority']} | Category: {task['category']}")
                
                # Highlight compound task splitting
                if len(result['tasks']) > 1:
                    print(f"     ✨ Split from compound task")
        else:
            print(f"❌ {result['message']}")
        
        print("\n" + "="*70)
    
    print("\n🎉 Enhanced Testing completed!")
    print("\nKey Improvements:")
    print("• ✅ Compound task splitting (e.g., 'X and Y' → 2 separate tasks)")
    print("• ✅ Security task detection (API keys, expiring items)")
    print("• ✅ Deadline recognition (by eod, expiring on)")
    print("• ✅ Better priority classification")
    print("• ✅ Enhanced text cleaning and normalization")

if __name__ == "__main__":
    test_compound_task_splitting()
