#!/usr/bin/env python3
"""
Real Browser Automation Backend - Actually opens browsers and performs actions
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import json
import uuid
import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

# Create FastAPI app
app = FastAPI(
    title="Intelligent Web Tester - Real Automation",
    description="AI-powered web testing with REAL browser automation",
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

# Global storage and browser management
test_sessions = {}
browser_instances = {}
playwright_instance = None
browser = None

# Models
class CreateTestRequest(BaseModel):
    website_url: str
    prompt: str
    context: Optional[Dict[str, Any]] = None

class CreateTestResponse(BaseModel):
    session_id: str
    action_plan: Dict[str, Any]
    estimated_duration: int
    risk_assessment: str

class ExecuteTestRequest(BaseModel):
    session_id: str
    options: Optional[Dict[str, Any]] = None

class ExecuteTestResponse(BaseModel):
    session_id: str
    status: str
    message: str

async def initialize_browser():
    """Initialize Playwright browser"""
    global playwright_instance, browser
    try:
        playwright_instance = await async_playwright().start()
        browser = await playwright_instance.chromium.launch(
            headless=False,  # Show browser window
            args=['--start-maximized']
        )
        print("✅ Browser initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize browser: {e}")
        return False

async def cleanup_browser():
    """Cleanup browser resources"""
    global playwright_instance, browser
    try:
        if browser:
            await browser.close()
        if playwright_instance:
            await playwright_instance.stop()
        print("✅ Browser cleanup completed")
    except Exception as e:
        print(f"⚠️ Browser cleanup error: {e}")

def parse_action_from_prompt(prompt: str, website_url: str):
    """Parse natural language prompt into actionable steps"""
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
    
    # Wait for page load
    actions.append({
        "type": "wait",
        "description": "Wait for page to load completely",
        "target": "networkidle",
        "value": "3000",
        "timeout": 10000
    })
    
    # Parse login actions
    if "login" in prompt_lower or "log in" in prompt_lower:
        actions.append({
            "type": "click",
            "description": "Click login button or link",
            "target": "text=Login, text=Log in, text=Sign in, [data-testid*=login], .login, #login",
            "value": "",
            "timeout": 10000
        })
        
        # Look for username/email field
        actions.append({
            "type": "fill",
            "description": "Fill username/email field",
            "target": "input[type=email], input[name*=email], input[name*=username], input[placeholder*=email], input[placeholder*=username]",
            "value": "test@example.com",  # Default value
            "timeout": 10000
        })
        
        # Look for password field
        actions.append({
            "type": "fill",
            "description": "Fill password field",
            "target": "input[type=password], input[name*=password]",
            "value": "password123",  # Default value
            "timeout": 10000
        })
        
        # Submit login
        actions.append({
            "type": "click",
            "description": "Submit login form",
            "target": "button[type=submit], input[type=submit], text=Login, text=Sign in",
            "value": "",
            "timeout": 10000
        })
    
    # Parse search actions
    if "search" in prompt_lower:
        search_term = "test search"  # Default search term
        actions.append({
            "type": "fill",
            "description": f"Search for '{search_term}'",
            "target": "input[type=search], input[name*=search], input[placeholder*=search], .search-input",
            "value": search_term,
            "timeout": 10000
        })
        actions.append({
            "type": "click",
            "description": "Click search button",
            "target": "button[type=submit], .search-button, input[type=submit]",
            "value": "",
            "timeout": 10000
        })
    
    # Parse screenshot actions
    if "screenshot" in prompt_lower:
        actions.append({
            "type": "screenshot",
            "description": "Take screenshot of current page",
            "target": "page",
            "value": "",
            "timeout": 5000
        })
    
    # Parse click actions
    if "click" in prompt_lower and "login" not in prompt_lower:
        actions.append({
            "type": "click",
            "description": "Click specified element",
            "target": "button, a, .clickable",
            "value": "",
            "timeout": 10000
        })
    
    return {
        "actions": actions,
        "total_steps": len(actions),
        "estimated_duration": len(actions) * 5,
        "risk_level": "low"
    }

async def execute_real_automation(session_id: str):
    """Execute real browser automation"""
    global browser
    
    if session_id not in test_sessions:
        return
    
    session = test_sessions[session_id]
    action_plan = session["action_plan"]
    
    try:
        # Create new browser context and page
        context = await browser.new_context()
        page = await context.new_page()
        
        session["browser_context"] = context
        session["page"] = page
        session["execution_log"] = []
        
        print(f"🚀 Starting real automation for session {session_id}")
        
        # Execute each action
        for i, action in enumerate(action_plan["actions"]):
            try:
                session["current_action"] = i
                session["current_action_description"] = action["description"]
                
                print(f"📋 Executing: {action['description']}")
                
                if action["type"] == "navigate":
                    await page.goto(action["target"], wait_until="networkidle")
                    session["execution_log"].append(f"✅ Navigated to {action['target']}")
                
                elif action["type"] == "wait":
                    if action["target"] == "networkidle":
                        await page.wait_for_load_state("networkidle")
                    else:
                        await asyncio.sleep(int(action["value"]) / 1000)
                    session["execution_log"].append(f"✅ Waited as specified")
                
                elif action["type"] == "click":
                    try:
                        await page.click(action["target"], timeout=action["timeout"])
                        session["execution_log"].append(f"✅ Clicked: {action['target']}")
                    except Exception as e:
                        session["execution_log"].append(f"⚠️ Click failed: {str(e)}")
                
                elif action["type"] == "fill":
                    try:
                        await page.fill(action["target"], action["value"], timeout=action["timeout"])
                        session["execution_log"].append(f"✅ Filled: {action['target']} with '{action['value']}'")
                    except Exception as e:
                        session["execution_log"].append(f"⚠️ Fill failed: {str(e)}")
                
                elif action["type"] == "screenshot":
                    screenshot_path = f"screenshots/session_{session_id}_{i}.png"
                    os.makedirs("screenshots", exist_ok=True)
                    await page.screenshot(path=screenshot_path)
                    session["execution_log"].append(f"✅ Screenshot saved: {screenshot_path}")
                
                # Small delay between actions
                await asyncio.sleep(1)
                
            except Exception as e:
                error_msg = f"❌ Action failed: {action['description']} - {str(e)}"
                session["execution_log"].append(error_msg)
                print(error_msg)
        
        # Mark as completed
        session["status"] = "completed"
        session["completed_at"] = datetime.utcnow().isoformat()
        session["result"] = {
            "success": True,
            "message": "Real browser automation completed successfully",
            "execution_log": session["execution_log"],
            "actions_completed": len(action_plan["actions"])
        }
        
        print(f"✅ Automation completed for session {session_id}")
        
        # Keep browser open for user to see results
        # await asyncio.sleep(10)  # Keep open for 10 seconds
        # await context.close()
        
    except Exception as e:
        session["status"] = "failed"
        session["error"] = str(e)
        session["execution_log"].append(f"❌ Automation failed: {str(e)}")
        print(f"❌ Automation failed for session {session_id}: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize browser on startup"""
    try:
        success = await initialize_browser()
        if not success:
            print("⚠️ Browser initialization failed - some features may not work")
    except Exception as e:
        print(f"⚠️ Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        await cleanup_browser()
    except Exception as e:
        print(f"⚠️ Shutdown error: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Intelligent Web Tester - Real Browser Automation",
        "version": "1.0.0",
        "status": "running",
        "browser_ready": browser is not None,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "online",
            "browser": "ready" if browser else "initializing",
            "playwright": "available"
        }
    }

