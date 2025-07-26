"""
Advanced Playwright browser automation engine with intelligent element detection
"""
import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Locator
from PIL import Image
import json

from ..config import settings
from ..models.test_models import TestAction, ActionType, ActionStatus, TestSession, WebsiteAnalysis

logger = logging.getLogger(__name__)


class SmartElementDetector:
    """Intelligent element detection with multiple fallback strategies"""
    
    @staticmethod
    async def find_element(page: Page, target: str, action_type: ActionType) -> Optional[Locator]:
        """
        Find element using multiple strategies based on action type
        """
        strategies = SmartElementDetector._get_strategies_for_action(action_type, target)
        
        for strategy in strategies:
            try:
                locator = page.locator(strategy)
                if await locator.count() > 0:
                    # Check if element is visible and interactable
                    if await SmartElementDetector._is_element_ready(locator, action_type):
                        logger.info(f"Found element using strategy: {strategy}")
                        return locator
            except Exception as e:
                logger.debug(f"Strategy '{strategy}' failed: {e}")
                continue
        
        return None
    
    @staticmethod
    def _get_strategies_for_action(action_type: ActionType, target: str) -> List[str]:
        """Get prioritized list of element detection strategies"""
        
        # If target looks like a CSS selector, try it first
        strategies = []
        if target and any(char in target for char in ['#', '.', '[', '>', ':', 'nth-']):
            strategies.append(target)
        
        if action_type == ActionType.CLICK:
            strategies.extend([
                f"button:has-text('{target}')",
                f"a:has-text('{target}')",
                f"[data-testid*='{target.lower()}']",
                f"[aria-label*='{target}']",
                f"input[value*='{target}']",
                f"*:has-text('{target}'):visible",
                f".{target.lower().replace(' ', '-')}",
                f"#{target.lower().replace(' ', '-')}",
            ])
        
        elif action_type == ActionType.TYPE:
            strategies.extend([
                f"input[placeholder*='{target}']",
                f"input[name*='{target.lower()}']",
                f"input[id*='{target.lower()}']",
                f"textarea[placeholder*='{target}']",
                f"[data-testid*='{target.lower()}']",
                f"input[type='text']",
                f"input[type='email']",
                f"input[type='password']",
                "input:visible",
                "textarea:visible"
            ])
        
        elif action_type == ActionType.SELECT:
            strategies.extend([
                f"select[name*='{target.lower()}']",
                f"select[id*='{target.lower()}']",
                f"[data-testid*='{target.lower()}'] select",
                "select:visible"
            ])
        
        # Add generic fallbacks
        strategies.extend([
            f"[title*='{target}']",
            f"[alt*='{target}']",
            f"[data-cy*='{target.lower()}']",
            f"[data-test*='{target.lower()}']"
        ])
        
        return strategies
    
    @staticmethod
    async def _is_element_ready(locator: Locator, action_type: ActionType) -> bool:
        """Check if element is ready for interaction"""
        try:
            # Check visibility
            if not await locator.is_visible():
                return False
            
            # Check if element is enabled for interactive actions
            if action_type in [ActionType.CLICK, ActionType.TYPE, ActionType.SELECT]:
                if not await locator.is_enabled():
                    return False
            
            # Additional checks for specific action types
            if action_type == ActionType.TYPE:
                # Check if element is editable
                if not await locator.is_editable():
                    return False
            
            return True
        except Exception:
            return False


