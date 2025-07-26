#!/usr/bin/env python3
"""
Working backend for the intelligent tester using FastAPI
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import json
import uuid
from datetime import datetime
import asyncio

# Create FastAPI app
app = FastAPI(
    title="Intelligent Web Tester",
    description="AI-powered web testing with natural language prompts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

def generate_action_plan(prompt: str, website_url: str):
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
        "description": "Wait for page to load",
        "target": "time",
        "value": "3000",
        "timeout": 5000
    })
    
    # Parse different actions based on prompt
    if "search" in prompt_lower:
        actions.append({
            "type": "fill",
            "description": "Fill search field",
            "target": "input[type='search'], input[name*='search'], input[placeholder*='search'], .search-input",
            "value": "search term",
            "timeout": 10000
        })
        actions.append({
            "type": "click",
            "description": "Click search button",
            "target": "button[type='submit'], .search-button, input[type='submit']",
            "value": "",
            "timeout": 10000
        })
    
    if "screenshot" in prompt_lower:
        actions.append({
            "type": "screenshot",
            "description": "Take screenshot",
            "target": "page",
            "value": "",
            "timeout": 5000
        })
    
    if "click" in prompt_lower:
        actions.append({
            "type": "click",
            "description": "Click element",
            "target": "button, a, .clickable",
            "value": "",
            "timeout": 10000
        })
    
    return {
        "actions": actions,
        "total_steps": len(actions),
        "estimated_duration": len(actions) * 5,  # 5 seconds per action
        "risk_level": "low"
    }

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
        
        # Generate action plan
        action_plan = generate_action_plan(request.prompt, request.website_url)
        
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
    """Execute a test session"""
    try:
        if request.session_id not in test_sessions:
            raise HTTPException(status_code=404, detail="Test session not found")
        
        session = test_sessions[request.session_id]
        
        if session["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Test is already {session['status']}")
        
        # Update session status
        session["status"] = "running"
        session["started_at"] = datetime.utcnow().isoformat()
        
        # Simulate execution (in a real implementation, this would trigger browser automation)
        # For now, we'll just mark it as completed after a short delay
        asyncio.create_task(simulate_execution(request.session_id))
        
        return ExecuteTestResponse(
            session_id=request.session_id,
            status="running",
            message="Test execution started"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def simulate_execution(session_id: str):
    """Simulate test execution"""
    await asyncio.sleep(5)  # Simulate execution time
    
    if session_id in test_sessions:
        test_sessions[session_id]["status"] = "completed"
        test_sessions[session_id]["completed_at"] = datetime.utcnow().isoformat()
        test_sessions[session_id]["result"] = {
            "success": True,
            "message": "Test completed successfully",
            "screenshots": [],
            "actions_completed": len(test_sessions[session_id]["action_plan"]["actions"])
        }

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
                "duration": 5,  # Simulated
                "actions_completed": session["action_plan"]["total_steps"],
                "success_rate": 100
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
        
        return {
            "session_id": session_id,
            "status": session["status"],
            "progress": 100 if session["status"] == "completed" else 50 if session["status"] == "running" else 0,
            "current_action": "Executing actions..." if session["status"] == "running" else None,
            "completed_actions": session["action_plan"]["total_steps"] if session["status"] == "completed" else 0,
            "total_actions": session["action_plan"]["total_steps"],
            "estimated_remaining": 0 if session["status"] == "completed" else 30
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Intelligent Web Tester Backend")
    print("📡 Server will run on http://localhost:8000")
    print("✅ Ready to process test requests!")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
