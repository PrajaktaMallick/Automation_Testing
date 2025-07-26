const OpenAI = require('openai');
const logger = require('../utils/logger');

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// Action types that our system supports
const SUPPORTED_ACTIONS = {
  NAVIGATE: 'navigate',
  CLICK: 'click',
  TYPE: 'type',
  WAIT: 'wait',
  VERIFY: 'verify',
  SCROLL: 'scroll',
  HOVER: 'hover',
  SELECT: 'select',
  UPLOAD: 'upload',
  SCREENSHOT: 'screenshot'
};

// System prompt for the OpenAI model
const SYSTEM_PROMPT = `You are an expert web automation assistant that converts natural language commands into structured test actions for Playwright automation.

Your task is to analyze user commands and convert them into JSON objects with the following structure:
{
  "type": "action_type",
  "target": "css_selector_or_text",
  "value": "input_value_if_needed",
  "description": "human_readable_description",
  "waitFor": "optional_wait_condition",
  "timeout": optional_timeout_in_ms
}

Supported action types:
- navigate: Navigate to a URL
- click: Click on an element
- type: Type text into an input field
- wait: Wait for an element or time
- verify: Verify text or element presence
- scroll: Scroll to an element or direction
- hover: Hover over an element
- select: Select option from dropdown
- upload: Upload a file
- screenshot: Take a screenshot

Guidelines:
1. Use specific CSS selectors when possible (id, class, data attributes)
2. For text-based targeting, use the exact text content
3. Include reasonable timeouts (default 30000ms)
4. Be specific about what to verify
5. Handle common UI patterns (buttons, forms, links, etc.)

Examples:
Input: "Click the login button"
Output: {"type": "click", "target": "button:has-text('Login'), [data-testid='login-button'], .login-btn", "description": "Click the login button"}

Input: "Type 'john@example.com' in the email field"
Output: {"type": "type", "target": "input[type='email'], input[name='email'], #email", "value": "john@example.com", "description": "Type email address in the email field"}

Input: "Verify the page title contains 'Dashboard'"
Output: {"type": "verify", "target": "title", "value": "Dashboard", "description": "Verify page title contains 'Dashboard'"}

Always respond with valid JSON only, no additional text.`;

/**
 * Translates a natural language command into a structured test action
 * @param {string} command - The natural language command
 * @param {string} targetUrl - The target URL for context
 * @returns {Promise<Object>} - The translated action object
 */
async function translateCommand(command, targetUrl = '') {
  try {
    logger.info(`Translating command: "${command}" for URL: ${targetUrl}`);

    const userPrompt = `Target URL: ${targetUrl}
Command: "${command}"

Convert this command into a structured test action:`;

    const response = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.1,
      max_tokens: 500
    });

    const content = response.choices[0].message.content.trim();
    logger.info(`OpenAI response: ${content}`);

    // Parse the JSON response
    let translatedAction;
    try {
      translatedAction = JSON.parse(content);
    } catch (parseError) {
      logger.error('Failed to parse OpenAI response as JSON:', parseError);
      throw new Error('Invalid response format from AI model');
    }

    // Validate the translated action
    const validatedAction = validateAction(translatedAction);
    
    logger.info(`Successfully translated command to action:`, validatedAction);
    return validatedAction;

  } catch (error) {
    logger.error('Error translating command:', error);
    
    // Fallback to basic pattern matching if OpenAI fails
    const fallbackAction = getFallbackAction(command);
    if (fallbackAction) {
      logger.info('Using fallback action:', fallbackAction);
      return fallbackAction;
    }
    
    throw new Error(`Failed to translate command: ${error.message}`);
  }
}

/**
 * Validates and normalizes a translated action
 * @param {Object} action - The action object to validate
 * @returns {Object} - The validated action object
 */
function validateAction(action) {
  if (!action || typeof action !== 'object') {
    throw new Error('Action must be an object');
  }

  if (!action.type || !Object.values(SUPPORTED_ACTIONS).includes(action.type)) {
    throw new Error(`Invalid action type: ${action.type}`);
  }

  // Set defaults
  const validatedAction = {
    type: action.type,
    target: action.target || '',
    value: action.value || '',
    description: action.description || `Execute ${action.type} action`,
    waitFor: action.waitFor || null,
    timeout: action.timeout || 30000
  };

  // Type-specific validation
  switch (action.type) {
    case SUPPORTED_ACTIONS.NAVIGATE:
      if (!validatedAction.value && !validatedAction.target) {
        throw new Error('Navigate action requires a URL in value or target field');
      }
      break;
    
    case SUPPORTED_ACTIONS.TYPE:
      if (!validatedAction.value) {
        throw new Error('Type action requires a value to type');
      }
      break;
    
    case SUPPORTED_ACTIONS.VERIFY:
      if (!validatedAction.value && !validatedAction.target) {
        throw new Error('Verify action requires something to verify');
      }
      break;
  }

  return validatedAction;
}

/**
 * Provides fallback actions using simple pattern matching
 * @param {string} command - The original command
 * @returns {Object|null} - Fallback action or null
 */
function getFallbackAction(command) {
  const lowerCommand = command.toLowerCase();

  // Simple pattern matching for common commands
  if (lowerCommand.includes('click')) {
    const buttonText = extractQuotedText(command) || 'button';
    return {
      type: SUPPORTED_ACTIONS.CLICK,
      target: `button:has-text('${buttonText}'), [data-testid*='${buttonText.toLowerCase()}']`,
      description: `Click ${buttonText}`,
      timeout: 30000
    };
  }

  if (lowerCommand.includes('type') || lowerCommand.includes('enter')) {
    const text = extractQuotedText(command);
    if (text) {
      return {
        type: SUPPORTED_ACTIONS.TYPE,
        target: 'input, textarea',
        value: text,
        description: `Type "${text}"`,
        timeout: 30000
      };
    }
  }

  if (lowerCommand.includes('navigate') || lowerCommand.includes('go to')) {
    const url = extractUrl(command);
    if (url) {
      return {
        type: SUPPORTED_ACTIONS.NAVIGATE,
        target: url,
        value: url,
        description: `Navigate to ${url}`,
        timeout: 30000
      };
    }
  }

  return null;
}

/**
 * Extracts text within quotes from a command
 * @param {string} command - The command string
 * @returns {string|null} - Extracted text or null
 */
function extractQuotedText(command) {
  const matches = command.match(/['"`]([^'"`]+)['"`]/);
  return matches ? matches[1] : null;
}

/**
 * Extracts URL from a command
 * @param {string} command - The command string
 * @returns {string|null} - Extracted URL or null
 */
function extractUrl(command) {
  const urlRegex = /(https?:\/\/[^\s]+)/;
  const matches = command.match(urlRegex);
  return matches ? matches[1] : null;
}

module.exports = {
  translateCommand,
  SUPPORTED_ACTIONS
};
