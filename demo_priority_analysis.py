#!/usr/bin/env python3
"""
Priority Analysis Demo
Showcases the comprehensive priority determination system
"""

import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ai_processor import TaskProcessor

def demo_priority_analysis():
    """Demonstrate the comprehensive priority analysis system."""
    processor = TaskProcessor()
    
    print("🎯 COMPREHENSIVE PRIORITY ANALYSIS DEMO")
    print("=" * 60)
    print()
    
    # Demo tasks with different priority levels
    demo_tasks = [
        "URGENT: Fix production database outage affecting all users",
        "Rotate API keys expiring tomorrow - security flagged",
        "Prepare quarterly report for board meeting next Friday",
        "Nice-to-have: Add dark mode toggle to user interface",
        "Fix client portal bug causing payment processing issues",
        "Update documentation when you have time",
        "EMERGENCY: Security breach detected in user database",
        "Schedule team standup meeting for next week",
        "Deploy hotfix to staging environment ASAP",
        "Clean up old log files from server"
    ]
    
    print("📋 ANALYZING TASK PRIORITIES")
    print("-" * 40)
    
    for i, task in enumerate(demo_tasks, 1):
        print(f"\n{i}. Task: {task}")
        
        # Get detailed priority analysis
        analysis = processor.get_priority_analysis(task)
        
        # Display results
        priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
        print(f"   Priority: {priority_emoji[analysis['priority']]} {analysis['priority']}")
        print(f"   Score: {analysis['total_score']} points")
        print(f"   Confidence: {analysis['confidence']}")
        
        if analysis['reasoning']:
            print(f"   Reasoning: {'; '.join(analysis['reasoning'])}")
        
        # Show score breakdown
        print("   Score Breakdown:")
        for component, score in analysis['score_breakdown'].items():
            if score != 0:
                print(f"     • {component.replace('_', ' ').title()}: {score:+d} points")
    
    print("\n" + "=" * 60)
    print("📊 PRIORITY SYSTEM FEATURES")
    print("=" * 60)
    
    features = [
        "✅ Multi-factor scoring algorithm (8 components)",
        "✅ Urgency keyword detection (critical, urgent, emergency, etc.)",
        "✅ Time sensitivity analysis (deadlines, specific times)",
        "✅ Security impact assessment (API keys, vulnerabilities, etc.)",
        "✅ Business impact evaluation (client issues, revenue, etc.)",
        "✅ Deadline pressure detection (committed dates, promises)",
        "✅ Context urgency (meetings, escalations, executive requests)",
        "✅ Negative indicators (nice-to-have, optional, etc.)",
        "✅ Confidence scoring based on multiple factors",
        "✅ Human-readable reasoning for decisions",
        "✅ Detailed score breakdown for transparency"
    ]
    
    for feature in features:
        print(feature)
    
    print("\n🎯 SCORING COMPONENTS")
    print("-" * 30)
    components = [
        ("Urgency Keywords", "0-40 points", "critical, urgent, emergency, asap, blocker"),
        ("Time Sensitivity", "0-35 points", "today, tomorrow, EOD, specific times"),
        ("Security Impact", "0-40 points", "API keys, vulnerabilities, breaches"),
        ("Business Impact", "0-30 points", "client issues, revenue, production"),
        ("Deadline Pressure", "0-25 points", "deadlines, commitments, promises"),
        ("Context Urgency", "0-20 points", "meetings, escalations, executives"),
        ("Positive Indicators", "0-10 points", "important, must, priority"),
        ("Negative Indicators", "-15 points", "nice-to-have, optional, future")
    ]
    
    for component, range_points, examples in components:
        print(f"• {component}: {range_points}")
        print(f"  Examples: {examples}")
        print()
    
    print("🎉 The system is now ready for production use!")
    print("It provides intelligent, context-aware priority determination")
    print("with full transparency and reasoning for each decision.")

if __name__ == "__main__":
    demo_priority_analysis()
