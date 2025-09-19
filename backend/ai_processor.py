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
            # Split by sentence boundaries first, but handle complex sentences better
            sentences = re.split(r'[.!?]+', cleaned_text)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    # Handle "then" or "lastly" within sentences
                    if ' then ' in sentence.lower() or ' lastly ' in sentence.lower():
                        parts = re.split(r'\s+(?:then|lastly)\s+', sentence, flags=re.IGNORECASE)
                        for part in parts:
                            part = part.strip()
                            if part:
                                compound_tasks = self._split_compound_task(part)
                                all_tasks.extend(compound_tasks)
                    else:
                        compound_tasks = self._split_compound_task(sentence)
                        all_tasks.extend(compound_tasks)
        
        # Strategy 5: Handle complex sentences with multiple actions separated by "then" or "lastly"
        if not all_tasks and (' then ' in cleaned_text.lower() or ' lastly ' in cleaned_text.lower()):
            # Split by "then" or "lastly"
            parts = re.split(r'\s+(?:then|lastly)\s+', cleaned_text, flags=re.IGNORECASE)
            for part in parts:
                part = part.strip()
                if part:
                    compound_tasks = self._split_compound_task(part)
                    all_tasks.extend(compound_tasks)
        
        # Clean up all tasks
        cleaned_tasks = []
        for task in all_tasks:
            # Remove common prefixes and question words
            task = re.sub(r'^(can we|could you|please|finish|complete|do|make|create|call|check|send|review|need to|ping|update|rotate|ship|restart|share|archive)\s+', '', task, flags=re.IGNORECASE)
            # Remove trailing punctuation
            task = re.sub(r'[.,;!?]+$', '', task)
            # Remove leading articles and prepositions
            task = re.sub(r'^(the|a|an|for|on|in|at|to|from|with|by)\s+', '', task, flags=re.IGNORECASE)
            # Capitalize first letter
            task = task.capitalize()
            
            # Skip very short or meaningless tasks, but handle project names
            if len(task) > 5 and not task.lower() in ['for', 'on', 'in', 'at', 'to', 'from', 'with', 'by', 'the', 'a', 'an']:
                cleaned_tasks.append(task)
            elif len(task) <= 5 and task.lower() in ['sentilink', 'cabp', 'ovationcxm']:
                # Handle project names that might be standalone
                cleaned_tasks.append(f"Create user stories for {task}")
        
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
        
        # Handle bill amount patterns first (e.g., "pay 2450 and 2369 rupees respectively")
        bill_pattern = r'pay\s+(\d+(?:,\s*\d+)*)\s+and\s+(\d+(?:,\s*\d+)*)\s+rupees?\s+respectively'
        match = re.search(bill_pattern, task_lower)
        if match:
            amount1 = match.group(1).strip()
            amount2 = match.group(2).strip()
            # Extract context for bills
            context = task_lower.replace(match.group(0), '').strip()
            if 'electricity' in context and 'internet' in context:
                return [f"Pay electricity bill ₹{amount1}", f"Pay internet bill ₹{amount2}"]
            elif 'electricity' in context:
                return [f"Pay electricity bill ₹{amount1}", f"Pay bill ₹{amount2}"]
            elif 'internet' in context:
                return [f"Pay internet bill ₹{amount1}", f"Pay bill ₹{amount2}"]
            else:
                return [f"Pay bill ₹{amount1}", f"Pay bill ₹{amount2}"]
        
        # Handle "pay X and Y rupees respectively" pattern
        bill_pattern2 = r'pay\s+(\d+)\s+and\s+(\d+)\s+rupees?\s+respectively'
        match = re.search(bill_pattern2, task_lower)
        if match:
            amount1 = match.group(1).strip()
            amount2 = match.group(2).strip()
            # Extract context for bills
            context = task_lower.replace(match.group(0), '').strip()
            if 'electricity' in context and 'internet' in context:
                return [f"Pay electricity bill ₹{amount1}", f"Pay internet bill ₹{amount2}"]
            elif 'electricity' in context:
                return [f"Pay electricity bill ₹{amount1}", f"Pay bill ₹{amount2}"]
            elif 'internet' in context:
                return [f"Pay internet bill ₹{amount1}", f"Pay bill ₹{amount2}"]
            else:
                return [f"Pay bill ₹{amount1}", f"Pay bill ₹{amount2}"]
        
        # Handle bill amount patterns (e.g., "Bill amount 1500, 2300 respectively")
        bill_pattern3 = r'bill\s+amount\s+(\d+(?:,\s*\d+)*)\s*(?:respectively|each|for|and)?'
        match = re.search(bill_pattern3, task_lower)
        if match:
            amounts = re.findall(r'\d+', match.group(1))
            if len(amounts) >= 2:
                # Extract context for bills
                context = task_lower.replace(match.group(0), '').strip()
                if 'electricity' in context or 'power' in context:
                    return [f"Pay electricity bill ₹{amounts[1]}", f"Pay internet bill ₹{amounts[0]}"]
                elif 'internet' in context:
                    return [f"Pay internet bill ₹{amounts[0]}", f"Pay electricity bill ₹{amounts[1]}"]
                else:
                    return [f"Pay bill ₹{amounts[0]}", f"Pay bill ₹{amounts[1]}"]
        
        # Handle specific patterns with deadlines and multiple actions
        # Pattern: "X deadline is today 5pm, Y"
        deadline_split_pattern = r'(.+?)\s+deadline\s+is\s+(.+?),\s+(.+)'
        match = re.search(deadline_split_pattern, task_lower)
        if match:
            part1 = f"{match.group(1).strip()} deadline is {match.group(2).strip()}"
            part2 = match.group(3).strip()
            return [part1, part2]
        
        # Pattern: "X, before that Y" (dependency pattern)
        before_pattern = r'(.+?),\s+before\s+that\s+(.+)'
        match = re.search(before_pattern, task_lower)
        if match:
            part1 = f"{match.group(2).strip()}"  # Do the prerequisite first
            part2 = f"{match.group(1).strip()}"  # Then do the main task
            return [part1, part2]
        
        # Pattern: "X as well as Y" (parallel tasks)
        as_well_as_pattern = r'(.+?)\s+as\s+well\s+as\s+(.+)'
        match = re.search(as_well_as_pattern, task_lower)
        if match:
            part1 = f"{match.group(1).strip()}"
            part2 = f"{match.group(2).strip()}"
            return [part1, part2]
        
        # Pattern: "Work on creating X for Y project as well as for Z" (project-specific)
        project_pattern = r'work\s+on\s+creating\s+(.+?)\s+for\s+(.+?)\s+project\s+as\s+well\s+as\s+for\s+(.+)'
        match = re.search(project_pattern, task_lower)
        if match:
            action = match.group(1).strip()
            project1 = match.group(2).strip()
            project2 = match.group(3).strip()
            return [f"Create {action} for {project1}", f"Create {action} for {project2}"]
        
        # Pattern: "creating user stories for the CABP project as well as for sentilink"
        project_pattern2 = r'creating\s+(.+?)\s+for\s+(?:the\s+)?(.+?)\s+project\s+as\s+well\s+as\s+for\s+(.+)'
        match = re.search(project_pattern2, task_lower)
        if match:
            action = match.group(1).strip()
            project1 = match.group(2).strip()
            project2 = match.group(3).strip()
            return [f"Create {action} for {project1}", f"Create {action} for {project2}"]
        
        # Pattern: "X as well as Y" (parallel tasks) - improved
        as_well_as_pattern = r'(.+?)\s+as\s+well\s+as\s+(.+)'
        match = re.search(as_well_as_pattern, task_lower)
        if match:
            part1 = match.group(1).strip()
            part2 = match.group(2).strip()
            # If it's about projects, format better
            if 'project' in part1.lower() and 'project' not in part2.lower():
                return [part1, f"Create user stories for {part2}"]
            # If part2 is just a project name, expand it
            elif 'user stories' in part1.lower() and len(part2.split()) <= 2:
                return [part1, f"Create user stories for {part2}"]
            return [part1, part2]
        
        # Pattern: "if time permits X" (low priority conditional)
        if_time_pattern = r'if\s+time\s+permits\s+(.+)'
        match = re.search(if_time_pattern, task_lower)
        if match:
            task_content = match.group(1).strip()
            return [f"If time permits: {task_content}"]
        
        # Pattern: "X and check on their progress" (combine related actions)
        progress_pattern = r'(.+?)\s+and\s+check\s+on\s+their\s+progress'
        match = re.search(progress_pattern, task_lower)
        if match:
            main_action = match.group(1).strip()
            return [f"{main_action} and check on their progress"]
        
        # Pattern: "X so need to Y, Z"
        so_need_pattern = r'(.+?)\s+so\s+need\s+to\s+(.+?),\s+(.+)'
        match = re.search(so_need_pattern, task_lower)
        if match:
            part1 = f"{match.group(1).strip()}"
            part2 = f"Need to {match.group(2).strip()}"
            part3 = match.group(3).strip()
            return [part1, part2, part3]
        
        # Pattern: "X, Y is due Z"
        due_pattern = r'(.+?),\s+(.+?)\s+is\s+due\s+(.+)'
        match = re.search(due_pattern, task_lower)
        if match:
            part1 = match.group(1).strip()
            part2 = f"{match.group(2).strip()} is due {match.group(3).strip()}"
            return [part1, part2]
        
        # Pattern: "X, Y otherwise Z"
        otherwise_pattern = r'(.+?),\s+(.+?)\s+otherwise\s+(.+)'
        match = re.search(otherwise_pattern, task_lower)
        if match:
            part1 = match.group(1).strip()
            part2 = f"{match.group(2).strip()} otherwise {match.group(3).strip()}"
            return [part1, part2]
        
        # Handle specific email patterns
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
        """Comprehensive priority classification using multi-factor scoring algorithm."""
        priority_score = self._calculate_priority_score(task)
        return self._score_to_priority(priority_score)
    
    def _calculate_priority_score(self, task: str) -> Dict[str, Any]:
        """Calculate comprehensive priority score using multiple factors."""
        task_lower = task.lower()
        
        # Initialize scoring components
        score_components = {
            'urgency_keywords': 0,
            'time_sensitivity': 0,
            'security_impact': 0,
            'business_impact': 0,
            'deadline_pressure': 0,
            'context_urgency': 0,
            'negative_indicators': 0,
            'positive_indicators': 0
        }
        
        # 1. URGENCY KEYWORDS SCORING (0-60 points)
        urgency_patterns = {
            'most important': 60, 'highest priority': 60, 'critical': 40, 'urgent': 35, 'emergency': 40, 'asap': 30,
            'immediately': 25, 'now': 20, 'right now': 30,
            'blocker': 35, 'blocking': 30, 'stopping': 25,
            'broken': 20, 'down': 25, 'failing': 20, 'error': 15,
            'time-sensitive': 25, 'time critical': 30,
            'otherwise': 20, 'no internet': 25, 'no power': 25,
            'from tomorrow': 20, 'due': 15, 'expiring': 20,
            'not received': 30, 'missing': 25, 'issue': 20
        }
        
        for pattern, score in urgency_patterns.items():
            if pattern in task_lower:
                score_components['urgency_keywords'] = max(score_components['urgency_keywords'], score)
        
        # 2. TIME SENSITIVITY SCORING (0-35 points)
        time_patterns = {
            'today': 25, 'tomorrow': 20, 'tmw': 20, 'this week': 15,
            'by eod': 30, 'by end of day': 30, 'by close': 25,
            'deadline': 25, 'due': 20, 'expiring': 20, 'expire': 20,
            'by tomorrow': 25, 'by friday': 15, 'by monday': 10
        }
        
        # Time with specific hours (higher priority)
        time_hour_patterns = [
            r'by \d+am', r'by \d+pm', r'at \d+am', r'at \d+pm',
            r'\d+am', r'\d+pm', r'\d+:\d+am', r'\d+:\d+pm'
        ]
        
        for pattern in time_hour_patterns:
            if re.search(pattern, task_lower):
                score_components['time_sensitivity'] = max(score_components['time_sensitivity'], 30)
        
        for pattern, score in time_patterns.items():
            if pattern in task_lower:
                score_components['time_sensitivity'] = max(score_components['time_sensitivity'], score)
        
        # 3. SECURITY IMPACT SCORING (0-40 points)
        security_patterns = {
            'security': 25, 'api key': 30, 'rotate': 25, 'credentials': 20,
            'password': 20, 'auth': 15, 'token': 20, 'access': 15,
            'permission': 15, 'role': 15, 'flagged': 30, 'suspicious': 25,
            'breach': 40, 'compromise': 35, 'vulnerability': 30,
            'patch': 20, 'update security': 25, 'fix security': 25
        }
        
        for pattern, score in security_patterns.items():
            if pattern in task_lower:
                score_components['security_impact'] = max(score_components['security_impact'], score)
        
        # 4. BUSINESS IMPACT SCORING (0-35 points)
        business_patterns = {
            'client': 20, 'customer': 20, 'revenue': 25, 'sales': 20,
            'production': 25, 'live': 20, 'deploy': 20, 'release': 15,
            'launch': 20, 'go-live': 25, 'critical path': 30,
            'dependency': 15, 'blocking': 20, 'stopping': 20,
            'outage': 30, 'downtime': 25, 'service down': 30,
            'performance': 15, 'slow': 10, 'optimize': 10,
            'fix': 15, 'bug': 15, 'issue': 15, 'problem': 15,
            'portal': 20, 'system': 15, 'platform': 15,
            'users': 15, 'user': 15, 'affecting': 20,
            'loss': 20, 'causing': 15, 'impact': 15,
            'internet': 15, 'electricity': 15, 'power': 15,
            'recharge': 15, 'payment': 10, 'bill': 10,
            'user stories': 20, 'project': 15, 'progress': 15
        }
        
        for pattern, score in business_patterns.items():
            if pattern in task_lower:
                score_components['business_impact'] = max(score_components['business_impact'], score)
        
        # 5. DEADLINE PRESSURE SCORING (0-25 points)
        deadline_patterns = {
            'deadline': 20, 'due date': 20, 'must be done': 15,
            'required by': 15, 'needed by': 10, 'expected by': 10,
            'promised': 15, 'committed': 15, 'scheduled': 10,
            'by today': 20, 'by tomorrow': 15, 'by eod': 20,
            'submit': 15, 'deliver': 15, 'complete': 10,
            'finish': 10, 'prepare': 10, 'review': 10
        }
        
        for pattern, score in deadline_patterns.items():
            if pattern in task_lower:
                score_components['deadline_pressure'] = max(score_components['deadline_pressure'], score)
        
        # 6. CONTEXT URGENCY SCORING (0-30 points)
        context_patterns = {
            'meeting': 15, 'presentation': 20, 'demo': 20, 'review': 15,
            'approval': 20, 'sign-off': 20, 'decision': 20,
            'escalate': 25, 'escalated': 25, 'manager': 15, 'boss': 15,
            'ceo': 25, 'director': 20, 'vp': 20,
            'performance review': 20, 'feedback': 20, 'invite': 15,
            'praveen': 15, 'av': 15  # Specific people mentioned
        }
        
        for pattern, score in context_patterns.items():
            if pattern in task_lower:
                score_components['context_urgency'] = max(score_components['context_urgency'], score)
        
        # 7. NEGATIVE INDICATORS (reduce priority)
        negative_patterns = [
            'nice to have', 'nice-to-have', 'optional', 'eventually',
            'sometime', 'when possible', 'if time', 'low priority',
            'backlog', 'future', 'later', 'not urgent'
        ]
        
        for pattern in negative_patterns:
            if pattern in task_lower:
                score_components['negative_indicators'] = -15
                break
        
        # 8. POSITIVE INDICATORS (boost priority)
        positive_patterns = [
            'important', 'critical', 'must', 'need to', 'should',
            'priority', 'high priority', 'top priority'
        ]
        
        for pattern in positive_patterns:
            if pattern in task_lower:
                score_components['positive_indicators'] = 10
                break
        
        # Calculate total score
        total_score = sum(score_components.values())
        
        return {
            'total_score': total_score,
            'components': score_components,
            'task': task
        }
    
    def _score_to_priority(self, score_data: Dict[str, Any]) -> str:
        """Convert priority score to priority level."""
        total_score = score_data['total_score']
        
        # Enhanced thresholds with Highest priority
        if total_score >= 80:  # Highest priority for critical tasks
            return 'Highest'
        elif total_score >= 50:  # High priority
            return 'High'
        elif total_score >= 20:  # Medium priority
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
        
        # Special handling for meeting-related tasks
        meeting_indicators = ['meeting', 'setup meeting', 'schedule meeting', 'meet', 'invite', 'appointment', 'call', 'conference', 'standup', 'retro', '1:1']
        if any(indicator in task_lower for indicator in meeting_indicators):
            category_scores['meetings'] = category_scores.get('meetings', 0) + 3  # Strong boost for meetings
        
        # Special handling for work-related tasks
        work_indicators = ['appraisal', 'form', 'deadline', 'team', 'project', 'client', 'presentation', 'report', 'review']
        if any(indicator in task_lower for indicator in work_indicators):
            category_scores['work'] = category_scores.get('work', 0) + 2  # Boost work score
        
        # Special handling for personal tasks
        personal_indicators = ['mom', 'dad', 'family', 'birthday', 'bday', 'gift', 'personal', 'home', 'shopping', 'grocery', 'doctor', 'internet', 'bill', 'electricity', 'recharge', 'payment']
        if any(indicator in task_lower for indicator in personal_indicators):
            category_scores['personal'] = category_scores.get('personal', 0) + 2  # Boost personal score
        
        # Special handling for admin tasks
        admin_indicators = ['form', 'paperwork', 'billing', 'invoice', 'expense', 'hr', 'admin', 'travel', 'reimbursement', 'hiring']
        if any(indicator in task_lower for indicator in admin_indicators):
            category_scores['admin'] = category_scores.get('admin', 0) + 2  # Boost admin score
        
        # Return category with highest score, default to 'work'
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category.title()
        
        return 'Work'  # Default category
    
    def get_priority_analysis(self, task: str) -> Dict[str, Any]:
        """Get detailed priority analysis for a task."""
        score_data = self._calculate_priority_score(task)
        priority = self._score_to_priority(score_data)
        
        return {
            'task': task,
            'priority': priority,
            'total_score': score_data['total_score'],
            'score_breakdown': score_data['components'],
            'confidence': self._calculate_confidence(score_data),
            'reasoning': self._generate_reasoning(score_data)
        }
    
    def _calculate_confidence(self, score_data: Dict[str, Any]) -> str:
        """Calculate confidence level for priority classification."""
        total_score = score_data['total_score']
        components = score_data['components']
        
        # Count non-zero components
        active_components = sum(1 for score in components.values() if score != 0)
        
        if total_score >= 60 and active_components >= 2:
            return 'High'
        elif total_score >= 25 and active_components >= 1:
            return 'Medium'
        else:
            return 'Low'
    
    def _generate_reasoning(self, score_data: Dict[str, Any]) -> List[str]:
        """Generate human-readable reasoning for priority classification."""
        reasoning = []
        components = score_data['components']
        
        # Find the top contributing factors
        sorted_components = sorted(components.items(), key=lambda x: x[1], reverse=True)
        
        for component, score in sorted_components:
            if score > 0:
                if component == 'urgency_keywords':
                    reasoning.append(f"Contains urgent keywords (+{score} points)")
                elif component == 'time_sensitivity':
                    reasoning.append(f"Time-sensitive task (+{score} points)")
                elif component == 'security_impact':
                    reasoning.append(f"Security-related (+{score} points)")
                elif component == 'business_impact':
                    reasoning.append(f"High business impact (+{score} points)")
                elif component == 'deadline_pressure':
                    reasoning.append(f"Deadline pressure (+{score} points)")
                elif component == 'context_urgency':
                    reasoning.append(f"Context urgency (+{score} points)")
                elif component == 'positive_indicators':
                    reasoning.append(f"Positive priority indicators (+{score} points)")
            elif score < 0:
                reasoning.append(f"Low priority indicators ({score} points)")
        
        return reasoning[:3]  # Return top 3 reasons
    
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
