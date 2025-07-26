const express = require('express');
const { v4: uuidv4 } = require('uuid');
const Joi = require('joi');
const { getDatabase } = require('../database/init');
const { translateCommand } = require('../services/nlpService');
const { executeTest } = require('../services/testExecutor');
const logger = require('../utils/logger');

const router = express.Router();
const db = getDatabase();

// Validation schemas
const createTestSchema = Joi.object({
  name: Joi.string().required().min(1).max(255),
  description: Joi.string().max(1000),
  commands: Joi.array().items(Joi.string().required()).min(1).required(),
  targetUrl: Joi.string().uri().required()
});

const executeStepSchema = Joi.object({
  sessionId: Joi.string().required(),
  stepId: Joi.string().required()
});

// Create a new test session
router.post('/create', async (req, res) => {
  try {
    const { error, value } = createTestSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const { name, description, commands, targetUrl } = value;
    const sessionId = uuidv4();

    // Create test session
    await new Promise((resolve, reject) => {
      db.run(
        'INSERT INTO test_sessions (id, name, description, total_steps) VALUES (?, ?, ?, ?)',
        [sessionId, name, description, commands.length],
        function(err) {
          if (err) reject(err);
          else resolve();
        }
      );
    });

    // Translate commands and create test steps
    const steps = [];
    for (let i = 0; i < commands.length; i++) {
      const stepId = uuidv4();
      const command = commands[i];
      
      try {
        const translatedAction = await translateCommand(command, targetUrl);
        
        await new Promise((resolve, reject) => {
          db.run(
            `INSERT INTO test_steps 
             (id, session_id, step_number, original_command, translated_action, action_type, target_element) 
             VALUES (?, ?, ?, ?, ?, ?, ?)`,
            [stepId, sessionId, i + 1, command, JSON.stringify(translatedAction), 
             translatedAction.type, translatedAction.target],
            function(err) {
              if (err) reject(err);
              else resolve();
            }
          );
        });

        steps.push({
          id: stepId,
          stepNumber: i + 1,
          originalCommand: command,
          translatedAction,
          status: 'pending'
        });
      } catch (error) {
        logger.error(`Failed to translate command: ${command}`, error);
        steps.push({
          id: stepId,
          stepNumber: i + 1,
          originalCommand: command,
          status: 'failed',
          error: error.message
        });
      }
    }

    res.json({
      sessionId,
      name,
      description,
      targetUrl,
      steps,
      status: 'created'
    });

  } catch (error) {
    logger.error('Error creating test session:', error);
    res.status(500).json({ error: 'Failed to create test session' });
  }
});

// Execute a test session
router.post('/execute/:sessionId', async (req, res) => {
  try {
    const { sessionId } = req.params;

    // Get test session and steps
    const session = await new Promise((resolve, reject) => {
      db.get('SELECT * FROM test_sessions WHERE id = ?', [sessionId], (err, row) => {
        if (err) reject(err);
        else resolve(row);
      });
    });

    if (!session) {
      return res.status(404).json({ error: 'Test session not found' });
    }

    const steps = await new Promise((resolve, reject) => {
      db.all(
        'SELECT * FROM test_steps WHERE session_id = ? ORDER BY step_number',
        [sessionId],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });

    // Update session status to running
    await new Promise((resolve, reject) => {
      db.run(
        'UPDATE test_sessions SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        ['running', sessionId],
        function(err) {
          if (err) reject(err);
          else resolve();
        }
      );
    });

    // Execute test steps
    const results = await executeTest(sessionId, steps);

    // Update session with final results
    const passedSteps = results.filter(r => r.status === 'passed').length;
    const failedSteps = results.filter(r => r.status === 'failed').length;
    const finalStatus = failedSteps > 0 ? 'failed' : 'passed';

    await new Promise((resolve, reject) => {
      db.run(
        `UPDATE test_sessions 
         SET status = ?, passed_steps = ?, failed_steps = ?, updated_at = CURRENT_TIMESTAMP 
         WHERE id = ?`,
        [finalStatus, passedSteps, failedSteps, sessionId],
        function(err) {
          if (err) reject(err);
          else resolve();
        }
      );
    });

    res.json({
      sessionId,
      status: finalStatus,
      results,
      summary: {
        total: steps.length,
        passed: passedSteps,
        failed: failedSteps
      }
    });

  } catch (error) {
    logger.error('Error executing test session:', error);
    res.status(500).json({ error: 'Failed to execute test session' });
  }
});

// Get test session details
router.get('/:sessionId', async (req, res) => {
  try {
    const { sessionId } = req.params;

    const session = await new Promise((resolve, reject) => {
      db.get('SELECT * FROM test_sessions WHERE id = ?', [sessionId], (err, row) => {
        if (err) reject(err);
        else resolve(row);
      });
    });

    if (!session) {
      return res.status(404).json({ error: 'Test session not found' });
    }

    const steps = await new Promise((resolve, reject) => {
      db.all(
        'SELECT * FROM test_steps WHERE session_id = ? ORDER BY step_number',
        [sessionId],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows.map(row => ({
            ...row,
            translatedAction: row.translated_action ? JSON.parse(row.translated_action) : null
          })));
        }
      );
    });

    res.json({
      ...session,
      steps
    });

  } catch (error) {
    logger.error('Error fetching test session:', error);
    res.status(500).json({ error: 'Failed to fetch test session' });
  }
});

// Get all test sessions
router.get('/', async (req, res) => {
  try {
    const sessions = await new Promise((resolve, reject) => {
      db.all(
        'SELECT * FROM test_sessions ORDER BY created_at DESC',
        [],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });

    res.json(sessions);

  } catch (error) {
    logger.error('Error fetching test sessions:', error);
    res.status(500).json({ error: 'Failed to fetch test sessions' });
  }
});

// Delete a test session
router.delete('/:sessionId', async (req, res) => {
  try {
    const { sessionId } = req.params;

    // Delete steps first (foreign key constraint)
    await new Promise((resolve, reject) => {
      db.run('DELETE FROM test_steps WHERE session_id = ?', [sessionId], function(err) {
        if (err) reject(err);
        else resolve();
      });
    });

    // Delete session
    await new Promise((resolve, reject) => {
      db.run('DELETE FROM test_sessions WHERE id = ?', [sessionId], function(err) {
        if (err) reject(err);
        else if (this.changes === 0) reject(new Error('Session not found'));
        else resolve();
      });
    });

    res.json({ message: 'Test session deleted successfully' });

  } catch (error) {
    logger.error('Error deleting test session:', error);
    res.status(500).json({ error: 'Failed to delete test session' });
  }
});

module.exports = router;
