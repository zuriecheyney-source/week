"""
Memory Store - Persistent memory system for multi-turn conversations
"""
import sqlite3
import json
import asyncio
import aiosqlite
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.state import MemoryEntry, AgentRole


class MemoryStore:
    """Persistent memory store for agent conversations and context"""
    
    def __init__(self, db_path: str = "data/agent_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    agent_role TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    timestamp TEXT NOT NULL,
                    importance_score REAL DEFAULT 0.5
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    agent_role TEXT NOT NULL,
                    state_data TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    total_messages INTEGER DEFAULT 0
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memory_entries(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_role ON memory_entries(agent_role)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_entries(timestamp)")
            
            conn.commit()
    
    async def add_memory_entry(self, entry: MemoryEntry) -> bool:
        """Add a new memory entry"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO memory_entries 
                    (session_id, agent_role, message_type, content, metadata, timestamp, importance_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.session_id,
                    entry.agent_role.value,
                    entry.message_type.value,
                    entry.content,
                    json.dumps(entry.metadata),
                    entry.timestamp.isoformat(),
                    entry.importance_score
                ))
                
                # Update session info
                await self._update_session(db, entry.session_id)
                
                await db.commit()
                return True
                
        except Exception as e:
            print(f"Error adding memory entry: {e}")
            return False
    
    async def get_memory_entries(self, session_id: str, 
                               agent_role: Optional[AgentRole] = None,
                               limit: int = 50,
                               min_importance: float = 0.0) -> List[MemoryEntry]:
        """Retrieve memory entries for a session"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                query = """
                    SELECT session_id, agent_role, message_type, content, metadata, timestamp, importance_score
                    FROM memory_entries
                    WHERE session_id = ? AND importance_score >= ?
                """
                params = [session_id, min_importance]
                
                if agent_role:
                    query += " AND agent_role = ?"
                    params.append(agent_role.value)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    
                    entries = []
                    for row in rows:
                        entries.append(MemoryEntry(
                            session_id=row[0],
                            agent_role=AgentRole(row[1]),
                            message_type=row[2],
                            content=row[3],
                            metadata=json.loads(row[4]) if row[4] else {},
                            timestamp=datetime.fromisoformat(row[5]),
                            importance_score=row[6]
                        ))
                    
                    return entries
                    
        except Exception as e:
            print(f"Error retrieving memory entries: {e}")
            return []
    
    async def search_memories(self, session_id: str, query: str,
                           agent_role: Optional[AgentRole] = None,
                           limit: int = 10) -> List[MemoryEntry]:
        """Search memory entries by content"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                search_query = """
                    SELECT session_id, agent_role, message_type, content, metadata, timestamp, importance_score
                    FROM memory_entries
                    WHERE session_id = ? AND content LIKE ?
                """
                params = [session_id, f"%{query}%"]
                
                if agent_role:
                    search_query += " AND agent_role = ?"
                    params.append(agent_role.value)
                
                search_query += " ORDER BY importance_score DESC, timestamp DESC LIMIT ?"
                params.append(limit)
                
                async with db.execute(search_query, params) as cursor:
                    rows = await cursor.fetchall()
                    
                    entries = []
                    for row in rows:
                        entries.append(MemoryEntry(
                            session_id=row[0],
                            agent_role=AgentRole(row[1]),
                            message_type=row[2],
                            content=row[3],
                            metadata=json.loads(row[4]) if row[4] else {},
                            timestamp=datetime.fromisoformat(row[5]),
                            importance_score=row[6]
                        ))
                    
                    return entries
                    
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []
    
    async def save_agent_state(self, session_id: str, agent_role: AgentRole, 
                             state_data: Dict[str, Any]) -> bool:
        """Save agent state for recovery"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO agent_states 
                    (session_id, agent_role, state_data, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (
                    session_id,
                    agent_role.value,
                    json.dumps(state_data),
                    datetime.now().isoformat()
                ))
                
                await db.commit()
                return True
                
        except Exception as e:
            print(f"Error saving agent state: {e}")
            return False
    
    async def get_agent_state(self, session_id: str, 
                            agent_role: AgentRole) -> Optional[Dict[str, Any]]:
        """Retrieve saved agent state"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT state_data FROM agent_states
                    WHERE session_id = ? AND agent_role = ?
                    ORDER BY timestamp DESC LIMIT 1
                """, (session_id, agent_role.value)) as cursor:
                    row = await cursor.fetchone()
                    
                    if row:
                        return json.loads(row[0])
                    
                    return None
                    
        except Exception as e:
            print(f"Error retrieving agent state: {e}")
            return None
    
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get session summary and statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get session info
                async with db.execute("""
                    SELECT created_at, last_updated, total_messages
                    FROM sessions
                    WHERE session_id = ?
                """, (session_id,)) as cursor:
                    session_row = await cursor.fetchone()
                
                # Get agent statistics
                async with db.execute("""
                    SELECT agent_role, COUNT(*) as message_count
                    FROM memory_entries
                    WHERE session_id = ?
                    GROUP BY agent_role
                """, (session_id,)) as cursor:
                    agent_rows = await cursor.fetchall()
                
                # Get recent messages
                async with db.execute("""
                    SELECT content, agent_role, timestamp
                    FROM memory_entries
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 5
                """, (session_id,)) as cursor:
                    recent_rows = await cursor.fetchall()
                
                summary = {
                    "session_id": session_id,
                    "created_at": session_row[0] if session_row else None,
                    "last_updated": session_row[1] if session_row else None,
                    "total_messages": session_row[2] if session_row else 0,
                    "agent_stats": {
                        row[0]: {"message_count": row[1]} 
                        for row in agent_rows
                    },
                    "recent_messages": [
                        {
                            "content": row[0],
                            "agent": row[1],
                            "timestamp": row[2]
                        }
                        for row in recent_rows
                    ]
                }
                
                return summary
                
        except Exception as e:
            print(f"Error getting session summary: {e}")
            return {}
    
    async def cleanup_old_memories(self, days_to_keep: int = 30) -> int:
        """Clean up old memory entries"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    DELETE FROM memory_entries
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                await db.commit()
                
                return deleted_count
                
        except Exception as e:
            print(f"Error cleaning up memories: {e}")
            return 0
    
    async def _update_session(self, db: aiosqlite.Connection, session_id: str):
        """Update session information"""
        await db.execute("""
            INSERT OR REPLACE INTO sessions (session_id, created_at, last_updated, total_messages)
            VALUES (?, 
                COALESCE((SELECT created_at FROM sessions WHERE session_id = ?), ?),
                ?,
                (SELECT COUNT(*) FROM memory_entries WHERE session_id = ?)
            )
        """, (session_id, session_id, datetime.now().isoformat(), datetime.now().isoformat(), session_id))
    
    async def close(self):
        """Close database connections"""
        # aiosqlite handles connection pooling automatically
        pass
