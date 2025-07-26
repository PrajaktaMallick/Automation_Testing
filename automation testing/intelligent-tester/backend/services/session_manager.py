"""
Session manager for handling test session persistence and retrieval
"""
import asyncio
import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import aiosqlite

from ..models.test_models import TestSession, TestStatus
from ..config import settings

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages test session persistence and retrieval"""
    
    def __init__(self):
        self.db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        self.connection_pool = None
        
    async def initialize(self):
        """Initialize the session manager and database"""
        await self._create_tables()
        logger.info("Session manager initialized")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.connection_pool:
            await self.connection_pool.close()
        logger.info("Session manager cleaned up")
    
    def is_healthy(self) -> bool:
        """Check if session manager is healthy"""
        return True  # Simple health check
    
    async def _create_tables(self):
        """Create database tables if they don't exist"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS test_sessions (
                    id TEXT PRIMARY KEY,
                    website_url TEXT NOT NULL,
                    original_prompt TEXT NOT NULL,
                    action_plan TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    total_duration INTEGER,
                    total_actions INTEGER DEFAULT 0,
                    successful_actions INTEGER DEFAULT 0,
                    failed_actions INTEGER DEFAULT 0,
                    screenshots TEXT,
                    execution_log TEXT,
                    error_summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_agent TEXT,
                    browser_info TEXT
                )
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_status ON test_sessions(status)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON test_sessions(created_at)
            """)
            
            await db.commit()
    
    async def save_session(self, session: TestSession) -> None:
        """Save a test session to the database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO test_sessions (
                        id, website_url, original_prompt, action_plan, status,
                        started_at, completed_at, total_duration, total_actions,
                        successful_actions, failed_actions, screenshots,
                        execution_log, error_summary, created_at, user_agent, browser_info
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.id,
                    session.website_url,
                    session.original_prompt,
                    json.dumps(session.action_plan.dict()),
                    session.status.value,
                    session.started_at,
                    session.completed_at,
                    session.total_duration,
                    session.total_actions,
                    session.successful_actions,
                    session.failed_actions,
                    json.dumps(session.screenshots),
                    json.dumps(session.execution_log),
                    session.error_summary,
                    session.created_at,
                    session.user_agent,
                    json.dumps(session.browser_info) if session.browser_info else None
                ))
                await db.commit()
                
            logger.info(f"Saved session {session.id}")
            
        except Exception as e:
            logger.error(f"Failed to save session {session.id}: {e}")
            raise
    
    async def update_session(self, session: TestSession) -> None:
        """Update an existing test session"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE test_sessions SET
                        action_plan = ?, status = ?, started_at = ?, completed_at = ?,
                        total_duration = ?, total_actions = ?, successful_actions = ?,
                        failed_actions = ?, screenshots = ?, execution_log = ?,
                        error_summary = ?, user_agent = ?, browser_info = ?
                    WHERE id = ?
                """, (
                    json.dumps(session.action_plan.dict()),
                    session.status.value,
                    session.started_at,
                    session.completed_at,
                    session.total_duration,
                    session.total_actions,
                    session.successful_actions,
                    session.failed_actions,
                    json.dumps(session.screenshots),
                    json.dumps(session.execution_log),
                    session.error_summary,
                    session.user_agent,
                    json.dumps(session.browser_info) if session.browser_info else None,
                    session.id
                ))
                await db.commit()
                
            logger.debug(f"Updated session {session.id}")
            
        except Exception as e:
            logger.error(f"Failed to update session {session.id}: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[TestSession]:
        """Get a test session by ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT * FROM test_sessions WHERE id = ?
                """, (session_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                if not row:
                    return None
                
                return self._row_to_session(row)
                
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            raise
    
    async def list_sessions(self, page: int = 1, per_page: int = 20, status: Optional[TestStatus] = None) -> Tuple[List[TestSession], int]:
        """List test sessions with pagination"""
        try:
            offset = (page - 1) * per_page
            
            # Build query
            where_clause = ""
            params = []
            if status:
                where_clause = "WHERE status = ?"
                params.append(status.value)
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                # Get total count
                count_query = f"SELECT COUNT(*) as total FROM test_sessions {where_clause}"
                async with db.execute(count_query, params) as cursor:
                    total_row = await cursor.fetchone()
                    total = total_row["total"]
                
                # Get sessions
                sessions_query = f"""
                    SELECT * FROM test_sessions {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """
                async with db.execute(sessions_query, params + [per_page, offset]) as cursor:
                    rows = await cursor.fetchall()
                
                sessions = [self._row_to_session(row) for row in rows]
                return sessions, total
                
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            raise
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a test session"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    DELETE FROM test_sessions WHERE id = ?
                """, (session_id,))
                await db.commit()
                
                deleted = cursor.rowcount > 0
                if deleted:
                    logger.info(f"Deleted session {session_id}")
                
                return deleted
                
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            raise
    
    async def update_session_status(self, session_id: str, status: TestStatus) -> bool:
        """Update session status"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    UPDATE test_sessions SET status = ? WHERE id = ?
                """, (status.value, session_id))
                await db.commit()
                
                updated = cursor.rowcount > 0
                if updated:
                    logger.debug(f"Updated session {session_id} status to {status.value}")
                
                return updated
                
        except Exception as e:
            logger.error(f"Failed to update session status {session_id}: {e}")
            raise
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                # Basic counts
                async with db.execute("""
                    SELECT 
                        COUNT(*) as total_tests,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_tests,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_tests,
                        SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running_tests,
                        AVG(total_duration) as average_duration
                    FROM test_sessions
                """) as cursor:
                    stats_row = await cursor.fetchone()
                
                # Success rate
                total_tests = stats_row["total_tests"] or 0
                successful_tests = stats_row["successful_tests"] or 0
                success_rate = (successful_tests / total_tests) if total_tests > 0 else 0
                
                # Most tested sites
                async with db.execute("""
                    SELECT website_url, COUNT(*) as count
                    FROM test_sessions
                    GROUP BY website_url
                    ORDER BY count DESC
                    LIMIT 5
                """) as cursor:
                    most_tested_sites = [
                        {"url": row["website_url"], "count": row["count"]}
                        for row in await cursor.fetchall()
                    ]
                
                # Common failures
                async with db.execute("""
                    SELECT error_summary, COUNT(*) as count
                    FROM test_sessions
                    WHERE status = 'failed' AND error_summary IS NOT NULL
                    GROUP BY error_summary
                    ORDER BY count DESC
                    LIMIT 5
                """) as cursor:
                    common_failures = [
                        {"error": row["error_summary"], "count": row["count"]}
                        for row in await cursor.fetchall()
                    ]
                
                return {
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "failed_tests": stats_row["failed_tests"] or 0,
                    "running_tests": stats_row["running_tests"] or 0,
                    "average_duration": int(stats_row["average_duration"] or 0),
                    "success_rate": success_rate,
                    "most_tested_sites": most_tested_sites,
                    "common_failures": common_failures
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def _row_to_session(self, row: aiosqlite.Row) -> TestSession:
        """Convert database row to TestSession object"""
        from ..models.test_models import ActionPlan
        
        # Parse JSON fields
        action_plan_data = json.loads(row["action_plan"])
        action_plan = ActionPlan(**action_plan_data)
        
        screenshots = json.loads(row["screenshots"]) if row["screenshots"] else []
        execution_log = json.loads(row["execution_log"]) if row["execution_log"] else []
        browser_info = json.loads(row["browser_info"]) if row["browser_info"] else None
        
        return TestSession(
            id=row["id"],
            website_url=row["website_url"],
            original_prompt=row["original_prompt"],
            action_plan=action_plan,
            status=TestStatus(row["status"]),
            started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
            total_duration=row["total_duration"],
            total_actions=row["total_actions"],
            successful_actions=row["successful_actions"],
            failed_actions=row["failed_actions"],
            screenshots=screenshots,
            execution_log=execution_log,
            error_summary=row["error_summary"],
            created_at=datetime.fromisoformat(row["created_at"]),
            user_agent=row["user_agent"],
            browser_info=browser_info
        )
