#!/usr/bin/env python3
"""
Comprehensive test script for AI To-Do List Manager
Tests against realistic "messy notes" scenarios to validate AI processing logic
"""

import json
import requests
import time
from typing import Dict, List, Any

# Test scenarios from the user's requirements
TEST_SCENARIOS = {
    "1_quick_bullets": {
        "name": "Quick bullets (easy)",
        "input": """finish PPT for Nexus call
check AWS CloudWatch logs for 5xx spikes
email Priya about invoice 349
book meeting room for Friday standup""",
        "expected_tasks": 4,
        "expected_high_priority": ["PPT", "CloudWatch", "logs", "5xx"],
        "expected_categories": ["Work", "Admin", "Meetings"]
    },
    
    "2_messy_paragraph": {
        "name": "Messy paragraph (realistic)",
        "input": """Need to clean up the repo (docs are stale), ping finance re: expense sheet, update client deck v3.1 by EOD Wed, and oh—rotate API keys (security flagged expiring on 30th). Also ship a short Loom to Anish about the demo flow.""",
        "expected_tasks": 5,
        "expected_high_priority": ["API keys", "security", "expiring", "EOD"],
        "expected_categories": ["Work", "Admin"]
    },
    
    "3_meeting_dump": {
        "name": "Meeting dump (timestamps + owners)",
        "input": """[10:02] Rahul: move CRM leads to new pipeline
[10:07] Me: create draft SOP for Challenge Hub submissions
[10:18] Shreya: test RAG bot with 20 FAQs
[10:26] Team: schedule retro next Tue 4pm""",
        "expected_tasks": 4,
        "expected_high_priority": [],
        "expected_categories": ["Work", "Meetings"]
    },
    
    "4_email_copy": {
        "name": "Email copy-paste (with dates)",
        "input": """Subject: URGENT – Client sandbox down
Can we restart the staging services and share a 2-line RCA by tomorrow 11am? Also, please archive old logs older than 14 days.
– Ops""",
        "expected_tasks": 3,
        "expected_high_priority": ["URGENT", "tomorrow", "11am"],
        "expected_categories": ["Work"]
    },
    
    "5_mixed_work_personal": {
        "name": "Mixed work/personal + shorthand",
        "input": """pay internet bill; renew SSL cert for portal; mom bday gift; write JD for AI intern; fix navbar bug (mobile)""",
        "expected_tasks": 5,
        "expected_high_priority": [],
        "expected_categories": ["Work", "Personal"]
    },
    
    "6_priority_hints": {
        "name": "With hints that imply priority",
        "input": """BLOCKER: S3 upload failing for large files
nice-to-have: dark mode toggle
time-sensitive: send offer letter by today 6pm""",
        "expected_tasks": 3,
        "expected_high_priority": ["BLOCKER", "time-sensitive", "today", "6pm"],
        "expected_categories": ["Work"]
    },
    
    "7_lightweight_tags": {
        "name": "With lightweight tags",
        "input": """#work close Q3 hiring loop
#admin claim travel reimbursement
#meetings set 1:1 with Amit (Fri)""",
        "expected_tasks": 3,
        "expected_high_priority": [],
        "expected_categories": ["Work", "Admin", "Meetings"]
    },
    
    "8_dates_times": {
        "name": "With dates/times & relative terms",
        "input": """submit timesheet today 5pm
prep talking points for Monday townhall
set reminder to renew domain on 30 Sept""",
        "expected_tasks": 3,
        "expected_high_priority": ["today", "5pm"],
        "expected_categories": ["Work", "Admin"]
    },
    
    "9_noisy_typos": {
        "name": "Noisy/typo'd (robustness)",
        "input": """Chk AWs logs 4 error burst; updt readme; meetin with Ketan tmw 3pm; inv. 912 followup""",
        "expected_tasks": 4,
        "expected_high_priority": ["tmw", "3pm"],
        "expected_categories": ["Work", "Admin"]
    },
    
    "10_multilingual": {
        "name": "Multilingual sprinkle (optional)",
        "input": """Draft client email (Hindi greeting), schedule demo kal 11 baje, export data report""",
        "expected_tasks": 3,
        "expected_high_priority": [],
        "expected_categories": ["Work"]
    }
}

