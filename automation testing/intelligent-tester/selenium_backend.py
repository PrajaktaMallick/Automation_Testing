#!/usr/bin/env python3
"""
Real Browser Automation Backend using Selenium - Actually opens browsers and performs actions
"""
import json
import os
import uuid
import time
import threading
import re
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Try to import Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
    print("✅ Selenium is available - Real browser automation enabled!")
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not available. Install with: pip install selenium")

# Global storage
test_sessions = {}
active_executions = {}

class RealBrowserAutomation:
    def __init__(self):
        self.driver = None
    
    def initialize(self):
        """Initialize real Chrome browser using Selenium"""
        if not SELENIUM_AVAILABLE:
            raise Exception("Selenium not available. Please install: pip install selenium")
        
        print("🚀 Launching real Chrome browser...")
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Try to create Chrome driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            print("✅ Chrome browser launched successfully!")
            
        except Exception as e:
            print(f"❌ Failed to launch Chrome: {e}")
            print("💡 Make sure Chrome is installed and chromedriver is in PATH")
            raise
        
    def cleanup(self):
        """Clean up browser resources"""
        try:
            print("🧹 Cleaning up browser...")
            if self.driver:
                self.driver.quit()
            print("✅ Browser cleanup complete")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
    
    def execute_action(self, action, session_id):
        """Execute a single action on the real browser"""
        action_type = action["type"]
        target = action["target"]
        value = action.get("value", "")
        
        try:
            print(f"🔄 Executing: {action['description']}")
            
            if action_type == "navigate":
                print(f"🌐 Navigating to: {target}")
                self.driver.get(target)
                time.sleep(3)  # Wait for page to load
                result = f"✅ Successfully navigated to {target}"
                
            elif action_type == "click":
                print(f"🖱️ Clicking: {target}")
                element = self._find_element_with_fallback(target, "click")
                if element:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(1)
                    element.click()
                    result = f"✅ Successfully clicked: {target}"
                else:
                    raise Exception(f"Could not find clickable element: {target}")
                    
            elif action_type == "type":
                print(f"⌨️ Typing: '{value}' into {target}")
                element = self._find_element_with_fallback(target, "input")
                if element:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(1)
                    element.clear()
                    element.send_keys(value)
                    result = f"✅ Successfully typed '{value}' into {target}"
                else:
                    raise Exception(f"Could not find input element: {target}")
                    
            elif action_type == "wait":
                wait_time = int(value) if value.isdigit() else 3000
                print(f"⏱️ Waiting {wait_time}ms...")
                time.sleep(wait_time / 1000)
                result = f"✅ Waited {wait_time}ms"
                
            elif action_type == "screenshot":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"real_{session_id}_{timestamp}.png"
                filepath = os.path.join("screenshots", filename)
                os.makedirs("screenshots", exist_ok=True)
                
                print(f"📸 Taking screenshot: {filename}")
                self.driver.save_screenshot(filepath)
                result = f"✅ Screenshot saved: /screenshots/{filename}"
                
            elif action_type == "verify":
                if target == "title":
                    page_title = self.driver.title
                    print(f"🔍 Verifying title: '{page_title}' contains '{value}'")
                    if value.lower() in page_title.lower():
                        result = f"✅ Title verification passed: '{page_title}' contains '{value}'"
                    else:
                        raise Exception(f"Title verification failed: '{page_title}' does not contain '{value}'")
                else:
                    result = f"⚠️ Verification type '{target}' not implemented"
                    
            else:
                result = f"⚠️ Action type '{action_type}' not implemented"
            
            print(f"✅ {result}")
            return {"status": "success", "result": result, "error": None}
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Action failed: {error_msg}")
            return {"status": "failed", "result": None, "error": error_msg}
    
    def _find_element_with_fallback(self, target, element_type):
        """Find element using multiple strategies"""
        selectors = self._generate_selectors(target, element_type)
        
        for selector_type, selector in selectors:
            try:
                print(f"   Trying {selector_type}: {selector}")
                
                if selector_type == "xpath":
                    element = self.driver.find_element(By.XPATH, selector)
                elif selector_type == "css":
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                elif selector_type == "id":
                    element = self.driver.find_element(By.ID, selector)
                elif selector_type == "name":
                    element = self.driver.find_element(By.NAME, selector)
                elif selector_type == "class":
                    element = self.driver.find_element(By.CLASS_NAME, selector)
                elif selector_type == "tag":
                    element = self.driver.find_element(By.TAG_NAME, selector)
                elif selector_type == "link_text":
                    element = self.driver.find_element(By.LINK_TEXT, selector)
                elif selector_type == "partial_link_text":
                    element = self.driver.find_element(By.PARTIAL_LINK_TEXT, selector)
                else:
                    continue
                
                if element and element.is_displayed():
                    print(f"   ✅ Found element with {selector_type}: {selector}")
                    return element
                    
            except (NoSuchElementException, Exception) as e:
                print(f"   ❌ {selector_type} failed: {selector}")
                continue
        
        return None
    
    def _generate_selectors(self, target, element_type):
        """Generate multiple selector strategies"""
        selectors = []
        target_lower = target.lower()
        
        # If it's already a CSS selector, try it first
        if any(char in target for char in ['[', '.', '#', ':', '>']):
            selectors.append(("css", target))
        
        if element_type == "click":
            # Button and link selectors
            selectors.extend([
                ("xpath", f"//button[contains(text(), '{target}')]"),
                ("xpath", f"//input[@type='button' and contains(@value, '{target}')]"),
                ("xpath", f"//input[@type='submit' and contains(@value, '{target}')]"),
                ("xpath", f"//a[contains(text(), '{target}')]"),
                ("link_text", target),
                ("partial_link_text", target),
            ])
            
            # Login-specific selectors
            if 'login' in target_lower:
                selectors.extend([
                    ("css", "button[type='submit']"),
                    ("css", "input[type='submit']"),
                    ("css", ".login-btn"),
                    ("css", ".login-button"),
                    ("id", "login-btn"),
                    ("id", "login-button"),
                    ("xpath", "//button[contains(@class, 'login')]"),
                    ("xpath", "//input[contains(@class, 'login')]"),
                ])
        
        elif element_type == "input":
            # Input field selectors
            if 'email' in target_lower:
                selectors.extend([
                    ("css", "input[type='email']"),
                    ("css", "input[name*='email']"),
                    ("css", "input[id*='email']"),
                    ("css", "input[placeholder*='email']"),
                    ("name", "email"),
                    ("id", "email"),
                ])
            elif 'password' in target_lower:
                selectors.extend([
                    ("css", "input[type='password']"),
                    ("css", "input[name*='password']"),
                    ("css", "input[id*='password']"),
                    ("name", "password"),
                    ("id", "password"),
                ])
            elif 'search' in target_lower:
                selectors.extend([
                    ("css", "input[type='search']"),
                    ("css", "input[name*='search']"),
                    ("css", "input[id*='search']"),
                    ("css", "input[placeholder*='search']"),
                    ("name", "search"),
                    ("id", "search"),
                    ("css", ".search-input"),
                ])
            elif 'name' in target_lower:
                selectors.extend([
                    ("css", "input[name*='name']"),
                    ("css", "input[id*='name']"),
                    ("css", "input[placeholder*='name']"),
                    ("name", "name"),
                    ("id", "name"),
                ])
            else:
                # Generic input selectors
                selectors.extend([
                    ("css", f"input[placeholder*='{target}']"),
                    ("css", f"input[name*='{target.lower()}']"),
                    ("css", f"input[id*='{target.lower()}']"),
                    ("css", "input[type='text']"),
                    ("css", "input:not([type])"),
                    ("tag", "input"),
                ])
        
        # Common fallback selectors
        target_slug = target_lower.replace(' ', '-').replace('_', '-')
        selectors.extend([
            ("id", target_slug),
            ("css", f".{target_slug}"),
            ("css", f"[data-testid*='{target_slug}']"),
            ("xpath", f"//*[contains(@aria-label, '{target}')]"),
            ("xpath", f"//*[contains(@title, '{target}')]"),
            ("xpath", f"//*[contains(text(), '{target}')]"),
        ])
        
        return selectors

