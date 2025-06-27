from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# Base Models
class BaseResponse(BaseModel):
    """Base response model"""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Session Models
class CreateSessionRequest(BaseModel):
    """Request model for creating a new session"""
    student_id: Optional[str] = Field(None, description="Student ID, will be generated if not provided")

class SessionResponse(BaseResponse):
    """Response model for session information"""
    session_id: str = Field(..., description="Unique session identifier")
    student_id: str = Field(..., description="Student identifier")
    created_at: str = Field(..., description="Session creation timestamp")
    status: str = Field(..., description="Session status")

# Concept Learning Models
class ExplainConceptRequest(BaseModel):
    """Request model for concept explanation"""
    subject: str = Field(..., description="Subject name (e.g., Mathematics, Physics)")
    topic: str = Field(..., description="Topic name (e.g., Quadratic Equations)")
    difficulty_level: str = Field(default="medium", description="Difficulty level: easy, medium, hard")
    learning_style: str = Field(default="visual", description="Learning style: visual, auditory, kinesthetic")

class ConceptExplanationResponse(BaseResponse):
    """Response model for concept explanation"""
    subject: str = Field(..., description="Subject name")
    topic: str = Field(..., description="Topic name")
    difficulty_level: str = Field(..., description="Difficulty level")
    learning_style: str = Field(..., description="Learning style")
    explanation: str = Field(..., description="Detailed explanation")

# Practice Problem Models
class GenerateProblemsRequest(BaseModel):
    """Request model for generating practice problems"""
    subject: str = Field(..., description="Subject name")
    topic: str = Field(..., description="Topic name")
    count: int = Field(default=1, ge=1, le=5, description="Number of problems to generate")
    difficulty: str = Field(default="medium", description="Difficulty level")

class ProblemData(BaseModel):
    """Model for problem data"""
    problem_id: str = Field(..., description="Unique problem identifier")
    question: str = Field(..., description="Problem question")
    subject: str = Field(..., description="Subject name")
    topic: str = Field(..., description="Topic name")
    difficulty: str = Field(..., description="Difficulty level")
    created_at: str = Field(..., description="Problem creation timestamp")

class PracticeProblemsResponse(BaseResponse):
    """Response model for practice problems"""
    session_id: str = Field(..., description="Session identifier")
    subject: str = Field(..., description="Subject name")
    topic: str = Field(..., description="Topic name")
    difficulty: str = Field(..., description="Difficulty level")
    problems: List[ProblemData] = Field(..., description="List of generated problems")
    generated_at: str = Field(..., description="Generation timestamp")

# Solution Evaluation Models
class EvaluateSolutionRequest(BaseModel):
    """Request model for solution evaluation"""
    problem_id: str = Field(..., description="Problem identifier")
    solution: str = Field(..., description="Student's solution")

class SolutionEvaluationResponse(BaseResponse):
    """Response model for solution evaluation"""
    problem_id: str = Field(..., description="Problem identifier")
    student_solution: str = Field(..., description="Student's solution")
    is_correct: bool = Field(..., description="Whether the solution is correct")
    performance_score: float = Field(..., ge=0.0, le=1.0, description="Performance score (0.0 to 1.0)")
    feedback: str = Field(..., description="Detailed feedback")
    evaluated_at: str = Field(..., description="Evaluation timestamp")

# Progress and Analytics Models
class ProgressReportResponse(BaseResponse):
    """Response model for progress report"""
    session_id: str = Field(..., description="Session identifier")
    student_id: str = Field(..., description="Student identifier")
    summary: str = Field(..., description="Progress summary")
    strengths: List[str] = Field(..., description="List of strengths")
    areas_for_improvement: List[str] = Field(..., description="Areas needing improvement")
    recommendations: List[str] = Field(..., description="Recommendations for improvement")
    generated_at: str = Field(..., description="Report generation timestamp")

class StudentAnalyticsResponse(BaseResponse):
    """Response model for student analytics"""
    student_id: str = Field(..., description="Student identifier")
    total_sessions: int = Field(..., description="Total number of sessions")
    total_problems_solved: int = Field(..., description="Total problems solved")
    average_score: float = Field(..., ge=0.0, le=1.0, description="Average performance score")
    subjects_studied: List[str] = Field(..., description="List of subjects studied")
    skill_progression: Dict[str, Dict[str, float]] = Field(..., description="Skill progression by subject/topic")
    time_spent_learning: int = Field(..., description="Total time spent learning (minutes)")
    generated_at: str = Field(..., description="Analytics generation timestamp")

