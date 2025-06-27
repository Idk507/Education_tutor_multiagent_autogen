import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import ConceptLearning from './pages/ConceptLearning/ConceptLearning';
import PracticeProblems from './pages/PracticeProblems/PracticeProblems';
import ProgressAnalytics from './pages/ProgressAnalytics/ProgressAnalytics';
import UserProfile from './pages/UserProfile/UserProfile';

import { apiService } from './services/api';
import { AppContext } from './context/AppContext';

function App() {
  const [loading, setLoading] = useState(true);
  const [apiConnected, setApiConnected] = useState(false);
  const [currentSession, setCurrentSession] = useState(null);
  const [studentId, setStudentId] = useState('student_demo_001');

  // Initialize app
  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      console.log('🚀 Initializing Educational Tutor App');
      
      // Check API connection
      await apiService.healthCheck();
      setApiConnected(true);
      console.log('✅ API connection established');
      
      // Create or restore session
      const savedSessionId = localStorage.getItem('currentSessionId');
      const savedStudentId = localStorage.getItem('studentId');
      
      if (savedStudentId) {
        setStudentId(savedStudentId);
      } else {
        localStorage.setItem('studentId', studentId);
      }

      if (savedSessionId) {
        try {
          const session = await apiService.getSession(savedSessionId);
          setCurrentSession(session);
          console.log('🔄 Restored session:', savedSessionId);
        } catch (error) {
          console.log('⚠️ Saved session invalid, creating new session');
          await createNewSession();
        }
      } else {
        await createNewSession();
      }
      
      toast.success('Welcome to Educational Tutor!');
      
    } catch (error) {
      console.error('❌ App initialization failed:', error);
      setApiConnected(false);
      toast.error('Failed to connect to the server. Please check if the API is running.');
    } finally {
      setLoading(false);
    }
  };

  const createNewSession = async () => {
    try {
      const session = await apiService.createSession(studentId);
      setCurrentSession(session);
      localStorage.setItem('currentSessionId', session.session_id);
      localStorage.setItem('studentId', studentId);
      console.log('✨ New session created:', session.session_id);
    } catch (error) {
      console.error('Failed to create session:', error);
      throw error;
    }
  };

  const contextValue = {
    currentSession,
    setCurrentSession,
    studentId,
    setStudentId,
    apiConnected,
    createNewSession,
  };

  if (loading) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        bgcolor="background.default"
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <CircularProgress size={60} thickness={4} />
        </motion.div>
        <Typography 
          variant="h6" 
          sx={{ mt: 2, color: 'text.secondary' }}
        >
          Initializing Educational Tutor...
        </Typography>
      </Box>
    );
  }

  if (!apiConnected) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        bgcolor="background.default"
        p={3}
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Typography variant="h4" align="center" color="error" gutterBottom>
            🔌 Connection Error
          </Typography>
          <Typography variant="body1" align="center" color="text.secondary" paragraph>
            Unable to connect to the Educational Tutor API.
          </Typography>
          <Typography variant="body2" align="center" color="text.secondary">
            Please ensure the FastAPI server is running on http://127.0.0.1:8000
          </Typography>
          <Box display="flex" justifyContent="center" mt={3}>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => window.location.reload()}
              style={{
                padding: '12px 24px',
                backgroundColor: '#1976d2',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: 500,
              }}
            >
              Retry Connection
            </motion.button>
          </Box>
        </motion.div>
      </Box>
    );
  }

  return (
    <AppContext.Provider value={contextValue}>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/learn" element={<ConceptLearning />} />
          <Route path="/practice" element={<PracticeProblems />} />
          <Route path="/progress" element={<ProgressAnalytics />} />
          <Route path="/profile" element={<UserProfile />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Layout>
    </AppContext.Provider>
  );
}

export default App; 