def generate_intelligent_action_plan(prompt, website_url):
    """Generate intelligent action plan from natural language prompt"""
    actions = []
    prompt_lower = prompt.lower()
    
    # Always start with navigation
    actions.append({
        "type": "navigate",
        "description": f"Navigate to {website_url}",
        "target": website_url,
        "value": "",
        "timeout": 30000
    })
    
    # Add wait after navigation
    actions.append({
        "type": "wait",
        "description": "Wait for page to fully load",
        "target": "time",
        "value": "3000",
        "timeout": 5000
    })
    
    # Parse login actions
    if "login" in prompt_lower:
        actions.extend(_generate_login_actions(prompt))
    
    # Parse search actions
    if "search" in prompt_lower:
        actions.extend(_generate_search_actions(prompt))
    
    # Parse form filling actions
    if "fill" in prompt_lower and "form" in prompt_lower:
        actions.extend(_generate_form_actions(prompt))
    
    # Parse add to cart actions
    if "add to cart" in prompt_lower or "add first" in prompt_lower:
        actions.extend(_generate_cart_actions(prompt))
    
    # Parse verification actions
    if "verify" in prompt_lower or "check" in prompt_lower:
        actions.extend(_generate_verification_actions(prompt))
    
    # Always add screenshot if mentioned or at the end
    if "screenshot" in prompt_lower or len([a for a in actions if a["type"] == "screenshot"]) == 0:
        actions.append({
            "type": "screenshot",
            "description": "Take final screenshot",
            "target": "",
            "value": "",
            "timeout": 5000
        })
    
    return actions

