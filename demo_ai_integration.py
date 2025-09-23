#!/usr/bin/env python3
"""
Demo script showing how to use the AI-powered task processor with API keys
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ai_processor import TaskProcessor
import json

def demo_with_api_keys():
    """Demo the AI processor with API keys."""
    
    print("🚀 AI-Powered Task Processor Demo")
    print("=" * 50)
    
    # Test input
    test_input = """
    setup meeting with av for performance review, before that talk to praveen and get his feedback. 
    Work on creating user stories for the CABP project as well as for sentilink. 
    then if time permits talk to OvationCXM guys and check on their progress. 
    Today is due date for electricity & internet so pay 2450 and 2369 rupees respectively 
    lastly Most important Shweta have not received the invite from ovation team so talk to Jim about it
    """
    
    print(f"📝 Test Input:")
    print(test_input.strip())
    print("\n" + "=" * 50)
    
    # Check if API keys are available
    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if openai_key:
        print("\n🔵 Testing with ChatGPT API...")
        try:
            chatgpt_processor = TaskProcessor(ai_provider="chatgpt")
            result = chatgpt_processor.process_tasks(test_input)
            
            if result['success']:
                print(f"✅ ChatGPT Success: {result['message']}")
                print(f"📊 Tasks Found: {len(result['tasks'])}")
                
                for i, task in enumerate(result['tasks'], 1):
                    print(f"  {i}. {task['description']}")
                    print(f"     Priority: {task['priority']} | Category: {task['category']}")
            else:
                print(f"❌ ChatGPT Failed: {result['message']}")
                
        except Exception as e:
            print(f"❌ ChatGPT Error: {e}")
    
    if gemini_key:
        print("\n🟡 Testing with Gemini API...")
        try:
            gemini_processor = TaskProcessor(ai_provider="gemini")
            result = gemini_processor.process_tasks(test_input)
            
            if result['success']:
                print(f"✅ Gemini Success: {result['message']}")
                print(f"📊 Tasks Found: {len(result['tasks'])}")
                
                for i, task in enumerate(result['tasks'], 1):
                    print(f"  {i}. {task['description']}")
                    print(f"     Priority: {task['priority']} | Category: {task['category']}")
            else:
                print(f"❌ Gemini Failed: {result['message']}")
                
        except Exception as e:
            print(f"❌ Gemini Error: {e}")
    
    if not openai_key and not gemini_key:
        print("\n⚠️  No API keys found!")
        print("To use AI-powered processing, set one of these environment variables:")
        print("  - OPENAI_API_KEY for ChatGPT")
        print("  - GEMINI_API_KEY for Gemini")
        print("\nThe system will automatically fall back to rule-based processing.")
        
        # Test fallback mode
        print("\n🔄 Testing Fallback Mode...")
        fallback_processor = TaskProcessor(ai_provider="chatgpt")
        result = fallback_processor.process_tasks(test_input)
        
        if result['success']:
            print(f"✅ Fallback Success: {result['message']}")
            print(f"📊 Tasks Found: {len(result['tasks'])}")
            
            for i, task in enumerate(result['tasks'], 1):
                print(f"  {i}. {task['description']}")
                print(f"     Priority: {task['priority']} | Category: {task['category']}")
    
    print("\n" + "=" * 50)
    print("🎯 Demo Complete!")

if __name__ == "__main__":
    demo_with_api_keys()
