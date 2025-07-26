"""
Intelligent action planning system that converts natural language to executable browser actions
"""
import asyncio
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
import json

from ..models.test_models import (
    TestAction, ActionType, ActionPlan, TestRequest, 
    WebsiteAnalysis, ActionSuggestion
)
from ..services.mcp_client import MCPClient, MCPRequest
from ..services.browser_engine import BrowserEngine
from ..config import settings

logger = logging.getLogger(__name__)


class ActionPlanner:
    """Intelligent action planning with context awareness"""
    
    def __init__(self):
        self.mcp_client = MCPClient()
        self.context_memory: Dict[str, Any] = {}
        
    async def create_action_plan(self, request: TestRequest) -> ActionPlan:
        """
        Create comprehensive action plan from natural language prompt
        """
        logger.info(f"Creating action plan for: {request.prompt}")
        
        # Analyze website first to get context
        website_analysis = await self._analyze_website_quick(request.website_url)
        
        # Prepare MCP request with context
        mcp_request = MCPRequest(
            prompt=request.prompt,
            website_url=request.website_url,
            context={
                "website_analysis": website_analysis.dict() if website_analysis else None,
                "user_context": request.context or {}
            }
        )
        
        # Get action plan from MCP/AI
        action_plan = await self.mcp_client.analyze_prompt(mcp_request)
        
        # Enhance action plan with intelligent optimizations
        enhanced_plan = await self._enhance_action_plan(action_plan, website_analysis)
        
        # Validate and adjust plan
        validated_plan = await self._validate_action_plan(enhanced_plan)
        
        logger.info(f"Created action plan with {len(validated_plan.actions)} actions")
        return validated_plan
    
    async def _analyze_website_quick(self, url: str) -> Optional[WebsiteAnalysis]:
        """Quick website analysis for context"""
        try:
            browser_engine = BrowserEngine()
            await browser_engine.initialize("analysis")
            
            analysis = await browser_engine.analyze_website(url)
            await browser_engine.cleanup()
            
            return analysis
        except Exception as e:
            logger.warning(f"Website analysis failed: {e}")
            return None
    
    async def _enhance_action_plan(self, plan: ActionPlan, analysis: Optional[WebsiteAnalysis]) -> ActionPlan:
        """Enhance action plan with intelligent optimizations"""
        enhanced_actions = []
        
        for i, action in enumerate(plan.actions):
            # Add smart waits before critical actions
            if action.critical and i > 0:
                wait_action = TestAction(
                    type=ActionType.WAIT,
                    description="Wait for page stability",
                    target="time",
                    value="1000",
                    timeout=5000
                )
                enhanced_actions.append(wait_action)
            
            # Enhance element targeting based on website analysis
            enhanced_action = await self._enhance_action_targeting(action, analysis)
            enhanced_actions.append(enhanced_action)
            
            # Add screenshots for important actions
            if action.type in [ActionType.CLICK, ActionType.TYPE] and action.critical:
                enhanced_action.screenshot = True
        
        plan.actions = enhanced_actions
        return plan
    
    async def _enhance_action_targeting(self, action: TestAction, analysis: Optional[WebsiteAnalysis]) -> TestAction:
        """Enhance action targeting based on website analysis"""
        if not analysis:
            return action
        
        # Use website-specific selectors if available
        if action.type == ActionType.CLICK:
            if "login" in action.description.lower() and "login_button" in analysis.common_selectors:
                action.target = analysis.common_selectors["login_button"]
            elif "search" in action.description.lower() and "search_input" in analysis.common_selectors:
                action.target = analysis.common_selectors["search_input"]
            elif "cart" in action.description.lower() and "cart_button" in analysis.common_selectors:
                action.target = analysis.common_selectors["cart_button"]
        
        elif action.type == ActionType.TYPE:
            if "search" in action.description.lower() and "search_input" in analysis.common_selectors:
                action.target = analysis.common_selectors["search_input"]
        
        # Adjust timeouts based on detected frameworks
        if analysis.detected_frameworks:
            if "React" in analysis.detected_frameworks or "Vue" in analysis.detected_frameworks:
                # SPA frameworks might need longer waits
                action.timeout = max(action.timeout, 10000)
        
        return action
    
    async def _validate_action_plan(self, plan: ActionPlan) -> ActionPlan:
        """Validate and adjust action plan for better reliability"""
        validated_actions = []
        
        for i, action in enumerate(plan.actions):
            # Ensure first action is navigation
            if i == 0 and action.type != ActionType.NAVIGATE:
                nav_action = TestAction(
                    type=ActionType.NAVIGATE,
                    description=f"Navigate to {plan.website_url}",
                    target=plan.website_url,
                    screenshot=True
                )
                validated_actions.append(nav_action)
            
            # Validate action parameters
            validated_action = self._validate_action_parameters(action)
            validated_actions.append(validated_action)
            
            # Add implicit waits after navigation
            if action.type == ActionType.NAVIGATE:
                wait_action = TestAction(
                    type=ActionType.WAIT,
                    description="Wait for page load",
                    target="time",
                    value="2000",
                    timeout=10000
                )
                validated_actions.append(wait_action)
        
        plan.actions = validated_actions
        return plan
    
    def _validate_action_parameters(self, action: TestAction) -> TestAction:
        """Validate and fix action parameters"""
        # Ensure required fields are present
        if not action.description:
            action.description = f"Execute {action.type.value} action"
        
        # Set reasonable timeouts
        if action.timeout < 5000:
            action.timeout = 5000
        elif action.timeout > 60000:
            action.timeout = 60000
        
        # Ensure type actions have values
        if action.type == ActionType.TYPE and not action.value:
            action.value = "test input"
        
        # Set retry counts based on action criticality
        if action.critical:
            action.retry_count = max(action.retry_count, 3)
        
        return action
    
    async def optimize_action_sequence(self, actions: List[TestAction]) -> List[TestAction]:
        """Optimize sequence of actions for better performance and reliability"""
        optimized = []
        
        i = 0
        while i < len(actions):
            action = actions[i]
            
            # Combine consecutive type actions on same element
            if (action.type == ActionType.TYPE and 
                i + 1 < len(actions) and 
                actions[i + 1].type == ActionType.TYPE and
                actions[i + 1].target == action.target):
                
                # Combine values
                combined_value = action.value + " " + actions[i + 1].value
                action.value = combined_value
                action.description = f"Type combined text: {combined_value}"
                i += 1  # Skip next action
            
            # Remove redundant waits
            elif (action.type == ActionType.WAIT and 
                  i + 1 < len(actions) and 
                  actions[i + 1].type == ActionType.WAIT):
                # Use longer wait time
                next_wait = actions[i + 1]
                action.value = str(max(int(action.value), int(next_wait.value)))
                i += 1  # Skip next action
            
            optimized.append(action)
            i += 1
        
        return optimized
    
    async def generate_action_suggestions(self, action: TestAction, context: Dict[str, Any]) -> List[ActionSuggestion]:
        """Generate intelligent suggestions for improving actions"""
        suggestions = []
        
        # Suggest better selectors
        if action.type == ActionType.CLICK and not any(attr in action.target for attr in ['data-testid', 'id', '#']):
            suggestions.append(ActionSuggestion(
                action_id=action.id,
                suggestion_type="optimization",
                message="Consider using more specific selectors like data-testid or id for better reliability",
                confidence=0.8
            ))
        
        # Suggest adding waits
        if action.type == ActionType.CLICK and action.critical and not action.wait_condition:
            suggestions.append(ActionSuggestion(
                action_id=action.id,
                suggestion_type="optimization",
                message="Consider adding a wait condition before this critical click action",
                confidence=0.9
            ))
        
        # Suggest screenshots for verification
        if action.type == ActionType.VERIFY and not action.screenshot:
            suggestions.append(ActionSuggestion(
                action_id=action.id,
                suggestion_type="optimization",
                message="Consider taking a screenshot for visual verification",
                confidence=0.7
            ))
        
        return suggestions
    
    def extract_test_data(self, prompt: str) -> Dict[str, Any]:
        """Extract test data from natural language prompt"""
        test_data = {}
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, prompt)
        if emails:
            test_data['email'] = emails[0]
        
        # Extract passwords (simple pattern)
        password_pattern = r'password[:\s]+([^\s]+)'
        passwords = re.findall(password_pattern, prompt, re.IGNORECASE)
        if passwords:
            test_data['password'] = passwords[0]
        
        # Extract search terms
        search_patterns = [
            r'search for (.+?)(?:\s+and|\s+then|$)',
            r'find (.+?)(?:\s+and|\s+then|$)',
            r'look for (.+?)(?:\s+and|\s+then|$)'
        ]
        for pattern in search_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            if matches:
                test_data['search_term'] = matches[0].strip()
                break
        
        # Extract product/item names
        item_patterns = [
            r'add (.+?) to cart',
            r'buy (.+?)(?:\s+and|\s+then|$)',
            r'purchase (.+?)(?:\s+and|\s+then|$)'
        ]
        for pattern in item_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            if matches:
                test_data['item_name'] = matches[0].strip()
                break
        
        # Extract quantities
        quantity_pattern = r'(\d+)\s+(?:items?|pieces?|units?)'
        quantities = re.findall(quantity_pattern, prompt, re.IGNORECASE)
        if quantities:
            test_data['quantity'] = int(quantities[0])
        
        return test_data
    
    def analyze_prompt_intent(self, prompt: str) -> Dict[str, Any]:
        """Analyze the intent and complexity of the prompt"""
        intent_analysis = {
            'primary_intent': 'unknown',
            'secondary_intents': [],
            'complexity': 'low',
            'estimated_steps': 1,
            'risk_factors': []
        }
        
        prompt_lower = prompt.lower()
        
        # Determine primary intent
        if any(word in prompt_lower for word in ['login', 'sign in', 'log in']):
            intent_analysis['primary_intent'] = 'authentication'
        elif any(word in prompt_lower for word in ['search', 'find', 'look for']):
            intent_analysis['primary_intent'] = 'search'
        elif any(word in prompt_lower for word in ['buy', 'purchase', 'add to cart', 'checkout']):
            intent_analysis['primary_intent'] = 'ecommerce'
        elif any(word in prompt_lower for word in ['test', 'verify', 'check']):
            intent_analysis['primary_intent'] = 'testing'
        
        # Count action words to estimate complexity
        action_words = ['click', 'type', 'enter', 'select', 'choose', 'navigate', 'go to', 'scroll']
        action_count = sum(1 for word in action_words if word in prompt_lower)
        
        if action_count > 5:
            intent_analysis['complexity'] = 'high'
            intent_analysis['estimated_steps'] = action_count * 2
        elif action_count > 2:
            intent_analysis['complexity'] = 'medium'
            intent_analysis['estimated_steps'] = action_count * 1.5
        else:
            intent_analysis['complexity'] = 'low'
            intent_analysis['estimated_steps'] = max(action_count, 3)
        
        # Identify risk factors
        if 'payment' in prompt_lower or 'credit card' in prompt_lower:
            intent_analysis['risk_factors'].append('financial_transaction')
        if 'delete' in prompt_lower or 'remove' in prompt_lower:
            intent_analysis['risk_factors'].append('destructive_action')
        if 'admin' in prompt_lower or 'administrator' in prompt_lower:
            intent_analysis['risk_factors'].append('administrative_action')
        
        return intent_analysis