def _generate_login_actions(prompt):
    """Generate login-specific actions"""
    actions = []
    
    # Extract email if present
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', prompt)
    email = email_match.group() if email_match else "jyoti@test.com"
    
    # Extract password if present
    password_match = re.search(r'password[:\s]+([^\s,]+)', prompt, re.IGNORECASE)
    password = password_match.group(1) if password_match else "123456"
    
    if "email" in prompt.lower() or "@" in prompt:
        actions.append({
            "type": "type",
            "description": f"Enter email: {email}",
            "target": "email",
            "value": email,
            "timeout": 10000
        })
    
    if "password" in prompt.lower():
        actions.append({
            "type": "type",
            "description": "Enter password",
            "target": "password",
            "value": password,
            "timeout": 10000
        })
    
    actions.append({
        "type": "click",
        "description": "Click login button",
        "target": "login",
        "value": "",
        "timeout": 10000
    })
    
    return actions

def _generate_search_actions(prompt):
    """Generate search-specific actions"""
    actions = []
    
    # Extract search term
    search_patterns = [
        r'search for (.+?)(?:\s+and|\s+then|$)',
        r'find (.+?)(?:\s+and|\s+then|$)',
        r'look for (.+?)(?:\s+and|\s+then|$)'
    ]
    
    search_term = "test"  # Default
    for pattern in search_patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            search_term = match.group(1).strip().strip('"\'')
            break
    
    actions.extend([
        {
            "type": "click",
            "description": "Click search box",
            "target": "search",
            "value": "",
            "timeout": 10000
        },
        {
            "type": "type",
            "description": f"Search for: {search_term}",
            "target": "search",
            "value": search_term,
            "timeout": 10000
        },
        {
            "type": "click",
            "description": "Submit search",
            "target": "button[type='submit']",
            "value": "",
            "timeout": 10000
        }
    ])
    
    return actions

def _generate_form_actions(prompt):
    """Generate form filling actions"""
    actions = []
    
    # Extract name if present
    name_match = re.search(r'name ["\']([^"\']+)["\']', prompt, re.IGNORECASE)
    name = name_match.group(1) if name_match else "John Doe"
    
    # Extract email if present
    email_match = re.search(r'email ["\']([^"\']+)["\']', prompt, re.IGNORECASE)
    email = email_match.group(1) if email_match else "john.doe@example.com"
    
    actions.extend([
        {
            "type": "type",
            "description": f"Fill name field with: {name}",
            "target": "name",
            "value": name,
            "timeout": 10000
        },
        {
            "type": "type",
            "description": f"Fill email field with: {email}",
            "target": "email",
            "value": email,
            "timeout": 10000
        }
    ])
    
    if "submit" in prompt.lower():
        actions.append({
            "type": "click",
            "description": "Submit form",
            "target": "button[type='submit']",
            "value": "",
            "timeout": 10000
        })
    
    return actions

def _generate_cart_actions(prompt):
    """Generate shopping cart actions"""
    return [
        {
            "type": "click",
            "description": "Click first product",
            "target": ".product:first-child",
            "value": "",
            "timeout": 10000
        },
        {
            "type": "click",
            "description": "Add to cart",
            "target": "add to cart",
            "value": "",
            "timeout": 10000
        }
    ]

def _generate_verification_actions(prompt):
    """Generate verification actions"""
    actions = []
    
    if "title" in prompt.lower():
        title_match = re.search(r'title contains ["\']([^"\']+)["\']', prompt, re.IGNORECASE)
        title_text = title_match.group(1) if title_match else "Example"
        
        actions.append({
            "type": "verify",
            "description": f"Verify page title contains '{title_text}'",
            "target": "title",
            "value": title_text,
            "timeout": 5000
        })
    
    return actions

