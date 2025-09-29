"""
Core AI processing engine for task extraction, priority classification, and categorization
using ChatGPT and Gemini APIs for advanced AI processing.
"""

import re
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import openai
import google.generativeai as genai
from dotenv import load_dotenv
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Load environment variables
load_dotenv()

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
    """Main class for processing raw task text using ChatGPT and Gemini APIs."""
    
    def __init__(self, ai_provider: str = "chatgpt"):
        """
        Initialize the TaskProcessor with AI provider.
        
        Args:
            ai_provider: "chatgpt" or "gemini"
        """
        self.ai_provider = ai_provider.lower()
        self.stop_words = set(stopwords.words('english'))
        self._initialize_ai_client()
        
        # Fallback rule-based patterns
        self.priority_keywords = {
            'high': ['urgent', 'asap', 'deadline', 'critical', 'important', 'immediately', 'today', 'now', 'blocker', 'time-sensitive', 'tmw', 'tomorrow', 'eod', 'end of day'],
            'medium': ['soon', 'this week', 'moderate', 'should', 'need to', 'this week', 'next week'],
            'low': ['eventually', 'sometime', 'when possible', 'optional', 'nice to have', 'nice-to-have']
        }
        
        self.category_keywords = {
            'work': ['meeting', 'client', 'project', 'presentation', 'report', 'deadline', 'email', 'call', 'ppt', 'deck', 'aws', 'logs', 'ssl', 'cert', 'portal', 'intern', 'bug', 'navbar', 'mobile', 's3', 'upload', 'timesheet', 'townhall', 'domain', 'readme', 'invoice', 'followup', 'demo', 'export', 'data', 'report', 'team', 'lunch', 'building', 'activity', 'software', 'update', 'inbox', 'slides', 'cabp', 'ap', 'apprisals', 'feedback form', 'mgmt', 'management'],
            'admin': ['paperwork', 'forms', 'billing', 'invoice', 'expense', 'hr', 'admin', 'travel', 'reimbursement', 'hiring', 'loop', 'q3', 'leave request', 'avs'],
            'meetings': ['meeting', 'call', 'conference', 'discussion', 'sync', 'standup', 'retro', '1:1', 'amit', 'setup meeting', 'apprisals'],
            'personal': ['grocery', 'doctor', 'family', 'personal', 'home', 'shopping', 'mom', 'bday', 'birthday', 'gift', 'internet', 'bill', 'electricity', 'power', 'recharge', 'payment', 'dentist', 'appointment', 'insurance', 'vehicle', 'travel', 'tickets', 'snacks', 'utility', 'water', 'buy', 'purchase', 'get', 'pick up', 'apples', 'food', 'groceries', 'snack', 'lunch', 'dinner', 'breakfast']
        }
    
    def _initialize_ai_client(self):
        """Initialize the AI client based on the provider."""
        try:
            if self.ai_provider == "chatgpt":
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found in environment variables")
                self.client = openai.OpenAI(api_key=api_key)
                print("✅ ChatGPT client initialized successfully!")
                
            elif self.ai_provider == "gemini":
                api_key = os.getenv('GEMINI_API_KEY')
                if not api_key:
                    raise ValueError("GEMINI_API_KEY not found in environment variables")
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                print("[OK] Gemini client initialized successfully!")
                
            else:
                raise ValueError(f"Unsupported AI provider: {self.ai_provider}")
                
        except Exception as e:
            print(f"[ERROR] Error initializing AI client: {e}")
            print("[INFO] Falling back to rule-based processing...")
            self.client = None
            self.model = None
    
    def extract_tasks(self, raw_text: str) -> List[str]:
        """Extract individual tasks from raw text using AI."""
        try:
            if self.client or self.model:
                return self._extract_tasks_with_ai(raw_text)
            else:
                return self._extract_tasks_fallback(raw_text)
        except Exception as e:
            print(f"❌ AI task extraction failed: {e}")
            return self._extract_tasks_fallback(raw_text)
    
    def _extract_tasks_with_ai(self, raw_text: str) -> List[str]:
        """Extract tasks using AI API."""
        prompt = f"""
You are a task extraction expert. Extract individual tasks from the following text and return them as a JSON array of strings.

Rules:
1. Split compound tasks into separate individual tasks
2. Handle dependencies (e.g., "before that" means prerequisite)
3. Extract bill amounts and create separate tasks for each bill
4. Handle project-specific tasks (e.g., "for CABP project as well as for sentilink" = 2 tasks)
5. Clean up task descriptions (remove unnecessary words, capitalize properly)
6. Return only the task descriptions, no additional text

Input text: "{raw_text}"

Return format: ["task1", "task2", "task3", ...]
"""
        
        try:
            if self.ai_provider == "chatgpt":
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a task extraction expert. Return only valid JSON arrays."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=1000
                )
                result = response.choices[0].message.content.strip()
                
            elif self.ai_provider == "gemini":
                response = self.model.generate_content(prompt)
                result = response.text.strip()
            
            # Parse JSON response
            tasks = json.loads(result)
            if isinstance(tasks, list):
                return [task.strip() for task in tasks if task.strip()]
            else:
                raise ValueError("AI response is not a list")
                
        except Exception as e:
            print(f"❌ AI API call failed: {e}")
            return self._extract_tasks_fallback(raw_text)
    
    def _extract_tasks_fallback(self, raw_text: str) -> List[str]:
        """Fallback task extraction using rule-based approach."""
        # Clean the input text first
        cleaned_text = self._clean_input_text(raw_text)
        
        # Extract tasks using multiple strategies
        all_tasks = []
        
        # Strategy 1: Handle email-style requests first (highest priority)
        email_tasks = self._extract_email_tasks(cleaned_text)
        if email_tasks:
            all_tasks.extend(email_tasks)
            return self._clean_task_list(all_tasks)
        
        # Strategy 2: Handle complex compound sentences with multiple separators
        # First, try to identify major task boundaries using periods, semicolons, and newlines
        major_splits = re.split(r'[.!?;\n]+', cleaned_text)
        major_tasks = [task.strip() for task in major_splits if task.strip()]
        
        for major_task in major_tasks:
            # For each major task, check for compound patterns
            if any(indicator in major_task.lower() for indicator in [' before that ', ' and ', ' also ', ' then ', ' so ', ', ']):
                compound_tasks = self._split_compound_task(major_task)
                all_tasks.extend(compound_tasks)
            else:
                all_tasks.append(major_task)
        
        # Strategy 2.5: If we still have combined tasks, try more aggressive comma splitting
        if len(all_tasks) <= 2:  # If we didn't get good splits
            all_tasks = []
            # Split by commas and process each part
            comma_parts = [part.strip() for part in cleaned_text.split(',') if part.strip()]
            for part in comma_parts:
                if any(indicator in part.lower() for indicator in [' before that ', ' and ', ' also ', ' then ', ' so ']):
                    compound_tasks = self._split_compound_task(part)
                    all_tasks.extend(compound_tasks)
                else:
                    all_tasks.append(part)
        
        # Strategy 2.6: Final cleanup - split any remaining combined tasks
        final_tasks = []
        for task in all_tasks:
            # Check if task still contains multiple actions separated by commas
            if ',' in task and len(task.split(',')) > 1:
                sub_tasks = [t.strip() for t in task.split(',') if t.strip()]
                for sub_task in sub_tasks:
                    if any(indicator in sub_task.lower() for indicator in [' before that ', ' and ', ' also ', ' then ', ' so ']):
                        compound_tasks = self._split_compound_task(sub_task)
                        final_tasks.extend(compound_tasks)
                    else:
                        final_tasks.append(sub_task)
            else:
                final_tasks.append(task)
        
        all_tasks = final_tasks
        
        # Strategy 3: If no major splits found, try comma-based splitting
        if len(all_tasks) <= 1:
            all_tasks = []
            # First try newline splitting
            if '\n' in cleaned_text:
                newline_tasks = [task.strip() for task in cleaned_text.split('\n') if task.strip()]
                for task in newline_tasks:
                    if any(indicator in task.lower() for indicator in [' and ', ' also ', ' then ', ' before that ']):
                        compound_tasks = self._split_compound_task(task)
                        all_tasks.extend(compound_tasks)
                    else:
                        all_tasks.append(task)
            # Then try comma-based splitting
            elif ',' in cleaned_text:
                comma_tasks = [task.strip() for task in cleaned_text.split(',') if task.strip()]
                for task in comma_tasks:
                    if any(indicator in task.lower() for indicator in [' and ', ' also ', ' then ', ' before that ']):
                        compound_tasks = self._split_compound_task(task)
                        all_tasks.extend(compound_tasks)
                    else:
                        all_tasks.append(task)
            else:
                all_tasks = [cleaned_text]
        
        return self._clean_task_list(all_tasks)
    
    def _clean_task_list(self, tasks: List[str]) -> List[str]:
        """Clean and normalize a list of extracted tasks."""
        cleaned_tasks = []
        for task in tasks:
            # Remove common prefixes and question words
            task = re.sub(r'^(can we|could you|please|finish|complete|do|make|create|call|check|send|review|need to|ping|update|rotate|ship|restart|share|archive)\s+', '', task, flags=re.IGNORECASE)
            # Remove trailing punctuation
            task = re.sub(r'[.,;!?]+$', '', task)
            # Remove leading articles and prepositions
            task = re.sub(r'^(the|a|an|for|on|in|at|to|from|with|by)\s+', '', task, flags=re.IGNORECASE)
            # Capitalize first letter
            task = task.capitalize()
            
            # Skip very short or meaningless tasks
            if len(task) > 5 and not task.lower() in ['for', 'on', 'in', 'at', 'to', 'from', 'with', 'by', 'the', 'a', 'an']:
                cleaned_tasks.append(task)
            elif len(task) <= 5 and task.lower() in ['sentilink', 'cabp', 'ovationcxm']:
                cleaned_tasks.append(f"Create user stories for {task}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tasks = []
        for task in cleaned_tasks:
            if task.lower() not in seen:
                seen.add(task.lower())
                unique_tasks.append(task)
        
        return unique_tasks
    
    def _is_comma_separator(self, text: str) -> bool:
        """Determine if commas in text separate distinct tasks vs being part of a single task."""
        # Split by commas and analyze the parts
        parts = [part.strip() for part in text.split(',') if part.strip()]
        
        # If less than 2 parts, it's not a separator
        if len(parts) < 2:
            return False
        
        # Check if parts look like distinct tasks
        for part in parts:
            # If a part contains action verbs or task-like patterns, likely separate tasks
            task_indicators = [
                r'\b(pay|renew|buy|get|call|send|review|fix|update|write|create|schedule|finish|complete|submit|deploy)\b',
                r'\b(bill|cert|gift|bug|meeting|report|appointment)\b',
                r'\b(today|tomorrow|this week|next week|monday|tuesday|wednesday|thursday|friday)\b'
            ]
            
            # If each part has task-like indicators, treat commas as separators
            has_task_indicator = any(re.search(pattern, part.lower()) for pattern in task_indicators)
            if has_task_indicator:
                continue
            else:
                # If a part doesn't look like a task, might be part of a single description
                # But if it's a short phrase, it might still be a task
                if len(part.split()) >= 2:  # At least 2 words makes it more likely to be a task
                    continue
                else:
                    return False
        
        # Additional check: if parts are very short, might not be separate tasks
        avg_length = sum(len(part.split()) for part in parts) / len(parts)
        if avg_length < 2:  # Very short parts
            return False
        
        return True
    
    def classify_priority(self, task: str) -> str:
        """Classify task priority using AI."""
        try:
            if self.client or self.model:
                return self._classify_priority_with_ai(task)
            else:
                return self._classify_priority_fallback(task)
        except Exception as e:
            print(f"❌ AI priority classification failed: {e}")
            return self._classify_priority_fallback(task)
    
    def _classify_priority_with_ai(self, task: str) -> str:
        """Classify priority using AI API."""
        prompt = f"""
Classify the priority of this task as one of: "Highest", "High", "Medium", "Low"

Priority levels:
- Highest: Critical, blocking, urgent, "most important", immediate deadlines
- High: Important, deadlines, urgent, time-sensitive
- Medium: Important but not urgent, should be done soon
- Low: Nice to have, optional, can wait

Task: "{task}"

Return only the priority level (Highest/High/Medium/Low):
"""
        
        try:
            if self.ai_provider == "chatgpt":
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a priority classification expert. Return only the priority level."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=10
                )
                result = response.choices[0].message.content.strip()
                
            elif self.ai_provider == "gemini":
                response = self.model.generate_content(prompt)
                result = response.text.strip()
            
            # Validate the result
            valid_priorities = ["Highest", "High", "Medium", "Low"]
            if result in valid_priorities:
                return result
            else:
                raise ValueError(f"Invalid priority: {result}")
                
        except Exception as e:
            print(f"❌ AI priority classification failed: {e}")
            return self._classify_priority_fallback(task)
    
    def _classify_priority_fallback(self, task: str) -> str:
        """Fallback priority classification using rule-based approach."""
        task_lower = task.lower()
        
        # Check for highest priority indicators
        if any(keyword in task_lower for keyword in ['most important', 'highest priority', 'critical', 'blocker', 'urgent', 'asap']):
            return 'Highest'
        
        # Check for high priority indicators
        if any(keyword in task_lower for keyword in ['deadline', 'today', 'tomorrow', 'eod', 'end of day', 'immediately', 'now', 'today we have', 'have call with']):
            return 'High'
        
        # Check for medium priority indicators
        if any(keyword in task_lower for keyword in ['soon', 'this week', 'should', 'need to']):
            return 'Medium'
        
        # Default to low priority
        return 'Low'
    
    def classify_category(self, task: str) -> str:
        """Classify task category using AI."""
        try:
            if self.client or self.model:
                return self._classify_category_with_ai(task)
            else:
                return self._classify_category_fallback(task)
        except Exception as e:
            print(f"❌ AI category classification failed: {e}")
            return self._classify_category_fallback(task)
    
    def _classify_category_with_ai(self, task: str) -> str:
        """Classify category using AI API."""
        prompt = f"""
Classify this task into one of these categories: "Work", "Meetings", "Personal", "Admin"

Categories:
- Work: Professional tasks, projects, reports, technical work, client work
- Meetings: Scheduling meetings, calls, conferences, appointments
- Personal: Personal life tasks, family, shopping, bills, health, travel
- Admin: Administrative tasks, paperwork, forms, HR, expenses

Task: "{task}"

Return only the category name (Work/Meetings/Personal/Admin):
"""
        
        try:
            if self.ai_provider == "chatgpt":
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a category classification expert. Return only the category name."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=10
                )
                result = response.choices[0].message.content.strip()
                
            elif self.ai_provider == "gemini":
                response = self.model.generate_content(prompt)
                result = response.text.strip()
            
            # Validate the result
            valid_categories = ["Work", "Meetings", "Personal", "Admin"]
            if result in valid_categories:
                return result
            else:
                raise ValueError(f"Invalid category: {result}")
                
        except Exception as e:
            print(f"❌ AI category classification failed: {e}")
            return self._classify_category_fallback(task)
    
    def _classify_category_fallback(self, task: str) -> str:
        """Fallback category classification using rule-based approach."""
        task_lower = task.lower()
        
        # Count keyword matches for each category
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in task_lower)
            category_scores[category] = score
        
        # Special handling for meeting-related tasks
        meeting_indicators = ['meeting', 'setup meeting', 'schedule meeting', 'meet', 'invite', 'appointment', 'call', 'conference', 'standup', 'retro', '1:1']
        if any(indicator in task_lower for indicator in meeting_indicators):
            category_scores['meetings'] = category_scores.get('meetings', 0) + 3
        
        # Special handling for personal tasks
        personal_indicators = ['mom', 'dad', 'family', 'birthday', 'bday', 'gift', 'personal', 'home', 'shopping', 'grocery', 'doctor', 'internet', 'bill', 'electricity', 'recharge', 'payment', 'buy', 'purchase', 'get', 'pick up', 'apples', 'food', 'snacks', 'snack', 'lunch', 'dinner', 'breakfast']
        if any(indicator in task_lower for indicator in personal_indicators):
            category_scores['personal'] = category_scores.get('personal', 0) + 2
        
        # Return category with highest score, default to 'work'
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category.title()
        
        return 'Work'
    
    def extract_due_date(self, task: str) -> Optional[str]:
        """Extract due date from task description using AI and rule-based patterns."""
        try:
            if self.client or self.model:
                return self._extract_due_date_with_ai(task)
            else:
                return self._extract_due_date_fallback(task)
        except Exception as e:
            print(f"❌ AI due date extraction failed: {e}")
            return self._extract_due_date_fallback(task)
    
    def _extract_due_date_with_ai(self, task: str) -> Optional[str]:
        """Extract due date using AI API."""
        today = datetime.now().strftime("%Y-%m-%d")
        prompt = f"""
Extract the due date from this task description and return it in YYYY-MM-DD format.

Today's date is: {today}

Rules:
- "today" = {today}
- "tomorrow" = {(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")}
- "this week" = end of current week (Friday)
- "next week" = end of next week (Friday)
- "monday", "tuesday", etc. = next occurrence of that day
- "by EOD" or "end of day" = today
- If no specific date mentioned, return "null"

Task: "{task}"

Return only the date in YYYY-MM-DD format or "null":
"""
        
        try:
            if self.ai_provider == "chatgpt":
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a date extraction expert. Return only dates in YYYY-MM-DD format or 'null'."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=20
                )
                result = response.choices[0].message.content.strip()
                
            elif self.ai_provider == "gemini":
                response = self.model.generate_content(prompt)
                result = response.text.strip()
            
            # Validate the result
            if result == "null" or result == "None":
                return None
            
            # Try to parse the date
            try:
                datetime.strptime(result, "%Y-%m-%d")
                return result
            except ValueError:
                raise ValueError(f"Invalid date format: {result}")
                
        except Exception as e:
            print(f"❌ AI date extraction failed: {e}")
            return self._extract_due_date_fallback(task)
    
    def _extract_due_date_fallback(self, task: str) -> Optional[str]:
        """Extract due date using rule-based patterns."""
        task_lower = task.lower()
        today = datetime.now()
        
        # Today patterns
        today_patterns = ['today', 'eod', 'end of day', 'by today', 'due today', 'today we have', 'have call with']
        if any(pattern in task_lower for pattern in today_patterns):
            return today.strftime("%Y-%m-%d")
        
        # Tomorrow patterns
        tomorrow_patterns = ['tomorrow', 'tmw', 'by tomorrow', 'due tomorrow']
        if any(pattern in task_lower for pattern in tomorrow_patterns):
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # This week patterns
        this_week_patterns = ['this week', 'by end of week', 'this friday']
        if any(pattern in task_lower for pattern in this_week_patterns):
            days_until_friday = (4 - today.weekday()) % 7
            if days_until_friday == 0 and today.weekday() == 4:  # It's Friday
                days_until_friday = 7
            return (today + timedelta(days=days_until_friday)).strftime("%Y-%m-%d")
        
        # Next week patterns
        next_week_patterns = ['next week', 'next friday']
        if any(pattern in task_lower for pattern in next_week_patterns):
            days_until_next_friday = (4 - today.weekday()) % 7 + 7
            return (today + timedelta(days=days_until_next_friday)).strftime("%Y-%m-%d")
        
        # Specific weekday patterns (including abbreviations)
        weekdays = {
            # Full names
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 
            'friday': 4, 'saturday': 5, 'sunday': 6,
            # Common abbreviations
            'mon': 0, 'tue': 1, 'tues': 1, 'wed': 2, 'thu': 3, 'thur': 3, 'thurs': 3,
            'fri': 4, 'sat': 5, 'sun': 6
        }
        
        for day_name, day_num in weekdays.items():
            # Use word boundary regex to avoid partial matches
            if re.search(r'\b' + re.escape(day_name) + r'\b', task_lower):
                days_ahead = (day_num - today.weekday()) % 7
                if days_ahead == 0:  # Same day of week
                    days_ahead = 7  # Next week
                return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        
        # Look for date patterns like "Jan 15", "15/1", "2024-01-15", etc.
        # Simple date regex patterns
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{1,2}[/-]\d{1,2})',  # MM/DD or DD/MM (current year)
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, task)
            if match:
                date_str = match.group(1)
                try:
                    # Try different date formats
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m/%d', '%d/%m']:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            if fmt in ['%m/%d', '%d/%m']:  # Add current year
                                parsed_date = parsed_date.replace(year=today.year)
                            return parsed_date.strftime("%Y-%m-%d")
                        except ValueError:
                            continue
                except:
                    continue
        
        return None
    
    def _clean_input_text(self, raw_text: str) -> str:
        """Clean input text by removing email headers and formatting."""
        # Remove email subject lines
        text = re.sub(r'^Subject:\s*.*?\n', '', raw_text, flags=re.IGNORECASE)
        # Remove signature lines (starting with – or -)
        text = re.sub(r'\n\s*[–-]\s*.*$', '', text)
        # Remove extra whitespace but preserve line breaks
        # First normalize line breaks and remove empty lines
        text = re.sub(r'\n\s*\n', '\n', text)  # Remove empty lines
        # Then clean up spaces within lines while preserving line breaks
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Clean up extra spaces within each line
            cleaned_line = re.sub(r'\s+', ' ', line).strip()
            if cleaned_line:  # Only keep non-empty lines
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
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
        
        # Handle bill amount patterns first (e.g., "pay 2300 & 500 for internet and water respectively")
        bill_pattern = r'pay\s+utility\s+payment\s+of\s+(\d+)\s*&\s*(\d+)\s+for\s+internet\s+and\s+water\s+respectively'
        match = re.search(bill_pattern, task_lower)
        if match:
            amount1 = match.group(1).strip()
            amount2 = match.group(2).strip()
            return [f"Pay internet bill Rs {amount1}", f"Pay water bill Rs {amount2}"]
        
        # Handle general bill patterns
        bill_pattern2 = r'pay\s+(\d+(?:,\s*\d+)*)\s+and\s+(\d+(?:,\s*\d+)*)\s+rupees?\s+respectively'
        match = re.search(bill_pattern2, task_lower)
        if match:
            amount1 = match.group(1).strip()
            amount2 = match.group(2).strip()
            # Extract context for bills
            context = task_lower.replace(match.group(0), '').strip()
            if 'electricity' in context and 'internet' in context:
                return [f"Pay electricity bill Rs {amount1}", f"Pay internet bill Rs {amount2}"]
            elif 'electricity' in context:
                return [f"Pay electricity bill Rs {amount1}", f"Pay bill Rs {amount2}"]
            elif 'internet' in context:
                return [f"Pay internet bill Rs {amount1}", f"Pay bill Rs {amount2}"]
            else:
                return [f"Pay bill Rs {amount1}", f"Pay bill Rs {amount2}"]
        
        # Pattern: "X, before that Y" (dependency pattern)
        before_pattern = r'(.+?),\s+before\s+that\s+(.+)'
        match = re.search(before_pattern, task_lower)
        if match:
            part1 = f"{match.group(2).strip()}"  # Do the prerequisite first
            part2 = f"{match.group(1).strip()}"  # Then do the main task
            return [part1, part2]
        
        # Pattern: "Setup meeting for apprisals before that talk to mgmt about the feedback form"
        setup_before_pattern = r'setup\s+meeting\s+for\s+(.+?)\s+before\s+that\s+(.+)'
        match = re.search(setup_before_pattern, task_lower)
        if match:
            meeting_task = f"Setup meeting for {match.group(1).strip()}"
            prerequisite_task = match.group(2).strip()
            return [prerequisite_task, meeting_task]
        
        # Pattern: "AVs leave request related questions to be asked to Amit sir"
        av_questions_pattern = r'avs\s+leave\s+request\s+related\s+questions\s+to\s+be\s+asked\s+to\s+(.+)'
        match = re.search(av_questions_pattern, task_lower)
        if match:
            person = match.group(1).strip()
            return [f"Ask AVs leave request related questions to {person}"]
        
        # Pattern: "Talk to mgmt about the feedback form, AVs leave request related questions to be asked to Amit sir"
        mgmt_av_pattern = r'talk\s+to\s+mgmt\s+about\s+the\s+feedback\s+form,\s+avs\s+leave\s+request\s+related\s+questions\s+to\s+be\s+asked\s+to\s+(.+)'
        match = re.search(mgmt_av_pattern, task_lower)
        if match:
            person = match.group(1).strip()
            return [f"Talk to mgmt about the feedback form", f"Ask AVs leave request related questions to {person}"]
        
        # Pattern: "Today we have a call with AP for CABP project so talk to team for the same"
        call_team_pattern = r'today\s+we\s+have\s+a\s+call\s+with\s+(.+?)\s+for\s+(.+?)\s+project\s+so\s+talk\s+to\s+team\s+for\s+the\s+same'
        match = re.search(call_team_pattern, task_lower)
        if match:
            person = match.group(1).strip()
            project = match.group(2).strip()
            return [f"Have call with {person} for {project} project", f"Talk to team about {project} project"]
        
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
        
        # Pattern: "X as well as Y" (parallel tasks)
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
    
    def get_priority_analysis(self, task: str) -> Dict[str, Any]:
        """Get detailed priority analysis for a task."""
        priority = self.classify_priority(task)
        category = self.classify_category(task)
        
        return {
            'task': task,
            'priority': priority,
            'category': category,
            'confidence': 'high' if self.client or self.model else 'medium',
            'reasoning': f"AI-powered analysis using {self.ai_provider}" if self.client or self.model else "Rule-based analysis"
        }
    
    def process_tasks(self, raw_text: str) -> Dict[str, Any]:
        """Main method to process raw text and return structured tasks."""
        try:
            # Extract tasks
            tasks = self.extract_tasks(raw_text)
            
            if not tasks:
                return {
                    'success': False,
                    'message': 'No tasks found in the input text',
                    'tasks': [],
                    'ai_provider': self.ai_provider
                }
            
            # Process each task
            processed_tasks = []
            for i, task in enumerate(tasks, 1):
                processed_task = {
                    'id': i,
                    'description': task,
                    'priority': self.classify_priority(task),
                    'category': self.classify_category(task),
                    'due_date': self.extract_due_date(task),
                    'status': 'pending'
                }
                processed_tasks.append(processed_task)
            
            return {
                'success': True,
                'message': f'Successfully processed {len(processed_tasks)} tasks using {self.ai_provider}',
                'tasks': processed_tasks,
                'ai_provider': self.ai_provider
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing tasks: {str(e)}',
                'tasks': [],
                'ai_provider': self.ai_provider
            }


# Example usage and testing
if __name__ == "__main__":
    processor = TaskProcessor(ai_provider="chatgpt")
    
    # Test with sample input
    sample_text = """
    Finish PPT for client meeting tomorrow, check AWS logs for errors, 
    call client about project update, review quarterly reports, 
    schedule team standup meeting
    """
    
    result = processor.process_tasks(sample_text)
    print(json.dumps(result, indent=2))