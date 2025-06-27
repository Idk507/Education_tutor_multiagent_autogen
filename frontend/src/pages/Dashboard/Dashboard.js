import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Avatar,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Skeleton,
  Alert,
} from '@mui/material';
import {
  School as SchoolIcon,
  Quiz as QuizIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  AccessTime as TimeIcon,
  CheckCircle as CheckIcon,
  ArrowForward as ArrowIcon,
  Star as StarIcon,
  EmojiEvents as TrophyIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

import { useAppContext } from '../../context/AppContext';
import { apiService } from '../../services/api';

const Dashboard = () => {
  const navigate = useNavigate();
  const { currentSession, studentId } = useAppContext();
  
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, [studentId]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [dashboardResponse, analyticsResponse] = await Promise.all([
        apiService.getDashboardData(studentId).catch(() => null),
        apiService.getStudentAnalytics(studentId).catch(() => null),
      ]);

      setDashboardData(dashboardResponse);
      setAnalytics(analyticsResponse);
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      title: 'Learn a New Concept',
      description: 'Get AI-powered explanations for any topic',
      icon: <SchoolIcon />,
      color: '#2e7d32',
      path: '/learn',
      gradient: 'linear-gradient(135deg, #4caf50 0%, #2e7d32 100%)',
    },
    {
      title: 'Practice Problems',
      description: 'Solve problems and get instant feedback',
      icon: <QuizIcon />,
      color: '#ed6c02',
      path: '/practice',
      gradient: 'linear-gradient(135deg, #ff9800 0%, #ed6c02 100%)',
    },
    {
      title: 'View Progress',
      description: 'Track your learning journey and analytics',
      icon: <AnalyticsIcon />,
      color: '#9c27b0',
      path: '/progress',
      gradient: 'linear-gradient(135deg, #ba68c8 0%, #9c27b0 100%)',
    },
  ];

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="text" width="30%" height={40} sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          {[1, 2, 3].map((item) => (
            <Grid item xs={12} md={4} key={item}>
              <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2 }} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Welcome Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Welcome back! 👋
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Ready to continue your learning journey? Let's make today productive!
          </Typography>
        </Box>
      </motion.div>

      {error && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          {error}. Some features may not be available.
        </Alert>
      )}

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ mb: 2 }}>
          Quick Actions
        </Typography>
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {quickActions.map((action, index) => (
            <Grid item xs={12} md={4} key={action.title}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 * (index + 1) }}
                whileHover={{ y: -5 }}
              >
                <Card
                  sx={{
                    height: '100%',
                    cursor: 'pointer',
                    background: action.gradient,
                    color: 'white',
                    transition: 'all 0.3s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                    },
                  }}
                  onClick={() => navigate(action.path)}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar
                        sx={{
                          bgcolor: 'rgba(255,255,255,0.2)',
                          color: 'white',
                          mr: 2,
                        }}
                      >
                        {action.icon}
                      </Avatar>
                      <Typography variant="h6" fontWeight="bold">
                        {action.title}
                      </Typography>
                    </Box>
                    <Typography variant="body2" sx={{ mb: 3, opacity: 0.9 }}>
                      {action.description}
                    </Typography>
                    <Button
                      endIcon={<ArrowIcon />}
                      sx={{
                        color: 'white',
                        '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' },
                      }}
                    >
                      Get Started
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </motion.div>

      <Grid container spacing={3}>
        {/* Performance Summary */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Your Performance Summary
                </Typography>
                
                {analytics ? (
                  <Grid container spacing={3}>
                    <Grid item xs={6} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" fontWeight="bold" color="primary">
                          {analytics.total_sessions}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Total Sessions
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" fontWeight="bold" color="success.main">
                          {analytics.total_problems_solved}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Problems Solved
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" fontWeight="bold" color="warning.main">
                          {Math.round(analytics.average_score * 100)}%
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Average Score
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" fontWeight="bold" color="info.main">
                          {analytics.subjects_studied.length}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Subjects Studied
                        </Typography>
                      </Box>
                    </Grid>

                    {analytics.subjects_studied.length > 0 && (
                      <Grid item xs={12}>
                        <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                          Subjects You're Learning:
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {analytics.subjects_studied.map((subject) => (
                            <Chip
                              key={subject}
                              label={subject}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                          ))}
                        </Box>
                      </Grid>
                    )}
                  </Grid>
                ) : (
                  <Typography color="text.secondary">
                    Start learning to see your performance summary!
                  </Typography>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Recent Activity
                </Typography>
                
                {dashboardData?.summary?.recent_activity?.length > 0 ? (
                  <List dense>
                    {dashboardData.summary.recent_activity.map((activity, index) => (
                      <ListItem key={index} sx={{ px: 0 }}>
                        <ListItemIcon>
                          {activity.type === 'session' && <TimeIcon color="primary" />}
                          {activity.type === 'problems' && <CheckIcon color="success" />}
                          {activity.type === 'subjects' && <StarIcon color="warning" />}
                        </ListItemIcon>
                        <ListItemText
                          primary={activity.description}
                          secondary="Recent activity"
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 3 }}>
                    <TrophyIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                    <Typography color="text.secondary">
                      No recent activity yet.
                      <br />
                      Start learning to see updates here!
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Recommendations */}
        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Recommended Next Steps
                </Typography>
                
                {dashboardData?.summary?.recommended_actions?.length > 0 ? (
                  <Grid container spacing={2}>
                    {dashboardData.summary.recommended_actions.map((action, index) => (
                      <Grid item xs={12} md={4} key={index}>
                        <Box
                          sx={{
                            p: 2,
                            border: '1px solid',
                            borderColor: 'grey.200',
                            borderRadius: 2,
                            textAlign: 'center',
                            '&:hover': {
                              bgcolor: 'grey.50',
                              borderColor: 'primary.main',
                            },
                            transition: 'all 0.2s ease-in-out',
                          }}
                        >
                          <TrendingUpIcon color="primary" sx={{ mb: 1 }} />
                          <Typography variant="body2">{action}</Typography>
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                ) : (
                  <Typography color="text.secondary">
                    Start using the Educational Tutor to get personalized recommendations!
                  </Typography>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 