#!/usr/bin/env python3
"""
Test script to verify the setup
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test FastAPI
        import fastapi
        print("✅ FastAPI imported successfully")
        
        # Test Playwright
        import playwright
        print("✅ Playwright imported successfully")
        
        # Test Pydantic
        import pydantic
        print("✅ Pydantic imported successfully")
        
        # Test our modules
        from backend.config import settings
        print("✅ Config imported successfully")
        
        from backend.models.test_models import TestAction, ActionType
        print("✅ Models imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration"""
    try:
        from backend.config import settings
        print(f"\nTesting configuration...")
        print(f"Backend Port: {settings.BACKEND_PORT}")
        print(f"Browser Type: {settings.BROWSER_TYPE}")
        print(f"Headless: {settings.HEADLESS}")
        print(f"Screenshots Dir: {settings.SCREENSHOTS_DIR}")
        print("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_directories():
    """Test if required directories exist"""
    try:
        from backend.config import settings
        
        # Check screenshots directory
        if os.path.exists(settings.SCREENSHOTS_DIR):
            print(f"✅ Screenshots directory exists: {settings.SCREENSHOTS_DIR}")
        else:
            os.makedirs(settings.SCREENSHOTS_DIR, exist_ok=True)
            print(f"✅ Created screenshots directory: {settings.SCREENSHOTS_DIR}")
        
        # Check logs directory
        if os.path.exists(settings.LOGS_DIR):
            print(f"✅ Logs directory exists: {settings.LOGS_DIR}")
        else:
            os.makedirs(settings.LOGS_DIR, exist_ok=True)
            print(f"✅ Created logs directory: {settings.LOGS_DIR}")
        
        return True
    except Exception as e:
        print(f"❌ Directory error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Intelligent Tester Setup\n")
    
    success = True
    success &= test_imports()
    success &= test_config()
    success &= test_directories()
    
    if success:
        print("\n🎉 Setup test completed successfully!")
        print("You can now start the backend server.")
    else:
        print("\n❌ Setup test failed. Please check the errors above.")
        sys.exit(1)
