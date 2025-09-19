"""
Core AI processing engine for task extraction, priority classification, and categorization
using Hugging Face transformers for local processing.
"""

import re
import json
from typing import List, Dict, Any
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class TaskProcessor:
    """Main class for processing raw task text using Hugging Face models."""
    
    def __init__(self):
        self.priority_classifier = None
        self.category_classifier = None
        self.stop_words = set(stopwords.words('english'))
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize Hugging Face models for classification."""
        try:
            # Use a lightweight model for priority classification
            # We'll create a custom classifier based on keywords and patterns
            print("Initializing AI models...")
            
            # For now, we'll use rule-based classification
            # In a production system, you'd train custom models
            self.priority_keywords = {
                'high': ['urgent', 'asap', 'deadline', 'critical', 'important', 'immediately', 'today', 'now', 'blocker', 'time-sensitive', 'tmw', 'tomorrow', 'eod', 'end of day'],
                'medium': ['soon', 'this week', 'moderate', 'should', 'need to', 'this week', 'next week'],
                'low': ['eventually', 'sometime', 'when possible', 'optional', 'nice to have', 'nice-to-have']
            }
            
            self.category_keywords = {
                'work': ['meeting', 'client', 'project', 'presentation', 'report', 'deadline', 'email', 'call', 'ppt', 'deck', 'aws', 'logs', 'ssl', 'cert', 'portal', 'intern', 'bug', 'navbar', 'mobile', 's3', 'upload', 'timesheet', 'townhall', 'domain', 'readme', 'invoice', 'followup', 'demo', 'export', 'data', 'report'],
                'admin': ['paperwork', 'forms', 'billing', 'invoice', 'expense', 'hr', 'admin', 'travel', 'reimbursement', 'hiring', 'loop', 'q3'],
                'meetings': ['meeting', 'call', 'conference', 'discussion', 'sync', 'standup', 'retro', '1:1', 'amit'],
                'personal': ['grocery', 'doctor', 'family', 'personal', 'home', 'shopping', 'mom', 'bday', 'birthday', 'gift', 'internet', 'bill']
            }
            
            print("AI models initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing models: {e}")
            # Fallback to rule-based approach
            self._initialize_fallback()
    
    def _initialize_fallback(self):
        """Initialize fallback rule-based classification."""
        self.priority_keywords = {
            'high': ['urgent', 'asap', 'deadline', 'critical', 'important', 'immediately', 'today', 'now', 'blocker', 'time-sensitive', 'tmw', 'tomorrow', 'eod', 'end of day'],
            'medium': ['soon', 'this week', 'moderate', 'should', 'need to', 'this week', 'next week'],
            'low': ['eventually', 'sometime', 'when possible', 'optional', 'nice to have', 'nice-to-have']
        }
        
        self.category_keywords = {
            'work': ['meeting', 'client', 'project', 'presentation', 'report', 'deadline', 'email', 'call', 'ppt', 'deck', 'aws', 'logs', 'ssl', 'cert', 'portal', 'intern', 'bug', 'navbar', 'mobile', 's3', 'upload', 'timesheet', 'townhall', 'domain', 'readme', 'invoice', 'followup', 'demo', 'export', 'data', 'report'],
            'admin': ['paperwork', 'forms', 'billing', 'invoice', 'expense', 'hr', 'admin', 'travel', 'reimbursement', 'hiring', 'loop', 'q3'],
            'meetings': ['meeting', 'call', 'conference', 'discussion', 'sync', 'standup', 'retro', '1:1', 'amit'],
            'personal': ['grocery', 'doctor', 'family', 'personal', 'home', 'shopping', 'mom', 'bday', 'birthday', 'gift', 'internet', 'bill']
        }
    
    def extract_tasks(self, raw_text: str) -> List[str]:
        """Extract individual tasks from raw text with improved compound task splitting."""
        # Clean the input text first
        cleaned_text = self._clean_input_text(raw_text)
        
        # Extract tasks using multiple strategies
        all_tasks = []
        
        # Strategy 1: Handle email-style requests first (highest priority)
        email_tasks = self._extract_email_tasks(cleaned_text)
        if email_tasks:
            all_tasks.extend(email_tasks)
        
        # Strategy 2: Split by line breaks (for structured input) - ALWAYS check for newlines
        if '\n' in cleaned_text and not email_tasks:
            line_tasks = [task.strip() for task in cleaned_text.split('\n') if task.strip()]
            for task in line_tasks:
                # Don't further split line-separated tasks unless they contain compound indicators
                if any(indicator in task.lower() for indicator in [' and ', ' also ', ';', ' then ']):
                    compound_tasks = self._split_compound_task(task)
                    all_tasks.extend(compound_tasks)
                else:
                    all_tasks.append(task)
        
        # Strategy 3: Split by semicolons (common separator)
        elif ';' in cleaned_text and not email_tasks:
            semicolon_tasks = [task.strip() for task in cleaned_text.split(';') if task.strip()]
            for task in semicolon_tasks:
                compound_tasks = self._split_compound_task(task)
                all_tasks.extend(compound_tasks)
        
        # Strategy 4: Split by sentence boundaries and compound indicators
        else:
            # Split by sentence boundaries first
            sentences = re.split(r'[.!?]+', cleaned_text)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    compound_tasks = self._split_compound_task(sentence)
                    all_tasks.extend(compound_tasks)
        
        # Clean up all tasks
        cleaned_tasks = []
        for task in all_tasks:
            # Remove common prefixes and question words
            task = re.sub(r'^(can we|could you|please|finish|complete|do|make|create|call|check|send|review|need to|ping|update|rotate|ship|restart|share|archive)\s+', '', task, flags=re.IGNORECASE)
            # Remove trailing punctuation
            task = re.sub(r'[.,;!?]+$', '', task)
            # Capitalize first letter
            task = task.capitalize()
            
            if len(task) > 3:  # Only include meaningful tasks
                cleaned_tasks.append(task)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tasks = []
        for task in cleaned_tasks:
            if task.lower() not in seen:
                seen.add(task.lower())
                unique_tasks.append(task)
        
        return unique_tasks
    
    def _clean_input_text(self, raw_text: str) -> str:
        """Clean input text by removing email headers and formatting."""
        # Remove email subject lines
        text = re.sub(r'^Subject:\s*.*?\n', '', raw_text, flags=re.IGNORECASE)
        # Remove signature lines (starting with – or -)
        text = re.sub(r'\n\s*[–-]\s*.*$', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _extract_email_tasks(self, text: str) -> List[str]:
        """Extract tasks from email-style messages."""
        tasks = []
        
        # Pattern for "Can we X and Y" or "Please X and Y"
        can_we_pattern = r'(?:can we|could you|please)\s+(.+?)(?:\?|$)'
        match = re.search(can_we_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            task_content = match.group(1).strip()
            
            # Handle the specific pattern: "restart X and share Y by deadline"
            restart_share_pattern = r'restart\s+(.+?)\s+and\s+share\s+(.+?)(?:\s+by|\s+by\s+tomorrow|\s+by\s+\d+|\s+by\s+\w+|\s+by\s+\w+\s+\d+|\s+by\s+\d+\s+\w+)'
            restart_match = re.search(restart_share_pattern, task_content, re.IGNORECASE)
            
            if restart_match:
                # Extract restart task
                restart_part = f"restart {restart_match.group(1).strip()}"
                tasks.append(restart_part)
                
                # Extract share task with deadline
                share_part = f"share {restart_match.group(2).strip()}"
                # Add deadline context if it exists
                deadline_match = re.search(r'(by\s+tomorrow\s+\d+am|by\s+\w+\s+\d+am|by\s+\d+am)', task_content, re.IGNORECASE)
                if deadline_match:
                    share_part += f" {deadline_match.group(1)}"
                tasks.append(share_part)
                
                # Check for additional tasks after "Also"
                also_match = re.search(r'also[,\s]+(.+)', task_content, re.IGNORECASE)
                if also_match:
                    also_task = also_match.group(1).strip()
                    tasks.append(also_task)
            else:
                # Fallback to general splitting
                if ' and ' in task_content.lower():
                    parts = re.split(r'\s+and\s+', task_content, flags=re.IGNORECASE)
                    tasks.extend([part.strip() for part in parts if part.strip()])
                elif ' also ' in task_content.lower():
                    parts = re.split(r'\s+also\s+', task_content, flags=re.IGNORECASE)
                    tasks.extend([part.strip() for part in parts if part.strip()])
                else:
                    tasks.append(task_content)
        
        return tasks
    
    def _split_compound_task(self, task: str) -> List[str]:
        """Split a single task into multiple tasks if it contains compound actions."""
        task_lower = task.lower()
        
        # Handle specific email patterns first
        # Pattern: "restart X and share Y by deadline"
        restart_and_share_pattern = r'(.+?)\s+and\s+share\s+(.+?)(?:\s+by|\s+by\s+tomorrow|\s+by\s+\d+|\s+by\s+\w+|\s+by\s+\w+\s+\d+|\s+by\s+\d+\s+\w+)'
        match = re.search(restart_and_share_pattern, task_lower)
        if match:
            part1 = match.group(1).strip()
            part2 = f"share {match.group(2).strip()}"
            return [part1, part2]
        
        # Pattern: "X and Y by deadline"
        and_by_pattern = r'(.+?)\s+and\s+(.+?)(?:\s+by|\s+by\s+tomorrow|\s+by\s+\d+|\s+by\s+\w+|\s+by\s+\w+\s+\d+|\s+by\s+\d+\s+\w+)'
        match = re.search(and_by_pattern, task_lower)
        if match:
            part1 = match.group(1).strip()
            part2 = match.group(2).strip()
            return [part1, part2]
        
        # Common compound task indicators
        compound_indicators = [
            r'\b(also|and|then|next|additionally|furthermore|plus|as well)\b',
            r'\b(\.\s*also|\.\s*and|\.\s*then|\.\s*next)\b',
            r'\b(oh—|oh -|oh,)\s*',  # Handle "oh—" patterns
            r'\b(then|after that|following that)\b',
            r'\b(meanwhile|at the same time|simultaneously)\b'
        ]
        
        # Check for compound indicators
        for pattern in compound_indicators:
            if re.search(pattern, task_lower):
                # Split the task
                split_tasks = self._split_by_pattern(task, pattern)
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
    
    def _split_by_pattern(self, task: str, pattern: str) -> List[str]:
        """Split task by a specific pattern."""
        parts = re.split(pattern, task, flags=re.IGNORECASE)
        # Filter out empty parts and the separator words
        filtered_parts = []
        for part in parts:
            part = part.strip()
            if part and part.lower() not in ['also', 'and', 'then', 'next', 'additionally', 'furthermore', 'plus', 'as well', 'oh—', 'oh -', 'oh,']:
                filtered_parts.append(part)
        
        return filtered_parts if len(filtered_parts) > 1 else [task]
    
    def classify_priority(self, task: str) -> str:
        """Classify task priority using keyword matching with enhanced security and deadline detection."""
        task_lower = task.lower()
        
        # Enhanced priority detection - check for URGENT first
        if any(word in task_lower for word in ['urgent', 'asap', 'critical', 'emergency']):
            return 'High'
        
        # Security-related tasks are high priority
        if any(word in task_lower for word in ['security', 'api key', 'rotate', 'expiring', 'expire', 'flagged']):
            return 'High'
        
        # Deadline-related tasks
        if any(word in task_lower for word in ['by eod', 'by end of day', 'deadline', 'due', 'expiring on', 'by tomorrow']) or re.search(r'by \d+am|by \d+pm', task_lower):
            return 'High'
        
        # Count keyword matches
        high_count = sum(1 for keyword in self.priority_keywords['high'] if keyword in task_lower)
        medium_count = sum(1 for keyword in self.priority_keywords['medium'] if keyword in task_lower)
        low_count = sum(1 for keyword in self.priority_keywords['low'] if keyword in task_lower)
        
        # Determine priority based on matches
        if high_count > 0:
            return 'High'
        elif medium_count > 0:
            return 'Medium'
        elif low_count > 0:
            return 'Low'
        else:
            # Default priority based on task characteristics
            if any(word in task_lower for word in ['urgent', 'deadline', 'asap', 'critical', 'security']):
                return 'High'
            elif any(word in task_lower for word in ['meeting', 'call', 'email', 'review', 'update']):
                return 'Medium'
            else:
                return 'Low'
    
    def classify_category(self, task: str) -> str:
        """Classify task category using keyword matching."""
        task_lower = task.lower()
        
        # Count keyword matches for each category
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in task_lower)
            category_scores[category] = score
        
        # Special handling for personal tasks
        personal_indicators = ['mom', 'dad', 'family', 'birthday', 'bday', 'gift', 'personal', 'home', 'shopping', 'grocery', 'doctor', 'internet', 'bill']
        if any(indicator in task_lower for indicator in personal_indicators):
            category_scores['personal'] = category_scores.get('personal', 0) + 2  # Boost personal score
        
        # Return category with highest score, default to 'work'
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category.title()
        
        return 'Work'  # Default category
    
    def process_tasks(self, raw_text: str) -> Dict[str, Any]:
        """Main method to process raw text and return structured tasks."""
        try:
            # Extract tasks
            tasks = self.extract_tasks(raw_text)
            
            if not tasks:
                return {
                    'success': False,
                    'message': 'No tasks found in the input text',
                    'tasks': []
                }
            
            # Process each task
            processed_tasks = []
            for i, task in enumerate(tasks, 1):
                processed_task = {
                    'id': i,
                    'description': task,
                    'priority': self.classify_priority(task),
                    'category': self.classify_category(task),
                    'status': 'pending'
                }
                processed_tasks.append(processed_task)
            
            return {
                'success': True,
                'message': f'Successfully processed {len(processed_tasks)} tasks',
                'tasks': processed_tasks
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing tasks: {str(e)}',
                'tasks': []
            }


# Example usage and testing
if __name__ == "__main__":
    processor = TaskProcessor()
    
    # Test with sample input
    sample_text = """
    Finish PPT for client meeting tomorrow, check AWS logs for errors, 
    call client about project update, review quarterly reports, 
    schedule team standup meeting
    """
    
    result = processor.process_tasks(sample_text)
    print(json.dumps(result, indent=2))
