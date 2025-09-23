#!/usr/bin/env python3
"""
Test the comprehensive task list scenario
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ai_processor import TaskProcessor

def test_comprehensive_scenario():
    """Test the comprehensive task list scenario."""
    processor = TaskProcessor()
    
    print("🎯 TESTING COMPREHENSIVE TASK LIST SCENARIO")
    print("=" * 70)
    
    # Input text
    input_text = "Pay electricity bill, Book travel tickets\nArrange team lunch\nSubmit report by EOD, Prepare meeting slides, Buy snacks. Install software update, Clean inbox. Plan team building activity\nSchedule dentist appointment, Call client, Renew vehicle insurance"
    
    # Expected output
    expected_tasks = [
        {"description": "Pay electricity bill", "priority": "High", "category": "Personal"},
        {"description": "Book travel tickets", "priority": "Medium", "category": "Personal"},
        {"description": "Arrange team lunch", "priority": "Medium", "category": "Work"},
        {"description": "Submit report by EOD", "priority": "High", "category": "Work"},
        {"description": "Prepare meeting slides", "priority": "Medium", "category": "Work"},
        {"description": "Buy snacks", "priority": "Low", "category": "Personal"},
        {"description": "Install software update", "priority": "Medium", "category": "Work"},
        {"description": "Clean inbox", "priority": "Low", "category": "Work"},
        {"description": "Plan team building activity", "priority": "Medium", "category": "Work"},
        {"description": "Schedule dentist appointment", "priority": "Medium", "category": "Personal"},
        {"description": "Call client", "priority": "High", "category": "Work"},
        {"description": "Renew vehicle insurance", "priority": "High", "category": "Personal"}
    ]
    
    print(f"Input: {input_text}")
    print(f"\nExpected Output ({len(expected_tasks)} tasks):")
    for i, task in enumerate(expected_tasks, 1):
        print(f"{i:2d}. {task['description']} | Priority: {task['priority']} | Category: {task['category']}")
    
    print(f"\n" + "=" * 70)
    print("ACTUAL OUTPUT:")
    print("=" * 70)
    
    # Process the input
    result = processor.process_tasks(input_text)
    
    if result['success']:
        tasks = result['tasks']
        print(f"✅ Processing successful: {len(tasks)} tasks extracted")
        
        for i, task in enumerate(tasks, 1):
            priority_emoji = {"Highest": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
            category_emoji = {"Work": "💼", "Meetings": "📅", "Personal": "🏠", "Admin": "📋"}
            
            print(f"{i:2d}. {task['description']}")
            print(f"    {priority_emoji.get(task['priority'], '⚪')} Priority: {task['priority']}")
            print(f"    {category_emoji.get(task['category'], '📝')} Category: {task['category']}")
        
        print(f"\n" + "=" * 70)
        print("ANALYSIS:")
        print("=" * 70)
        
        # Task count analysis
        print(f"Task Count: Expected {len(expected_tasks)}, Got {len(tasks)}")
        
        # Priority distribution
        priorities = [task['priority'] for task in tasks]
        priority_counts = {}
        for p in priorities:
            priority_counts[p] = priority_counts.get(p, 0) + 1
        
        print(f"Priority Distribution: {priority_counts}")
        
        # Category distribution
        categories = [task['category'] for task in tasks]
        category_counts = {}
        for c in categories:
            category_counts[c] = category_counts.get(c, 0) + 1
        
        print(f"Category Distribution: {category_counts}")
        
        # Check specific high-priority tasks
        print(f"\nHigh Priority Task Analysis:")
        high_priority_tasks = [t for t in tasks if t['priority'] == 'High']
        expected_high = [t for t in expected_tasks if t['priority'] == 'High']
        
        print(f"Expected High Priority: {len(expected_high)} tasks")
        print(f"Actual High Priority: {len(high_priority_tasks)} tasks")
        
        for task in high_priority_tasks:
            print(f"  ✅ {task['description']} - {task['category']}")
        
        # Check for missing high-priority tasks
        expected_high_descriptions = [t['description'].lower() for t in expected_high]
        actual_high_descriptions = [t['description'].lower() for t in high_priority_tasks]
        
        missing_high = []
        for expected_desc in expected_high_descriptions:
            if not any(expected_desc in actual_desc for actual_desc in actual_high_descriptions):
                missing_high.append(expected_desc)
        
        if missing_high:
            print(f"\n⚠️ Missing High Priority Tasks:")
            for missing in missing_high:
                print(f"  ❌ {missing}")
        
        # Overall accuracy assessment
        print(f"\n" + "=" * 70)
        print("ACCURACY ASSESSMENT:")
        print("=" * 70)
        
        # Check task splitting accuracy
        if len(tasks) == len(expected_tasks):
            print("✅ Task count: Perfect match")
        elif abs(len(tasks) - len(expected_tasks)) <= 2:
            print("⚠️ Task count: Close match")
        else:
            print("❌ Task count: Significant difference")
        
        # Check priority accuracy
        high_priority_accuracy = len(high_priority_tasks) / len(expected_high) * 100 if expected_high else 100
        print(f"High Priority Accuracy: {high_priority_accuracy:.1f}%")
        
        # Overall assessment
        if len(tasks) == len(expected_tasks) and high_priority_accuracy >= 80:
            print("🎉 EXCELLENT! System is performing very well!")
        elif len(tasks) >= len(expected_tasks) * 0.8 and high_priority_accuracy >= 60:
            print("👍 GOOD! System is performing well with minor issues!")
        else:
            print("🔧 NEEDS IMPROVEMENT! System needs further tuning!")
    
    else:
        print(f"❌ Processing failed: {result['message']}")

if __name__ == "__main__":
    test_comprehensive_scenario()
