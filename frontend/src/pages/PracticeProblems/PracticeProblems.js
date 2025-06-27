import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper,
  Stepper,
  Step,
  StepLabel,
  StepContent,
} from '@mui/material';
import {
  Quiz as QuizIcon,
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
  AutoAwesome as AutoAwesomeIcon,
  PlayArrow as PlayIcon,
  Send as SendIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';
import { v4 as uuidv4 } from 'uuid';

import { useAppContext } from '../../context/AppContext';
import { apiService } from '../../services/api';

const PracticeProblems = () => {
  const { currentSession } = useAppContext();
  
  const [formData, setFormData] = useState({
    subject: 'Mathematics',
    topic: 'Algebra',
    count: 1,
    difficulty: 'medium',
  });
  
  const [subjects, setSubjects] = useState([]);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(false);
  const [problems, setProblems] = useState([]);
  const [currentProblem, setCurrentProblem] = useState(null);
  const [solution, setSolution] = useState('');
  const [evaluation, setEvaluation] = useState(null);
  const [evaluating, setEvaluating] = useState(false);
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    loadSubjects();
  }, []);

  useEffect(() => {
    if (formData.subject) {
      loadTopics(formData.subject);
    }
  }, [formData.subject]);

  const loadSubjects = async () => {
    try {
      const subjectsData = await apiService.getSubjects();
      setSubjects(subjectsData || ['Mathematics', 'Physics', 'Chemistry', 'Biology']);
    } catch (error) {
      console.error('Error loading subjects:', error);
      setSubjects(['Mathematics', 'Physics', 'Chemistry', 'Biology']);
    }
  };

  const loadTopics = async (subject) => {
    try {
      const topicsData = await apiService.getTopics(subject);
      setTopics(topicsData || ['Algebra', 'Geometry', 'Calculus']);
    } catch (error) {
      console.error('Error loading topics:', error);
      setTopics(['Algebra', 'Geometry', 'Calculus']);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleGenerateProblems = async () => {
    if (!currentSession) {
      toast.error('No active session. Please refresh the page.');
      return;
    }

    try {
      setLoading(true);
      setActiveStep(1);
      
      const response = await apiService.generateProblems(currentSession.session_id, formData);
      
      // Handle different response formats
      let problemData;
      if (response.problems && response.problems.length > 0) {
        problemData = response.problems[0];
      } else if (response.question) {
        problemData = {
          problem_id: uuidv4(),
          question: response.question,
          subject: formData.subject,
          topic: formData.topic,
          difficulty: formData.difficulty,
        };
      } else {
        throw new Error('No problems generated');
      }
      
      setCurrentProblem(problemData);
      setActiveStep(2);
      toast.success('Practice problem generated successfully!');
      
    } catch (error) {
      console.error('Error generating problems:', error);
      toast.error('Failed to generate problems');
      setActiveStep(0);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitSolution = async () => {
    if (!currentSession || !currentProblem || !solution.trim()) {
      toast.error('Please enter your solution');
      return;
    }

    try {
      setEvaluating(true);
      setActiveStep(3);
      
      const response = await apiService.evaluateSolution(currentSession.session_id, {
        problem_id: currentProblem.problem_id,
        solution: solution.trim(),
      });
      
      setEvaluation(response);
      setActiveStep(4);
      
      if (response.is_correct) {
        toast.success('Correct! Well done! 🎉');
      } else {
        toast.success('Solution evaluated. Check the feedback!');
      }
      
    } catch (error) {
      console.error('Error evaluating solution:', error);
      toast.error('Failed to evaluate solution');
      setActiveStep(2);
    } finally {
      setEvaluating(false);
    }
  };

  const handleNewProblem = () => {
    setCurrentProblem(null);
    setProblems([]);
    setSolution('');
    setEvaluation(null);
    setActiveStep(0);
  };

  const handleRetryProblem = () => {
    setSolution('');
    setEvaluation(null);
    setActiveStep(2);
  };

  const steps = [
    'Generate Problem',
    'AI Creating Problem',
    'Solve Problem',
    'AI Evaluating',
    'Review Feedback',
  ];

  const difficultyOptions = [
    { value: 'easy', label: 'Easy', color: 'success' },
    { value: 'medium', label: 'Medium', color: 'warning' },
    { value: 'hard', label: 'Hard', color: 'error' },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Practice Problems 🧮
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Generate custom practice problems and get instant AI feedback on your solutions.
          </Typography>
        </Box>
      </motion.div>

      <Grid container spacing={3}>
        {/* Problem Generation Form */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Generate Practice Problems
                </Typography>
                
                <Box sx={{ mt: 3 }}>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <FormControl fullWidth>
                        <InputLabel>Subject</InputLabel>
                        <Select
                          value={formData.subject}
                          label="Subject"
                          onChange={(e) => handleInputChange('subject', e.target.value)}
                        >
                          {subjects.map((subject) => (
                            <MenuItem key={subject} value={subject}>
                              {subject}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12}>
                      <FormControl fullWidth>
                        <InputLabel>Topic</InputLabel>
                        <Select
                          value={formData.topic}
                          label="Topic"
                          onChange={(e) => handleInputChange('topic', e.target.value)}
                        >
                          {topics.map((topic) => (
                            <MenuItem key={topic} value={topic}>
                              {topic}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Or enter custom topic"
                        placeholder="e.g., Linear Equations, Photosynthesis"
                        value={formData.topic}
                        onChange={(e) => handleInputChange('topic', e.target.value)}
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <Typography variant="subtitle2" gutterBottom>
                        Difficulty Level
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        {difficultyOptions.map((option) => (
                          <Chip
                            key={option.value}
                            label={option.label}
                            onClick={() => handleInputChange('difficulty', option.value)}
                            color={formData.difficulty === option.value ? option.color : 'default'}
                            variant={formData.difficulty === option.value ? 'filled' : 'outlined'}
                            sx={{ cursor: 'pointer' }}
                          />
                        ))}
                      </Box>
                    </Grid>

                    <Grid item xs={12}>
                      <Button
                        fullWidth
                        variant="contained"
                        size="large"
                        onClick={handleGenerateProblems}
                        disabled={loading || !formData.subject || !formData.topic}
                        startIcon={loading ? <CircularProgress size={20} /> : <AutoAwesomeIcon />}
                        sx={{ mt: 2 }}
                      >
                        {loading ? 'Generating...' : 'Generate Problem'}
                      </Button>
                    </Grid>
                  </Grid>
                </Box>
              </CardContent>
            </Card>

            {/* Progress Stepper */}
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Progress
                </Typography>
                <Stepper activeStep={activeStep} orientation="vertical">
                  {steps.map((label, index) => (
                    <Step key={label}>
                      <StepLabel>
                        <Typography variant="body2">{label}</Typography>
                      </StepLabel>
                    </Step>
                  ))}
                </Stepper>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Problem Solving Area */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card sx={{ minHeight: '500px' }}>
              <CardContent>
                {loading ? (
                  <Box sx={{ textAlign: 'center', py: 8 }}>
                    <CircularProgress size={60} />
                    <Typography variant="h6" sx={{ mt: 2 }}>
                      Generating your practice problem...
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Our AI tutor is creating a custom problem for you
                    </Typography>
                  </Box>
                ) : currentProblem ? (
                  <Box>
                    {/* Problem Display */}
                    <Box sx={{ mb: 4 }}>
                      <Typography variant="h5" fontWeight="bold" gutterBottom>
                        Practice Problem
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
                        <Chip label={formData.subject} size="small" color="primary" />
                        <Chip label={formData.topic} size="small" color="secondary" />
                        <Chip label={formData.difficulty} size="small" color="warning" />
                      </Box>
                      
                      <Paper
                        sx={{
                          p: 3,
                          bgcolor: 'grey.50',
                          border: '2px solid',
                          borderColor: 'primary.main',
                          borderRadius: 2,
                        }}
                      >
                        <Typography
                          variant="body1"
                          sx={{
                            fontSize: '1.1rem',
                            lineHeight: 1.6,
                            fontWeight: 500,
                          }}
                        >
                          {currentProblem.question}
                        </Typography>
                      </Paper>
                    </Box>

                    {/* Solution Input */}
                    {!evaluation && (
                      <Box sx={{ mb: 4 }}>
                        <Typography variant="h6" fontWeight="bold" gutterBottom>
                          Your Solution
                        </Typography>
                        <TextField
                          fullWidth
                          multiline
                          rows={4}
                          placeholder="Enter your solution here... Show your work step by step for better feedback!"
                          value={solution}
                          onChange={(e) => setSolution(e.target.value)}
                          sx={{ mb: 2 }}
                        />
                        <Box sx={{ display: 'flex', gap: 2 }}>
                          <Button
                            variant="contained"
                            onClick={handleSubmitSolution}
                            disabled={evaluating || !solution.trim()}
                            startIcon={evaluating ? <CircularProgress size={20} /> : <SendIcon />}
                          >
                            {evaluating ? 'Evaluating...' : 'Submit Solution'}
                          </Button>
                          <Button
                            variant="outlined"
                            onClick={handleNewProblem}
                            startIcon={<RefreshIcon />}
                          >
                            New Problem
                          </Button>
                        </Box>
                      </Box>
                    )}

                    {/* Evaluation Results */}
                    {evaluation && (
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                      >
                        <Card
                          sx={{
                            border: '2px solid',
                            borderColor: evaluation.is_correct ? 'success.main' : 'warning.main',
                            bgcolor: evaluation.is_correct ? 'success.50' : 'warning.50',
                          }}
                        >
                          <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                              {evaluation.is_correct ? (
                                <CheckIcon color="success" sx={{ mr: 1, fontSize: 28 }} />
                              ) : (
                                <CancelIcon color="warning" sx={{ mr: 1, fontSize: 28 }} />
                              )}
                              <Typography variant="h6" fontWeight="bold">
                                {evaluation.is_correct ? 'Correct! 🎉' : 'Not quite right 🤔'}
                              </Typography>
                            </Box>

                            <Typography variant="body2" color="text.secondary" gutterBottom>
                              Performance Score: {Math.round(evaluation.performance_score * 100)}%
                            </Typography>

                            <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ mt: 3 }}>
                              Feedback:
                            </Typography>
                            <Box
                              sx={{
                                '& p': { mb: 1, lineHeight: 1.6 },
                                '& ul, & ol': { mb: 1, pl: 3 },
                              }}
                            >
                              <ReactMarkdown>{evaluation.feedback}</ReactMarkdown>
                            </Box>

                            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                              <Button
                                variant="contained"
                                onClick={handleNewProblem}
                                startIcon={<RefreshIcon />}
                              >
                                Try Another Problem
                              </Button>
                              {!evaluation.is_correct && (
                                <Button
                                  variant="outlined"
                                  onClick={handleRetryProblem}
                                  startIcon={<PlayIcon />}
                                >
                                  Try Again
                                </Button>
                              )}
                            </Box>
                          </CardContent>
                        </Card>
                      </motion.div>
                    )}
                  </Box>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 8 }}>
                    <QuizIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                      Ready to Practice?
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Select a subject and topic to generate your first practice problem.
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Quick Subject Selection */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Popular Practice Topics
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {[
                { subject: 'Mathematics', topic: 'Quadratic Equations' },
                { subject: 'Mathematics', topic: 'Linear Algebra' },
                { subject: 'Physics', topic: 'Kinematics' },
                { subject: 'Chemistry', topic: 'Stoichiometry' },
                { subject: 'Biology', topic: 'Genetics' },
                { subject: 'Mathematics', topic: 'Calculus' },
              ].map((suggestion, index) => (
                <Chip
                  key={index}
                  label={`${suggestion.topic} (${suggestion.subject})`}
                  variant="outlined"
                  onClick={() => {
                    setFormData({
                      ...formData,
                      subject: suggestion.subject,
                      topic: suggestion.topic,
                    });
                  }}
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>
          </CardContent>
        </Card>
      </motion.div>
    </Box>
  );
};

export default PracticeProblems; 