#!/usr/bin/env python3
"""
Real Browser Automation Backend - Actually opens browsers and performs actions
"""
import json
import os
import uuid
import time
import threading
import re
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Try to import Playwright
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
    print("✅ Playwright is available - Real browser automation enabled!")
except ImportError:
    try:
        # Try alternative import
        import subprocess
        result = subprocess.run(['python', '-c', 'from playwright.sync_api import sync_playwright; print("OK")'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            from playwright.sync_api import sync_playwright
            PLAYWRIGHT_AVAILABLE = True
            print("✅ Playwright is available - Real browser automation enabled!")
        else:
            raise ImportError("Playwright not found")
    except:
        PLAYWRIGHT_AVAILABLE = False
        print("⚠️  Playwright not available. Install with: pip install playwright && playwright install")

# Global storage
test_sessions = {}
active_executions = {}

class RealBrowserAutomation:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.context = None
    
    def initialize(self):
        """Initialize real Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright not available. Please install: pip install playwright && playwright install")
        
        print("🚀 Launching real browser...")
        self.playwright = sync_playwright().start()
        
        # Launch browser with visible window
        self.browser = self.playwright.chromium.launch(
            headless=False,  # Show the browser window
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create browser context
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Create new page
        self.page = self.context.new_page()
        
        # Set timeouts
        self.page.set_default_timeout(30000)
        self.page.set_default_navigation_timeout(30000)
        
        print("✅ Browser launched successfully!")
        
    def cleanup(self):
        """Clean up browser resources"""
        try:
            print("🧹 Cleaning up browser...")
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            print("✅ Browser cleanup complete")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
    
    def execute_action(self, action, session_id):
        """Execute a single action on the real browser"""
        action_type = action["type"]
        target = action["target"]
        value = action.get("value", "")
        
        try:
            print(f"🔄 Executing: {action['description']}")
            
            if action_type == "navigate":
                print(f"🌐 Navigating to: {target}")
                self.page.goto(target, wait_until="networkidle", timeout=30000)
                self.page.wait_for_load_state("domcontentloaded")
                time.sleep(2)  # Extra wait for dynamic content
                result = f"✅ Successfully navigated to {target}"
                
            elif action_type == "click":
                print(f"🖱️ Clicking: {target}")
                selectors = self._generate_click_selectors(target)
                
                element_found = False
                for selector in selectors:
                    try:
                        print(f"   Trying selector: {selector}")
                        element = self.page.locator(selector).first
                        if element.count() > 0:
                            element.scroll_into_view_if_needed()
                            element.click(timeout=10000)
                            element_found = True
                            result = f"✅ Successfully clicked: {target} (using {selector})"
                            break
                    except Exception as e:
                        print(f"   ❌ Selector failed: {selector} - {e}")
                        continue
                
                if not element_found:
                    raise Exception(f"Could not find clickable element: {target}")
                    
            elif action_type == "type":
                print(f"⌨️ Typing: '{value}' into {target}")
                selectors = self._generate_input_selectors(target, value)
                
                element_found = False
                for selector in selectors:
                    try:
                        print(f"   Trying input selector: {selector}")
                        element = self.page.locator(selector).first
                        if element.count() > 0:
                            element.scroll_into_view_if_needed()
                            element.clear()
                            element.type(value, delay=100)  # Human-like typing
                            element_found = True
                            result = f"✅ Successfully typed '{value}' into {target} (using {selector})"
                            break
                    except Exception as e:
                        print(f"   ❌ Input selector failed: {selector} - {e}")
                        continue
                
                if not element_found:
                    raise Exception(f"Could not find input element: {target}")
                    
            elif action_type == "wait":
                wait_time = int(value) if value.isdigit() else 3000
                print(f"⏱️ Waiting {wait_time}ms...")
                time.sleep(wait_time / 1000)
                result = f"✅ Waited {wait_time}ms"
                
            elif action_type == "screenshot":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"real_{session_id}_{timestamp}.png"
                filepath = os.path.join("screenshots", filename)
                os.makedirs("screenshots", exist_ok=True)
                
                print(f"📸 Taking screenshot: {filename}")
                self.page.screenshot(path=filepath, full_page=True)
                result = f"✅ Screenshot saved: /screenshots/{filename}"
                
            elif action_type == "key":
                print(f"⌨️ Pressing key: {value}")
                if target == "search":
                    # Find search input and press key
                    search_selectors = self._generate_input_selectors("search", "")
                    for selector in search_selectors:
                        try:
                            element = self.page.locator(selector).first
                            if element.count() > 0:
                                element.press(value)
                                result = f"✅ Pressed {value} key in search box"
                                break
                        except:
                            continue
                else:
                    self.page.keyboard.press(value)
                    result = f"✅ Pressed {value} key"

            elif action_type == "scroll":
                print(f"📜 Scrolling {target}")
                if target == "down":
                    scroll_amount = int(value) if value.isdigit() else 500
                    self.page.mouse.wheel(0, scroll_amount)
                elif target == "up":
                    scroll_amount = int(value) if value.isdigit() else 500
                    self.page.mouse.wheel(0, -scroll_amount)
                result = f"✅ Scrolled {target} by {value}px"

            elif action_type == "verify":
                if target == "title":
                    page_title = self.page.title()
                    print(f"🔍 Verifying title: '{page_title}' contains '{value}'")
                    if value.lower() in page_title.lower():
                        result = f"✅ Title verification passed: '{page_title}' contains '{value}'"
                    else:
                        raise Exception(f"Title verification failed: '{page_title}' does not contain '{value}'")
                else:
                    result = f"⚠️ Verification type '{target}' not implemented"

            else:
                result = f"⚠️ Action type '{action_type}' not implemented"
            
            print(f"✅ {result}")
            return {"status": "success", "result": result, "error": None}
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Action failed: {error_msg}")
            return {"status": "failed", "result": None, "error": error_msg}
    
    def _generate_click_selectors(self, target):
        """Generate multiple selector strategies for clicking"""
        selectors = []
        
        # If it's already a CSS selector, try it first
        if any(char in target for char in ['[', '.', '#', ':', '>']):
            selectors.append(target)
        
        # Generate smart selectors based on common patterns
        target_lower = target.lower()

        # Handle special smart targets
        if target_lower == "first_result":
            selectors.extend([
                ".search-result:first-child a",
                ".result:first-child a",
                ".search-results > div:first-child a",
                "h3:first-child a",
                ".repo-list-item:first-child a"
            ])
        elif target_lower == "first_product":
            selectors.extend([
                ".product:first-child",
                ".product-item:first-child",
                ".inventory-item:first-child",
                "[data-testid='product']:first-child",
                ".product-card:first-child"
            ])
        elif target_lower == "first_link":
            selectors.extend([
                "a:first-child",
                "main a:first-child",
                ".content a:first-child"
            ])
        elif target_lower == "first_item":
            selectors.extend([
                ":first-child",
                "li:first-child",
                "div:first-child"
            ])
        elif target_lower == "add_to_cart":
            selectors.extend([
                "button:has-text('Add to cart')",
                "button:has-text('Add to Cart')",
                ".add-to-cart",
                "#add-to-cart",
                "[data-testid='add-to-cart']",
                "button[name='add-to-cart']"
            ])
        elif target_lower == "search_button":
            selectors.extend([
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Search')",
                ".search-btn",
                "#search-btn",
                "[data-testid='search-button']"
            ])
        elif target_lower == "form_submit":
            selectors.extend([
                "button[type='submit']",
                "input[type='submit']",
                "form button:last-child",
                ".submit-btn"
            ])
        else:
            # Standard button selectors
            selectors.extend([
                f"button:has-text('{target}')",
                f"input[type='button']:has([value*='{target}' i])",
                f"input[type='submit']:has([value*='{target}' i])",
                f"a:has-text('{target}')",
            ])

            # Common class and ID patterns
            target_slug = target_lower.replace(' ', '-').replace('_', '-')
            selectors.extend([
                f"#{target_slug}",
                f".{target_slug}",
                f"[data-testid*='{target_slug}']",
                f"[aria-label*='{target}' i]",
                f"[title*='{target}' i]",
            ])

            # Text-based selectors
            selectors.extend([
                f"*:has-text('{target}'):visible",
                f"span:has-text('{target}')",
                f"div:has-text('{target}')",
            ])

            # Login-specific selectors
            if 'login' in target_lower:
                selectors.extend([
                    "button[type='submit']",
                    "input[type='submit']",
                    ".login-btn", ".login-button", "#login-btn", "#login-button",
                    "[data-testid='login']", "[data-testid='login-button']"
                ])
        
        return selectors
    
    def _generate_input_selectors(self, target, value):
        """Generate multiple selector strategies for inputs"""
        selectors = []
        
        # If it's already a CSS selector, try it first
        if any(char in target for char in ['[', '.', '#', ':', '>']):
            selectors.append(target)
        
        target_lower = target.lower()

        # Handle smart input targets
        if target_lower == "username":
            selectors.extend([
                "input[name='username']",
                "input[id='username']",
                "input[name='user']",
                "input[id='user']",
                "input[placeholder*='username' i]",
                "input[placeholder*='user' i]",
                "[data-testid*='username']"
            ])
        elif 'email' in target_lower or '@' in value:
            selectors.extend([
                "input[type='email']",
                "input[name*='email' i]",
                "input[id*='email' i]",
                "input[placeholder*='email' i]",
                "[data-testid*='email']"
            ])
        elif 'password' in target_lower:
            selectors.extend([
                "input[type='password']",
                "input[name*='password' i]",
                "input[id*='password' i]",
                "input[placeholder*='password' i]",
                "[data-testid*='password']"
            ])
        elif 'search' in target_lower:
            selectors.extend([
                "input[type='search']",
                "input[name*='search' i]",
                "input[id*='search' i]",
                "input[placeholder*='search' i]",
                "[data-testid*='search']",
                ".search-input", "#search-input",
                "input[name='q']",  # Common search parameter
                "input[name='query']"
            ])
        elif 'name' in target_lower and 'username' not in target_lower:
            selectors.extend([
                "input[name*='name' i]",
                "input[id*='name' i]",
                "input[placeholder*='name' i]",
                "[data-testid*='name']",
                "input[name='first_name']",
                "input[name='last_name']",
                "input[name='full_name']"
            ])
        elif target_lower in ["first name", "firstname"]:
            selectors.extend([
                "input[name*='first' i]",
                "input[id*='first' i]",
                "input[placeholder*='first' i]"
            ])
        elif target_lower in ["last name", "lastname"]:
            selectors.extend([
                "input[name*='last' i]",
                "input[id*='last' i]",
                "input[placeholder*='last' i]"
            ])
        
        # Generic input selectors
        selectors.extend([
            f"input[placeholder*='{target}' i]",
            f"input[name*='{target.lower()}']",
            f"input[id*='{target.lower()}']",
            f"textarea[placeholder*='{target}' i]",
            f"textarea[name*='{target.lower()}']",
            "input[type='text']",
            "input:not([type])",
            "input:visible"
        ])
        
        return selectors

def generate_intelligent_action_plan(prompt, website_url):
    """Generate intelligent action plan from natural language prompt with advanced understanding"""
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
        "description": "Wait for page to fully load",
        "target": "time",
        "value": "3000",
        "timeout": 5000
    })

    # Advanced prompt parsing with better understanding
    actions.extend(_parse_advanced_actions(prompt, website_url))

    # Always add screenshot if mentioned or at the end
    if "screenshot" in prompt_lower or len([a for a in actions if a["type"] == "screenshot"]) == 0:
        actions.append({
            "type": "screenshot",
            "description": "Take final screenshot",
            "target": "",
            "value": "",
            "timeout": 5000
        })

    return actions

def _parse_advanced_actions(prompt, website_url):
    """Advanced parsing of natural language prompts into specific actions"""
    actions = []
    prompt_lower = prompt.lower()

    # Split prompt into sentences for better understanding
    sentences = [s.strip() for s in prompt.replace(',', '.').split('.') if s.strip()]

    for sentence in sentences:
        sentence_lower = sentence.lower()

        # Login actions with better pattern matching
        if any(word in sentence_lower for word in ['login', 'log in', 'sign in', 'signin']):
            actions.extend(_generate_smart_login_actions(sentence))

        # Search actions with better understanding
        elif any(word in sentence_lower for word in ['search', 'find', 'look for', 'query']):
            actions.extend(_generate_smart_search_actions(sentence))

        # Click actions with specific targeting
        elif any(word in sentence_lower for word in ['click', 'press', 'tap', 'select']):
            actions.extend(_generate_smart_click_actions(sentence))

        # Type/input actions
        elif any(word in sentence_lower for word in ['type', 'enter', 'input', 'fill']):
            actions.extend(_generate_smart_type_actions(sentence))

        # Navigation actions
        elif any(word in sentence_lower for word in ['go to', 'navigate', 'visit', 'open']):
            actions.extend(_generate_smart_navigation_actions(sentence, website_url))

        # Form submission
        elif any(word in sentence_lower for word in ['submit', 'send', 'post']):
            actions.extend(_generate_smart_submit_actions(sentence))

        # Shopping/cart actions
        elif any(word in sentence_lower for word in ['add to cart', 'buy', 'purchase', 'add first']):
            actions.extend(_generate_smart_cart_actions(sentence))

        # Scroll actions
        elif any(word in sentence_lower for word in ['scroll', 'scroll down', 'scroll up']):
            actions.extend(_generate_smart_scroll_actions(sentence))

        # Wait actions
        elif any(word in sentence_lower for word in ['wait', 'pause', 'delay']):
            actions.extend(_generate_smart_wait_actions(sentence))

    return actions

def _generate_smart_login_actions(sentence):
    """Generate smart login actions from sentence"""
    actions = []

    # Extract credentials with better patterns
    email_patterns = [
        r'with\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'email[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    ]

    password_patterns = [
        r'password[:\s/]+([^\s,]+)',
        r'/\s*([^\s,]+)',
        r'with\s+\w+\s*/\s*([^\s,]+)'
    ]

    username_patterns = [
        r'with\s+([a-zA-Z0-9_]+)\s*/',
        r'username[:\s]+([a-zA-Z0-9_]+)',
        r'user[:\s]+([a-zA-Z0-9_]+)'
    ]

    email = None
    password = None
    username = None

    # Try to extract email
    for pattern in email_patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            email = match.group(1)
            break

    # Try to extract password
    for pattern in password_patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            password = match.group(1)
            break

    # Try to extract username
    for pattern in username_patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            username = match.group(1)
            break

    # Add login actions based on what we found
    if username:
        actions.append({
            "type": "type",
            "description": f"Enter username: {username}",
            "target": "username",
            "value": username,
            "timeout": 10000
        })

    if email:
        actions.append({
            "type": "type",
            "description": f"Enter email: {email}",
            "target": "email",
            "value": email,
            "timeout": 10000
        })

    if password:
        actions.append({
            "type": "type",
            "description": f"Enter password: {password}",
            "target": "password",
            "value": password,
            "timeout": 10000
        })

    # Add login button click
    actions.append({
        "type": "click",
        "description": "Click login button",
        "target": "login",
        "value": "",
        "timeout": 10000
    })

    return actions

def _generate_smart_search_actions(sentence):
    """Generate smart search actions from sentence"""
    actions = []

    # Extract search term with better patterns
    search_patterns = [
        r'search for ["\']([^"\']+)["\']',
        r'search for (.+?)(?:\s+and|\s+then|\s+in|$)',
        r'find ["\']([^"\']+)["\']',
        r'find (.+?)(?:\s+and|\s+then|\s+in|$)',
        r'look for ["\']([^"\']+)["\']',
        r'look for (.+?)(?:\s+and|\s+then|\s+in|$)',
        r'query ["\']([^"\']+)["\']',
        r'query (.+?)(?:\s+and|\s+then|\s+in|$)'
    ]

    search_term = "test"  # Default
    for pattern in search_patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            search_term = match.group(1).strip().strip('"\'')
            break

    # Click search box first
    actions.append({
        "type": "click",
        "description": "Click search box",
        "target": "search",
        "value": "",
        "timeout": 10000
    })

    # Type search term
    actions.append({
        "type": "type",
        "description": f"Search for: {search_term}",
        "target": "search",
        "value": search_term,
        "timeout": 10000
    })

    # Submit search (press Enter or click search button)
    if "press enter" in sentence.lower() or "hit enter" in sentence.lower():
        actions.append({
            "type": "key",
            "description": "Press Enter to search",
            "target": "search",
            "value": "Enter",
            "timeout": 10000
        })
    else:
        actions.append({
            "type": "click",
            "description": "Click search button",
            "target": "search_button",
            "value": "",
            "timeout": 10000
        })

    return actions

def _generate_smart_click_actions(sentence):
    """Generate smart click actions from sentence"""
    actions = []

    # Extract what to click with better patterns
    click_patterns = [
        r'click (?:on )?(?:the )?["\']([^"\']+)["\']',
        r'click (?:on )?(?:the )?(.+?)(?:\s+and|\s+then|\s+to|$)',
        r'press (?:the )?["\']([^"\']+)["\']',
        r'press (?:the )?(.+?)(?:\s+and|\s+then|\s+to|$)',
        r'tap (?:on )?(?:the )?["\']([^"\']+)["\']',
        r'tap (?:on )?(?:the )?(.+?)(?:\s+and|\s+then|\s+to|$)',
        r'select (?:the )?["\']([^"\']+)["\']',
        r'select (?:the )?(.+?)(?:\s+and|\s+then|\s+to|$)'
    ]

    target = "button"  # Default
    for pattern in click_patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            target = match.group(1).strip().strip('"\'')
            break

    # Special handling for common elements
    if "first" in sentence.lower():
        if "result" in sentence.lower():
            target = "first_result"
        elif "product" in sentence.lower():
            target = "first_product"
        elif "link" in sentence.lower():
            target = "first_link"
        else:
            target = "first_item"

    actions.append({
        "type": "click",
        "description": f"Click {target}",
        "target": target,
        "value": "",
        "timeout": 10000
    })

    return actions

def _generate_smart_type_actions(sentence):
    """Generate smart typing actions from sentence"""
    actions = []

    # Extract what to type and where
    type_patterns = [
        r'type ["\']([^"\']+)["\'] (?:in|into) (?:the )?(.+?)(?:\s+and|\s+then|$)',
        r'enter ["\']([^"\']+)["\'] (?:in|into) (?:the )?(.+?)(?:\s+and|\s+then|$)',
        r'input ["\']([^"\']+)["\'] (?:in|into) (?:the )?(.+?)(?:\s+and|\s+then|$)',
        r'fill (?:the )?(.+?) with ["\']([^"\']+)["\']',
        r'type ["\']([^"\']+)["\']',
        r'enter ["\']([^"\']+)["\']'
    ]

    text = ""
    target = "input"

    for pattern in type_patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            if "with" in pattern:  # fill X with Y pattern
                target = match.group(1).strip()
                text = match.group(2).strip()
            else:  # type X into Y pattern
                text = match.group(1).strip()
                if match.lastindex > 1:
                    target = match.group(2).strip()
            break

    if text:
        actions.append({
            "type": "type",
            "description": f"Type '{text}' into {target}",
            "target": target,
            "value": text,
            "timeout": 10000
        })

    return actions

def _generate_smart_navigation_actions(sentence, website_url):
    """Generate smart navigation actions from sentence"""
    actions = []

    # Extract navigation target
    nav_patterns = [
        r'go to (?:the )?(.+?)(?:\s+and|\s+then|$)',
        r'navigate to (?:the )?(.+?)(?:\s+and|\s+then|$)',
        r'visit (?:the )?(.+?)(?:\s+and|\s+then|$)',
        r'open (?:the )?(.+?)(?:\s+and|\s+then|$)'
    ]

    target = ""
    for pattern in nav_patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            target = match.group(1).strip()
            break

    if target and not target.startswith('http'):
        # It's likely a page section or relative navigation
        actions.append({
            "type": "click",
            "description": f"Navigate to {target}",
            "target": target,
            "value": "",
            "timeout": 10000
        })

    return actions

def _generate_smart_submit_actions(sentence):
    """Generate smart submit actions from sentence"""
    actions = []

    # Extract what to submit
    if "form" in sentence.lower():
        target = "form_submit"
    elif "search" in sentence.lower():
        target = "search_submit"
    else:
        target = "submit"

    actions.append({
        "type": "click",
        "description": f"Submit {target}",
        "target": target,
        "value": "",
        "timeout": 10000
    })

    return actions

def _generate_smart_cart_actions(sentence):
    """Generate smart shopping cart actions from sentence"""
    actions = []

    if "first" in sentence.lower():
        actions.append({
            "type": "click",
            "description": "Click first product",
            "target": "first_product",
            "value": "",
            "timeout": 10000
        })

    actions.append({
        "type": "click",
        "description": "Add to cart",
        "target": "add_to_cart",
        "value": "",
        "timeout": 10000
    })

    return actions

def _generate_smart_scroll_actions(sentence):
    """Generate smart scroll actions from sentence"""
    actions = []

    if "down" in sentence.lower():
        direction = "down"
    elif "up" in sentence.lower():
        direction = "up"
    else:
        direction = "down"  # Default

    actions.append({
        "type": "scroll",
        "description": f"Scroll {direction}",
        "target": direction,
        "value": "500",  # pixels
        "timeout": 5000
    })

    return actions

def _generate_smart_wait_actions(sentence):
    """Generate smart wait actions from sentence"""
    actions = []

    # Extract wait time if specified
    time_match = re.search(r'(\d+)\s*(?:second|sec|ms|millisecond)', sentence, re.IGNORECASE)
    if time_match:
        wait_time = int(time_match.group(1))
        if "ms" in sentence.lower() or "millisecond" in sentence.lower():
            wait_ms = wait_time
        else:
            wait_ms = wait_time * 1000
    else:
        wait_ms = 2000  # Default 2 seconds

    actions.append({
        "type": "wait",
        "description": f"Wait {wait_ms}ms",
        "target": "time",
        "value": str(wait_ms),
        "timeout": wait_ms + 1000
    })

    return actions

def _generate_form_actions(prompt):
    """Generate form filling actions"""
    actions = []
    
    # Extract name if present
    name_match = re.search(r'name ["\']([^"\']+)["\']', prompt, re.IGNORECASE)
    name = name_match.group(1) if name_match else "John Doe"
    
    # Extract email if present
    email_match = re.search(r'email ["\']([^"\']+)["\']', prompt, re.IGNORECASE)
    email = email_match.group(1) if email_match else "john.doe@example.com"
    
    actions.extend([
        {
            "type": "type",
            "description": f"Fill name field with: {name}",
            "target": "name",
            "value": name,
            "timeout": 10000
        },
        {
            "type": "type",
            "description": f"Fill email field with: {email}",
            "target": "email",
            "value": email,
            "timeout": 10000
        }
    ])
    
    if "submit" in prompt.lower():
        actions.append({
            "type": "click",
            "description": "Submit form",
            "target": "button[type='submit']",
            "value": "",
            "timeout": 10000
        })
    
    return actions

def _generate_cart_actions(prompt):
    """Generate shopping cart actions"""
    return [
        {
            "type": "click",
            "description": "Click first product",
            "target": ".product:first-child",
            "value": "",
            "timeout": 10000
        },
        {
            "type": "click",
            "description": "Add to cart",
            "target": "add to cart",
            "value": "",
            "timeout": 10000
        }
    ]

def _generate_verification_actions(prompt):
    """Generate verification actions"""
    actions = []
    
    if "title" in prompt.lower():
        title_match = re.search(r'title contains ["\']([^"\']+)["\']', prompt, re.IGNORECASE)
        title_text = title_match.group(1) if title_match else "Example"
        
        actions.append({
            "type": "verify",
            "description": f"Verify page title contains '{title_text}'",
            "target": "title",
            "value": title_text,
            "timeout": 5000
        })
    
    return actions

def execute_real_test_session(session_id):
    """Execute test session with REAL browser automation"""
    session = test_sessions[session_id]
    browser_automation = None
    
    try:
        print(f"🚀 Starting REAL test execution for session {session_id}")
        
        # Initialize real browser
        browser_automation = RealBrowserAutomation()
        browser_automation.initialize()
        
        active_executions[session_id] = {
            "browser": browser_automation,
            "current_action": 0,
            "start_time": time.time()
        }
        
        successful_actions = 0
        failed_actions = 0
        action_results = []
        
        # Execute each action on the real browser
        for i, action in enumerate(session["action_plan"]["actions"]):
            active_executions[session_id]["current_action"] = i
            
            result = browser_automation.execute_action(action, session_id)
            action_results.append({
                "action": action,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            if result["status"] == "success":
                successful_actions += 1
            else:
                failed_actions += 1
                # Continue with other actions even if one fails
            
            # Add delay between actions for stability
            time.sleep(2)
        
        # Update session with results
        session["status"] = "completed"
        session["completed_at"] = datetime.utcnow().isoformat()
        session["successful_actions"] = successful_actions
        session["failed_actions"] = failed_actions
        session["total_duration"] = int(time.time() - active_executions[session_id]["start_time"])
        session["action_results"] = action_results
        
        print(f"🎉 REAL test completed: {successful_actions} successful, {failed_actions} failed")
        
        # Keep browser open for longer to see results
        print("🔍 Keeping browser open for 30 seconds to view results...")
        print("🌐 You can interact with the browser window that opened!")
        print("⏰ Browser will close automatically in 30 seconds...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ REAL test execution failed: {e}")
        session["status"] = "failed"
        session["error_summary"] = str(e)
        session["completed_at"] = datetime.utcnow().isoformat()
        
    finally:
        # Cleanup browser
        if browser_automation:
            browser_automation.cleanup()
        if session_id in active_executions:
            del active_executions[session_id]

class RequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        
        if path == '/health':
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "playwright_available": PLAYWRIGHT_AVAILABLE,
                "active_sessions": len(active_executions),
                "total_sessions": len(test_sessions),
                "mode": "REAL_BROWSER_AUTOMATION",
                "timestamp": datetime.utcnow().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path.startswith('/api/tests/') and len(path.split('/')) == 4:
            # Get test results
            session_id = path.split('/')[-1]
            
            if session_id in test_sessions:
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                session = test_sessions[session_id]
                execution_status = {}
                
                if session_id in active_executions:
                    exec_info = active_executions[session_id]
                    execution_status = {
                        "current_action": exec_info["current_action"],
                        "progress": (exec_info["current_action"] / len(session["action_plan"]["actions"])) * 100
                    }
                
                response = {
                    "session": session,
                    "execution_status": execution_status
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        
        # Read request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
        except:
            self.send_response(400)
            self.end_headers()
            return
        
        if path == '/api/tests/create':
            # Create test
            session_id = str(uuid.uuid4())

            # Debug: Print received data
            print(f"🔍 DEBUG: Received prompt: '{data.get('prompt', 'NO PROMPT')}'")
            print(f"🔍 DEBUG: Received website_url: '{data.get('website_url', 'NO URL')}'")
            print(f"🔍 DEBUG: Full data received: {data}")

            # Generate intelligent action plan
            actions = generate_intelligent_action_plan(data["prompt"], data["website_url"])
            
            action_plan = {
                "id": str(uuid.uuid4()),
                "website_url": data["website_url"],
                "actions": actions,
                "confidence": 0.95,
                "reasoning": "Generated for REAL browser automation with intelligent element detection",
                "estimated_duration": len(actions) * 5,
                "risk_level": "low"
            }
            
            # Store session
            test_sessions[session_id] = {
                "id": session_id,
                "website_url": data["website_url"],
                "original_prompt": data["prompt"],
                "action_plan": action_plan,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "total_actions": len(actions),
                "successful_actions": 0,
                "failed_actions": 0,
                "screenshots": []
            }
            
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "session_id": session_id,
                "action_plan": action_plan,
                "estimated_duration": action_plan["estimated_duration"],
                "risk_assessment": action_plan["risk_level"]
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/tests/execute':
            # Execute test with REAL browser
            session_id = data["session_id"]
            
            if session_id not in test_sessions:
                self.send_response(404)
                self.end_headers()
                return
            
            session = test_sessions[session_id]
            
            if session["status"] != "pending":
                self.send_response(400)
                self.end_headers()
                return
            
            # Start REAL execution in background thread
            session["status"] = "running"
            session["started_at"] = datetime.utcnow().isoformat()
            
            thread = threading.Thread(target=execute_real_test_session, args=(session_id,))
            thread.daemon = True
            thread.start()
            
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "session_id": session_id,
                "status": "running",
                "message": "🚀 REAL browser automation started! Browser will open shortly..."
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    """Run the HTTP server"""
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    
    print("🚀 Starting REAL Browser Automation Server")
    print("🌐 This version will actually open browsers and perform actions!")
    print(f"📡 Server running on http://localhost:8000")
    print(f"🎭 Playwright available: {PLAYWRIGHT_AVAILABLE}")
    print("🔥 REAL browser automation mode enabled!")
    print()
    
    if not PLAYWRIGHT_AVAILABLE:
        print("⚠️  To enable real browser automation:")
        print("   pip install playwright")
        print("   playwright install")
        print()
    else:
        print("✅ Ready to launch real browsers and perform actual automation!")
        print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()
