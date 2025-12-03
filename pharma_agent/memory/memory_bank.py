"""
Memory Bank - Long-term memory storage for agent
Demonstrates: Persistent memory, knowledge retention, retrieval
"""

import logging
import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class MemoryBank:
    """
    Long-term memory storage for competitive intelligence.
    Stores historical analyses, competitor profiles, and insights.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("memory", {}).get("memory_bank", {}).get("enabled", True)
        self.storage_type = config.get("memory", {}).get("memory_bank", {}).get("storage_type", "sqlite")
        self.db_path = config.get("memory", {}).get("memory_bank", {}).get("db_path", "./data/memory_bank.db")
        
        if self.enabled:
            self._init_storage()
        
        logger.info(f"Memory Bank initialized (type: {self.storage_type})")
    
    def _init_storage(self):
        """Initialize storage backend."""
        if self.storage_type == "sqlite":
            self._init_sqlite()
        elif self.storage_type == "redis":
            self._init_redis()
        elif self.storage_type == "postgresql":
            self._init_postgres()
    
    def _init_sqlite(self):
        """Initialize SQLite database."""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                query TEXT,
                competitors TEXT,
                results TEXT,
                timestamp TEXT,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS competitor_profiles (
                competitor TEXT PRIMARY KEY,
                profile_data TEXT,
                last_updated TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insights (
                id TEXT PRIMARY KEY,
                insight_type TEXT,
                content TEXT,
                relevance_score REAL,
                timestamp TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info(f"SQLite Memory Bank initialized: {self.db_path}")
    
    def _init_redis(self):
        """Initialize Redis connection."""
        # Placeholder for Redis implementation
        logger.info("Redis Memory Bank not yet implemented")
    
    def _init_postgres(self):
        """Initialize PostgreSQL connection."""
        # Placeholder for PostgreSQL implementation
        logger.info("PostgreSQL Memory Bank not yet implemented")
    
    async def store_analysis(
        self,
        query: str,
        competitors: List[str],
        results: Dict[str, Any],
        timestamp: datetime
    ) -> str:
        """
        Store a completed analysis in memory bank.
        
        Args:
            query: Original query
            competitors: List of analyzed competitors
            results: Analysis results
            timestamp: When analysis was completed
            
        Returns:
            Analysis ID
        """
        if not self.enabled:
            return ""
        
        # Generate unique ID
        analysis_id = self._generate_id(query, timestamp)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO analyses (id, query, competitors, results, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                query,
                json.dumps(competitors),
                json.dumps(results),
                timestamp.isoformat(),
                json.dumps({"stored_at": datetime.now().isoformat()})
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Analysis stored in memory bank: {analysis_id}")
            
            # Also update competitor profiles
            for competitor in competitors:
                await self._update_competitor_profile(competitor, results)
            
            return analysis_id
            
        except Exception as e:
            logger.error(f"Error storing analysis: {e}")
            return ""
    
    async def retrieve_relevant_memories(
        self,
        query: str,
        competitors: List[str],
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve relevant historical memories for context.
        
        Args:
            query: Current query
            competitors: Competitors being analyzed
            limit: Max number of memories to retrieve
            
        Returns:
            Relevant historical context
        """
        if not self.enabled:
            return {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Retrieve recent analyses for these competitors
            cursor.execute("""
                SELECT id, query, results, timestamp
                FROM analyses
                WHERE competitors LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f"%{competitors[0]}%", limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            memories = []
            for row in rows:
                memories.append({
                    "id": row[0],
                    "query": row[1],
                    "results_summary": self._summarize_results(json.loads(row[2])),
                    "timestamp": row[3]
                })
            
            # Get competitor profiles
            profiles = await self.get_competitor_profiles(competitors)
            
            context = {
                "previous_analyses": memories,
                "competitor_profiles": profiles,
                "summary": self._create_context_summary(memories, profiles)
            }
            
            logger.info(f"Retrieved {len(memories)} relevant memories")
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return {}
    
    async def get_competitor_profiles(
        self,
        competitors: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Get stored profiles for competitors."""
        if not self.enabled:
            return {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            profiles = {}
            for competitor in competitors:
                cursor.execute("""
                    SELECT profile_data, last_updated
                    FROM competitor_profiles
                    WHERE competitor = ?
                """, (competitor,))
                
                row = cursor.fetchone()
                if row:
                    profiles[competitor] = {
                        "data": json.loads(row[0]),
                        "last_updated": row[1]
                    }
            
            conn.close()
            return profiles
            
        except Exception as e:
            logger.error(f"Error retrieving competitor profiles: {e}")
            return {}
    
    async def _update_competitor_profile(
        self,
        competitor: str,
        analysis_results: Dict[str, Any]
    ):
        """Update competitor profile with new information."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get existing profile
            cursor.execute("""
                SELECT profile_data FROM competitor_profiles WHERE competitor = ?
            """, (competitor,))
            
            row = cursor.fetchone()
            if row:
                profile = json.loads(row[0])
            else:
                profile = {"competitor": competitor, "history": []}
            
            # Add new analysis to history
            profile["history"].append({
                "timestamp": datetime.now().isoformat(),
                "insights": analysis_results.get("key_insights", [])
            })
            
            # Keep only recent history (last 10 entries)
            profile["history"] = profile["history"][-10:]
            
            # Update last known state
            profile["last_known_state"] = {
                "trends": analysis_results.get("trends", []),
                "position": analysis_results.get("competitive_positioning", {})
            }
            
            cursor.execute("""
                INSERT OR REPLACE INTO competitor_profiles (competitor, profile_data, last_updated)
                VALUES (?, ?, ?)
            """, (
                competitor,
                json.dumps(profile),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Updated profile for: {competitor}")
            
        except Exception as e:
            logger.error(f"Error updating competitor profile: {e}")
    
    def _generate_id(self, query: str, timestamp: datetime) -> str:
        """Generate unique ID for analysis."""
        content = f"{query}{timestamp.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _summarize_results(self, results: Dict[str, Any]) -> str:
        """Create brief summary of results."""
        insights = results.get("key_insights", [])
        if insights:
            return "; ".join(insights[:3])
        return "No specific insights"
    
    def _create_context_summary(
        self,
        memories: List[Dict[str, Any]],
        profiles: Dict[str, Dict[str, Any]]
    ) -> str:
        """Create textual summary of historical context."""
        if not memories and not profiles:
            return "No historical context available"
        
        summary = f"Historical context: {len(memories)} previous analyses available. "
        
        if profiles:
            summary += f"Profiles available for: {', '.join(profiles.keys())}. "
        
        if memories:
            summary += f"Most recent analysis: {memories[0]['query']} ({memories[0]['timestamp']})"
        
        return summary
    
    async def close(self):
        """Cleanup resources."""
        logger.info("Closing memory bank")
        # SQLite connections are closed after each operation
        # For other backends, close persistent connections here
