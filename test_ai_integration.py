#!/usr/bin/env python3
"""
Test script for the new AI-powered task processor using ChatGPT/Gemini APIs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ai_processor import TaskProcessor
import json

def test_ai_processor():
    """Test the AI processor with different providers."""
    
    print("🤖 Testing AI-Powered Task Processor")
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
    
    # Test with ChatGPT (if API key is available)
    print("\n🔵 Testing with ChatGPT...")
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
    
    print("\n" + "=" * 50)
    
    # Test with Gemini (if API key is available)
    print("\n🟡 Testing with Gemini...")
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
    
    print("\n" + "=" * 50)
    
    # Test fallback mode (no API keys)
    print("\n🔄 Testing Fallback Mode (No API Keys)...")
    try:
        # Temporarily remove API keys to test fallback
        original_openai_key = os.environ.get('OPENAI_API_KEY')
        original_gemini_key = os.environ.get('GEMINI_API_KEY')
        
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        
        fallback_processor = TaskProcessor(ai_provider="chatgpt")
        result = fallback_processor.process_tasks(test_input)
        
        if result['success']:
            print(f"✅ Fallback Success: {result['message']}")
            print(f"📊 Tasks Found: {len(result['tasks'])}")
            
            for i, task in enumerate(result['tasks'], 1):
                print(f"  {i}. {task['description']}")
                print(f"     Priority: {task['priority']} | Category: {task['category']}")
        else:
            print(f"❌ Fallback Failed: {result['message']}")
        
        # Restore API keys
        if original_openai_key:
            os.environ['OPENAI_API_KEY'] = original_openai_key
        if original_gemini_key:
            os.environ['GEMINI_API_KEY'] = original_gemini_key
            
    except Exception as e:
        print(f"❌ Fallback Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Complete!")

def test_comprehensive_list():
    """Test with the comprehensive list from earlier."""
    
    print("\n🧪 Testing Comprehensive List")
    print("=" * 50)
    
    test_input = """Pay electricity bill, Book travel tickets
Arrange team lunch
Submit report by EOD, Prepare meeting slides, Buy snacks. Install software update, Clean inbox. Plan team building activity
Schedule dentist appointment, Call client, Renew vehicle insurance"""
    
    print(f"📝 Test Input:")
    print(test_input)
    print("\n" + "=" * 50)
    
    # Test with ChatGPT
    print("\n🔵 Testing with ChatGPT...")
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

if __name__ == "__main__":
    test_ai_processor()
    test_comprehensive_list()