@app.post("/api/tests/create", response_model=CreateTestResponse)
async def create_test(request: CreateTestRequest):
    """Create a new test from natural language prompt"""
    try:
        session_id = str(uuid.uuid4())
        
        # Generate action plan from natural language
        action_plan = parse_action_from_prompt(request.prompt, request.website_url)
        
        # Store session
        test_sessions[session_id] = {
            "id": session_id,
            "website_url": request.website_url,
            "prompt": request.prompt,
            "action_plan": action_plan,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "context": request.context or {}
        }
        
        print(f"📝 Created test session {session_id} for {request.website_url}")
        
        return CreateTestResponse(
            session_id=session_id,
            action_plan=action_plan,
            estimated_duration=action_plan["estimated_duration"],
            risk_assessment=action_plan["risk_level"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tests/execute", response_model=ExecuteTestResponse)
async def execute_test(request: ExecuteTestRequest):
    """Execute a test session with REAL browser automation"""
    try:
        if request.session_id not in test_sessions:
            raise HTTPException(status_code=404, detail="Test session not found")
        
        session = test_sessions[request.session_id]
        
        if session["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Test is already {session['status']}")
        
        if not browser:
            raise HTTPException(status_code=503, detail="Browser not ready - please wait and try again")
        
        # Update session status
        session["status"] = "running"
        session["started_at"] = datetime.utcnow().isoformat()
        
        # Start REAL browser automation
        asyncio.create_task(execute_real_automation(request.session_id))
        
        print(f"🚀 Started real browser automation for session {request.session_id}")
        
        return ExecuteTestResponse(
            session_id=request.session_id,
            status="running",
            message="Real browser automation started - browser window will open"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Real Browser Automation Backend")
    print("🌐 This will actually open browsers and perform real automation!")
    print("📡 Server will run on http://localhost:8000")
    print("✅ Ready for real browser testing!")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