class BrowserEngine:
    """Advanced browser automation engine"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.session_id: Optional[str] = None
        
    async def initialize(self, session_id: str) -> None:
        """Initialize browser instance"""
        self.session_id = session_id
        self.playwright = await async_playwright().start()
        
        # Choose browser type
        if settings.BROWSER_TYPE.lower() == "firefox":
            self.browser = await self.playwright.firefox.launch(headless=settings.HEADLESS)
        elif settings.BROWSER_TYPE.lower() == "webkit":
            self.browser = await self.playwright.webkit.launch(headless=settings.HEADLESS)
        else:
            self.browser = await self.playwright.chromium.launch(
                headless=settings.HEADLESS,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
        
        # Create context with realistic settings
        self.context = await self.browser.new_context(
            viewport={'width': settings.VIEWPORT_WIDTH, 'height': settings.VIEWPORT_HEIGHT},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Create page
        self.page = await self.context.new_page()
        
        # Set default timeout
        self.page.set_default_timeout(settings.DEFAULT_TIMEOUT)
        
        logger.info(f"Browser initialized for session {session_id}")
    
    async def cleanup(self) -> None:
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def execute_action(self, action: TestAction) -> TestAction:
        """Execute a single browser action"""
        start_time = time.time()
        action.status = ActionStatus.RUNNING
        
        try:
            logger.info(f"Executing action: {action.description}")
            
            # Add delay before action if specified
            if action.delay_before > 0:
                await asyncio.sleep(action.delay_before / 1000)
            
            # Execute based on action type
            if action.type == ActionType.NAVIGATE:
                await self._execute_navigate(action)
            elif action.type == ActionType.CLICK:
                await self._execute_click(action)
            elif action.type == ActionType.TYPE:
                await self._execute_type(action)
            elif action.type == ActionType.WAIT:
                await self._execute_wait(action)
            elif action.type == ActionType.SCROLL:
                await self._execute_scroll(action)
            elif action.type == ActionType.HOVER:
                await self._execute_hover(action)
            elif action.type == ActionType.SELECT:
                await self._execute_select(action)
            elif action.type == ActionType.VERIFY:
                await self._execute_verify(action)
            elif action.type == ActionType.SCREENSHOT:
                await self._execute_screenshot(action)
            else:
                raise Exception(f"Unsupported action type: {action.type}")
            
            # Take screenshot if requested
            if action.screenshot:
                action.screenshot_path = await self._take_screenshot(f"{action.id}_success")
            
            # Add delay after action if specified
            if action.delay_after > 0:
                await asyncio.sleep(action.delay_after / 1000)
            
            action.status = ActionStatus.SUCCESS
            action.element_found = True
            
        except Exception as e:
            logger.error(f"Action failed: {action.description} - {e}")
            action.status = ActionStatus.FAILED
            action.error_message = str(e)
            
            # Take screenshot on failure
            try:
                action.screenshot_path = await self._take_screenshot(f"{action.id}_error")
            except Exception:
                pass
        
        finally:
            action.execution_time = int((time.time() - start_time) * 1000)
        
        return action
    
    async def _execute_navigate(self, action: TestAction) -> None:
        """Execute navigation action"""
        url = action.target or action.value
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        await self.page.goto(url, wait_until='networkidle')
        action.actual_result = f"Navigated to {self.page.url}"
    
    async def _execute_click(self, action: TestAction) -> None:
        """Execute click action with smart element detection"""
        element = await SmartElementDetector.find_element(self.page, action.target, ActionType.CLICK)
        
        if not element:
            raise Exception(f"Could not find clickable element: {action.target}")
        
        # Scroll element into view
        await element.scroll_into_view_if_needed()
        
        # Wait for element to be stable
        await element.wait_for(state='visible', timeout=action.timeout)
        
        # Click the element
        await element.click(timeout=action.timeout)
        action.actual_result = f"Clicked element: {action.target}"
    
    async def _execute_type(self, action: TestAction) -> None:
        """Execute typing action"""
        element = await SmartElementDetector.find_element(self.page, action.target, ActionType.TYPE)
        
        if not element:
            raise Exception(f"Could not find input element: {action.target}")
        
        # Clear existing content and type new value
        await element.clear()
        await element.fill(action.value)
        action.actual_result = f"Typed '{action.value}' into {action.target}"
    
    async def _execute_wait(self, action: TestAction) -> None:
        """Execute wait action"""
        if action.target.lower() == 'time' or action.target.isdigit():
            # Wait for specified time
            wait_time = int(action.value) if action.value.isdigit() else int(action.target)
            await asyncio.sleep(wait_time / 1000)
            action.actual_result = f"Waited for {wait_time}ms"
        else:
            # Wait for element
            await self.page.wait_for_selector(action.target, timeout=action.timeout)
            action.actual_result = f"Waited for element: {action.target}"
    
    async def _execute_scroll(self, action: TestAction) -> None:
        """Execute scroll action"""
        if action.target.lower() == 'top':
            await self.page.evaluate("window.scrollTo(0, 0)")
        elif action.target.lower() == 'bottom':
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        else:
            # Scroll to element
            element = await SmartElementDetector.find_element(self.page, action.target, ActionType.SCROLL)
            if element:
                await element.scroll_into_view_if_needed()
            else:
                raise Exception(f"Could not find element to scroll to: {action.target}")
        
        action.actual_result = f"Scrolled to {action.target}"
    
    async def _execute_hover(self, action: TestAction) -> None:
        """Execute hover action"""
        element = await SmartElementDetector.find_element(self.page, action.target, ActionType.HOVER)
        
        if not element:
            raise Exception(f"Could not find element to hover: {action.target}")
        
        await element.hover(timeout=action.timeout)
        action.actual_result = f"Hovered over {action.target}"
    
    async def _execute_select(self, action: TestAction) -> None:
        """Execute select action"""
        element = await SmartElementDetector.find_element(self.page, action.target, ActionType.SELECT)
        
        if not element:
            raise Exception(f"Could not find select element: {action.target}")
        
        await element.select_option(value=action.value, timeout=action.timeout)
        action.actual_result = f"Selected '{action.value}' from {action.target}"
    
    async def _execute_verify(self, action: TestAction) -> None:
        """Execute verification action"""
        if action.target.lower() == 'title':
            title = await self.page.title()
            if action.value.lower() not in title.lower():
                raise Exception(f"Title verification failed: '{title}' does not contain '{action.value}'")
            action.actual_result = f"Title verification passed: '{title}'"
        elif action.target.lower() == 'url':
            current_url = self.page.url
            if action.value not in current_url:
                raise Exception(f"URL verification failed: '{current_url}' does not contain '{action.value}'")
            action.actual_result = f"URL verification passed: '{current_url}'"
        else:
            # Verify element or text presence
            try:
                await self.page.wait_for_selector(action.target, timeout=action.timeout)
                action.actual_result = f"Element verification passed: {action.target}"
            except:
                # Try text verification
                if await self.page.locator(f"text={action.value}").count() > 0:
                    action.actual_result = f"Text verification passed: '{action.value}'"
                else:
                    raise Exception(f"Verification failed: Could not find '{action.target}' or '{action.value}'")
    
    async def _execute_screenshot(self, action: TestAction) -> None:
        """Execute screenshot action"""
        screenshot_path = await self._take_screenshot(action.id)
        action.screenshot_path = screenshot_path
        action.actual_result = f"Screenshot saved: {screenshot_path}"
    
    async def _take_screenshot(self, name: str) -> str:
        """Take and save screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.session_id}_{name}_{timestamp}.png"
        filepath = os.path.join(settings.SCREENSHOTS_DIR, filename)
        
        await self.page.screenshot(path=filepath, full_page=True)
        
        # Optimize screenshot size
        await self._optimize_screenshot(filepath)
        
        return f"/screenshots/{filename}"
    
    async def _optimize_screenshot(self, filepath: str) -> None:
        """Optimize screenshot file size"""
        try:
            with Image.open(filepath) as img:
                # Resize if too large
                max_width, max_height = map(int, settings.MAX_SCREENSHOT_SIZE.split('x'))
                if img.width > max_width or img.height > max_height:
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    img.save(filepath, optimize=True, quality=85)
        except Exception as e:
            logger.warning(f"Failed to optimize screenshot: {e}")
    
    async def analyze_website(self, url: str) -> WebsiteAnalysis:
        """Analyze website structure and capabilities"""
        await self.page.goto(url)
        
        # Get basic info
        title = await self.page.title()
        
        # Detect common elements
        has_login = await self._detect_login_elements()
        has_search = await self._detect_search_elements()
        has_cart = await self._detect_cart_elements()
        
        # Detect frameworks
        frameworks = await self._detect_frameworks()
        
        # Get common selectors
        selectors = await self._get_common_selectors()
        
        # Check mobile friendliness
        mobile_friendly = await self._check_mobile_friendly()
        
        return WebsiteAnalysis(
            url=url,
            title=title,
            has_login=has_login,
            has_search=has_search,
            has_cart=has_cart,
            detected_frameworks=frameworks,
            common_selectors=selectors,
            mobile_friendly=mobile_friendly
        )
    
    async def _detect_login_elements(self) -> bool:
        """Detect if page has login functionality"""
        login_indicators = [
            "input[type='password']",
            "input[name*='password']",
            "button:has-text('login')",
            "a:has-text('login')",
            ".login",
            "#login"
        ]
        
        for selector in login_indicators:
            if await self.page.locator(selector).count() > 0:
                return True
        return False
    
    async def _detect_search_elements(self) -> bool:
        """Detect if page has search functionality"""
        search_indicators = [
            "input[type='search']",
            "input[name*='search']",
            "input[placeholder*='search']",
            ".search",
            "#search"
        ]
        
        for selector in search_indicators:
            if await self.page.locator(selector).count() > 0:
                return True
        return False
    
    async def _detect_cart_elements(self) -> bool:
        """Detect if page has shopping cart functionality"""
        cart_indicators = [
            "button:has-text('add to cart')",
            ".cart",
            "#cart",
            "[data-testid*='cart']",
            "a:has-text('cart')"
        ]
        
        for selector in cart_indicators:
            if await self.page.locator(selector).count() > 0:
                return True
        return False
    
    async def _detect_frameworks(self) -> List[str]:
        """Detect JavaScript frameworks and libraries"""
        frameworks = []
        
        # Check for common frameworks
        checks = {
            "React": "window.React",
            "Vue": "window.Vue",
            "Angular": "window.ng",
            "jQuery": "window.jQuery",
            "Bootstrap": "window.bootstrap"
        }
        
        for framework, check in checks.items():
            try:
                result = await self.page.evaluate(f"typeof {check} !== 'undefined'")
                if result:
                    frameworks.append(framework)
            except:
                pass
        
        return frameworks
    
    async def _get_common_selectors(self) -> Dict[str, str]:
        """Get common element selectors for the website"""
        selectors = {}
        
        # Try to find common elements
        common_elements = {
            "search_input": ["input[type='search']", "input[name*='search']", ".search-input"],
            "login_button": ["button:has-text('login')", ".login-btn", "#login"],
            "cart_button": ["button:has-text('cart')", ".cart-btn", "#cart"],
            "menu_button": ["button:has-text('menu')", ".menu-btn", "#menu"]
        }
        
        for element_name, selectors_list in common_elements.items():
            for selector in selectors_list:
                if await self.page.locator(selector).count() > 0:
                    selectors[element_name] = selector
                    break
        
        return selectors
    
    async def _check_mobile_friendly(self) -> bool:
        """Check if website is mobile-friendly"""
        try:
            # Check for viewport meta tag
            viewport = await self.page.locator("meta[name='viewport']").count()
            return viewport > 0
        except:
            return False
