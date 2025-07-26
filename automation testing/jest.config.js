module.exports = {
  testEnvironment: 'node',
  testMatch: [
    '**/tests/**/*.test.js',
    '**/server/**/*.test.js'
  ],
  collectCoverageFrom: [
    'server/**/*.js',
    '!server/tests/**',
    '!server/node_modules/**'
  ],
  setupFilesAfterEnv: ['<rootDir>/server/tests/setup.js'],
  testTimeout: 30000
};
