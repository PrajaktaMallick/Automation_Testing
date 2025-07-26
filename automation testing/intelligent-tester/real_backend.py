#!/usr/bin/env python3
"""
Real backend with Playwright integration for actual browser automation
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import asyncio
import os
import json
import uuid
from datetime import datetime
import time

# Try to import Playwright, fall back gracefully if not available
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright not available. Install with: pip install playwright")

# Create FastAPI app
app = FastAPI(
    title="Intelligent Web Tester - Real Execution",
    description="AI-powered web testing with actual browser automation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create screenshots directory
os.makedirs("screenshots", exist_ok=True)
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

# Global storage
test_sessions = {}
active_executions = {}

# Models
class CreateTestRequest(BaseModel):
    website_url: str
    prompt: str
    context: Optional[Dict[str, Any]] = None

class ExecuteTestRequest(BaseModel):
    session_id: str
    options: Optional[Dict[str, Any]] = None

# Browser automation class
class BrowserAutomation:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
    
    async def initialize(self):
        """Initialize Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright not available. Please install: pip install playwright && playwright install")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Set to True for headless mode
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        self.page = await context.new_page()
        
    async def cleanup(self):
        """Clean up browser resources"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def execute_action(self, action, session_id):
        """Execute a single action"""
        action_type = action["type"]
        target = action["target"]
        value = action.get("value", "")
        
        try:
            if action_type == "navigate":
                await self.page.goto(target, wait_until="networkidle")
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
                        if await element.count() > 0:
                            break
                    except:
                        continue
                
                if element and await element.count() > 0:
                    await element.click(timeout=10000)
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
                        if await element.count() > 0:
                            break
                    except:
                        continue
                
                if element and await element.count() > 0:
                    await element.clear()
                    await element.fill(value)
                    result = f"Typed '{value}' into {target}"
                else:
                    raise Exception(f"Could not find input element: {target}")
                    
            elif action_type == "wait":
                wait_time = int(value) if value.isdigit() else 2000
                await asyncio.sleep(wait_time / 1000)
                result = f"Waited {wait_time}ms"
                
            elif action_type == "screenshot":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{session_id}_{timestamp}.png"
                filepath = os.path.join("screenshots", filename)
                await self.page.screenshot(path=filepath, full_page=True)
                result = f"Screenshot saved: /screenshots/{filename}"
                
            else:
                result = f"Action type '{action_type}' not implemented"
            
            return {"status": "success", "result": result, "error": None}
            
        except Exception as e:
            return {"status": "failed", "result": None, "error": str(e)}

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
    
    # Parse login actions
    if "login" in prompt_lower:
        actions.append({
            "type": "click",
            "description": "Click login button",
            "target": "login",
            "value": "",
            "timeout": 10000
        })
        
        if "email" in prompt_lower or "@" in prompt:
            email = "jyoti@test.com"  # Default
            # Try to extract email from prompt
            import re
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', prompt)
            if email_match:
                email = email_match.group()
            
            actions.append({
                "type": "type",
                "description": "Enter email address",
                "target": "email",
                "value": email,
                "timeout": 10000
            })
        
        if "password" in prompt_lower:
            password = "123456"  # Default
            # Try to extract password from prompt
            password_match = re.search(r'password[:\s]+([^\s,]+)', prompt, re.IGNORECASE)
            if password_match:
                password = password_match.group(1)
            
            actions.append({
                "type": "type",
                "description": "Enter password",
                "target": "password",
                "value": password,
                "timeout": 10000
            })
        
        actions.append({
            "type": "click",
            "description": "Submit login form",
            "target": "button[type='submit']",
            "value": "",
            "timeout": 10000
        })
        
        actions.append({
            "type": "wait",
            "description": "Wait for login to complete",
            "target": "time",
            "value": "3000",
            "timeout": 5000
        })
    
    # Parse search actions
    if "search" in prompt_lower:
        search_term = "headphones"  # Default
        # Try to extract search term
        search_patterns = [
            r'search for (.+?)(?:\s+and|\s+then|$)',
            r'find (.+?)(?:\s+and|\s+then|$)',
            r'look for (.+?)(?:\s+and|\s+then|$)'
        ]
        for pattern in search_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                search_term = match.group(1).strip()
                break
        
        actions.append({
            "type": "click",
            "description": "Click search box",
            "target": "input[type='search']",
            "value": "",
            "timeout": 10000
        })
        
        actions.append({
            "type": "type",
            "description": f"Search for {search_term}",
            "target": "search",
            "value": search_term,
            "timeout": 10000
        })
        
        actions.append({
            "type": "click",
            "description": "Click search button",
            "target": "search",
            "value": "",
            "timeout": 10000
        })
        
        actions.append({
            "type": "wait",
            "description": "Wait for search results",
            "target": "time",
            "value": "3000",
            "timeout": 5000
        })
    
    # Parse add to cart actions
    if "add to cart" in prompt_lower or "add first" in prompt_lower:
        actions.append({
            "type": "click",
            "description": "Click first product",
            "target": ".product:first-child, .item:first-child, [data-testid*='product']:first",
            "value": "",
            "timeout": 10000
        })
        
        actions.append({
            "type": "wait",
            "description": "Wait for product page to load",
            "target": "time",
            "value": "2000",
            "timeout": 5000
        })
        
        actions.append({
            "type": "click",
            "description": "Add to cart",
            "target": "add to cart",
            "value": "",
            "timeout": 10000
        })
    
    # Always end with screenshot
    actions.append({
        "type": "screenshot",
        "description": "Take final screenshot",
        "target": "",
        "value": "",
        "timeout": 5000
    })
    
    return actions

# Routes
@app.get("/")
async def root():
    return {
        "message": "Intelligent Web Tester - Real Execution",
        "version": "1.0.0",
        "status": "running",
        "playwright_available": PLAYWRIGHT_AVAILABLE,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "playwright_available": PLAYWRIGHT_AVAILABLE,
        "active_sessions": len(active_executions),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/tests/create")
async def create_test(request: CreateTestRequest):
    try:
        session_id = str(uuid.uuid4())
        
        # Generate action plan
        actions = generate_action_plan(request.prompt, request.website_url)
        
        action_plan = {
            "id": str(uuid.uuid4()),
            "website_url": request.website_url,
            "actions": actions,
            "confidence": 0.8,
            "reasoning": "Generated using pattern matching with real execution",
            "estimated_duration": len(actions) * 3,
            "risk_level": "low"
        }
        
        # Store session
        test_sessions[session_id] = {
            "id": session_id,
            "website_url": request.website_url,
            "original_prompt": request.prompt,
            "action_plan": action_plan,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "total_actions": len(actions),
            "successful_actions": 0,
            "failed_actions": 0,
            "screenshots": []
        }
        
        return {
            "session_id": session_id,
            "action_plan": action_plan,
            "estimated_duration": action_plan["estimated_duration"],
            "risk_assessment": action_plan["risk_level"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tests/execute")
async def execute_test(request: ExecuteTestRequest, background_tasks: BackgroundTasks):
    try:
        if request.session_id not in test_sessions:
            raise HTTPException(status_code=404, detail="Test session not found")
        
        session = test_sessions[request.session_id]
        
        if session["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Test is already {session['status']}")
        
        # Start execution in background
        background_tasks.add_task(execute_test_session, request.session_id)
        
        # Update session status
        session["status"] = "running"
        session["started_at"] = datetime.utcnow().isoformat()
        
        return {
            "session_id": request.session_id,
            "status": "running",
            "message": "Real test execution started!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def execute_test_session(session_id: str):
    """Execute test session with real browser automation"""
    session = test_sessions[session_id]
    browser_automation = None
    
    try:
        # Initialize browser
        browser_automation = BrowserAutomation()
        await browser_automation.initialize()
        
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
            
            print(f"Executing action {i+1}/{len(session['action_plan']['actions'])}: {action['description']}")
            
            result = await browser_automation.execute_action(action, session_id)
            
            if result["status"] == "success":
                successful_actions += 1
                print(f"✅ {result['result']}")
            else:
                failed_actions += 1
                print(f"❌ {result['error']}")
            
            # Add small delay between actions
            await asyncio.sleep(1)
        
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
            await browser_automation.cleanup()
        if session_id in active_executions:
            del active_executions[session_id]

@app.get("/api/tests/{session_id}")
async def get_test_results(session_id: str):
    if session_id not in test_sessions:
        raise HTTPException(status_code=404, detail="Test session not found")
    
    session = test_sessions[session_id]
    
    # Get execution status
    execution_status = {}
    if session_id in active_executions:
        exec_info = active_executions[session_id]
        execution_status = {
            "current_action": exec_info["current_action"],
            "progress": (exec_info["current_action"] / len(session["action_plan"]["actions"])) * 100
        }
    
    return {
        "session": session,
        "execution_status": execution_status
    }

@app.get("/api/tests")
async def list_tests():
    sessions = list(test_sessions.values())
    return {
        "sessions": sessions,
        "total": len(sessions)
    }

if __name__ == "__main__":
    print("🚀 Starting Intelligent Web Tester with REAL Browser Automation")
    print("🌐 This version will actually execute actions on websites!")
    print("⚠️  Make sure Playwright is installed: pip install playwright && playwright install")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