def execute_real_test_session(session_id):
    """Execute test session with REAL browser automation using Selenium"""
    session = test_sessions[session_id]
    browser_automation = None
    
    try:
        print(f"🚀 Starting REAL test execution for session {session_id}")
        
        # Initialize real browser
        browser_automation = RealBrowserAutomation()
        browser_automation.initialize()
        
        active_executions[session_id] = {
            "browser": browser_automation,
            "current_action": 0,
            "start_time": time.time()
        }
        
        successful_actions = 0
        failed_actions = 0
        action_results = []
        
        # Execute each action on the real browser
        for i, action in enumerate(session["action_plan"]["actions"]):
            active_executions[session_id]["current_action"] = i
            
            result = browser_automation.execute_action(action, session_id)
            action_results.append({
                "action": action,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            if result["status"] == "success":
                successful_actions += 1
            else:
                failed_actions += 1
                # Continue with other actions even if one fails
            
            # Add delay between actions for stability
            time.sleep(2)
        
        # Update session with results
        session["status"] = "completed"
        session["completed_at"] = datetime.utcnow().isoformat()
        session["successful_actions"] = successful_actions
        session["failed_actions"] = failed_actions
        session["total_duration"] = int(time.time() - active_executions[session_id]["start_time"])
        session["action_results"] = action_results
        
        print(f"🎉 REAL test completed: {successful_actions} successful, {failed_actions} failed")
        
        # Keep browser open for a moment to see results
        print("🔍 Keeping browser open for 10 seconds to view results...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ REAL test execution failed: {e}")
        session["status"] = "failed"
        session["error_summary"] = str(e)
        session["completed_at"] = datetime.utcnow().isoformat()
        
    finally:
        # Cleanup browser
        if browser_automation:
            browser_automation.cleanup()
        if session_id in active_executions:
            del active_executions[session_id]

class RequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        
        if path == '/health':
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "selenium_available": SELENIUM_AVAILABLE,
                "active_sessions": len(active_executions),
                "total_sessions": len(test_sessions),
                "mode": "REAL_BROWSER_AUTOMATION_SELENIUM",
                "timestamp": datetime.utcnow().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path.startswith('/api/tests/') and len(path.split('/')) == 4:
            # Get test results
            session_id = path.split('/')[-1]
            
            if session_id in test_sessions:
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                session = test_sessions[session_id]
                execution_status = {}
                
                if session_id in active_executions:
                    exec_info = active_executions[session_id]
                    execution_status = {
                        "current_action": exec_info["current_action"],
                        "progress": (exec_info["current_action"] / len(session["action_plan"]["actions"])) * 100
                    }
                
                response = {
                    "session": session,
                    "execution_status": execution_status
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        
        # Read request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
        except:
            self.send_response(400)
            self.end_headers()
            return
        
        if path == '/api/tests/create':
            # Create test
            session_id = str(uuid.uuid4())
            
            # Generate intelligent action plan
            actions = generate_intelligent_action_plan(data["prompt"], data["website_url"])
            
            action_plan = {
                "id": str(uuid.uuid4()),
                "website_url": data["website_url"],
                "actions": actions,
                "confidence": 0.95,
                "reasoning": "Generated for REAL browser automation using Selenium with intelligent element detection",
                "estimated_duration": len(actions) * 5,
                "risk_level": "low"
            }
            
            # Store session
            test_sessions[session_id] = {
                "id": session_id,
                "website_url": data["website_url"],
                "original_prompt": data["prompt"],
                "action_plan": action_plan,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "total_actions": len(actions),
                "successful_actions": 0,
                "failed_actions": 0,
                "screenshots": []
            }
            
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "session_id": session_id,
                "action_plan": action_plan,
                "estimated_duration": action_plan["estimated_duration"],
                "risk_assessment": action_plan["risk_level"]
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/tests/execute':
            # Execute test with REAL browser
            session_id = data["session_id"]
            
            if session_id not in test_sessions:
                self.send_response(404)
                self.end_headers()
                return
            
            session = test_sessions[session_id]
            
            if session["status"] != "pending":
                self.send_response(400)
                self.end_headers()
                return
            
            # Start REAL execution in background thread
            session["status"] = "running"
            session["started_at"] = datetime.utcnow().isoformat()
            
            thread = threading.Thread(target=execute_real_test_session, args=(session_id,))
            thread.daemon = True
            thread.start()
            
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "session_id": session_id,
                "status": "running",
                "message": "🚀 REAL Chrome browser will open shortly and perform your actions!"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    """Run the HTTP server"""
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    
    print("🚀 Starting REAL Browser Automation Server (Selenium)")
    print("🌐 This version will actually open Chrome and perform actions!")
    print(f"📡 Server running on http://localhost:8000")
    print(f"🔧 Selenium available: {SELENIUM_AVAILABLE}")
    print("🔥 REAL browser automation mode enabled!")
    print()
    
    if not SELENIUM_AVAILABLE:
        print("⚠️  To enable real browser automation:")
        print("   pip install selenium")
        print("   Make sure Chrome is installed")
        print()
    else:
        print("✅ Ready to launch real Chrome browser and perform actual automation!")
        print("🎯 When you run a test, a Chrome window will open and perform your actions!")
        print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()
