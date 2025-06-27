import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Skeleton,
  Alert,
  Paper,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Star as StarIcon,
  CheckCircle as CheckIcon,
  Assignment as AssignmentIcon,
  School as SchoolIcon,
  Analytics as AnalyticsIcon,
  EmojiEvents as TrophyIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import toast from 'react-hot-toast';

import { useAppContext } from '../../context/AppContext';
import { apiService } from '../../services/api';

const ProgressAnalytics = () => {
  const { currentSession, studentId } = useAppContext();
  
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState(null);
  const [progressReport, setProgressReport] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalyticsData();
  }, [studentId, currentSession]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [analyticsData, progressData] = await Promise.all([
        apiService.getStudentAnalytics(studentId).catch(() => null),
        currentSession ? apiService.getProgressReport(currentSession.session_id).catch(() => null) : null,
      ]);

      setAnalytics(analyticsData);
      setProgressReport(progressData);
      
    } catch (error) {
      console.error('Error loading analytics data:', error);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const getSkillLevelColor = (level) => {
    if (level >= 0.8) return 'success';
    if (level >= 0.6) return 'warning';
    return 'error';
  };

  const getSkillLevelLabel = (level) => {
    if (level >= 0.8) return 'Excellent';
    if (level >= 0.6) return 'Good';
    if (level >= 0.4) return 'Fair';
    return 'Needs Improvement';
  };

  const pieChartColors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff7f'];

  // Prepare chart data
  const performanceData = analytics?.performance_over_time?.map((item, index) => ({
    session: `Session ${index + 1}`,
    score: Math.round(item.score * 100),
    date: item.date,
  })) || [];

  const subjectData = analytics?.subjects_studied?.map((subject, index) => ({
    subject,
    problems: Math.floor(Math.random() * 20) + 5, // Mock data
    accuracy: Math.floor(Math.random() * 30) + 70, // Mock accuracy
  })) || [];

  const skillData = analytics?.skill_distribution ? Object.entries(analytics.skill_distribution).map(([skill, level]) => ({
    skill,
    level: Math.round(level * 100),
  })) : [];

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="text" width="40%" height={40} sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((item) => (
            <Grid item xs={12} md={6} key={item}>
              <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 2 }} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Progress Analytics 📊
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Track your learning journey and identify areas for improvement.
            </Typography>
          </Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadAnalyticsData}
            disabled={loading}
          >
            Refresh Data
          </Button>
        </Box>
      </motion.div>

      {error && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          {error}. Some data may not be available.
        </Alert>
      )}

      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card sx={{ textAlign: 'center', p: 2 }}>
              <TrophyIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
              <Typography variant="h4" fontWeight="bold" color="primary">
                {analytics?.total_sessions || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Learning Sessions
              </Typography>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card sx={{ textAlign: 'center', p: 2 }}>
              <AssignmentIcon sx={{ fontSize: 48, color: 'success.main', mb: 1 }} />
              <Typography variant="h4" fontWeight="bold" color="success.main">
                {analytics?.total_problems_solved || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Problems Solved
              </Typography>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card sx={{ textAlign: 'center', p: 2 }}>
              <TrendingUpIcon sx={{ fontSize: 48, color: 'warning.main', mb: 1 }} />
              <Typography variant="h4" fontWeight="bold" color="warning.main">
                {analytics?.average_score ? Math.round(analytics.average_score * 100) : 0}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average Score
              </Typography>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card sx={{ textAlign: 'center', p: 2 }}>
              <SchoolIcon sx={{ fontSize: 48, color: 'info.main', mb: 1 }} />
              <Typography variant="h4" fontWeight="bold" color="info.main">
                {analytics?.subjects_studied?.length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Subjects Studied
              </Typography>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Performance Over Time */}
        <Grid item xs={12} lg={8}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Performance Over Time
                </Typography>
                {performanceData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="session" />
                      <YAxis domain={[0, 100]} />
                      <Tooltip 
                        formatter={(value) => [`${value}%`, 'Score']}
                        labelFormatter={(label) => `Session: ${label}`}
                      />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="score" 
                        stroke="#8884d8" 
                        strokeWidth={2}
                        dot={{ fill: '#8884d8', strokeWidth: 2, r: 4 }}
                        activeDot={{ r: 6, stroke: '#8884d8', strokeWidth: 2 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <AnalyticsIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                    <Typography color="text.secondary">
                      No performance data available yet.
                      <br />
                      Start solving problems to see your progress!
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Subject Distribution */}
        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Subject Distribution
                </Typography>
                {analytics?.subjects_studied?.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={analytics.subjects_studied.map((subject, index) => ({
                          name: subject,
                          value: Math.floor(Math.random() * 10) + 1,
                        }))}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {analytics.subjects_studied.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={pieChartColors[index % pieChartColors.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <SchoolIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                    <Typography color="text.secondary">
                      No subjects data available yet.
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Subject Performance */}
        <Grid item xs={12} lg={8}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.7 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Subject Performance
                </Typography>
                {subjectData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={subjectData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="subject" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="problems" fill="#8884d8" name="Problems Solved" />
                      <Bar dataKey="accuracy" fill="#82ca9d" name="Accuracy %" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <AssignmentIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                    <Typography color="text.secondary">
                      No subject performance data available yet.
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Skill Levels */}
        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.8 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Skill Levels
                </Typography>
                {skillData.length > 0 ? (
                  <List>
                    {skillData.map((skill, index) => (
                      <ListItem key={skill.skill} sx={{ px: 0 }}>
                        <ListItemIcon>
                          <StarIcon color={getSkillLevelColor(skill.level / 100)} />
                        </ListItemIcon>
                        <ListItemText
                          primary={skill.skill}
                          secondary={
                            <Box>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                <Typography variant="body2" color="text.secondary">
                                  {skill.level}%
                                </Typography>
                                <Chip
                                  label={getSkillLevelLabel(skill.level / 100)}
                                  size="small"
                                  color={getSkillLevelColor(skill.level / 100)}
                                />
                              </Box>
                              <LinearProgress
                                variant="determinate"
                                value={skill.level}
                                color={getSkillLevelColor(skill.level / 100)}
                                sx={{ height: 6, borderRadius: 3 }}
                              />
                            </Box>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <StarIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                    <Typography color="text.secondary">
                      No skill data available yet.
                      <br />
                      Practice more to see your skill levels!
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Detailed Progress Report */}
        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.9 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Detailed Progress Report
                </Typography>
                
                {progressReport ? (
                  <Grid container spacing={3}>
                    {/* Summary */}
                    <Grid item xs={12} lg={6}>
                      <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                          Summary
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {progressReport.summary || 'No summary available'}
                        </Typography>
                      </Paper>
                    </Grid>

                    {/* Strengths */}
                    <Grid item xs={12} lg={6}>
                      <Paper sx={{ p: 2, bgcolor: 'success.50' }}>
                        <Typography variant="subtitle1" fontWeight="bold" gutterBottom color="success.dark">
                          Strengths
                        </Typography>
                        {progressReport.strengths?.length > 0 ? (
                          <List dense>
                            {progressReport.strengths.map((strength, index) => (
                              <ListItem key={index} sx={{ px: 0 }}>
                                <ListItemIcon>
                                  <CheckIcon color="success" />
                                </ListItemIcon>
                                <ListItemText primary={strength} />
                              </ListItem>
                            ))}
                          </List>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            Keep practicing to identify your strengths!
                          </Typography>
                        )}
                      </Paper>
                    </Grid>

                    {/* Areas for Improvement */}
                    <Grid item xs={12} lg={6}>
                      <Paper sx={{ p: 2, bgcolor: 'warning.50' }}>
                        <Typography variant="subtitle1" fontWeight="bold" gutterBottom color="warning.dark">
                          Areas for Improvement
                        </Typography>
                        {progressReport.areas_for_improvement?.length > 0 ? (
                          <List dense>
                            {progressReport.areas_for_improvement.map((area, index) => (
                              <ListItem key={index} sx={{ px: 0 }}>
                                <ListItemIcon>
                                  <TrendingUpIcon color="warning" />
                                </ListItemIcon>
                                <ListItemText primary={area} />
                              </ListItem>
                            ))}
                          </List>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            Great job! No major areas for improvement identified.
                          </Typography>
                        )}
                      </Paper>
                    </Grid>

                    {/* Recommendations */}
                    <Grid item xs={12} lg={6}>
                      <Paper sx={{ p: 2, bgcolor: 'info.50' }}>
                        <Typography variant="subtitle1" fontWeight="bold" gutterBottom color="info.dark">
                          Recommendations
                        </Typography>
                        {progressReport.recommendations?.length > 0 ? (
                          <List dense>
                            {progressReport.recommendations.map((rec, index) => (
                              <ListItem key={index} sx={{ px: 0 }}>
                                <ListItemIcon>
                                  <TrendingUpIcon color="info" />
                                </ListItemIcon>
                                <ListItemText primary={rec} />
                              </ListItem>
                            ))}
                          </List>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            Continue your excellent work!
                          </Typography>
                        )}
                      </Paper>
                    </Grid>
                  </Grid>
                ) : (
                  <Typography color="text.secondary">
                    No detailed progress report available yet. Start learning to generate insights!
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

export default ProgressAnalytics; 