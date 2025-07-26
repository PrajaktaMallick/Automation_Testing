#!/usr/bin/env python3
"""
Simple backend server for testing the intelligent tester
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import os
import json
import uuid
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Intelligent Web Tester",
    description="AI-powered web testing with natural language prompts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for screenshots
if os.path.exists("screenshots"):
    app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

# Simple in-memory storage
test_sessions = {}

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

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Intelligent Web Tester API",
        "version": "1.0.0",
        "status": "running",
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
            "browser": "ready"
        }
    }

@app.post("/api/tests/create", response_model=CreateTestResponse)
async def create_test(request: CreateTestRequest):
    """Create a new test from natural language prompt"""
    try:
        session_id = str(uuid.uuid4())
        
        # Simple action plan generation (fallback logic)
        actions = []
        prompt_lower = request.prompt.lower()
        
        # Always start with navigation
        actions.append({
            "type": "navigate",
            "description": f"Navigate to {request.website_url}",
            "target": request.website_url,
            "value": "",
            "timeout": 30000,
            "screenshot": True
        })
        
        # Parse common actions from prompt
        if "login" in prompt_lower:
            actions.append({
                "type": "click",
                "description": "Click login button",
                "target": "button:has-text('login'), a:has-text('login'), .login",
                "value": "",
                "timeout": 30000
            })
            
            if "email" in prompt_lower or "@" in request.prompt:
                actions.append({
                    "type": "type",
                    "description": "Enter email",
                    "target": "input[type='email'], input[name*='email']",
                    "value": "jyoti@test.com",
                    "timeout": 30000
                })
            
            if "password" in prompt_lower:
                actions.append({
                    "type": "type",
                    "description": "Enter password",
                    "target": "input[type='password'], input[name*='password']",
                    "value": "123456",
                    "timeout": 30000
                })
                
                actions.append({
                    "type": "click",
                    "description": "Click login submit",
                    "target": "button[type='submit'], input[type='submit']",
                    "value": "",
                    "timeout": 30000,
                    "screenshot": True
                })
        
        if "search" in prompt_lower:
            # Extract search term
            search_term = "headphones"  # default
            if "for " in prompt_lower:
                parts = request.prompt.split("for ")
                if len(parts) > 1:
                    search_term = parts[1].split(" ")[0].strip()
            
            actions.append({
                "type": "click",
                "description": "Click search box",
                "target": "input[type='search'], input[name*='search'], .search-input",
                "value": "",
                "timeout": 30000
            })
            
            actions.append({
                "type": "type",
                "description": f"Search for {search_term}",
                "target": "input[type='search'], input[name*='search'], .search-input",
                "value": search_term,
                "timeout": 30000
            })
            
            actions.append({
                "type": "click",
                "description": "Click search button",
                "target": "button[type='submit'], .search-btn, button:has-text('search')",
                "value": "",
                "timeout": 30000,
                "screenshot": True
            })
        
        if "add to cart" in prompt_lower or "add first" in prompt_lower:
            actions.append({
                "type": "click",
                "description": "Click first product",
                "target": ".product:first-child, .item:first-child, [data-testid*='product']:first",
                "value": "",
                "timeout": 30000
            })
            
            actions.append({
                "type": "click",
                "description": "Add to cart",
                "target": "button:has-text('add to cart'), .add-to-cart, [data-testid*='cart']",
                "value": "",
                "timeout": 30000,
                "screenshot": True
            })
        
        # Always end with a screenshot
        actions.append({
            "type": "screenshot",
            "description": "Take final screenshot",
            "target": "",
            "value": "",
            "timeout": 5000,
            "screenshot": True
        })
        
        action_plan = {
            "id": str(uuid.uuid4()),
            "website_url": request.website_url,
            "actions": actions,
            "confidence": 0.8,
            "reasoning": "Generated using fallback pattern matching",
            "estimated_duration": len(actions) * 5,
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
            "failed_actions": 0
        }
        
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
    """Execute a test session (mock implementation)"""
    try:
        if request.session_id not in test_sessions:
            raise HTTPException(status_code=404, detail="Test session not found")
        
        session = test_sessions[request.session_id]
        
        if session["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Test is already {session['status']}")
        
        # Mock execution - just update status
        session["status"] = "running"
        session["started_at"] = datetime.utcnow().isoformat()
        
        # Simulate completion after a short delay
        import asyncio
        async def complete_test():
            await asyncio.sleep(2)  # Simulate execution time
            session["status"] = "completed"
            session["completed_at"] = datetime.utcnow().isoformat()
            session["successful_actions"] = len(session["action_plan"]["actions"])
            session["failed_actions"] = 0
        
        # Start background task
        asyncio.create_task(complete_test())
        
        return ExecuteTestResponse(
            session_id=request.session_id,
            status="running",
            message="Test execution started (mock)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tests/{session_id}")
async def get_test_results(session_id: str):
    """Get test results for a session"""
    try:
        if session_id not in test_sessions:
            raise HTTPException(status_code=404, detail="Test session not found")
        
        session = test_sessions[session_id]
        
        # Mock execution result
        execution_result = {
            "session_id": session_id,
            "status": session["status"],
            "success_rate": 1.0 if session["status"] == "completed" else 0.0,
            "total_duration": 30,  # Mock duration
            "action_results": [
                {
                    "id": str(uuid.uuid4()),
                    "type": action["type"],
                    "description": action["description"],
                    "status": "success" if session["status"] == "completed" else "pending",
                    "execution_time": 5000,
                    "screenshot_path": f"/screenshots/mock_{i}.png" if action.get("screenshot") else None
                }
                for i, action in enumerate(session["action_plan"]["actions"])
            ],
            "screenshots": [f"/screenshots/mock_{i}.png" for i in range(3)],
            "summary": f"Mock test execution for {session['website_url']}",
            "recommendations": ["This is a mock implementation", "Install full dependencies for real testing"]
        }
        
        return {
            "session": session,
            "execution_result": execution_result,
            "metrics": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tests")
async def list_tests(page: int = 1, per_page: int = 20):
    """List all test sessions"""
    try:
        sessions = list(test_sessions.values())
        total = len(sessions)
        
        # Simple pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_sessions = sessions[start:end]
        
        return {
            "sessions": paginated_sessions,
            "total": total,
            "page": page,
            "per_page": per_page
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    try:
        total_tests = len(test_sessions)
        completed_tests = sum(1 for s in test_sessions.values() if s["status"] == "completed")
        running_tests = sum(1 for s in test_sessions.values() if s["status"] == "running")
        
        return {
            "total_tests": total_tests,
            "successful_tests": completed_tests,
            "failed_tests": 0,
            "running_tests": running_tests,
            "average_duration": 30,
            "success_rate": 1.0 if total_tests > 0 else 0.0,
            "most_tested_sites": [
                {"url": "https://example.com", "count": 1}
            ],
            "common_failures": []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Intelligent Web Tester (Simple Mode)")
    print("📝 Note: This is a simplified version for demonstration")
    print("🔧 Install full dependencies for complete functionality")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
