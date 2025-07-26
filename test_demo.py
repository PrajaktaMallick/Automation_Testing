#!/usr/bin/env python3
"""
Demo script to test the intelligent tester
"""
import requests
import json
import time

def test_intelligent_tester():
    """Run a demo test of the intelligent tester"""
    
    print("🚀 Starting Intelligent Tester Demo...")
    print("=" * 50)
    
    # Test data
    test_data = {
        'website_url': 'https://example.com',
        'prompt': 'Navigate to the website and take a screenshot'
    }
    
    print(f"🌐 Website URL: {test_data['website_url']}")
    print(f"📝 Test Prompt: {test_data['prompt']}")
    print("=" * 50)
    
    try:
        print("📡 Sending request to intelligent tester backend...")
        response = requests.post('http://localhost:8000/api/tests/create', json=test_data)
        
        print(f"✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("🎉 Test Created Successfully!")
            print(f"📋 Session ID: {result.get('session_id', 'N/A')}")
            print(f"🎯 Actions Planned: {len(result.get('actions', []))}")
            
            # Show the planned actions
            actions = result.get('actions', [])
            print("\n📋 Planned Actions:")
            for i, action in enumerate(actions, 1):
                print(f"  {i}. {action.get('description', 'No description')}")
            
            print("\n🌐 A real browser window should now open and perform these actions!")
            print("⏰ The browser will stay open for 30 seconds for you to interact with it.")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the backend server.")
        print("🔧 Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_intelligent_tester()
