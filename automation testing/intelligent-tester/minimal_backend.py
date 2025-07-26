#!/usr/bin/env python3
"""
Minimal backend that actually opens a browser and performs actions
"""
import asyncio
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Try to import Playwright
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright not available. Install with: pip install playwright")

# Global storage
test_sessions = {}
active_executions = {}

class BrowserAutomation:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
    
    def initialize(self):
        """Initialize Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright not available")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False,  # Show browser
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        self.page = context.new_page()
        
    def cleanup(self):
        """Clean up browser resources"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def execute_action(self, action, session_id):
        """Execute a single action"""
        action_type = action["type"]
        target = action["target"]
        value = action.get("value", "")
        
        try:
            print(f"🔄 Executing: {action['description']}")
            
            if action_type == "navigate":
                self.page.goto(target, wait_until="networkidle")
                result = f"Navigated to {target}"
                
            elif action_type == "click":
                # Try multiple selector strategies
                selectors = [target]
                if ":" not in target:  # If not a complex selector, add alternatives
                    selectors.extend([
                        f"button:has-text('{target}')",
                        f"a:has-text('{target}')",
                        f"[aria-label*='{target}']",
                        f"*:has-text('{target}'):visible"
                    ])
                
                element = None
                for selector in selectors:
                    try:
                        element = self.page.locator(selector).first
                        if element.count() > 0:
                            break
                    except:
                        continue
                
                if element and element.count() > 0:
                    element.click(timeout=10000)
                    result = f"Clicked element: {target}"
                else:
                    raise Exception(f"Could not find element: {target}")
                    
            elif action_type == "type":
                # Try multiple input selector strategies
                selectors = [target]
                if "input" not in target.lower():
                    selectors.extend([
                        f"input[placeholder*='{target}']",
                        f"input[name*='{target.lower()}']",
                        f"input[type='text']",
                        f"input[type='email']",
                        f"input[type='password']",
                        "input:visible"
                    ])
                
                element = None
                for selector in selectors:
                    try:
                        element = self.page.locator(selector).first
                        if element.count() > 0:
                            break
                    except:
                        continue
                
                if element and element.count() > 0:
                    element.clear()
                    element.fill(value)
                    result = f"Typed '{value}' into {target}"
                else:
                    raise Exception(f"Could not find input element: {target}")
                    
            elif action_type == "wait":
                wait_time = int(value) if value.isdigit() else 2000
                time.sleep(wait_time / 1000)
                result = f"Waited {wait_time}ms"
                
            elif action_type == "screenshot":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{session_id}_{timestamp}.png"
                filepath = os.path.join("screenshots", filename)
                os.makedirs("screenshots", exist_ok=True)
                self.page.screenshot(path=filepath, full_page=True)
                result = f"Screenshot saved: /screenshots/{filename}"
                
            else:
                result = f"Action type '{action_type}' not implemented"
            
            print(f"✅ {result}")
            return {"status": "success", "result": result, "error": None}
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ {error_msg}")
            return {"status": "failed", "result": None, "error": error_msg}

def generate_action_plan(prompt, website_url):
    """Generate action plan from natural language prompt"""
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
        "description": "Wait for page to load",
        "target": "time",
        "value": "3000",
        "timeout": 5000
    })
    
    # Parse common actions from prompt
    if "screenshot" in prompt_lower:
        actions.append({
            "type": "screenshot",
            "description": "Take screenshot",
            "target": "",
            "value": "",
            "timeout": 5000
        })
    
    # Always end with screenshot if not already added
    if not any(action["type"] == "screenshot" for action in actions):
        actions.append({
            "type": "screenshot",
            "description": "Take final screenshot",
            "target": "",
            "value": "",
            "timeout": 5000
        })
    
    return actions

def execute_test_session(session_id):
    """Execute test session with real browser automation"""
    session = test_sessions[session_id]
    browser_automation = None
    
    try:
        print(f"🚀 Starting test execution for session {session_id}")
        
        # Initialize browser
        browser_automation = BrowserAutomation()
        browser_automation.initialize()
        
        active_executions[session_id] = {
            "browser": browser_automation,
            "current_action": 0,
            "start_time": time.time()
        }
        
        successful_actions = 0
        failed_actions = 0
        
        # Execute each action
        for i, action in enumerate(session["action_plan"]["actions"]):
            active_executions[session_id]["current_action"] = i
            
            result = browser_automation.execute_action(action, session_id)
            
            if result["status"] == "success":
                successful_actions += 1
            else:
                failed_actions += 1
            
            # Add small delay between actions
            time.sleep(1)
        
        # Update session with results
        session["status"] = "completed"
        session["completed_at"] = datetime.utcnow().isoformat()
        session["successful_actions"] = successful_actions
        session["failed_actions"] = failed_actions
        session["total_duration"] = int(time.time() - active_executions[session_id]["start_time"])
        
        print(f"🎉 Test completed: {successful_actions} successful, {failed_actions} failed")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        session["status"] = "failed"
        session["error_summary"] = str(e)
        session["completed_at"] = datetime.utcnow().isoformat()
        
    finally:
        # Cleanup
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
        self.send_header('Access-Control-Allow-Origin', '*')
        
        if path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "playwright_available": PLAYWRIGHT_AVAILABLE,
                "active_sessions": len(active_executions),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path.startswith('/api/tests/') and len(path.split('/')) == 4:
            # Get test results
            session_id = path.split('/')[-1]
            
            if session_id in test_sessions:
                self.send_response(200)
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
            
            # Generate action plan
            actions = generate_action_plan(data["prompt"], data["website_url"])
            
            action_plan = {
                "id": str(uuid.uuid4()),
                "website_url": data["website_url"],
                "actions": actions,
                "confidence": 0.8,
                "reasoning": "Generated using pattern matching with real execution",
                "estimated_duration": len(actions) * 3,
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
            
            self.send_response(200)
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
            # Execute test
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
            
            # Start execution in background thread
            session["status"] = "running"
            session["started_at"] = datetime.utcnow().isoformat()
            
            thread = threading.Thread(target=execute_test_session, args=(session_id,))
            thread.daemon = True
            thread.start()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "session_id": session_id,
                "status": "running",
                "message": "Real test execution started!"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    """Run the HTTP server"""
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    
    print("🚀 Starting Intelligent Web Tester with REAL Browser Automation")
    print("🌐 This version will actually execute actions on websites!")
    print(f"📡 Server running on http://localhost:8000")
    print(f"🎭 Playwright available: {PLAYWRIGHT_AVAILABLE}")
    print()
    
    if not PLAYWRIGHT_AVAILABLE:
        print("⚠️  To enable real browser automation:")
        print("   pip install playwright")
        print("   playwright install")
        print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()
