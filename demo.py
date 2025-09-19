"""
AI To-Do List Manager - Demo Script
This script demonstrates how the AI processor works without requiring Python installation.
"""

def demo_ai_processor():
    """Demonstrate the AI processing logic."""
    print("🤖 AI To-Do List Manager - Demo")
    print("=" * 50)
    
    # Simulate the AI processor logic
    def extract_tasks(raw_text):
        """Extract tasks from raw text (enhanced version with compound splitting)."""
        import re
        
        # First, try to split by line breaks
        if '\n' in raw_text:
            tasks = [task.strip() for task in raw_text.split('\n') if task.strip()]
        else:
            # Split by commas and semicolons
            tasks = re.split(r'[,;]', raw_text)
            tasks = [task.strip() for task in tasks if task.strip()]
        
        # Process each task for compound splitting
        all_tasks = []
        for task in tasks:
            compound_tasks = split_compound_task(task)
            all_tasks.extend(compound_tasks)
        
        # Clean up tasks
        cleaned_tasks = []
        for task in all_tasks:
            # Remove common prefixes
            task = re.sub(r'^(finish|complete|do|make|create|call|check|send|review|need to|ping|update|rotate|ship)\s+', '', task, flags=re.IGNORECASE)
            # Remove trailing punctuation
            task = re.sub(r'[.,;!?]+$', '', task)
            # Capitalize first letter
            task = task.capitalize()
            
            if len(task) > 3:
                cleaned_tasks.append(task)
        
        return cleaned_tasks
    
    def split_compound_task(task):
        """Split a single task into multiple tasks if it contains compound actions."""
        task_lower = task.lower()
        
        # Common compound task indicators
        compound_indicators = [
            r'\b(also|and|then|next|additionally|furthermore|plus|as well)\b',
            r'\b(\.\s*also|\.\s*and|\.\s*then|\.\s*next)\b',
            r'\b(oh—|oh -|oh,)\s*',  # Handle "oh—" patterns
            r'\b(then|after that|following that)\b'
        ]
        
        # Check for compound indicators
        for pattern in compound_indicators:
            if re.search(pattern, task_lower):
                # Split the task
                split_tasks = split_by_pattern(task, pattern)
                if len(split_tasks) > 1:
                    return split_tasks
        
        # Check for specific patterns that indicate multiple actions
        multi_action_patterns = [
            r'(.+?)\s+(and|also|then)\s+(.+)',  # "do X and Y"
            r'(.+?)\s*\.\s*(also|and|then)\s+(.+)',  # "do X. also Y"
            r'(.+?)\s*;\s*(.+)',  # "do X; do Y"
            r'(.+?)\s*—\s*(.+)',  # "do X — do Y"
            r'(.+?)\s*-\s*(.+)',  # "do X - do Y"
        ]
        
        for pattern in multi_action_patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                # Extract the parts
                parts = [part.strip() for part in match.groups() if part.strip()]
                if len(parts) >= 2:
                    return parts
        
        # If no compound patterns found, return as single task
        return [task]
    
    def split_by_pattern(task, pattern):
        """Split task by a specific pattern."""
        parts = re.split(pattern, task, flags=re.IGNORECASE)
        # Filter out empty parts and the separator words
        filtered_parts = []
        for part in parts:
            part = part.strip()
            if part and part.lower() not in ['also', 'and', 'then', 'next', 'additionally', 'furthermore', 'plus', 'as well', 'oh—', 'oh -', 'oh,']:
                filtered_parts.append(part)
        
        return filtered_parts if len(filtered_parts) > 1 else [task]
    
    def classify_priority(task):
        """Classify task priority (simplified version)."""
        task_lower = task.lower()
        
        priority_keywords = {
            'high': ['urgent', 'asap', 'deadline', 'critical', 'important', 'immediately', 'today', 'now'],
            'medium': ['soon', 'this week', 'moderate', 'should', 'need to'],
            'low': ['eventually', 'sometime', 'when possible', 'optional', 'nice to have']
        }
        
        # Count keyword matches
        high_count = sum(1 for keyword in priority_keywords['high'] if keyword in task_lower)
        medium_count = sum(1 for keyword in priority_keywords['medium'] if keyword in task_lower)
        low_count = sum(1 for keyword in priority_keywords['low'] if keyword in task_lower)
        
        if high_count > 0:
            return 'High'
        elif medium_count > 0:
            return 'Medium'
        elif low_count > 0:
            return 'Low'
        else:
            if any(word in task_lower for word in ['urgent', 'deadline', 'asap', 'critical']):
                return 'High'
            elif any(word in task_lower for word in ['meeting', 'call', 'email', 'review']):
                return 'Medium'
            else:
                return 'Low'
    
    def classify_category(task):
        """Classify task category (simplified version)."""
        task_lower = task.lower()
        
        category_keywords = {
            'work': ['meeting', 'client', 'project', 'presentation', 'report', 'deadline', 'email', 'call'],
            'admin': ['paperwork', 'forms', 'billing', 'invoice', 'expense', 'hr', 'admin'],
            'meetings': ['meeting', 'call', 'conference', 'discussion', 'sync', 'standup'],
            'personal': ['grocery', 'doctor', 'family', 'personal', 'home', 'shopping']
        }
        
        # Count keyword matches for each category
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in task_lower)
            category_scores[category] = score
        
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category.title()
        
        return 'Work'
    
    # Test cases
    test_cases = [
        {
            "name": "Compound Task from Screenshot",
            "input": "And oh—rotate api keys (security flagged expiring on 30th). also ship a short loom to anish about the demo flow"
        },
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
            "name": "Multiple Compound Tasks",
            "input": "Update client deck v3.1 by eod wed and schedule follow-up meeting; also ping finance re: expense sheet"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print("-" * 30)
        print(f"Input: {test_case['input']}")
        print("\nProcessing...")
        
        # Extract tasks
        tasks = extract_tasks(test_case['input'])
        
        if tasks:
            print(f"✅ Successfully extracted {len(tasks)} tasks!")
            print("\n📋 Processed Tasks:")
            
            for j, task in enumerate(tasks, 1):
                priority = classify_priority(task)
                category = classify_category(task)
                
                print(f"  {j}. {task}")
                print(f"     Priority: {priority} | Category: {category}")
        else:
            print("❌ No tasks found")
        
        print("\n" + "="*50)
    
    print("\n🎉 Demo completed!")
    print("\nTo run the full application:")
    print("1. Install Python 3.8+ from https://www.python.org/downloads/")
    print("2. Install Node.js 16+ from https://nodejs.org/")
    print("3. Run: pip install -r requirements.txt")
    print("4. Run: cd frontend && npm install")
    print("5. Start backend: python backend/app.py")
    print("6. Start frontend: cd frontend && npm start")
    print("7. Open: http://localhost:3000")

if __name__ == "__main__":
    demo_ai_processor()