class TestRunner:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results = {}
    
    def test_api_health(self) -> bool:
        """Test if the API is running"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is healthy and running")
                return True
            else:
                print(f"❌ API health check failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to API: {e}")
            print("Make sure the backend is running on http://localhost:5000")
            return False
    
    def process_tasks(self, text: str) -> Dict[str, Any]:
        """Send text to the API for processing"""
        try:
            response = requests.post(
                f"{self.base_url}/api/process-tasks",
                json={"text": text},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "message": f"API error: {response.status_code}",
                    "tasks": []
                }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Request error: {e}",
                "tasks": []
            }
    
    def analyze_results(self, scenario_name: str, result: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the results against expected outcomes"""
        analysis = {
            "scenario": scenario_name,
            "success": result.get("success", False),
            "message": result.get("message", ""),
            "tasks": result.get("tasks", []),
            "analysis": {}
        }
        
        tasks = result.get("tasks", [])
        
        # Check task count
        actual_count = len(tasks)
        expected_count = expected.get("expected_tasks", 0)
        analysis["analysis"]["task_count"] = {
            "actual": actual_count,
            "expected": expected_count,
            "match": actual_count == expected_count,
            "status": "✅" if actual_count == expected_count else "⚠️"
        }
        
        # Check priority distribution
        priorities = [task.get("priority", "Unknown") for task in tasks]
        priority_counts = {"High": 0, "Medium": 0, "Low": 0, "Unknown": 0}
        for p in priorities:
            priority_counts[p] = priority_counts.get(p, 0) + 1
        
        analysis["analysis"]["priority_distribution"] = priority_counts
        
        # Check for expected high priority keywords
        high_priority_found = []
        expected_high_keywords = expected.get("expected_high_priority", [])
        for task in tasks:
            task_text = task.get("description", "").lower()
            task_priority = task.get("priority", "")
            for keyword in expected_high_keywords:
                if keyword.lower() in task_text and task_priority == "High":
                    high_priority_found.append(keyword)
        
        analysis["analysis"]["high_priority_detection"] = {
            "expected_keywords": expected_high_keywords,
            "found_keywords": list(set(high_priority_found)),
            "coverage": len(set(high_priority_found)) / len(expected_high_keywords) if expected_high_keywords else 1.0
        }
        
        # Check category distribution
        categories = [task.get("category", "Unknown") for task in tasks]
        category_counts = {}
        for c in categories:
            category_counts[c] = category_counts.get(c, 0) + 1
        
        analysis["analysis"]["category_distribution"] = category_counts
        
        return analysis
    
    def run_single_test(self, scenario_id: str, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test scenario"""
        print(f"\n🧪 Testing: {scenario_data['name']}")
        print("=" * 60)
        
        # Process the input
        result = self.process_tasks(scenario_data["input"])
        
        # Analyze results
        analysis = self.analyze_results(scenario_id, result, scenario_data)
        
        # Print results
        if result.get("success"):
            print(f"✅ Processing successful: {result.get('message', '')}")
            print(f"📊 Tasks extracted: {len(result.get('tasks', []))}")
            
            # Show task details
            for i, task in enumerate(result.get("tasks", []), 1):
                print(f"  {i}. {task.get('description', 'N/A')}")
                print(f"     Priority: {task.get('priority', 'N/A')} | Category: {task.get('category', 'N/A')}")
            
            # Show analysis
            analysis_data = analysis["analysis"]
            print(f"\n📈 Analysis:")
            print(f"  Task count: {analysis_data['task_count']['actual']}/{analysis_data['task_count']['expected']} {analysis_data['task_count']['status']}")
            print(f"  Priority distribution: {analysis_data['priority_distribution']}")
            print(f"  Category distribution: {analysis_data['category_distribution']}")
            
            if analysis_data['high_priority_detection']['expected_keywords']:
                coverage = analysis_data['high_priority_detection']['coverage']
                print(f"  High priority detection: {coverage:.1%} coverage")
                print(f"    Expected: {analysis_data['high_priority_detection']['expected_keywords']}")
                print(f"    Found: {analysis_data['high_priority_detection']['found_keywords']}")
        else:
            print(f"❌ Processing failed: {result.get('message', 'Unknown error')}")
        
        return analysis
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test scenarios"""
        print("🚀 Starting comprehensive AI To-Do List Manager tests")
        print("=" * 80)
        
        # Check API health first
        if not self.test_api_health():
            return {"error": "API not available"}
        
        all_results = {}
        total_scenarios = len(TEST_SCENARIOS)
        successful_scenarios = 0
        
        for scenario_id, scenario_data in TEST_SCENARIOS.items():
            try:
                result = self.run_single_test(scenario_id, scenario_data)
                all_results[scenario_id] = result
                
                if result.get("success"):
                    successful_scenarios += 1
                
                # Small delay between tests
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error in scenario {scenario_id}: {e}")
                all_results[scenario_id] = {
                    "scenario": scenario_id,
                    "success": False,
                    "error": str(e)
                }
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total scenarios: {total_scenarios}")
        print(f"Successful: {successful_scenarios}")
        print(f"Failed: {total_scenarios - successful_scenarios}")
        print(f"Success rate: {successful_scenarios/total_scenarios:.1%}")
        
        return {
            "summary": {
                "total_scenarios": total_scenarios,
                "successful_scenarios": successful_scenarios,
                "failed_scenarios": total_scenarios - successful_scenarios,
                "success_rate": successful_scenarios/total_scenarios
            },
            "results": all_results
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = "test_results.json"):
        """Save test results to a JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")

def main():
    """Main function to run the tests"""
    print("AI To-Do List Manager - Realistic Scenario Testing")
    print("=" * 60)
    
    # Initialize test runner
    runner = TestRunner()
    
    # Run all tests
    results = runner.run_all_tests()
    
    # Save results
    if "error" not in results:
        runner.save_results(results)
        
        # Print final recommendations
        print("\n🎯 RECOMMENDATIONS")
        print("=" * 40)
        success_rate = results["summary"]["success_rate"]
        
        if success_rate >= 0.9:
            print("🎉 Excellent! The AI processor handles realistic scenarios very well.")
        elif success_rate >= 0.7:
            print("👍 Good performance! Consider fine-tuning for edge cases.")
        elif success_rate >= 0.5:
            print("⚠️ Moderate performance. Review failed scenarios for improvements.")
        else:
            print("🔧 Needs improvement. Check AI processing logic and keyword matching.")
        
        print("\nNext steps:")
        print("1. Review failed scenarios in test_results.json")
        print("2. Adjust priority keywords in ai_processor.py if needed")
        print("3. Enhance category detection patterns")
        print("4. Test with your own real-world inputs")

if __name__ == "__main__":
    main()
