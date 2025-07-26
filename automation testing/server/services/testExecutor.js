const { chromium, firefox, webkit } = require('playwright');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const { getDatabase } = require('../database/init');
const { SUPPORTED_ACTIONS } = require('./nlpService');
const logger = require('../utils/logger');

const db = getDatabase();

// Ensure screenshots directory exists
const screenshotsDir = './screenshots';
if (!fs.existsSync(screenshotsDir)) {
  fs.mkdirSync(screenshotsDir, { recursive: true });
}

/**
 * Executes a complete test session
 * @param {string} sessionId - The test session ID
 * @param {Array} steps - Array of test steps to execute
 * @returns {Promise<Array>} - Array of execution results
 */
async function executeTest(sessionId, steps) {
  let browser = null;
  let context = null;
  let page = null;
  const results = [];

  try {
    logger.info(`Starting test execution for session: ${sessionId}`);

    // Launch browser
    const browserType = process.env.BROWSER_TYPE || 'chromium';
    const headless = process.env.HEADLESS !== 'false';
    
    browser = await getBrowser(browserType).launch({ 
      headless,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    context = await browser.newContext({
      viewport: { width: 1280, height: 720 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    });
    
    page = await context.newPage();

    // Execute each step
    for (const step of steps) {
      const result = await executeStep(page, step, sessionId);
      results.push(result);
      
      // Stop execution if a critical step fails
      if (result.status === 'failed' && result.critical) {
        logger.warn(`Critical step failed, stopping execution: ${step.id}`);
        break;
      }
    }

    logger.info(`Test execution completed for session: ${sessionId}`);
    return results;

  } catch (error) {
    logger.error('Error during test execution:', error);
    throw error;
  } finally {
    // Cleanup
    if (page) await page.close();
    if (context) await context.close();
    if (browser) await browser.close();
  }
}

/**
 * Executes a single test step
 * @param {Page} page - Playwright page object
 * @param {Object} step - Test step to execute
 * @param {string} sessionId - Session ID for context
 * @returns {Promise<Object>} - Execution result
 */
async function executeStep(page, step, sessionId) {
  const startTime = Date.now();
  let screenshotPath = null;
  let result = {
    stepId: step.id,
    status: 'pending',
    error: null,
    actualResult: null,
    executionTime: 0
  };

  try {
    logger.info(`Executing step ${step.step_number}: ${step.original_command}`);

    // Parse the translated action
    const action = JSON.parse(step.translated_action);
    
    // Update step status to running
    await updateStepStatus(step.id, 'running');

    // Execute the action based on type
    switch (action.type) {
      case SUPPORTED_ACTIONS.NAVIGATE:
        await executeNavigate(page, action);
        break;
      
      case SUPPORTED_ACTIONS.CLICK:
        await executeClick(page, action);
        break;
      
      case SUPPORTED_ACTIONS.TYPE:
        await executeType(page, action);
        break;
      
      case SUPPORTED_ACTIONS.WAIT:
        await executeWait(page, action);
        break;
      
      case SUPPORTED_ACTIONS.VERIFY:
        result.actualResult = await executeVerify(page, action);
        break;
      
      case SUPPORTED_ACTIONS.SCROLL:
        await executeScroll(page, action);
        break;
      
      case SUPPORTED_ACTIONS.HOVER:
        await executeHover(page, action);
        break;
      
      case SUPPORTED_ACTIONS.SELECT:
        await executeSelect(page, action);
        break;
      
      case SUPPORTED_ACTIONS.SCREENSHOT:
        screenshotPath = await takeScreenshot(page, sessionId, step.id);
        break;
      
      default:
        throw new Error(`Unsupported action type: ${action.type}`);
    }

    // Take screenshot after successful execution
    if (!screenshotPath) {
      screenshotPath = await takeScreenshot(page, sessionId, step.id);
    }

    result.status = 'passed';
    result.actualResult = result.actualResult || 'Action completed successfully';

  } catch (error) {
    logger.error(`Step execution failed: ${step.id}`, error);
    result.status = 'failed';
    result.error = error.message;
    
    // Take screenshot on failure
    try {
      screenshotPath = await takeScreenshot(page, sessionId, step.id, 'error');
    } catch (screenshotError) {
      logger.error('Failed to take error screenshot:', screenshotError);
    }
  } finally {
    result.executionTime = Date.now() - startTime;
    
    // Update step in database
    await updateStepResult(step.id, result, screenshotPath);
  }

  return result;
}

/**
 * Navigate to a URL
 */
async function executeNavigate(page, action) {
  const url = action.value || action.target;
  logger.info(`Navigating to: ${url}`);
  await page.goto(url, { waitUntil: 'networkidle', timeout: action.timeout });
}

/**
 * Click on an element
 */
async function executeClick(page, action) {
  logger.info(`Clicking element: ${action.target}`);
  
  // Try multiple selector strategies
  const selectors = action.target.split(',').map(s => s.trim());
  
  for (const selector of selectors) {
    try {
      await page.waitForSelector(selector, { timeout: 5000 });
      await page.click(selector, { timeout: action.timeout });
      return;
    } catch (error) {
      logger.debug(`Selector failed: ${selector}`, error.message);
    }
  }
  
  throw new Error(`Could not find clickable element with any of the selectors: ${action.target}`);
}

/**
 * Type text into an input field
 */
async function executeType(page, action) {
  logger.info(`Typing into element: ${action.target}`);
  
  const selectors = action.target.split(',').map(s => s.trim());
  
  for (const selector of selectors) {
    try {
      await page.waitForSelector(selector, { timeout: 5000 });
      await page.fill(selector, action.value);
      return;
    } catch (error) {
      logger.debug(`Selector failed: ${selector}`, error.message);
    }
  }
  
  throw new Error(`Could not find input element with any of the selectors: ${action.target}`);
}

/**
 * Wait for an element or time
 */
async function executeWait(page, action) {
  if (action.target === 'time' || !action.target) {
    const waitTime = parseInt(action.value) || 1000;
    logger.info(`Waiting for ${waitTime}ms`);
    await page.waitForTimeout(waitTime);
  } else {
    logger.info(`Waiting for element: ${action.target}`);
    await page.waitForSelector(action.target, { timeout: action.timeout });
  }
}

/**
 * Verify text or element presence
 */
async function executeVerify(page, action) {
  logger.info(`Verifying: ${action.target}`);
  
  if (action.target === 'title') {
    const title = await page.title();
    const expected = action.value;
    if (title.includes(expected)) {
      return `Title verification passed: "${title}" contains "${expected}"`;
    } else {
      throw new Error(`Title verification failed: "${title}" does not contain "${expected}"`);
    }
  } else {
    // Verify element presence or text content
    const element = await page.locator(action.target).first();
    const isVisible = await element.isVisible();
    
    if (!isVisible) {
      throw new Error(`Element not visible: ${action.target}`);
    }
    
    if (action.value) {
      const text = await element.textContent();
      if (!text.includes(action.value)) {
        throw new Error(`Text verification failed: "${text}" does not contain "${action.value}"`);
      }
      return `Text verification passed: found "${action.value}"`;
    }
    
    return `Element verification passed: ${action.target} is visible`;
  }
}

/**
 * Scroll to an element or in a direction
 */
async function executeScroll(page, action) {
  logger.info(`Scrolling: ${action.target}`);

  if (action.target === 'top') {
    await page.evaluate(() => window.scrollTo(0, 0));
  } else if (action.target === 'bottom') {
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  } else {
    // Scroll to element
    await page.locator(action.target).scrollIntoViewIfNeeded();
  }
}

/**
 * Hover over an element
 */
async function executeHover(page, action) {
  logger.info(`Hovering over element: ${action.target}`);
  await page.hover(action.target, { timeout: action.timeout });
}

/**
 * Select option from dropdown
 */
async function executeSelect(page, action) {
  logger.info(`Selecting option: ${action.value} from ${action.target}`);
  await page.selectOption(action.target, action.value, { timeout: action.timeout });
}

/**
 * Take a screenshot
 */
async function takeScreenshot(page, sessionId, stepId, type = 'step') {
  try {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${sessionId}_${stepId}_${type}_${timestamp}.png`;
    const screenshotPath = path.join(screenshotsDir, filename);

    await page.screenshot({
      path: screenshotPath,
      fullPage: true
    });

    logger.info(`Screenshot saved: ${screenshotPath}`);
    return `/screenshots/${filename}`;
  } catch (error) {
    logger.error('Failed to take screenshot:', error);
    return null;
  }
}

/**
 * Get browser instance based on type
 */
function getBrowser(browserType) {
  switch (browserType.toLowerCase()) {
    case 'firefox':
      return firefox;
    case 'webkit':
    case 'safari':
      return webkit;
    case 'chromium':
    case 'chrome':
    default:
      return chromium;
  }
}

/**
 * Update step status in database
 */
async function updateStepStatus(stepId, status) {
  return new Promise((resolve, reject) => {
    db.run(
      'UPDATE test_steps SET status = ? WHERE id = ?',
      [status, stepId],
      function(err) {
        if (err) reject(err);
        else resolve();
      }
    );
  });
}

/**
 * Update step result in database
 */
async function updateStepResult(stepId, result, screenshotPath) {
  return new Promise((resolve, reject) => {
    db.run(
      `UPDATE test_steps
       SET status = ?, actual_result = ?, error_message = ?,
           execution_time = ?, screenshot_path = ?
       WHERE id = ?`,
      [result.status, result.actualResult, result.error,
       result.executionTime, screenshotPath, stepId],
      function(err) {
        if (err) reject(err);
        else resolve();
      }
    );
  });
}

module.exports = {
  executeTest,
  executeStep,
  takeScreenshot
};
