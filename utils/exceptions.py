"""Custom exceptions for the Educational Tutor API"""

class EducationalTutorException(Exception):
    """Base exception for all educational tutor errors"""
    pass

class AgentException(EducationalTutorException):
    """Exception raised when there's an error with the educational agents"""
    pass

class SessionNotFoundException(EducationalTutorException):
    """Exception raised when a session is not found"""
    pass

class InvalidInputException(EducationalTutorException):
    """Exception raised when input validation fails"""
    pass

class ServiceUnavailableException(EducationalTutorException):
    """Exception raised when a service is temporarily unavailable"""
    pass

class RateLimitException(EducationalTutorException):
    """Exception raised when rate limit is exceeded"""
    pass

class AuthenticationException(EducationalTutorException):
    """Exception raised when authentication fails"""
    pass

class AuthorizationException(EducationalTutorException):
    """Exception raised when authorization fails"""
    pass 