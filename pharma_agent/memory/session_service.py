"""
Session Service - Manages agent sessions and state
Demonstrates: InMemorySessionService, session persistence
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class SessionService:
    """
    Manages agent sessions for continuity across interactions.
    Implements InMemorySessionService pattern.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session_type = config.get("memory", {}).get("session_service", {}).get("type", "InMemory")
        self.max_sessions = config.get("memory", {}).get("session_service", {}).get("max_sessions", 100)
        
        # In-memory storage
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._checkpoints: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Session Service initialized (type: {self.session_type})")
    
    async def get_or_create_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get existing session or create new one.
        
        Args:
            session_id: Optional existing session ID
            
        Returns:
            Session dictionary
        """
        if session_id and session_id in self._sessions:
            logger.info(f"Retrieved existing session: {session_id}")
            return self._sessions[session_id]
        
        # Create new session
        new_session_id = session_id or str(uuid.uuid4())
        session = {
            "id": new_session_id,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "analysis_count": 0,
            "state": {},
            "history": []
        }
        
        self._sessions[new_session_id] = session
        
        # Enforce max sessions limit
        if len(self._sessions) > self.max_sessions:
            self._evict_oldest_session()
        
        logger.info(f"Created new session: {new_session_id}")
        return session
    
    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update session state.
        
        Args:
            session_id: Session ID
            updates: Dictionary of updates
            
        Returns:
            Updated session
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = self._sessions[session_id]
        session.update(updates)
        session["last_accessed"] = datetime.now().isoformat()
        
        logger.debug(f"Updated session: {session_id}")
        return session
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        return self._sessions.get(session_id)
    
    async def delete_session(self, session_id: str):
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
    
    async def save_checkpoint(self, checkpoint: Dict[str, Any]) -> str:
        """
        Save execution checkpoint for pause/resume.
        
        Args:
            checkpoint: Checkpoint data
            
        Returns:
            Checkpoint ID
        """
        checkpoint_id = checkpoint.get("id", str(uuid.uuid4()))
        self._checkpoints[checkpoint_id] = {
            **checkpoint,
            "saved_at": datetime.now().isoformat()
        }
        
        logger.info(f"Checkpoint saved: {checkpoint_id}")
        return checkpoint_id
    
    async def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a saved checkpoint.
        
        Args:
            checkpoint_id: Checkpoint ID
            
        Returns:
            Checkpoint data or None
        """
        checkpoint = self._checkpoints.get(checkpoint_id)
        if checkpoint:
            logger.info(f"Checkpoint loaded: {checkpoint_id}")
        else:
            logger.warning(f"Checkpoint not found: {checkpoint_id}")
        
        return checkpoint
    
    async def list_checkpoints(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available checkpoints, optionally filtered by session."""
        checkpoints = list(self._checkpoints.values())
        
        if session_id:
            checkpoints = [
                cp for cp in checkpoints 
                if cp.get("state", {}).get("session_id") == session_id
            ]
        
        return checkpoints
    
    def _evict_oldest_session(self):
        """Remove oldest session when max limit is reached."""
        if not self._sessions:
            return
        
        # Find oldest session
        oldest_id = min(
            self._sessions.keys(),
            key=lambda sid: self._sessions[sid]["last_accessed"]
        )
        
        del self._sessions[oldest_id]
        logger.info(f"Evicted oldest session: {oldest_id}")
    
    def create_session_context(self):
        """Create an async context manager for sessions."""
        return SessionContext(self)
    
    async def close(self):
        """Cleanup resources."""
        logger.info("Closing session service")
        
        # In production, persist important sessions to database
        if self.session_type == "Redis":
            # Save to Redis
            pass
        
        self._sessions.clear()
        self._checkpoints.clear()


class SessionContext:
    """Async context manager for sessions."""
    
    def __init__(self, service: SessionService):
        self.service = service
        self.session = None
    
    async def __aenter__(self):
        self.session = await self.service.get_or_create_session()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Update session with any final state
        if self.session:
            await self.service.update_session(
                self.session["id"],
                {"last_accessed": datetime.now().isoformat()}
            )
