# Educational Tutor FastAPI Backend

A comprehensive FastAPI backend for the Educational Tutor System that provides AI-powered tutoring through REST APIs.

## Features

- **Session Management**: Create and manage learning sessions
- **Concept Explanation**: Get detailed explanations for academic concepts
- **Practice Problems**: Generate and evaluate practice problems
- **Progress Tracking**: Monitor student learning progress and analytics
- **User Profiles**: Manage student profiles and preferences
- **Conversation History**: Track learning conversations
- **Multi-subject Support**: Mathematics, Physics, Chemistry, Biology, and more

## Architecture

The application is built using:
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **AsyncIO**: Asynchronous programming for better performance
- **AutoGen**: Multi-agent conversation framework
- **LangChain**: Framework for building applications with language models

## Project Structure

```
educational_tutor_agent/
├── app.py                          # Main FastAPI application
├── agent.py                        # Original educational agent system
├── models/
│   ├── __init__.py
│   └── api_models.py              # Pydantic models for API
├── services/
│   ├── __init__.py
│   ├── agent_service.py           # Service layer for agents
│   └── session_manager.py         # Session management
├── utils/
│   ├── __init__.py
│   └── exceptions.py              # Custom exceptions
├── requirements_fastapi.txt        # FastAPI dependencies
└── README_FastAPI.md              # This file
```

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd educational_tutor_agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements_fastapi.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   # Azure OpenAI Configuration
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_VERSION=2024-02-01
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
   
   # Application Settings
   DEBUG=True
   LOG_LEVEL=INFO
   ```

4. **Configure Azure OpenAI** in `agent.py`:
   Update the `llm_config` dictionary with your Azure OpenAI credentials.

## Running the Application

### Development Mode

```bash
# Run with auto-reload
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Or run directly
python app.py
```

### Production Mode

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative API docs**: http://localhost:8000/redoc

## API Endpoints

### Session Management

- `POST /api/sessions` - Create a new learning session
- `GET /api/sessions/{session_id}` - Get session information
- `DELETE /api/sessions/{session_id}` - Delete a session

### Concept Learning

- `POST /api/sessions/{session_id}/concepts/explain` - Get concept explanation

### Practice Problems

- `POST /api/sessions/{session_id}/problems/generate` - Generate practice problems
- `POST /api/sessions/{session_id}/problems/evaluate` - Evaluate student solutions

### Progress & Analytics

- `GET /api/sessions/{session_id}/progress` - Get progress report
- `GET /api/students/{student_id}/analytics` - Get student analytics
- `GET /api/students/{student_id}/dashboard` - Get dashboard data

### User Management

- `GET /api/students/{student_id}/profile` - Get user profile
- `PUT /api/students/{student_id}/profile` - Update user profile

### Conversation History

- `GET /api/sessions/{session_id}/conversation` - Get conversation history

### Utilities

- `GET /api/subjects` - Get available subjects
- `GET /api/subjects/{subject}/topics` - Get topics for a subject

## Usage Examples

### 1. Create a Session

```python
import requests

# Create a new session
response = requests.post("http://localhost:8000/api/sessions", 
                        json={"student_id": "student_123"})
session_data = response.json()
session_id = session_data["session_id"]
```

### 2. Explain a Concept

```python
# Get explanation for quadratic equations
response = requests.post(
    f"http://localhost:8000/api/sessions/{session_id}/concepts/explain",
    json={
        "subject": "Mathematics",
        "topic": "Quadratic Equations",
        "difficulty_level": "medium",
        "learning_style": "visual"
    }
)
explanation = response.json()
print(explanation["explanation"])
```

### 3. Generate Practice Problems

```python
# Generate practice problems
response = requests.post(
    f"http://localhost:8000/api/sessions/{session_id}/problems/generate",
    json={
        "subject": "Mathematics",
        "topic": "Quadratic Equations",
        "count": 2,
        "difficulty": "medium"
    }
)
problems = response.json()
```

### 4. Evaluate Solution

```python
# Evaluate student's solution
response = requests.post(
    f"http://localhost:8000/api/sessions/{session_id}/problems/evaluate",
    json={
        "problem_id": "problem_123",
        "solution": "x = 2, x = 5"
    }
)
evaluation = response.json()
print(f"Correct: {evaluation['is_correct']}")
print(f"Feedback: {evaluation['feedback']}")
```

### 5. Get Progress Report

```python
# Get progress report
response = requests.get(f"http://localhost:8000/api/sessions/{session_id}/progress")
progress = response.json()
print(f"Summary: {progress['summary']}")
print(f"Strengths: {progress['strengths']}")
```

## Frontend Integration

The API is designed to work with the UI requirements specified in `ui_structure.md`:

### Dashboard Integration
```javascript
// Fetch dashboard data
const dashboardData = await fetch(`/api/students/${studentId}/dashboard`);
const data = await dashboardData.json();
```

### Concept Learning Page
```javascript
// Explain concept
const explanation = await fetch(`/api/sessions/${sessionId}/concepts/explain`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        subject: 'Mathematics',
        topic: 'Derivatives',
        difficulty_level: 'medium',
        learning_style: 'visual'
    })
});
```

### Practice Problems Page
```javascript
// Generate problems
const problems = await fetch(`/api/sessions/${sessionId}/problems/generate`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        subject: 'Mathematics',
        topic: 'Algebra',
        count: 3,
        difficulty: 'medium'
    })
});
```

## Error Handling

The API uses standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (validation errors)
- `404` - Not Found (session/resource not found)
- `500` - Internal Server Error

Error responses include detailed messages:
```json
{
    "detail": "Session not found",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Authentication (Future)

Currently, the API doesn't require authentication. For production use, consider adding:

- JWT token authentication
- Rate limiting
- User roles and permissions
- API key management

## Testing

Run tests using pytest:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

## Deployment

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_fastapi.txt .
RUN pip install -r requirements_fastapi.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment

The application can be deployed to:
- **Azure App Service**
- **AWS Lambda** (with Mangum adapter)
- **Google Cloud Run**
- **Heroku**

## Monitoring and Logging

The application includes:
- Structured logging with timestamps
- Request/response logging
- Error tracking
- Performance metrics

For production, integrate with:
- Application Insights (Azure)
- CloudWatch (AWS)
- Stackdriver (Google Cloud)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review the error logs
- Create an issue in the repository 