# Conversation History Models
class ConversationMessage(BaseModel):
    """Model for conversation message"""
    role: str = Field(..., description="Message role (student, tutor, system)")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="Message timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class ConversationHistoryResponse(BaseResponse):
    """Response model for conversation history"""
    session_id: str = Field(..., description="Session identifier")
    messages: List[ConversationMessage] = Field(..., description="List of conversation messages")
    total_messages: int = Field(..., description="Total number of messages")

# User Profile Models
class LearningPreferences(BaseModel):
    """Model for learning preferences"""
    default_difficulty: str = Field(default="medium", description="Default difficulty level")
    preferred_learning_style: str = Field(default="visual", description="Preferred learning style")
    notification_settings: Dict[str, bool] = Field(default_factory=dict, description="Notification preferences")

class AchievementBadge(BaseModel):
    """Model for achievement badge"""
    badge_id: str = Field(..., description="Badge identifier")
    name: str = Field(..., description="Badge name")
    description: str = Field(..., description="Badge description")
    earned_at: str = Field(..., description="Badge earned timestamp")
    subject: Optional[str] = Field(None, description="Related subject")

class UserProfileResponse(BaseResponse):
    """Response model for user profile"""
    student_id: str = Field(..., description="Student identifier")
    learning_preferences: LearningPreferences = Field(..., description="Learning preferences")
    achievement_badges: List[AchievementBadge] = Field(..., description="List of earned badges")
    total_sessions: int = Field(..., description="Total number of sessions")
    created_at: str = Field(..., description="Profile creation timestamp")

class UpdateUserProfileRequest(BaseModel):
    """Request model for updating user profile"""
    learning_preferences: LearningPreferences = Field(..., description="Updated learning preferences")

# Error Models
class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error detail message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Dashboard Models
class DashboardSummary(BaseModel):
    """Model for dashboard summary"""
    recent_activity: List[Dict[str, Any]] = Field(..., description="Recent learning activities")
    performance_summary: Dict[str, float] = Field(..., description="Performance summary")
    recommended_actions: List[str] = Field(..., description="Recommended next actions")
    active_sessions: int = Field(..., description="Number of active sessions")

class DashboardResponse(BaseResponse):
    """Response model for dashboard data"""
    student_id: str = Field(..., description="Student identifier")
    summary: DashboardSummary = Field(..., description="Dashboard summary")

# Search and Filter Models
class SearchConceptsRequest(BaseModel):
    """Request model for searching concepts"""
    query: str = Field(..., min_length=1, description="Search query")
    subject: Optional[str] = Field(None, description="Filter by subject")
    difficulty: Optional[str] = Field(None, description="Filter by difficulty")

class ConceptSearchResult(BaseModel):
    """Model for concept search result"""
    subject: str = Field(..., description="Subject name")
    topic: str = Field(..., description="Topic name")
    description: str = Field(..., description="Brief description")
    difficulty_levels: List[str] = Field(..., description="Available difficulty levels")

class SearchConceptsResponse(BaseResponse):
    """Response model for concept search"""
    query: str = Field(..., description="Search query")
    results: List[ConceptSearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")

# Batch Operations Models
class BatchEvaluationRequest(BaseModel):
    """Request model for batch solution evaluation"""
    evaluations: List[EvaluateSolutionRequest] = Field(..., description="List of solutions to evaluate")

class BatchEvaluationResponse(BaseResponse):
    """Response model for batch evaluation"""
    session_id: str = Field(..., description="Session identifier")
    evaluations: List[SolutionEvaluationResponse] = Field(..., description="List of evaluation results")
    summary: Dict[str, Any] = Field(..., description="Batch evaluation summary")

# Statistics Models
class SubjectStatistics(BaseModel):
    """Model for subject statistics"""
    subject: str = Field(..., description="Subject name")
    total_problems: int = Field(..., description="Total problems in subject")
    solved_problems: int = Field(..., description="Problems solved by student")
    average_score: float = Field(..., description="Average score in subject")
    topics_covered: List[str] = Field(..., description="Topics covered in subject")

class LearningStatisticsResponse(BaseResponse):
    """Response model for learning statistics"""
    student_id: str = Field(..., description="Student identifier")
    subjects: List[SubjectStatistics] = Field(..., description="Statistics by subject")
    overall_progress: float = Field(..., description="Overall learning progress")
    streak_days: int = Field(..., description="Current learning streak in days") 