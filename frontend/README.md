# Educational Tutor Frontend

This is the React frontend for the AI-Powered Educational Tutor System. It provides a modern, responsive user interface for students to interact with the educational AI tutor.

## Features

- **Dashboard**: Overview of learning progress and quick actions
- **Concept Learning**: Request AI explanations for any academic topic
- **Practice Problems**: Generate and solve practice problems with AI feedback
- **Progress Analytics**: Detailed charts and analytics of learning progress
- **User Profile**: Manage personal information and learning preferences

## Prerequisites

- Node.js (version 14 or higher)
- npm or yarn
- The FastAPI backend server running on http://127.0.0.1:8000

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

1. Start the development server:
```bash
npm start
```

2. Open your browser and navigate to:
```
http://localhost:3000
```

The application will automatically connect to the FastAPI backend at http://127.0.0.1:8000.

## Project Structure

```
frontend/
├── public/              # Static files
├── src/
│   ├── components/      # Reusable UI components
│   │   └── Layout/      # Main layout component
│   ├── context/         # React context for state management
│   ├── pages/          # Main application pages
│   │   ├── Dashboard/
│   │   ├── ConceptLearning/
│   │   ├── PracticeProblems/
│   │   ├── ProgressAnalytics/
│   │   └── UserProfile/
│   ├── services/       # API service layer
│   ├── App.js          # Main app component
│   └── index.js        # Entry point
├── package.json
└── README.md
```

## Key Dependencies

- **React 18**: Core framework
- **Material-UI (MUI)**: UI component library
- **React Router**: Navigation and routing
- **Recharts**: Charts and data visualization
- **Axios**: HTTP client for API calls
- **Framer Motion**: Smooth animations
- **React Hot Toast**: Notifications
- **React Markdown**: Markdown rendering
- **React KaTeX**: Math equation rendering

## API Integration

The frontend integrates with the FastAPI backend through the following endpoints:

- Session management
- Concept explanations
- Practice problem generation and evaluation
- Progress tracking and analytics
- User profile management

## Environment Variables

Create a `.env` file in the frontend directory if you need to customize the API URL:

```
REACT_APP_API_URL=http://127.0.0.1:8000
```

## Building for Production

To create a production build:

```bash
npm run build
```

This will create a `build` directory with optimized production files.

## Features Overview

### Dashboard
- Quick action cards for main features
- Performance overview with statistics
- Recent activity and recommendations

### Concept Learning
- Subject and topic selection
- Difficulty level and learning style preferences
- AI-generated explanations with markdown support
- Math equation rendering with KaTeX

### Practice Problems
- Custom problem generation
- Interactive problem-solving workflow
- Step-by-step progress tracking
- AI evaluation with detailed feedback

### Progress Analytics
- Performance charts over time
- Subject distribution pie charts
- Skill level tracking with progress bars
- Detailed progress reports

### User Profile
- Personal information management
- Learning preferences configuration
- Subject preferences
- Recent activity tracking

## Troubleshooting

1. **Connection Error**: Ensure the FastAPI backend is running on http://127.0.0.1:8000
2. **Port Issues**: If port 3000 is occupied, the app will prompt to use a different port
3. **Missing Dependencies**: Run `npm install` to ensure all packages are installed

## Development

To contribute to the frontend:

1. Follow the existing code structure and patterns
2. Use Material-UI components for consistency
3. Implement proper error handling and loading states
4. Add TypeScript types for better development experience (optional)
5. Write unit tests for new components (optional)

## License

This project is part of the Educational Tutor System. See the main project license for details. 