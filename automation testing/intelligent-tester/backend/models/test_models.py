"""
Data models for the intelligent web tester
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class ActionType(str, Enum):
    """Types of browser actions that can be performed"""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    WAIT = "wait"
    SCROLL = "scroll"
    HOVER = "hover"
    SELECT = "select"
    VERIFY = "verify"
    SCREENSHOT = "screenshot"
    UPLOAD = "upload"
    DRAG_DROP = "drag_drop"
    KEYBOARD = "keyboard"
    MOUSE = "mouse"


class TestStatus(str, Enum):
    """Status of test execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ActionStatus(str, Enum):
    """Status of individual action execution"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class TestAction(BaseModel):
    """Individual browser action to be performed"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: ActionType
    description: str
    target: str = ""
    value: str = ""
    wait_condition: Optional[str] = None
    timeout: int = 30000
    screenshot: bool = False
    critical: bool = False
    retry_count: int = 3
    delay_before: int = 0  # milliseconds
    delay_after: int = 0   # milliseconds
    
    # Execution results
    status: ActionStatus = ActionStatus.PENDING
    execution_time: Optional[int] = None  # milliseconds
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    element_found: bool = False
    actual_result: Optional[str] = None


class ActionPlan(BaseModel):
    """Complete plan of actions for a test"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    website_url: str
    actions: List[TestAction]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    estimated_duration: int  # seconds
    risk_level: str = Field(regex="^(low|medium|high)$")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TestRequest(BaseModel):
    """Request to create and execute a test"""
    website_url: str = Field(..., description="Target website URL")
    prompt: str = Field(..., description="Natural language test description")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Test execution options")


class TestSession(BaseModel):
    """Complete test session with execution details"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    website_url: str
    original_prompt: str
    action_plan: ActionPlan
    status: TestStatus = TestStatus.PENDING
    
    # Execution details
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration: Optional[int] = None  # seconds
    
    # Results
    total_actions: int = 0
    successful_actions: int = 0
    failed_actions: int = 0
    screenshots: List[str] = Field(default_factory=list)
    
    # Logs and errors
    execution_log: List[Dict[str, Any]] = Field(default_factory=list)
    error_summary: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_agent: Optional[str] = None
    browser_info: Optional[Dict[str, Any]] = None


class ExecutionResult(BaseModel):
    """Result of test execution"""
    session_id: str
    status: TestStatus
    success_rate: float
    total_duration: int
    action_results: List[TestAction]
    screenshots: List[str]
    summary: str
    recommendations: List[str] = Field(default_factory=list)


class WebsiteAnalysis(BaseModel):
    """Analysis of website structure and capabilities"""
    url: str
    title: str
    has_login: bool = False
    has_search: bool = False
    has_cart: bool = False
    detected_frameworks: List[str] = Field(default_factory=list)
    common_selectors: Dict[str, str] = Field(default_factory=dict)
    accessibility_score: Optional[float] = None
    mobile_friendly: bool = False
    load_time: Optional[int] = None  # milliseconds


class ActionSuggestion(BaseModel):
    """AI-generated suggestion for improving actions"""
    action_id: str
    suggestion_type: str  # "optimization", "alternative", "warning"
    message: str
    confidence: float
    alternative_action: Optional[TestAction] = None


class TestMetrics(BaseModel):
    """Metrics and analytics for test execution"""
    session_id: str
    page_load_times: List[int] = Field(default_factory=list)
    action_timings: Dict[str, int] = Field(default_factory=dict)
    element_detection_rates: Dict[str, float] = Field(default_factory=dict)
    error_patterns: List[str] = Field(default_factory=list)
    performance_score: Optional[float] = None
    reliability_score: Optional[float] = None


# Request/Response models for API
class CreateTestRequest(BaseModel):
    website_url: str
    prompt: str
    context: Optional[Dict[str, Any]] = None


class CreateTestResponse(BaseModel):
    session_id: str
    action_plan: ActionPlan
    estimated_duration: int
    risk_assessment: str


class ExecuteTestRequest(BaseModel):
    session_id: str
    options: Optional[Dict[str, Any]] = None


class ExecuteTestResponse(BaseModel):
    session_id: str
    status: TestStatus
    message: str


class GetTestResultsResponse(BaseModel):
    session: TestSession
    execution_result: ExecutionResult
    metrics: Optional[TestMetrics] = None


class ListTestsResponse(BaseModel):
    sessions: List[TestSession]
    total: int
    page: int
    per_page: int
