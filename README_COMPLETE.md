# 🎓 Educational Tutor System - Complete Full-Stack Application

A modern, AI-powered educational tutoring platform with a React frontend and FastAPI backend, featuring multi-agent AI tutors for personalized learning experiences.

## 🚀 Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd educational_tutor_agent
   ```

2. **Run the complete application:**
   ```bash
   python start_app.py
   ```

   This will:
   - Check and install all dependencies
   - Start the FastAPI backend on http://127.0.0.1:8000
   - Start the React frontend on http://localhost:3000
   - Open your browser automatically

## 📋 System Requirements

- **Python 3.8+** with pip
- **Node.js 14+** with npm
- **Azure OpenAI API** credentials (required for AI features)
- **8GB RAM** minimum (for AI model operations)

## 🏗️ Architecture Overview

### Backend (FastAPI)
- **Multi-agent AI system** using AutoGen framework
- **Three specialized agents:**
  - 🧠 Educational Tutor (concept explanations, problem generation)
  - 👤 Student Learner (user interaction, learning engagement)  
  - 📊 Progress Tracker (analytics, progress reports)
- **Azure OpenAI integration** with GPT-4o model
- **Session management** with automatic cleanup
- **Comprehensive API** with 15+ endpoints
- **Data persistence** in JSON format

### Frontend (React)
- **Modern Material-UI design** with responsive layout
- **5 main pages:**
  - 🏠 Dashboard (overview, quick actions)
  - 📚 Concept Learning (AI explanations)
  - 🧮 Practice Problems (problem solving with feedback)
  - 📊 Progress Analytics (charts, insights)
  - 👤 User Profile (preferences, settings)
- **Real-time features** with WebSocket-like updates
- **Math rendering** with KaTeX support
- **Smooth animations** with Framer Motion

## 🔧 Manual Setup (Alternative)

### Backend Setup
1. **Install Python dependencies:**
   ```bash
   pip install -r requirements_fastapi.txt
   ```

2. **Configure Azure OpenAI:**
   - Copy your Azure OpenAI credentials to `config/llm_config.py`
   - Update endpoint, API key, and model deployment names

3. **Start the backend:**
   ```bash
   python run_fastapi.py
   ```

### Frontend Setup
1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

## 🎯 Features Showcase

### 🧠 AI-Powered Learning
- **Adaptive explanations** based on learning style and difficulty preference
- **Custom problem generation** for any subject and topic
- **Intelligent feedback** with step-by-step solution analysis
- **Progress tracking** with skill level assessment

### 💻 Modern UI/UX
- **Responsive design** that works on desktop, tablet, and mobile
- **Intuitive navigation** with sidebar and breadcrumbs
- **Interactive charts** showing learning progress over time
- **Real-time notifications** for immediate feedback

### 🔄 Session Management
- **Automatic session creation** for new users
- **Persistent conversation history** across sessions
- **Progress data synchronization** between frontend and backend
- **Session cleanup** to prevent memory leaks

## 📊 API Documentation

Once the backend is running, visit:
- **Interactive API docs:** http://127.0.0.1:8000/docs
- **OpenAPI spec:** http://127.0.0.1:8000/redoc

### Key Endpoints
```
POST /api/sessions                    # Create new learning session
GET  /api/sessions/{id}              # Get session details
POST /api/sessions/{id}/concepts/explain    # Request concept explanation
POST /api/sessions/{id}/problems/generate   # Generate practice problems
POST /api/sessions/{id}/problems/evaluate   # Evaluate solutions
GET  /api/sessions/{id}/progress            # Get progress report
GET  /api/students/{id}/analytics           # Get student analytics
```

## 🎨 Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── Layout/                 # Navigation and layout
│   │   ├── pages/
│   │   │   ├── Dashboard/              # Landing page with overview
│   │   │   ├── ConceptLearning/        # AI explanations interface
│   │   │   ├── PracticeProblems/       # Problem solving workflow
│   │   │   ├── ProgressAnalytics/      # Charts and analytics
│   │   │   └── UserProfile/            # Profile management
│   │   ├── services/
│   │   │   └── api.js                  # API integration layer
│   │   ├── context/
│   │   │   └── AppContext.js           # Global state management
│   │   └── App.js                      # Main application component
│   └── App.js                      # Main application component
```

## 🧪 Testing the Application

### Backend Testing
```bash
python test_api.py
```

### Frontend Testing
1. **Concept Learning:**
   - Select Mathematics > Algebra
   - Choose difficulty level and learning style
   - Request explanation and verify AI response

2. **Practice Problems:**
   - Generate a problem for any subject
   - Submit a solution and get AI feedback
   - Try different difficulty levels

3. **Progress Analytics:**
   - Check dashboard for session statistics
   - View charts showing learning progress
   - Explore skill level breakdowns

## 🔐 Security Features

- **Input validation** with Pydantic models
- **Error handling** with proper HTTP status codes
- **CORS configuration** for cross-origin requests
- **Session isolation** preventing data leakage
- **API rate limiting** (can be configured)

## 🌟 Advanced Features

### Adaptive Learning
- **Difficulty adjustment** based on performance
- **Learning style recognition** from user interactions
- **Personalized recommendations** for study topics
- **Skill gap identification** with targeted suggestions

### Analytics & Insights
- **Performance trends** over time
- **Subject mastery levels** with visual indicators
- **Session completion rates** and engagement metrics
- **Comparative analysis** across different topics

## 🚧 Troubleshooting

### Common Issues

1. **Backend won't start:**
   - Check Azure OpenAI credentials in `config/llm_config.py`
   - Ensure all Python packages are installed
   - Verify port 8000 is not in use

2. **Frontend connection errors:**
   - Confirm backend is running on http://127.0.0.1:8000
   - Check browser console for CORS errors
   - Verify Node.js version (14+)

3. **AI responses not working:**
   - Validate Azure OpenAI API key and endpoint
   - Check model deployment names match configuration
   - Monitor API usage quotas

### Performance Optimization

- **Backend:** Adjust session timeout and cleanup intervals
- **Frontend:** Enable React production build for deployment
- **Database:** Consider PostgreSQL for production use
- **Caching:** Implement Redis for session data

## 🚀 Deployment

### Development
- Backend: http://127.0.0.1:8000
- Frontend: http://localhost:3000

### Production
1. **Backend deployment:**
   - Use Docker with `uvicorn` server
   - Configure environment variables
   - Set up reverse proxy (nginx)

2. **Frontend deployment:**
   - Build optimized bundle: `npm run build`
   - Deploy to CDN or static hosting
   - Configure API endpoint URLs

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎉 Success!

If you see this message after running `python start_app.py`, your Educational Tutor System is ready! 

- 🌐 **Frontend:** http://localhost:3000
- 🔗 **Backend:** http://127.0.0.1:8000
- 📖 **API Docs:** http://127.0.0.1:8000/docs

Start learning with AI-powered personalized tutoring! 🚀 