"""
Test orchestrator that coordinates all testing components
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

from ..models.test_models import (
    TestSession, TestStatus, ActionStatus, TestRequest, 
    ActionPlan, ExecutionResult, TestMetrics, WebsiteAnalysis
)
from ..services.action_planner import ActionPlanner
from ..services.browser_engine import BrowserEngine
from ..services.session_manager import SessionManager
from ..config import settings

logger = logging.getLogger(__name__)


class TestOrchestrator:
    """Orchestrates the entire testing process"""
    
    def __init__(self):
        self.action_planner = ActionPlanner()
        self.session_manager = SessionManager()
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.execution_lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize the orchestrator"""
        await self.session_manager.initialize()
        logger.info("Test orchestrator initialized")
    
    async def cleanup(self):
        """Cleanup resources"""
        # Stop all active executions
        for session_id in list(self.active_executions.keys()):
            await self.stop_test_execution(session_id)
        
        await self.session_manager.cleanup()
        logger.info("Test orchestrator cleaned up")
    
    def is_healthy(self) -> bool:
        """Check if orchestrator is healthy"""
        return len(self.active_executions) < settings.MAX_CONCURRENT_TESTS
    
    async def create_test_session(self, website_url: str, prompt: str, context: Optional[Dict[str, Any]] = None) -> TestSession:
        """Create a new test session with action plan"""
        try:
            # Create test request
            test_request = TestRequest(
                website_url=website_url,
                prompt=prompt,
                context=context
            )
            
            # Generate action plan
            action_plan = await self.action_planner.create_action_plan(test_request)
            
            # Create test session
            session = TestSession(
                website_url=website_url,
                original_prompt=prompt,
                action_plan=action_plan,
                total_actions=len(action_plan.actions)
            )
            
            # Save session
            await self.session_manager.save_session(session)
            
            logger.info(f"Created test session {session.id} with {len(action_plan.actions)} actions")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create test session: {e}")
            raise
    
    async def execute_test_session(self, session_id: str, options: Dict[str, Any]) -> None:
        """Execute a test session"""
        async with self.execution_lock:
            if session_id in self.active_executions:
                raise Exception("Test is already running")
            
            # Initialize execution tracking
            self.active_executions[session_id] = {
                "status": "starting",
                "current_action_index": 0,
                "start_time": datetime.utcnow(),
                "browser_engine": None,
                "cancelled": False
            }
        
        try:
            await self._execute_test_internal(session_id, options)
        except Exception as e:
            logger.error(f"Test execution failed for session {session_id}: {e}")
            await self._handle_execution_error(session_id, str(e))
        finally:
            # Cleanup execution tracking
            if session_id in self.active_executions:
                browser_engine = self.active_executions[session_id].get("browser_engine")
                if browser_engine:
                    await browser_engine.cleanup()
                del self.active_executions[session_id]
    
    async def _execute_test_internal(self, session_id: str, options: Dict[str, Any]) -> None:
        """Internal test execution logic"""
        # Get session
        session = await self.session_manager.get_session(session_id)
        if not session:
            raise Exception("Session not found")
        
        # Update session status
        session.status = TestStatus.RUNNING
        session.started_at = datetime.utcnow()
        await self.session_manager.update_session(session)
        
        # Initialize browser engine
        browser_engine = BrowserEngine()
        await browser_engine.initialize(session_id)
        
        # Store browser engine reference
        self.active_executions[session_id]["browser_engine"] = browser_engine
        self.active_executions[session_id]["status"] = "running"
        
        try:
            # Execute actions
            successful_actions = 0
            failed_actions = 0
            
            for i, action in enumerate(session.action_plan.actions):
                # Check if execution was cancelled
                if self.active_executions[session_id].get("cancelled", False):
                    logger.info(f"Test execution cancelled for session {session_id}")
                    break
                
                # Update current action
                self.active_executions[session_id]["current_action_index"] = i
                
                # Execute action with retries
                executed_action = await self._execute_action_with_retries(browser_engine, action)
                
                # Update action in session
                session.action_plan.actions[i] = executed_action
                
                # Update counters
                if executed_action.status == ActionStatus.SUCCESS:
                    successful_actions += 1
                else:
                    failed_actions += 1
                    
                    # Stop on critical action failure
                    if executed_action.critical:
                        logger.error(f"Critical action failed, stopping execution: {executed_action.description}")
                        break
                
                # Add screenshot path to session
                if executed_action.screenshot_path:
                    session.screenshots.append(executed_action.screenshot_path)
                
                # Log progress
                progress = ((i + 1) / len(session.action_plan.actions)) * 100
                logger.info(f"Session {session_id} progress: {progress:.1f}% ({i + 1}/{len(session.action_plan.actions)})")
                
                # Update session periodically
                if i % 5 == 0:  # Update every 5 actions
                    await self.session_manager.update_session(session)
            
            # Finalize session
            session.status = TestStatus.COMPLETED if failed_actions == 0 else TestStatus.FAILED
            session.completed_at = datetime.utcnow()
            session.total_duration = int((session.completed_at - session.started_at).total_seconds())
            session.successful_actions = successful_actions
            session.failed_actions = failed_actions
            
            # Generate execution summary
            session.error_summary = self._generate_error_summary(session.action_plan.actions)
            
            await self.session_manager.update_session(session)
            
            logger.info(f"Test execution completed for session {session_id}: {successful_actions} successful, {failed_actions} failed")
            
        except Exception as e:
            logger.error(f"Test execution error for session {session_id}: {e}")
            raise
        finally:
            await browser_engine.cleanup()
    
    async def _execute_action_with_retries(self, browser_engine: BrowserEngine, action) -> Any:
        """Execute action with retry logic"""
        last_error = None
        
        for attempt in range(action.retry_count):
            try:
                executed_action = await browser_engine.execute_action(action)
                if executed_action.status == ActionStatus.SUCCESS:
                    return executed_action
                
                last_error = executed_action.error_message
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Action attempt {attempt + 1} failed: {e}")
            
            # Wait before retry
            if attempt < action.retry_count - 1:
                await asyncio.sleep(1)
        
        # All retries failed
        action.status = ActionStatus.FAILED
        action.error_message = f"Failed after {action.retry_count} attempts. Last error: {last_error}"
        return action
    
    async def _handle_execution_error(self, session_id: str, error_message: str) -> None:
        """Handle execution error"""
        try:
            session = await self.session_manager.get_session(session_id)
            if session:
                session.status = TestStatus.FAILED
                session.error_summary = error_message
                session.completed_at = datetime.utcnow()
                if session.started_at:
                    session.total_duration = int((session.completed_at - session.started_at).total_seconds())
                await self.session_manager.update_session(session)
        except Exception as e:
            logger.error(f"Failed to handle execution error: {e}")
    
    def _generate_error_summary(self, actions) -> Optional[str]:
        """Generate error summary from failed actions"""
        failed_actions = [action for action in actions if action.status == ActionStatus.FAILED]
        
        if not failed_actions:
            return None
        
        error_messages = []
        for action in failed_actions:
            error_messages.append(f"- {action.description}: {action.error_message}")
        
        return f"Failed actions:\n" + "\n".join(error_messages)
    
    async def stop_test_execution(self, session_id: str) -> bool:
        """Stop a running test execution"""
        if session_id not in self.active_executions:
            return False
        
        # Mark as cancelled
        self.active_executions[session_id]["cancelled"] = True
        
        # Update session status
        session = await self.session_manager.get_session(session_id)
        if session:
            session.status = TestStatus.CANCELLED
            session.completed_at = datetime.utcnow()
            if session.started_at:
                session.total_duration = int((session.completed_at - session.started_at).total_seconds())
            await self.session_manager.update_session(session)
        
        logger.info(f"Test execution stopped for session {session_id}")
        return True
    
    async def get_execution_result(self, session_id: str) -> ExecutionResult:
        """Get execution result for a session"""
        session = await self.session_manager.get_session(session_id)
        if not session:
            raise Exception("Session not found")
        
        # Calculate success rate
        total_actions = len(session.action_plan.actions)
        success_rate = (session.successful_actions / total_actions) if total_actions > 0 else 0
        
        # Generate summary
        summary = f"Executed {total_actions} actions in {session.total_duration or 0} seconds. "
        summary += f"Success rate: {success_rate:.1%}"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(session)
        
        return ExecutionResult(
            session_id=session_id,
            status=session.status,
            success_rate=success_rate,
            total_duration=session.total_duration or 0,
            action_results=session.action_plan.actions,
            screenshots=session.screenshots,
            summary=summary,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, session: TestSession) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze failed actions
        failed_actions = [action for action in session.action_plan.actions if action.status == ActionStatus.FAILED]
        
        if failed_actions:
            # Common failure patterns
            element_not_found_count = sum(1 for action in failed_actions if "not find" in (action.error_message or "").lower())
            timeout_count = sum(1 for action in failed_actions if "timeout" in (action.error_message or "").lower())
            
            if element_not_found_count > 0:
                recommendations.append("Consider using more specific element selectors or data-testid attributes")
            
            if timeout_count > 0:
                recommendations.append("Consider increasing timeout values for slow-loading elements")
            
            if len(failed_actions) > len(session.action_plan.actions) * 0.5:
                recommendations.append("High failure rate detected. Consider reviewing the website structure or prompt clarity")
        
        # Performance recommendations
        if session.total_duration and session.total_duration > session.action_plan.estimated_duration * 1.5:
            recommendations.append("Test took longer than expected. Consider optimizing wait times and action sequences")
        
        return recommendations
    
    async def get_execution_status(self, session_id: str) -> Dict[str, Any]:
        """Get real-time execution status"""
        if session_id not in self.active_executions:
            session = await self.session_manager.get_session(session_id)
            if not session:
                return {}
            
            return {
                "progress": 100 if session.status == TestStatus.COMPLETED else 0,
                "current_action": None,
                "completed_actions": session.successful_actions + session.failed_actions,
                "estimated_remaining": 0
            }
        
        execution = self.active_executions[session_id]
        session = await self.session_manager.get_session(session_id)
        
        if not session:
            return {}
        
        current_index = execution["current_action_index"]
        total_actions = len(session.action_plan.actions)
        progress = (current_index / total_actions) * 100 if total_actions > 0 else 0
        
        current_action = None
        if current_index < len(session.action_plan.actions):
            current_action = session.action_plan.actions[current_index].description
        
        # Estimate remaining time
        elapsed_time = (datetime.utcnow() - execution["start_time"]).total_seconds()
        estimated_remaining = 0
        if current_index > 0:
            avg_time_per_action = elapsed_time / current_index
            remaining_actions = total_actions - current_index
            estimated_remaining = int(avg_time_per_action * remaining_actions)
        
        return {
            "progress": progress,
            "current_action": current_action,
            "completed_actions": current_index,
            "estimated_remaining": estimated_remaining
        }
    
    async def get_test_metrics(self, session_id: str) -> Optional[TestMetrics]:
        """Get test metrics for a session"""
        session = await self.session_manager.get_session(session_id)
        if not session:
            return None
        
        # Calculate metrics
        action_timings = {}
        element_detection_rates = {}
        error_patterns = []
        
        for action in session.action_plan.actions:
            if action.execution_time:
                action_timings[action.type.value] = action_timings.get(action.type.value, 0) + action.execution_time
            
            if action.element_found is not None:
                action_type = action.type.value
                if action_type not in element_detection_rates:
                    element_detection_rates[action_type] = {"found": 0, "total": 0}
                
                element_detection_rates[action_type]["total"] += 1
                if action.element_found:
                    element_detection_rates[action_type]["found"] += 1
            
            if action.error_message:
                error_patterns.append(action.error_message)
        
        # Convert detection rates to percentages
        for action_type in element_detection_rates:
            stats = element_detection_rates[action_type]
            element_detection_rates[action_type] = stats["found"] / stats["total"] if stats["total"] > 0 else 0
        
        # Calculate performance score
        success_rate = session.successful_actions / session.total_actions if session.total_actions > 0 else 0
        performance_score = success_rate * 100
        
        return TestMetrics(
            session_id=session_id,
            action_timings=action_timings,
            element_detection_rates=element_detection_rates,
            error_patterns=error_patterns,
            performance_score=performance_score,
            reliability_score=success_rate * 100
        )
    
    async def get_session_screenshots(self, session_id: str) -> List[str]:
        """Get all screenshots for a session"""
        session = await self.session_manager.get_session(session_id)
        if not session:
            return []
        
        return session.screenshots
    
    async def analyze_website(self, url: str) -> WebsiteAnalysis:
        """Analyze a website for testing capabilities"""
        browser_engine = BrowserEngine()
        try:
            await browser_engine.initialize("analysis")
            analysis = await browser_engine.analyze_website(url)
            return analysis
        finally:
            await browser_engine.cleanup()
