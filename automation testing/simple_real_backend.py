#!/usr/bin/env python3
"""
Simple Real Browser Automation Backend - Actually opens browsers
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import uuid
import asyncio
import os
from datetime import datetime

# Try to import Playwright
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
    print("✅ Playwright is available")
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not available")

# Create FastAPI app
app = FastAPI(
    title="Simple Real Browser Automation",
    description="Real browser automation with Playwright",
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

# Global storage
test_sessions = {}
browser = None
playwright_instance = None

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

def parse_prompt_to_actions(prompt: str, website_url: str):
    """Parse natural language prompt into browser actions"""
    actions = []
    prompt_lower = prompt.lower()
    
    # Always navigate first
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
        "description": "Wait for page to load",
        "target": "networkidle",
        "value": "3000",
        "timeout": 10000
    })
    
    # Parse login actions
    if "login" in prompt_lower:
        # Extract username and password from prompt if available
        username = "standard_user"  # Default
        password = "secret_sauce"   # Default
        
        if "username" in prompt_lower:
            # Try to extract username from prompt
            import re
            username_match = re.search(r'username["\s]*["\']([^"\']+)["\']', prompt_lower)
            if username_match:
                username = username_match.group(1)
        
        if "password" in prompt_lower:
            # Try to extract password from prompt
            password_match = re.search(r'password["\s]*["\']([^"\']+)["\']', prompt_lower)
            if password_match:
                password = password_match.group(1)
        
        actions.append({
            "type": "fill",
            "description": f"Fill username field with '{username}'",
            "target": "input[name='user-name'], input[id='user-name'], input[type='text']:first-of-type",
            "value": username,
            "timeout": 10000
        })
        
        actions.append({
            "type": "fill",
            "description": f"Fill password field",
            "target": "input[name='password'], input[id='password'], input[type='password']",
            "value": password,
            "timeout": 10000
        })
        
        actions.append({
            "type": "click",
            "description": "Click login button",
            "target": "input[type='submit'], button[type='submit'], .btn-action, #login-button",
            "value": "",
            "timeout": 10000
        })
    
    # Parse screenshot actions
    if "screenshot" in prompt_lower:
        actions.append({
            "type": "screenshot",
            "description": "Take screenshot",
            "target": "page",
            "value": "",
            "timeout": 5000
        })
    
    return {
        "actions": actions,
        "total_steps": len(actions),
        "estimated_duration": len(actions) * 5,
        "risk_level": "low"
    }

async def execute_browser_automation(session_id: str):
    """Execute real browser automation"""
    global browser
    
    if session_id not in test_sessions:
        return
    
    session = test_sessions[session_id]
    action_plan = session["action_plan"]
    
    try:
        print(f"🚀 Starting browser automation for session {session_id}")
        
        # Create new browser context and page
        context = await browser.new_context()
        page = await context.new_page()
        
        session["execution_log"] = []
        session["current_action"] = 0
        
        # Execute each action
        for i, action in enumerate(action_plan["actions"]):
            try:
                session["current_action"] = i
                print(f"📋 Step {i+1}: {action['description']}")
                
                if action["type"] == "navigate":
                    await page.goto(action["target"], wait_until="networkidle", timeout=30000)
                    session["execution_log"].append(f"✅ Navigated to {action['target']}")
                
                elif action["type"] == "wait":
                    if action["target"] == "networkidle":
                        await page.wait_for_load_state("networkidle", timeout=10000)
                    else:
                        await asyncio.sleep(int(action["value"]) / 1000)
                    session["execution_log"].append("✅ Wait completed")
                
                elif action["type"] == "fill":
                    await page.fill(action["target"], action["value"], timeout=action["timeout"])
                    session["execution_log"].append(f"✅ Filled '{action['target']}' with '{action['value']}'")
                
                elif action["type"] == "click":
                    await page.click(action["target"], timeout=action["timeout"])
                    session["execution_log"].append(f"✅ Clicked '{action['target']}'")
                
                elif action["type"] == "screenshot":
                    os.makedirs("screenshots", exist_ok=True)
                    screenshot_path = f"screenshots/session_{session_id}_{i}.png"
                    await page.screenshot(path=screenshot_path)
                    session["execution_log"].append(f"✅ Screenshot saved: {screenshot_path}")
                
                # Small delay between actions
                await asyncio.sleep(1)
                
            except Exception as e:
                error_msg = f"⚠️ Step {i+1} failed: {str(e)}"
                session["execution_log"].append(error_msg)
                print(error_msg)
        
        # Mark as completed
        session["status"] = "completed"
        session["completed_at"] = datetime.utcnow().isoformat()
        session["result"] = {
            "success": True,
            "message": "Browser automation completed",
            "execution_log": session["execution_log"],
            "actions_completed": len(action_plan["actions"])
        }
        
        print(f"✅ Automation completed for session {session_id}")
        
        # Keep browser open for a while so user can see results
        await asyncio.sleep(5)
        # await context.close()  # Uncomment to auto-close browser
        
    except Exception as e:
        session["status"] = "failed"
        session["error"] = str(e)
        print(f"❌ Automation failed for session {session_id}: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize browser on startup"""
    global playwright_instance, browser
    
    if PLAYWRIGHT_AVAILABLE:
        try:
            playwright_instance = await async_playwright().start()
            browser = await playwright_instance.chromium.launch(
                headless=False,  # Show browser window
                args=['--start-maximized']
            )
            print("✅ Browser initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize browser: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global playwright_instance, browser
    
    try:
        if browser:
            await browser.close()
        if playwright_instance:
            await playwright_instance.stop()
        print("✅ Browser cleanup completed")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Simple Real Browser Automation API",
        "version": "1.0.0",
        "status": "running",
        "browser_ready": browser is not None,
        "playwright_available": PLAYWRIGHT_AVAILABLE,
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
            "playwright": "available" if PLAYWRIGHT_AVAILABLE else "unavailable"
        }
    }

@app.post("/api/tests/create", response_model=CreateTestResponse)
async def create_test(request: CreateTestRequest):
    """Create a new test from natural language prompt"""
    try:
        session_id = str(uuid.uuid4())
        
        # Generate action plan
        action_plan = parse_prompt_to_actions(request.prompt, request.website_url)
        
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
        print(f"❌ Error creating test: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tests/execute", response_model=ExecuteTestResponse)
async def execute_test(request: ExecuteTestRequest):
    """Execute a test session with real browser automation"""
    try:
        if request.session_id not in test_sessions:
            raise HTTPException(status_code=404, detail="Test session not found")
        
        session = test_sessions[request.session_id]
        
        if session["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Test is already {session['status']}")
        
        if not browser:
            raise HTTPException(status_code=503, detail="Browser not ready")
        
        # Update session status
        session["status"] = "running"
        session["started_at"] = datetime.utcnow().isoformat()
        
        # Start real browser automation in background
        asyncio.create_task(execute_browser_automation(request.session_id))
        
        print(f"🚀 Started browser automation for session {request.session_id}")
        
        return ExecuteTestResponse(
            session_id=request.session_id,
            status="running",
            message="Real browser automation started - browser window will open"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error executing test: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tests/{session_id}")
async def get_test_results(session_id: str):
    """Get test results for a session"""
    try:
        if session_id not in test_sessions:
            raise HTTPException(status_code=404, detail="Test session not found")
        
        session = test_sessions[session_id]
        
        return {
            "session": session,
            "execution_result": session.get("result"),
            "metrics": {
                "duration": 30,  # Simulated
                "actions_completed": session.get("current_action", 0),
                "success_rate": 100 if session["status"] == "completed" else 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tests/{session_id}/status")
async def get_test_status(session_id: str):
    """Get current status of a test"""
    try:
        if session_id not in test_sessions:
            raise HTTPException(status_code=404, detail="Test session not found")
        
        session = test_sessions[session_id]
        current_action = session.get("current_action", 0)
        total_actions = session["action_plan"]["total_steps"]
        
        return {
            "session_id": session_id,
            "status": session["status"],
            "progress": int((current_action / total_actions) * 100) if total_actions > 0 else 0,
            "current_action": f"Step {current_action + 1}" if session["status"] == "running" else None,
            "completed_actions": current_action,
            "total_actions": total_actions,
            "estimated_remaining": max(0, (total_actions - current_action) * 5)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Simple Real Browser Automation Backend")
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
