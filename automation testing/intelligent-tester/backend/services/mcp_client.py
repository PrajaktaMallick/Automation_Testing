"""
MCP (Model Context Protocol) Client for intelligent prompt understanding
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import httpx
from pydantic import BaseModel
import openai
from anthropic import Anthropic

from ..config import settings
from ..models.test_models import ActionPlan, TestAction, ActionType

logger = logging.getLogger(__name__)


class MCPRequest(BaseModel):
    prompt: str
    website_url: str
    context: Optional[Dict[str, Any]] = None
    previous_actions: Optional[List[Dict[str, Any]]] = None


class MCPResponse(BaseModel):
    action_plan: List[Dict[str, Any]]
    confidence: float
    reasoning: str
    estimated_duration: int  # seconds
    risk_level: str  # low, medium, high


class MCPClient:
    """Client for communicating with MCP servers and AI models"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
        self.mcp_server_url = settings.MCP_SERVER_URL
        self.timeout = settings.MCP_TIMEOUT
        
    async def analyze_prompt(self, request: MCPRequest) -> ActionPlan:
        """
        Analyze natural language prompt and convert to action plan
        """
        try:
            # Try MCP server first if available
            if self.mcp_server_url:
                try:
                    return await self._query_mcp_server(request)
                except Exception as e:
                    logger.warning(f"MCP server failed, falling back to AI models: {e}")
            
            # Fallback to AI models
            return await self._query_ai_model(request)
            
        except Exception as e:
            logger.error(f"Failed to analyze prompt: {e}")
            # Ultimate fallback to rule-based parsing
            return await self._fallback_parsing(request)
    
    async def _query_mcp_server(self, request: MCPRequest) -> ActionPlan:
        """Query MCP server for action plan"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.mcp_server_url}/analyze",
                json=request.dict(),
                headers={"Authorization": f"Bearer {settings.MCP_API_KEY}"}
            )
            response.raise_for_status()
            
            mcp_response = MCPResponse(**response.json())
            return self._convert_mcp_to_action_plan(mcp_response, request.website_url)
    
    async def _query_ai_model(self, request: MCPRequest) -> ActionPlan:
        """Query AI model (OpenAI/Anthropic) for action plan"""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(request)
        
        try:
            if self.openai_client:
                return await self._query_openai(system_prompt, user_prompt, request.website_url)
            elif self.anthropic_client:
                return await self._query_anthropic(system_prompt, user_prompt, request.website_url)
            else:
                raise Exception("No AI model available")
        except Exception as e:
            logger.error(f"AI model query failed: {e}")
            raise
    
    async def _query_openai(self, system_prompt: str, user_prompt: str, website_url: str) -> ActionPlan:
        """Query OpenAI GPT model"""
        response = await asyncio.to_thread(
            self.openai_client.chat.completions.create,
            model=settings.DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )
        
        content = response.choices[0].message.content
        return self._parse_ai_response(content, website_url)
    
    async def _query_anthropic(self, system_prompt: str, user_prompt: str, website_url: str) -> ActionPlan:
        """Query Anthropic Claude model"""
        response = await asyncio.to_thread(
            self.anthropic_client.messages.create,
            model="claude-3-sonnet-20240229",
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        content = response.content[0].text
        return self._parse_ai_response(content, website_url)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for AI models"""
        return """You are an expert web automation specialist. Your task is to analyze natural language prompts and convert them into detailed, executable browser automation steps.

You must respond with a JSON object containing an action plan with the following structure:
{
  "actions": [
    {
      "type": "navigate|click|type|wait|scroll|hover|select|verify|screenshot",
      "description": "Human readable description",
      "target": "CSS selector, text content, or coordinate",
      "value": "Text to type or option to select (if applicable)",
      "wait_condition": "Element to wait for (if applicable)",
      "timeout": 30000,
      "screenshot": true/false,
      "critical": true/false
    }
  ],
  "confidence": 0.95,
  "reasoning": "Explanation of the action plan",
  "estimated_duration": 45,
  "risk_level": "low"
}

Action Types:
- navigate: Go to a URL
- click: Click on an element (buttons, links, etc.)
- type: Type text into input fields
- wait: Wait for elements or time
- scroll: Scroll to element or direction
- hover: Hover over an element
- select: Select from dropdown
- verify: Verify text or element presence
- screenshot: Take a screenshot

Guidelines:
1. Break complex tasks into atomic actions
2. Include appropriate waits for dynamic content
3. Use specific selectors when possible
4. Handle common UI patterns (modals, dropdowns, forms)
5. Add verification steps for critical actions
6. Consider mobile responsiveness
7. Handle errors gracefully
8. Take screenshots at key moments

Be intelligent about element selection:
- Use data-testid, id, or class attributes when available
- Fall back to text content for buttons and links
- Use nth-child or position for similar elements
- Consider accessibility attributes

Always respond with valid JSON only."""

    def _build_user_prompt(self, request: MCPRequest) -> str:
        """Build user prompt for AI models"""
        prompt = f"""Website URL: {request.website_url}
User Prompt: "{request.prompt}"

"""
        
        if request.context:
            prompt += f"Additional Context: {json.dumps(request.context, indent=2)}\n\n"
        
        if request.previous_actions:
            prompt += f"Previous Actions: {json.dumps(request.previous_actions, indent=2)}\n\n"
        
        prompt += """Please analyze this prompt and create a detailed action plan that a browser automation tool can execute. Consider the website's likely structure and common UI patterns.

Focus on:
1. Login flows (email/password fields, login buttons)
2. Search functionality (search boxes, filters)
3. E-commerce actions (add to cart, checkout)
4. Navigation (menus, breadcrumbs, pagination)
5. Form interactions (dropdowns, checkboxes, radio buttons)

Respond with the JSON action plan:"""
        
        return prompt
    
    def _parse_ai_response(self, content: str, website_url: str) -> ActionPlan:
        """Parse AI model response into ActionPlan"""
        try:
            # Extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            json_str = content[start_idx:end_idx]
            
            data = json.loads(json_str)
            
            actions = []
            for action_data in data.get('actions', []):
                action = TestAction(
                    type=ActionType(action_data['type']),
                    description=action_data['description'],
                    target=action_data.get('target', ''),
                    value=action_data.get('value', ''),
                    wait_condition=action_data.get('wait_condition'),
                    timeout=action_data.get('timeout', 30000),
                    screenshot=action_data.get('screenshot', False),
                    critical=action_data.get('critical', False)
                )
                actions.append(action)
            
            return ActionPlan(
                website_url=website_url,
                actions=actions,
                confidence=data.get('confidence', 0.8),
                reasoning=data.get('reasoning', 'AI-generated action plan'),
                estimated_duration=data.get('estimated_duration', 60),
                risk_level=data.get('risk_level', 'medium')
            )
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            raise Exception(f"Invalid AI response format: {e}")
    
    async def _fallback_parsing(self, request: MCPRequest) -> ActionPlan:
        """Fallback rule-based parsing when AI models fail"""
        prompt = request.prompt.lower()
        actions = []
        
        # Navigate to website
        actions.append(TestAction(
            type=ActionType.NAVIGATE,
            description=f"Navigate to {request.website_url}",
            target=request.website_url,
            screenshot=True
        ))
        
        # Simple pattern matching
        if 'login' in prompt:
            if 'email' in prompt or '@' in prompt:
                actions.append(TestAction(
                    type=ActionType.CLICK,
                    description="Click email field",
                    target="input[type='email'], input[name*='email'], #email"
                ))
                actions.append(TestAction(
                    type=ActionType.TYPE,
                    description="Type email address",
                    target="input[type='email'], input[name*='email'], #email",
                    value="jyoti@test.com"  # Default from example
                ))
            
            if 'password' in prompt:
                actions.append(TestAction(
                    type=ActionType.CLICK,
                    description="Click password field",
                    target="input[type='password'], input[name*='password'], #password"
                ))
                actions.append(TestAction(
                    type=ActionType.TYPE,
                    description="Type password",
                    target="input[type='password'], input[name*='password'], #password",
                    value="123456"  # Default from example
                ))
            
            actions.append(TestAction(
                type=ActionType.CLICK,
                description="Click login button",
                target="button:has-text('login'), input[type='submit'], .login-btn",
                critical=True
            ))
        
        if 'search' in prompt:
            # Extract search term
            search_term = "headphones"  # Default
            if 'for ' in prompt:
                parts = prompt.split('for ')
                if len(parts) > 1:
                    search_term = parts[1].split(' and ')[0].strip()
            
            actions.append(TestAction(
                type=ActionType.CLICK,
                description="Click search box",
                target="input[type='search'], input[name*='search'], .search-input"
            ))
            actions.append(TestAction(
                type=ActionType.TYPE,
                description=f"Search for {search_term}",
                target="input[type='search'], input[name*='search'], .search-input",
                value=search_term
            ))
            actions.append(TestAction(
                type=ActionType.CLICK,
                description="Click search button",
                target="button[type='submit'], .search-btn, button:has-text('search')"
            ))
        
        if 'add to cart' in prompt or 'add first' in prompt:
            actions.append(TestAction(
                type=ActionType.CLICK,
                description="Click first product",
                target=".product:first-child, .item:first-child, [data-testid*='product']:first"
            ))
            actions.append(TestAction(
                type=ActionType.CLICK,
                description="Add to cart",
                target="button:has-text('add to cart'), .add-to-cart, [data-testid*='cart']",
                critical=True,
                screenshot=True
            ))
        
        return ActionPlan(
            website_url=request.website_url,
            actions=actions,
            confidence=0.6,
            reasoning="Fallback rule-based parsing",
            estimated_duration=len(actions) * 5,
            risk_level="medium"
        )
    
    def _convert_mcp_to_action_plan(self, mcp_response: MCPResponse, website_url: str) -> ActionPlan:
        """Convert MCP response to ActionPlan"""
        actions = []
        for action_data in mcp_response.action_plan:
            action = TestAction(**action_data)
            actions.append(action)
        
        return ActionPlan(
            website_url=website_url,
            actions=actions,
            confidence=mcp_response.confidence,
            reasoning=mcp_response.reasoning,
            estimated_duration=mcp_response.estimated_duration,
            risk_level=mcp_response.risk_level
        )
