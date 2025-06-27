from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os

# Import models and services
from models.api_models import *
from services.agent_service import EducationalAgentService
from services.session_manager import SessionManager
from utils.exceptions import AgentException, SessionNotFoundException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
agent_service = EducationalAgentService()
session_manager = SessionManager()
executor = ThreadPoolExecutor(max_workers=4)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Educational Tutor API")
    yield
    logger.info("Shutting down Educational Tutor API")
    executor.shutdown(wait=True)

# Create FastAPI app
app = FastAPI(
    title="Educational Tutor API",
    description="AI-powered educational tutoring system with personalized learning",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for getting session
async def get_session(session_id: str) -> Dict[str, Any]:
    """Get session data"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

# Root endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Educational Tutor API is running",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# Session Management Endpoints
@app.post("/api/sessions", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create a new learning session"""
    try:
        session_id = str(uuid.uuid4())
        student_id = request.student_id or f"student_{uuid.uuid4().hex[:8]}"
        
        # Create session in background
        loop = asyncio.get_event_loop()
        session_data = await loop.run_in_executor(
            executor, 
            agent_service.create_session, 
            student_id, 
            session_id
        )
        
        session_manager.create_session(session_id, student_id, session_data)
        
        return SessionResponse(
            session_id=session_id,
            student_id=student_id,
            created_at=datetime.now().isoformat(),
            status="active"
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")

@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def get_session_info(session_id: str, session: Dict = Depends(get_session)):
    """Get session information"""
    return SessionResponse(
        session_id=session_id,
        student_id=session["student_id"],
        created_at=session["created_at"],
        status=session["status"]
    )

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, session: Dict = Depends(get_session)):
    """Delete a session"""
    session_manager.delete_session(session_id)
    return {"message": "Session deleted successfully"}

# Concept Learning Endpoints
@app.post("/api/sessions/{session_id}/concepts/explain", response_model=ConceptExplanationResponse)
async def explain_concept(
    session_id: str, 
    request: ExplainConceptRequest,
    session: Dict = Depends(get_session)
):
    """Get explanation for a concept"""
    try:
        loop = asyncio.get_event_loop()
        explanation = await loop.run_in_executor(
            executor,
            agent_service.explain_concept,
            session_id,
            request.subject,
            request.topic,
            request.difficulty_level,
            request.learning_style
        )
        
        return ConceptExplanationResponse(
            subject=request.subject,
            topic=request.topic,
            difficulty_level=request.difficulty_level,
            learning_style=request.learning_style,
            explanation=explanation,
            timestamp=datetime.now().isoformat()
        )
    except AgentException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error explaining concept: {e}")
        raise HTTPException(status_code=500, detail="Failed to explain concept")

# Practice Problem Endpoints
@app.post("/api/sessions/{session_id}/problems/generate", response_model=PracticeProblemsResponse)
async def generate_practice_problems(
    session_id: str,
    request: GenerateProblemsRequest,
    session: Dict = Depends(get_session)
):
    """Generate practice problems"""
    try:
        loop = asyncio.get_event_loop()
        problems = await loop.run_in_executor(
            executor,
            agent_service.create_practice_problems,
            session_id,
            request.subject,
            request.topic,
            request.count,
            request.difficulty
        )
        
        return PracticeProblemsResponse(
            session_id=session_id,
            subject=request.subject,
            topic=request.topic,
            difficulty=request.difficulty,
            problems=[
                ProblemData(
                    problem_id=str(uuid.uuid4()),
                    question=problems.get("problem", ""),
                    subject=request.subject,
                    topic=request.topic,
                    difficulty=request.difficulty,
                    created_at=datetime.now().isoformat()
                )
            ] if not isinstance(problems, list) else [
                ProblemData(
                    problem_id=str(uuid.uuid4()),
                    question=problem.get("problem", ""),
                    subject=request.subject,
                    topic=request.topic,
                    difficulty=request.difficulty,
                    created_at=datetime.now().isoformat()
                ) for problem in problems
            ],
            generated_at=datetime.now().isoformat()
        )
    except AgentException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating problems: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate problems")

@app.post("/api/sessions/{session_id}/problems/evaluate", response_model=SolutionEvaluationResponse)
async def evaluate_solution(
    session_id: str,
    request: EvaluateSolutionRequest,
    session: Dict = Depends(get_session)
):
    """Evaluate a student's solution"""
    try:
        loop = asyncio.get_event_loop()
        evaluation = await loop.run_in_executor(
            executor,
            agent_service.evaluate_solution,
            session_id,
            request.solution
        )
        
        if "error" in evaluation:
            raise AgentException(evaluation["error"])
        
        return SolutionEvaluationResponse(
            problem_id=request.problem_id,
            student_solution=request.solution,
            is_correct=evaluation.get("is_correct", False),
            performance_score=evaluation.get("performance_score", 0.0),
            feedback=evaluation.get("feedback", ""),
            evaluated_at=datetime.now().isoformat()
        )
    except AgentException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error evaluating solution: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate solution")

# Progress Analytics Endpoints
@app.get("/api/sessions/{session_id}/progress", response_model=ProgressReportResponse)
async def get_progress_report(
    session_id: str,
    session: Dict = Depends(get_session)
):
    """Get progress report for a session"""
    try:
        loop = asyncio.get_event_loop()
        report = await loop.run_in_executor(
            executor,
            agent_service.generate_progress_report,
            session_id
        )
        
        if "error" in report:
            raise AgentException(report["error"])
        
        return ProgressReportResponse(
            session_id=session_id,
            student_id=session["student_id"],
            summary=report.get("summary", ""),
            strengths=report.get("strengths", []),
            areas_for_improvement=report.get("areas_for_improvement", []),
            recommendations=report.get("recommendations", []),
            generated_at=report.get("timestamp", datetime.now().isoformat())
        )
    except AgentException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting progress report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get progress report")

@app.get("/api/students/{student_id}/analytics", response_model=StudentAnalyticsResponse)
async def get_student_analytics(student_id: str):
    """Get comprehensive analytics for a student"""
    try:
        loop = asyncio.get_event_loop()
        analytics = await loop.run_in_executor(
            executor,
            agent_service.get_student_analytics,
            student_id
        )
        
        return StudentAnalyticsResponse(
            student_id=student_id,
            total_sessions=analytics.get("total_sessions", 0),
            total_problems_solved=analytics.get("total_problems_solved", 0),
            average_score=analytics.get("average_score", 0.0),
            subjects_studied=analytics.get("subjects_studied", []),
            skill_progression=analytics.get("skill_progression", {}),
            time_spent_learning=analytics.get("time_spent_learning", 0),
            generated_at=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error getting student analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get student analytics")

# Conversation History Endpoints
@app.get("/api/sessions/{session_id}/conversation", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    session_id: str,
    limit: int = 50,
    session: Dict = Depends(get_session)
):
    """Get conversation history for a session"""
    try:
        loop = asyncio.get_event_loop()
        history = await loop.run_in_executor(
            executor,
            agent_service.get_conversation_history,
            session_id,
            limit
        )
        
        return ConversationHistoryResponse(
            session_id=session_id,
            messages=[
                ConversationMessage(
                    role=msg.get("role", ""),
                    content=msg.get("content", ""),
                    timestamp=msg.get("timestamp", datetime.now().isoformat()),
                    metadata=msg.get("metadata", {})
                ) for msg in history
            ],
            total_messages=len(history)
        )
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation history")

# User Profile Endpoints (Basic implementation)
@app.get("/api/students/{student_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(student_id: str):
    """Get user profile"""
    try:
        loop = asyncio.get_event_loop()
        profile = await loop.run_in_executor(
            executor,
            agent_service.get_user_profile,
            student_id
        )
        
        return UserProfileResponse(
            student_id=student_id,
            learning_preferences=profile.get("learning_preferences", {}),
            achievement_badges=profile.get("achievement_badges", []),
            total_sessions=profile.get("total_sessions", 0),
            created_at=profile.get("created_at", datetime.now().isoformat())
        )
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@app.put("/api/students/{student_id}/profile", response_model=UserProfileResponse)
async def update_user_profile(student_id: str, request: UpdateUserProfileRequest):
    """Update user profile"""
    try:
        loop = asyncio.get_event_loop()
        profile = await loop.run_in_executor(
            executor,
            agent_service.update_user_profile,
            student_id,
            request.learning_preferences
        )
        
        return UserProfileResponse(
            student_id=student_id,
            learning_preferences=profile.get("learning_preferences", {}),
            achievement_badges=profile.get("achievement_badges", []),
            total_sessions=profile.get("total_sessions", 0),
            created_at=profile.get("created_at", datetime.now().isoformat())
        )
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user profile")

# Utility Endpoints
@app.get("/api/subjects", response_model=List[str])
async def get_available_subjects():
    """Get list of available subjects"""
    return ["Mathematics", "Physics", "Chemistry", "Biology", "General"]

@app.get("/api/subjects/{subject}/topics", response_model=List[str])
async def get_subject_topics(subject: str):
    """Get topics for a specific subject"""
    topics_map = {
        "Mathematics": ["Algebra", "Geometry", "Calculus", "Statistics", "Trigonometry"],
        "Physics": ["Mechanics", "Thermodynamics", "Electromagnetism", "Optics", "Modern Physics"],
        "Chemistry": ["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry", "Biochemistry"],
        "Biology": ["Cell Biology", "Genetics", "Ecology", "Evolution", "Human Biology"],
        "General": ["Problem Solving", "Critical Thinking", "Study Skills"]
    }
    return topics_map.get(subject, [])

# Dashboard endpoint
@app.get("/api/students/{student_id}/dashboard", response_model=DashboardResponse)
async def get_dashboard_data(student_id: str):
    """Get dashboard data for a student"""
    try:
        loop = asyncio.get_event_loop()
        analytics = await loop.run_in_executor(
            executor,
            agent_service.get_student_analytics,
            student_id
        )
        
        # Create dashboard summary
        dashboard_summary = DashboardSummary(
            recent_activity=[
                {"type": "session", "description": f"Completed {analytics['total_sessions']} sessions"},
                {"type": "problems", "description": f"Solved {analytics['total_problems_solved']} problems"},
                {"type": "subjects", "description": f"Studied {len(analytics['subjects_studied'])} subjects"}
            ],
            performance_summary={
                "average_score": analytics["average_score"],
                "total_problems": analytics["total_problems_solved"],
                "subjects_count": len(analytics["subjects_studied"])
            },
            recommended_actions=[
                "Try practicing more problems",
                "Review challenging topics",
                "Explore new subjects"
            ],
            active_sessions=len(session_manager.get_student_sessions(student_id))
        )
        
        return DashboardResponse(
            student_id=student_id,
            summary=dashboard_summary,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

# Error handlers
@app.exception_handler(SessionNotFoundException)
async def session_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Session not found"}
    )

@app.exception_handler(AgentException)
async def agent_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

if __name__ == "__main__":
    # Ensure Docker is disabled for AutoGen
    os.environ["AUTOGEN_USE_DOCKER"] = "False"
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 