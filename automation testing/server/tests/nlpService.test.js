const { translateCommand, SUPPORTED_ACTIONS } = require('../services/nlpService');

// Mock OpenAI for testing
jest.mock('openai', () => {
  return {
    __esModule: true,
    default: jest.fn().mockImplementation(() => ({
      chat: {
        completions: {
          create: jest.fn().mockResolvedValue({
            choices: [{
              message: {
                content: JSON.stringify({
                  type: 'click',
                  target: 'button:has-text("Login")',
                  description: 'Click the login button'
                })
              }
            }]
          })
        }
      }
    }))
  };
});

describe('NLP Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('translateCommand', () => {
    test('should translate a simple click command', async () => {
      const command = 'Click the login button';
      const result = await translateCommand(command, 'https://example.com');

      expect(result).toEqual({
        type: 'click',
        target: 'button:has-text("Login")',
        value: '',
        description: 'Click the login button',
        waitFor: null,
        timeout: 30000
      });
    });

    test('should handle fallback for simple commands', async () => {
      // Mock OpenAI to throw an error to test fallback
      const OpenAI = require('openai');
      const mockInstance = new OpenAI();
      mockInstance.chat.completions.create.mockRejectedValueOnce(new Error('API Error'));

      const command = 'Click "Submit"';
      const result = await translateCommand(command, 'https://example.com');

      expect(result.type).toBe(SUPPORTED_ACTIONS.CLICK);
      expect(result.target).toContain('Submit');
    });

    test('should validate action types', async () => {
      const OpenAI = require('openai');
      const mockInstance = new OpenAI();
      mockInstance.chat.completions.create.mockResolvedValueOnce({
        choices: [{
          message: {
            content: JSON.stringify({
              type: 'invalid_action',
              target: 'button'
            })
          }
        }]
      });

      await expect(translateCommand('Invalid command', 'https://example.com'))
        .rejects.toThrow('Invalid action type');
    });

    test('should handle type action validation', async () => {
      const OpenAI = require('openai');
      const mockInstance = new OpenAI();
      mockInstance.chat.completions.create.mockResolvedValueOnce({
        choices: [{
          message: {
            content: JSON.stringify({
              type: 'type',
              target: 'input[name="email"]'
              // Missing value
            })
          }
        }]
      });

      await expect(translateCommand('Type in email field', 'https://example.com'))
        .rejects.toThrow('Type action requires a value to type');
    });
  });

  describe('Fallback patterns', () => {
    test('should handle navigate commands', async () => {
      const OpenAI = require('openai');
      const mockInstance = new OpenAI();
      mockInstance.chat.completions.create.mockRejectedValueOnce(new Error('API Error'));

      const command = 'Navigate to https://example.com';
      const result = await translateCommand(command);

      expect(result.type).toBe(SUPPORTED_ACTIONS.NAVIGATE);
      expect(result.target).toBe('https://example.com');
    });

    test('should handle type commands with quoted text', async () => {
      const OpenAI = require('openai');
      const mockInstance = new OpenAI();
      mockInstance.chat.completions.create.mockRejectedValueOnce(new Error('API Error'));

      const command = 'Type "hello world" in the input';
      const result = await translateCommand(command);

      expect(result.type).toBe(SUPPORTED_ACTIONS.TYPE);
      expect(result.value).toBe('hello world');
    });
  });
});
