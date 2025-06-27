import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import threading
import time

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages session lifecycle and storage"""
    
    def __init__(self, cleanup_interval: int = 3600, session_timeout: int = 7200):
        """
        Initialize session manager
        
        Args:
            cleanup_interval: Interval in seconds for cleanup thread (default: 1 hour)
            session_timeout: Session timeout in seconds (default: 2 hours)
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.cleanup_interval = cleanup_interval
        self.session_timeout = session_timeout
        self._lock = threading.RLock()
        self._cleanup_thread = None
        self._stop_cleanup = False
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def create_session(self, session_id: str, student_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new session"""
        with self._lock:
            session_info = {
                "session_id": session_id,
                "student_id": student_id,
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "status": "active",
                "data": session_data
            }
            
            self.sessions[session_id] = session_info
            logger.info(f"Session {session_id} created for student {student_id}")
            
            return session_info
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        with self._lock:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            
            # Check if session is expired
            last_accessed = datetime.fromisoformat(session["last_accessed"])
            if datetime.now() - last_accessed > timedelta(seconds=self.session_timeout):
                logger.info(f"Session {session_id} expired, removing")
                del self.sessions[session_id]
                return None
            
            # Update last accessed time
            session["last_accessed"] = datetime.now().isoformat()
            
            return session
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data"""
        with self._lock:
            if session_id not in self.sessions:
                return False
            
            self.sessions[session_id]["data"].update(data)
            self.sessions[session_id]["last_accessed"] = datetime.now().isoformat()
            
            logger.debug(f"Session {session_id} updated")
            return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        with self._lock:
            if session_id not in self.sessions:
                return False
            
            del self.sessions[session_id]
            logger.info(f"Session {session_id} deleted")
            return True
    
    def get_student_sessions(self, student_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a student"""
        with self._lock:
            student_sessions = [
                session for session in self.sessions.values()
                if session["student_id"] == student_id
            ]
            
            return student_sessions
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        with self._lock:
            return len(self.sessions)
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        with self._lock:
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, session in self.sessions.items():
                last_accessed = datetime.fromisoformat(session["last_accessed"])
                if current_time - last_accessed > timedelta(seconds=self.session_timeout):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                logger.info(f"Cleaning up expired session {session_id}")
                del self.sessions[session_id]
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def _start_cleanup_thread(self):
        """Start the background cleanup thread"""
        def cleanup_worker():
            while not self._stop_cleanup:
                try:
                    self.cleanup_expired_sessions()
                    time.sleep(self.cleanup_interval)
                except Exception as e:
                    logger.error(f"Error in cleanup thread: {e}")
                    time.sleep(60)  # Wait a minute before retrying
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        logger.info("Session cleanup thread started")
    
    def stop_cleanup_thread(self):
        """Stop the background cleanup thread"""
        self._stop_cleanup = True
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
        logger.info("Session cleanup thread stopped")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        with self._lock:
            stats = {
                "total_sessions": len(self.sessions),
                "active_sessions": len([s for s in self.sessions.values() if s["status"] == "active"]),
                "students_count": len(set(s["student_id"] for s in self.sessions.values())),
                "oldest_session": None,
                "newest_session": None
            }
            
            if self.sessions:
                sessions_by_age = sorted(
                    self.sessions.values(),
                    key=lambda x: x["created_at"]
                )
                stats["oldest_session"] = sessions_by_age[0]["created_at"]
                stats["newest_session"] = sessions_by_age[-1]["created_at"]
            
            return stats
    
    def export_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export session data for backup/analysis"""
        with self._lock:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id].copy()
            # Remove sensitive data if any
            return session
    
    def import_session_data(self, session_data: Dict[str, Any]) -> bool:
        """Import session data from backup"""
        try:
            with self._lock:
                session_id = session_data["session_id"]
                self.sessions[session_id] = session_data
                logger.info(f"Session {session_id} imported successfully")
                return True
        except Exception as e:
            logger.error(f"Error importing session data: {e}")
            return False
    
    def __del__(self):
        """Cleanup when session manager is destroyed"""
        self.stop_cleanup_thread() 