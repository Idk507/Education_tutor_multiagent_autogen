import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# Add the parent directory to the path to import from agent.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import (
    create_educational_agents, 
    extract_subject_and_topic,
    ProgressMemory,
    LangChainConversationMemory
)
from utils.exceptions import AgentException, SessionNotFoundException

logger = logging.getLogger(__name__)

class EducationalAgentService:
    """Service layer for educational agent functionality"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def create_session(self, student_id: str, session_id: str) -> Dict[str, Any]:
        """Create a new educational session"""
        try:
            logger.info(f"Creating session {session_id} for student {student_id}")
            
            # Create agents using the existing function from agent.py
            agents = create_educational_agents(student_id, session_id)
            
            session_data = {
                "session_id": session_id,
                "student_id": student_id,
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "agents": agents,
                "last_activity": datetime.now().isoformat()
            }
            
            self.active_sessions[session_id] = session_data
            logger.info(f"Session {session_id} created successfully")
            
            return session_data
            
        except Exception as e:
            logger.error(f"Error creating session {session_id}: {e}")
            raise AgentException(f"Failed to create session: {str(e)}")
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session data"""
        if session_id not in self.active_sessions:
            raise SessionNotFoundException(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session["last_activity"] = datetime.now().isoformat()
        return session
    
    def explain_concept(
        self, 
        session_id: str, 
        subject: str, 
        topic: str, 
        difficulty_level: str = "medium", 
        learning_style: str = "visual"
    ) -> str:
        """Explain a concept using the tutor agent"""
        try:
            session = self.get_session(session_id)
            agents = session["agents"]
            
            # Use the explain_concept function from the agents
            explanation = agents["explain_concept"](subject, topic, difficulty_level, learning_style)
            
            logger.info(f"Concept explained for session {session_id}: {subject}/{topic}")
            return explanation
            
        except SessionNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error explaining concept in session {session_id}: {e}")
            raise AgentException(f"Failed to explain concept: {str(e)}")
    
    def create_practice_problems(
        self, 
        session_id: str, 
        subject: str, 
        topic: str, 
        count: int = 1, 
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """Create practice problems using the tutor agent"""
        try:
            session = self.get_session(session_id)
            agents = session["agents"]
            
            # Use the create_practice_problems function from the agents
            problems = agents["create_practice_problems"](subject, topic, count, difficulty)
            
            if "error" in problems:
                raise AgentException(problems["error"])
            
            logger.info(f"Practice problems created for session {session_id}: {count} problems")
            return problems
            
        except SessionNotFoundException:
            raise
        except AgentException:
            raise
        except Exception as e:
            logger.error(f"Error creating practice problems in session {session_id}: {e}")
            raise AgentException(f"Failed to create practice problems: {str(e)}")
    
    def evaluate_solution(self, session_id: str, solution: str) -> Dict[str, Any]:
        """Evaluate a student's solution"""
        try:
            session = self.get_session(session_id)
            agents = session["agents"]
            
            # Use the evaluate_solution function from the agents
            evaluation = agents["evaluate_solution"](session_id, solution)
            
            if "error" in evaluation:
                raise AgentException(evaluation["error"])
            
            logger.info(f"Solution evaluated for session {session_id}")
            return evaluation
            
        except SessionNotFoundException:
            raise
        except AgentException:
            raise
        except Exception as e:
            logger.error(f"Error evaluating solution in session {session_id}: {e}")
            raise AgentException(f"Failed to evaluate solution: {str(e)}")
    
    def generate_progress_report(self, session_id: str) -> Dict[str, Any]:
        """Generate a progress report for the session"""
        try:
            session = self.get_session(session_id)
            agents = session["agents"]
            
            # Use the generate_progress_report function from the agents
            report = agents["generate_progress_report"]()
            
            if "error" in report:
                raise AgentException(report["error"])
            
            logger.info(f"Progress report generated for session {session_id}")
            return report
            
        except SessionNotFoundException:
            raise
        except AgentException:
            raise
        except Exception as e:
            logger.error(f"Error generating progress report for session {session_id}: {e}")
            raise AgentException(f"Failed to generate progress report: {str(e)}")
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        try:
            session = self.get_session(session_id)
            agents = session["agents"]
            conv_memory = agents["conv_memory"]
            
            messages = conv_memory.get_messages()
            
            # Add timestamps if not present
            for i, message in enumerate(messages):
                if "timestamp" not in message:
                    message["timestamp"] = datetime.now().isoformat()
            
            # Apply limit
            if limit and len(messages) > limit:
                messages = messages[-limit:]
            
            logger.info(f"Retrieved {len(messages)} conversation messages for session {session_id}")
            return messages
            
        except SessionNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error getting conversation history for session {session_id}: {e}")
            raise AgentException(f"Failed to get conversation history: {str(e)}")
    
    def get_student_analytics(self, student_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a student across all sessions"""
        try:
            # Find all sessions for this student
            student_sessions = [
                session for session in self.active_sessions.values() 
                if session["student_id"] == student_id
            ]
            
            if not student_sessions:
                # Try to load from progress data
                try:
                    progress_memory = ProgressMemory(student_id)
                    report = progress_memory.get_progress_report()
                    
                    # Calculate analytics from progress data
                    analytics = self._calculate_analytics_from_progress(report)
                    analytics["student_id"] = student_id
                    
                    return analytics
                    
                except Exception:
                    # Return default analytics if no data found
                    return {
                        "student_id": student_id,
                        "total_sessions": 0,
                        "total_problems_solved": 0,
                        "average_score": 0.0,
                        "subjects_studied": [],
                        "skill_progression": {},
                        "time_spent_learning": 0
                    }
            
            # Aggregate data from active sessions
            total_sessions = len(student_sessions)
            subjects_studied = set()
            skill_progression = {}
            total_problems = 0
            total_score = 0.0
            
            for session in student_sessions:
                try:
                    agents = session["agents"]
                    progress_memory = agents["progress_memory"]
                    report = progress_memory.get_progress_report()
                    
                    # Aggregate subjects and skills
                    for subject, topics in report.get("subjects", {}).items():
                        subjects_studied.add(subject)
                        if subject not in skill_progression:
                            skill_progression[subject] = {}
                        
                        for topic, progress in topics.items():
                            skill_progression[subject][topic] = progress.get("skill_level", 0.0)
                            total_problems += progress.get("attempts", 0)
                            total_score += progress.get("skill_level", 0.0) * progress.get("attempts", 0)
                    
                except Exception as e:
                    logger.warning(f"Error processing session {session['session_id']}: {e}")
                    continue
            
            average_score = total_score / max(total_problems, 1)
            
            analytics = {
                "student_id": student_id,
                "total_sessions": total_sessions,
                "total_problems_solved": total_problems,
                "average_score": average_score,
                "subjects_studied": list(subjects_studied),
                "skill_progression": skill_progression,
                "time_spent_learning": total_sessions * 30  # Estimate 30 minutes per session
            }
            
            logger.info(f"Analytics generated for student {student_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics for student {student_id}: {e}")
            raise AgentException(f"Failed to get student analytics: {str(e)}")
    
    def get_user_profile(self, student_id: str) -> Dict[str, Any]:
        """Get user profile information"""
        try:
            # This would typically come from a user database
            # For now, we'll create a basic profile
            profile = {
                "student_id": student_id,
                "learning_preferences": {
                    "default_difficulty": "medium",
                    "preferred_learning_style": "visual",
                    "notification_settings": {
                        "progress_updates": True,
                        "new_problems": True,
                        "achievements": True
                    }
                },
                "achievement_badges": [],
                "total_sessions": len([
                    s for s in self.active_sessions.values() 
                    if s["student_id"] == student_id
                ]),
                "created_at": datetime.now().isoformat()
            }
            
            # Add some sample badges based on progress
            analytics = self.get_student_analytics(student_id)
            if analytics["total_problems_solved"] > 10:
                profile["achievement_badges"].append({
                    "badge_id": "problem_solver",
                    "name": "Problem Solver",
                    "description": "Solved 10+ problems",
                    "earned_at": datetime.now().isoformat()
                })
            
            if analytics["average_score"] > 0.8:
                profile["achievement_badges"].append({
                    "badge_id": "high_achiever",
                    "name": "High Achiever", 
                    "description": "Maintained 80%+ average score",
                    "earned_at": datetime.now().isoformat()
                })
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting user profile for {student_id}: {e}")
            raise AgentException(f"Failed to get user profile: {str(e)}")
    
    def update_user_profile(self, student_id: str, learning_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        try:
            # In a real implementation, this would update a database
            profile = self.get_user_profile(student_id)
            profile["learning_preferences"].update(learning_preferences)
            
            logger.info(f"User profile updated for student {student_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error updating user profile for {student_id}: {e}")
            raise AgentException(f"Failed to update user profile: {str(e)}")
    
    def close_session(self, session_id: str):
        """Close and clean up a session"""
        try:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session["status"] = "closed"
                session["closed_at"] = datetime.now().isoformat()
                
                # Clean up resources if needed
                del self.active_sessions[session_id]
                
                logger.info(f"Session {session_id} closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing session {session_id}: {e}")
            raise AgentException(f"Failed to close session: {str(e)}")
    
    def _calculate_analytics_from_progress(self, progress_report: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate analytics from progress report data"""
        subjects = progress_report.get("subjects", {})
        sessions = progress_report.get("sessions", [])
        
        total_problems = 0
        total_score = 0.0
        subjects_studied = list(subjects.keys())
        skill_progression = {}
        
        for subject, topics in subjects.items():
            skill_progression[subject] = {}
            for topic, progress in topics.items():
                attempts = progress.get("attempts", 0)
                skill_level = progress.get("skill_level", 0.0)
                
                total_problems += attempts
                total_score += skill_level * attempts
                skill_progression[subject][topic] = skill_level
        
        average_score = total_score / max(total_problems, 1)
        total_sessions = len(sessions)
        
        return {
            "total_sessions": total_sessions,
            "total_problems_solved": total_problems,
            "average_score": average_score,
            "subjects_studied": subjects_studied,
            "skill_progression": skill_progression,
            "time_spent_learning": total_sessions * 30  # Estimate
        } 