"""
FastAPI backend for intelligent web tester
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

from .config import settings
from .models.test_models import (
    CreateTestRequest, CreateTestResponse, ExecuteTestRequest, ExecuteTestResponse,
    GetTestResultsResponse, ListTestsResponse, TestSession, TestStatus
)
from .services.test_orchestrator import TestOrchestrator
from .services.session_manager import SessionManager
from .utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global instances
test_orchestrator = TestOrchestrator()
session_manager = SessionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Intelligent Web Tester API")
    
    # Initialize services
    await test_orchestrator.initialize()
    await session_manager.initialize()
    
    yield
    
    # Cleanup
    await test_orchestrator.cleanup()
    await session_manager.cleanup()
    logger.info("Intelligent Web Tester API stopped")


# Create FastAPI app
app = FastAPI(
    title="Intelligent Web Tester",
    description="AI-powered web testing with natural language prompts",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for screenshots
if os.path.exists(settings.SCREENSHOTS_DIR):
    app.mount("/screenshots", StaticFiles(directory=settings.SCREENSHOTS_DIR), name="screenshots")


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
            "orchestrator": test_orchestrator.is_healthy(),
            "session_manager": session_manager.is_healthy()
        }
    }


@app.post("/api/tests/create", response_model=CreateTestResponse)
async def create_test(request: CreateTestRequest):
    """
    Create a new test from natural language prompt
    """
    try:
        logger.info(f"Creating test for URL: {request.website_url}")
        
        # Create test session
        session = await test_orchestrator.create_test_session(
            website_url=request.website_url,
            prompt=request.prompt,
            context=request.context
        )
        
        return CreateTestResponse(
            session_id=session.id,
            action_plan=session.action_plan,
            estimated_duration=session.action_plan.estimated_duration,
            risk_assessment=session.action_plan.risk_level
        )
        
    except Exception as e:
        logger.error(f"Failed to create test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tests/execute", response_model=ExecuteTestResponse)
async def execute_test(request: ExecuteTestRequest, background_tasks: BackgroundTasks):
    """
    Execute a test session
    """
    try:
        session = await session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Test session not found")
        
        if session.status != TestStatus.PENDING:
            raise HTTPException(status_code=400, detail=f"Test is already {session.status}")
        
        # Start execution in background
        background_tasks.add_task(
            test_orchestrator.execute_test_session,
            request.session_id,
            request.options or {}
        )
        
        # Update session status
        await session_manager.update_session_status(request.session_id, TestStatus.RUNNING)
        
        return ExecuteTestResponse(
            session_id=request.session_id,
            status=TestStatus.RUNNING,
            message="Test execution started"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tests/{session_id}", response_model=GetTestResultsResponse)
async def get_test_results(session_id: str):
    """
    Get test results for a session
    """
    try:
        session = await session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Test session not found")
        
        execution_result = await test_orchestrator.get_execution_result(session_id)
        metrics = await test_orchestrator.get_test_metrics(session_id)
        
        return GetTestResultsResponse(
            session=session,
            execution_result=execution_result,
            metrics=metrics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get test results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tests", response_model=ListTestsResponse)
async def list_tests(page: int = 1, per_page: int = 20):
    """
    List all test sessions
    """
    try:
        sessions, total = await session_manager.list_sessions(page=page, per_page=per_page)
        
        return ListTestsResponse(
            sessions=sessions,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Failed to list tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/tests/{session_id}")
async def delete_test(session_id: str):
    """
    Delete a test session
    """
    try:
        success = await session_manager.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Test session not found")
        
        return {"message": "Test session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tests/{session_id}/stop")
async def stop_test(session_id: str):
    """
    Stop a running test
    """
    try:
        success = await test_orchestrator.stop_test_execution(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Test session not found or not running")
        
        return {"message": "Test execution stopped"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tests/{session_id}/status")
async def get_test_status(session_id: str):
    """
    Get current status of a test
    """
    try:
        session = await session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Test session not found")
        
        # Get real-time execution status
        execution_status = await test_orchestrator.get_execution_status(session_id)
        
        return {
            "session_id": session_id,
            "status": session.status,
            "progress": execution_status.get("progress", 0),
            "current_action": execution_status.get("current_action"),
            "completed_actions": execution_status.get("completed_actions", 0),
            "total_actions": session.total_actions,
            "estimated_remaining": execution_status.get("estimated_remaining", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get test status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tests/{session_id}/screenshots")
async def get_test_screenshots(session_id: str):
    """
    Get all screenshots for a test session
    """
    try:
        session = await session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Test session not found")
        
        screenshots = await test_orchestrator.get_session_screenshots(session_id)
        
        return {
            "session_id": session_id,
            "screenshots": screenshots
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get screenshots: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-website")
async def analyze_website(request: dict):
    """
    Analyze a website for testing capabilities
    """
    try:
        url = request.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        analysis = await test_orchestrator.analyze_website(url)
        
        return {
            "url": url,
            "analysis": analysis.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze website: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """
    Get system statistics
    """
    try:
        stats = await session_manager.get_statistics()
        
        return {
            "total_tests": stats.get("total_tests", 0),
            "successful_tests": stats.get("successful_tests", 0),
            "failed_tests": stats.get("failed_tests", 0),
            "running_tests": stats.get("running_tests", 0),
            "average_duration": stats.get("average_duration", 0),
            "success_rate": stats.get("success_rate", 0),
            "most_tested_sites": stats.get("most_tested_sites", []),
            "common_failures": stats.get("common_failures", [])
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "internal_error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )
