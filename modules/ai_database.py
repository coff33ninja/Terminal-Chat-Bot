"""
Async SQL Database Module for AI
"""

import aiosqlite
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class AIDatabase:
    def __init__(self, db_path: str = "data/ai_database.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            await self._create_tables(db)
            await db.commit()
        logger.info(f"AI Database initialized at {self.db_path}")
    
    async def _create_tables(self, db: aiosqlite.Connection):
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                channel_id TEXT,
                guild_id TEXT,
                message_content TEXT NOT NULL,
                ai_response TEXT,
                model_used TEXT,
                tokens_used INTEGER DEFAULT 0,
                response_time REAL DEFAULT 0.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                context_data TEXT
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_ai_preferences (
                user_id TEXT PRIMARY KEY,
                preferred_model TEXT DEFAULT 'gemini-pro',
                personality_mode TEXT DEFAULT 'default',
                response_length TEXT DEFAULT 'medium',
                temperature REAL DEFAULT 0.7,
                max_tokens INTEGER DEFAULT 1000,
                conversation_memory INTEGER DEFAULT 0,
                custom_instructions TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                request_count INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0.0,
                success_rate REAL DEFAULT 100.0,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                date_tracked DATE DEFAULT (DATE('now')),
                UNIQUE(model_name, date_tracked)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key_term TEXT NOT NULL,
                content TEXT NOT NULL,
                relevance_score REAL DEFAULT 1.0,
                usage_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, key_term)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ai_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                user_id TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                feedback_content TEXT,
                ai_response_quality INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ai_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                memory_key TEXT NOT NULL,
                memory_value TEXT NOT NULL,
                memory_type TEXT DEFAULT 'fact',
                importance INTEGER DEFAULT 5,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                UNIQUE(user_id, memory_key)
            )
        """)

    async def save_conversation(self, user_id: str, message: str, ai_response: str, 
                              model_used: str, tokens_used: int = 0, 
                              response_time: float = 0.0, channel_id: str = None,
                              guild_id: str = None, context_data: Dict = None) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO conversations 
                (user_id, channel_id, guild_id, message_content, ai_response, 
                 model_used, tokens_used, response_time, context_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, channel_id, guild_id, message, ai_response, 
                  model_used, tokens_used, response_time, 
                  json.dumps(context_data) if context_data else None))
            
            conversation_id = cursor.lastrowid
            await db.commit()
            return conversation_id

    async def get_conversation_history(self, user_id: str, limit: int = 10,
                                     channel_id: str = None) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            if channel_id:
                cursor = await db.execute("""
                    SELECT * FROM conversations 
                    WHERE user_id = ? AND channel_id = ?
                    ORDER BY timestamp DESC LIMIT ?
                """, (user_id, channel_id, limit))
            else:
                cursor = await db.execute("""
                    SELECT * FROM conversations 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC LIMIT ?
                """, (user_id, limit))
            
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            conversations = []
            for row in rows:
                conv = dict(zip(columns, row))
                if conv['context_data']:
                    conv['context_data'] = json.loads(conv['context_data'])
                conversations.append(conv)
            
            return list(reversed(conversations))

    async def get_user_preferences(self, user_id: str) -> Dict:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM user_ai_preferences WHERE user_id = ?
            """, (user_id,))
            
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            
            return {
                'user_id': user_id,
                'preferred_model': 'gemini-pro',
                'personality_mode': 'default',
                'response_length': 'medium',
                'temperature': 0.7,
                'max_tokens': 1000,
                'conversation_memory': 0,
                'custom_instructions': None
            }

    async def update_user_preferences(self, user_id: str, preferences: Dict):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT user_id FROM user_ai_preferences WHERE user_id = ?
            """, (user_id,))
            
            exists = await cursor.fetchone()
            
            if exists:
                set_clauses = []
                values = []
                for key, value in preferences.items():
                    if key != 'user_id':
                        set_clauses.append(f"{key} = ?")
                        values.append(value)
                
                values.append(user_id)
                await db.execute(f"""
                    UPDATE user_ai_preferences 
                    SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, values)
            else:
                preferences['user_id'] = user_id
                columns = list(preferences.keys())
                placeholders = ', '.join(['?' for _ in columns])
                
                await db.execute(f"""
                    INSERT INTO user_ai_preferences ({', '.join(columns)})
                    VALUES ({placeholders})
                """, list(preferences.values()))
            
            await db.commit()

    async def track_model_performance(self, model_name: str, tokens_used: int,
                                    response_time: float, success: bool = True):
        async with aiosqlite.connect(self.db_path) as db:
            today = datetime.now().date()
            
            cursor = await db.execute("""
                SELECT * FROM model_performance 
                WHERE model_name = ? AND date_tracked = ?
            """, (model_name, today))
            
            existing = await cursor.fetchone()
            
            if existing:
                new_count = existing[2] + 1
                new_tokens = existing[3] + tokens_used
                new_avg_time = ((existing[4] * existing[2]) + response_time) / new_count
                new_success_rate = ((existing[5] * existing[2]) + (100 if success else 0)) / new_count
                
                await db.execute("""
                    UPDATE model_performance 
                    SET request_count = ?, total_tokens = ?, avg_response_time = ?,
                        success_rate = ?, last_used = CURRENT_TIMESTAMP
                    WHERE model_name = ? AND date_tracked = ?
                """, (new_count, new_tokens, new_avg_time, new_success_rate, model_name, today))
            else:
                await db.execute("""
                    INSERT INTO model_performance 
                    (model_name, request_count, total_tokens, avg_response_time, 
                     success_rate, date_tracked)
                    VALUES (?, 1, ?, ?, ?, ?)
                """, (model_name, tokens_used, response_time, 100 if success else 0, today))
            
            await db.commit()

    async def add_knowledge(self, category: str, key_term: str, content: str,
                          relevance_score: float = 1.0):
        async with aiosqlite.connect(self.db_path) as db:
            # Use upsert semantics: insert new record or update content for same (category,key_term)
            await db.execute("""
                INSERT INTO knowledge_base (category, key_term, content, relevance_score)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(category, key_term) DO UPDATE SET
                    content = excluded.content,
                    relevance_score = excluded.relevance_score,
                    updated_at = CURRENT_TIMESTAMP
            """, (category, key_term, content, relevance_score))
            await db.commit()

    async def search_knowledge(self, query: str, category: str = None, 
                             limit: int = 5) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            if category:
                cursor = await db.execute("""
                    SELECT * FROM knowledge_base 
                    WHERE category = ? AND (key_term LIKE ? OR content LIKE ?)
                    ORDER BY relevance_score DESC, usage_count DESC
                    LIMIT ?
                """, (category, f"%{query}%", f"%{query}%", limit))
            else:
                cursor = await db.execute("""
                    SELECT * FROM knowledge_base 
                    WHERE key_term LIKE ? OR content LIKE ?
                    ORDER BY relevance_score DESC, usage_count DESC
                    LIMIT ?
                """, (f"%{query}%", f"%{query}%", limit))
            
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            for row in rows:
                await db.execute("""
                    UPDATE knowledge_base 
                    SET usage_count = usage_count + 1 
                    WHERE id = ?
                """, (row[0],))
            
            await db.commit()
            return [dict(zip(columns, row)) for row in rows]

    async def get_random_knowledge(self, category: str = None) -> Optional[Dict]:
        """
        Return a single random knowledge_base entry optionally filtered by category.
        Returns None if no entry found.
        """
        async with aiosqlite.connect(self.db_path) as db:
            if category:
                cursor = await db.execute("""
                    SELECT * FROM knowledge_base WHERE category = ? ORDER BY RANDOM() LIMIT 1
                """, (category,))
            else:
                cursor = await db.execute("""
                    SELECT * FROM knowledge_base ORDER BY RANDOM() LIMIT 1
                """)

            row = await cursor.fetchone()
            if not row:
                return None

            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))

    async def save_feedback(self, conversation_id: int, user_id: str,
                          feedback_type: str, feedback_content: str = None,
                          quality_rating: int = None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO ai_feedback 
                (conversation_id, user_id, feedback_type, feedback_content, ai_response_quality)
                VALUES (?, ?, ?, ?, ?)
            """, (conversation_id, user_id, feedback_type, feedback_content, quality_rating))
            await db.commit()

    async def get_analytics(self, days: int = 7) -> Dict:
        async with aiosqlite.connect(self.db_path) as db:
            since_date = datetime.now() - timedelta(days=days)
            
            cursor = await db.execute("""
                SELECT COUNT(*) FROM conversations WHERE timestamp >= ?
            """, (since_date,))
            total_conversations = (await cursor.fetchone())[0]
            
            cursor = await db.execute("""
                SELECT COUNT(DISTINCT user_id) FROM conversations WHERE timestamp >= ?
            """, (since_date,))
            unique_users = (await cursor.fetchone())[0]
            
            cursor = await db.execute("""
                SELECT model_used, COUNT(*) as usage_count 
                FROM conversations 
                WHERE timestamp >= ? 
                GROUP BY model_used 
                ORDER BY usage_count DESC
            """, (since_date,))
            model_usage = dict(await cursor.fetchall())
            
            cursor = await db.execute("""
                SELECT AVG(response_time) FROM conversations 
                WHERE timestamp >= ? AND response_time > 0
            """, (since_date,))
            avg_response_time = (await cursor.fetchone())[0] or 0
            
            cursor = await db.execute("""
                SELECT SUM(tokens_used) FROM conversations WHERE timestamp >= ?
            """, (since_date,))
            total_tokens = (await cursor.fetchone())[0] or 0
            
            return {
                'period_days': days,
                'total_conversations': total_conversations,
                'unique_users': unique_users,
                'model_usage': model_usage,
                'avg_response_time': round(avg_response_time, 2),
                'total_tokens': total_tokens
            }

    async def cleanup_old_data(self, days_to_keep: int = 30):
        async with aiosqlite.connect(self.db_path) as db:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            cursor = await db.execute("""
                DELETE FROM conversations WHERE timestamp < ?
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            await db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old conversation records")
            return deleted_count

    async def remember(self, user_id: str, key: str, value: str, 
                      memory_type: str = 'fact', importance: int = 5):
        """Store a memory about a user"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO ai_memory (user_id, memory_key, memory_value, memory_type, importance)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id, memory_key) DO UPDATE SET
                    memory_value = excluded.memory_value,
                    memory_type = excluded.memory_type,
                    importance = excluded.importance,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, key, value, memory_type, importance))
            await db.commit()
    
    async def recall(self, user_id: str, key: str = None) -> Optional[Dict] | List[Dict]:
        """Recall a specific memory or all memories for a user"""
        async with aiosqlite.connect(self.db_path) as db:
            if key:
                cursor = await db.execute("""
                    SELECT * FROM ai_memory WHERE user_id = ? AND memory_key = ?
                """, (user_id, key))
                row = await cursor.fetchone()
                
                if row:
                    # Update access tracking
                    await db.execute("""
                        UPDATE ai_memory 
                        SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND memory_key = ?
                    """, (user_id, key))
                    await db.commit()
                    
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
            else:
                cursor = await db.execute("""
                    SELECT * FROM ai_memory 
                    WHERE user_id = ? 
                    ORDER BY importance DESC, updated_at DESC
                """, (user_id,))
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
    
    async def forget(self, user_id: str, key: str) -> bool:
        """Forget a specific memory"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                DELETE FROM ai_memory WHERE user_id = ? AND memory_key = ?
            """, (user_id, key))
            await db.commit()
            return cursor.rowcount > 0
    
    async def search_memories(self, user_id: str, query: str, limit: int = 10) -> List[Dict]:
        """Search memories by content"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM ai_memory 
                WHERE user_id = ? AND (memory_key LIKE ? OR memory_value LIKE ?)
                ORDER BY importance DESC, updated_at DESC
                LIMIT ?
            """, (user_id, f"%{query}%", f"%{query}%", limit))
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    async def close(self):
        logger.info("AI Database connections closed")


ai_db = AIDatabase()

async def initialize_ai_database():
    await ai_db.initialize()

async def save_ai_conversation(user_id: str, message: str, response: str, 
                             model: str, **kwargs) -> int:
    return await ai_db.save_conversation(user_id, message, response, model, **kwargs)

async def get_user_ai_history(user_id: str, limit: int = 10) -> List[Dict]:
    return await ai_db.get_conversation_history(user_id, limit)

async def get_ai_preferences(user_id: str) -> Dict:
    return await ai_db.get_user_preferences(user_id)

async def get_random_knowledge(category: str = None) -> Optional[Dict]:
    """
    Return a single random knowledge_base row optionally filtered by category.
    Returns None if no entry found.
    """
    return await ai_db.get_random_knowledge(category)
