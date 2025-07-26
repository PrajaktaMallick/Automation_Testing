// Test setup file
require('dotenv').config({ path: '.env.test' });

// Mock environment variables for testing
process.env.NODE_ENV = 'test';
process.env.DB_PATH = ':memory:'; // Use in-memory SQLite for tests
process.env.OPENAI_API_KEY = 'test-key';
process.env.LOG_LEVEL = 'error'; // Reduce log noise during tests

// Global test timeout
jest.setTimeout(30000);
