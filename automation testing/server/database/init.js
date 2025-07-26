const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const DB_PATH = process.env.DB_PATH || './data/tests.db';

// Ensure data directory exists
const dataDir = path.dirname(DB_PATH);
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

const db = new sqlite3.Database(DB_PATH);

const initializeDatabase = () => {
  return new Promise((resolve, reject) => {
    db.serialize(() => {
      // Test sessions table
      db.run(`
        CREATE TABLE IF NOT EXISTS test_sessions (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          description TEXT,
          status TEXT DEFAULT 'pending',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          total_steps INTEGER DEFAULT 0,
          passed_steps INTEGER DEFAULT 0,
          failed_steps INTEGER DEFAULT 0
        )
      `);

      // Test steps table
      db.run(`
        CREATE TABLE IF NOT EXISTS test_steps (
          id TEXT PRIMARY KEY,
          session_id TEXT NOT NULL,
          step_number INTEGER NOT NULL,
          original_command TEXT NOT NULL,
          translated_action TEXT,
          action_type TEXT,
          target_element TEXT,
          expected_result TEXT,
          actual_result TEXT,
          status TEXT DEFAULT 'pending',
          screenshot_path TEXT,
          error_message TEXT,
          execution_time INTEGER,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (session_id) REFERENCES test_sessions (id)
        )
      `);

      // Test results table for detailed logging
      db.run(`
        CREATE TABLE IF NOT EXISTS test_results (
          id TEXT PRIMARY KEY,
          step_id TEXT NOT NULL,
          result_type TEXT NOT NULL,
          result_data TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (step_id) REFERENCES test_steps (id)
        )
      `, (err) => {
        if (err) {
          reject(err);
        } else {
          resolve();
        }
      });
    });
  });
};

const getDatabase = () => db;

module.exports = {
  initializeDatabase,
  getDatabase
};
