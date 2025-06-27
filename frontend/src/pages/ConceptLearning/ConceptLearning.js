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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  School as SchoolIcon,
  Lightbulb as LightbulbIcon,
  Psychology as PsychologyIcon,
  AutoStories as BookIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';

import { useAppContext } from '../../context/AppContext';
import { apiService } from '../../services/api';

const ConceptLearning = () => {
  const { currentSession } = useAppContext();
  
  const [formData, setFormData] = useState({
    subject: '',
    topic: '',
    difficulty_level: 'medium',
    learning_style: 'visual',
  });
  
  const [subjects, setSubjects] = useState([]);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(false);
  const [explanation, setExplanation] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadSubjects();
  }, []);

  useEffect(() => {
    if (formData.subject) {
      loadTopics(formData.subject);
    } else {
      setTopics([]);
    }
  }, [formData.subject]);

  const loadSubjects = async () => {
    try {
      const subjectsData = await apiService.getSubjects();
      setSubjects(subjectsData);
    } catch (error) {
      console.error('Error loading subjects:', error);
      toast.error('Failed to load subjects');
    }
  };

  const loadTopics = async (subject) => {
    try {
      const topicsData = await apiService.getTopics(subject);
      setTopics(topicsData);
    } catch (error) {
      console.error('Error loading topics:', error);
      setTopics([]);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
    
    if (field === 'subject') {
      setFormData(prev => ({
        ...prev,
        topic: '', // Reset topic when subject changes
      }));
    }
  };

  const handleExplainConcept = async () => {
    if (!currentSession) {
      toast.error('No active session. Please refresh the page.');
      return;
    }

    if (!formData.subject || !formData.topic) {
      toast.error('Please select both subject and topic');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.explainConcept(currentSession.session_id, formData);
      setExplanation(response);
      toast.success('Concept explanation generated successfully!');
      
    } catch (error) {
      console.error('Error explaining concept:', error);
      setError('Failed to generate explanation. Please try again.');
      toast.error('Failed to generate explanation');
    } finally {
      setLoading(false);
    }
  };

  const difficultyLevels = [
    { value: 'easy', label: 'Easy', description: 'Basic concepts and simple explanations' },
    { value: 'medium', label: 'Medium', description: 'Balanced depth with examples' },
    { value: 'hard', label: 'Hard', description: 'Advanced concepts with detailed analysis' },
  ];

  const learningStyles = [
    { value: 'visual', label: 'Visual', description: 'Diagrams, charts, and visual aids' },
    { value: 'auditory', label: 'Auditory', description: 'Spoken explanations and verbal cues' },
    { value: 'kinesthetic', label: 'Kinesthetic', description: 'Hands-on examples and practical applications' },
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
            Learn New Concepts 📚
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Get AI-powered explanations tailored to your learning style and difficulty preference.
          </Typography>
        </Box>
      </motion.div>

      <Grid container spacing={3}>
        {/* Concept Request Form */}
        <Grid item xs={12} lg={5}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Request Concept Explanation
                </Typography>
                
                <Box sx={{ mt: 3 }}>
                  <Grid container spacing={2}>
                    {/* Subject Selection */}
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

                    {/* Topic Selection */}
                    <Grid item xs={12}>
                      <FormControl fullWidth disabled={!formData.subject}>
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

                    {/* Custom Topic Input */}
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Or enter custom topic"
                        placeholder="e.g., Quadratic Equations, Photosynthesis, etc."
                        value={formData.topic}
                        onChange={(e) => handleInputChange('topic', e.target.value)}
                        helperText="You can type any topic you want to learn about"
                      />
                    </Grid>

                    {/* Difficulty Level */}
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" gutterBottom>
                        Difficulty Level
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {difficultyLevels.map((level) => (
                          <Chip
                            key={level.value}
                            label={level.label}
                            onClick={() => handleInputChange('difficulty_level', level.value)}
                            color={formData.difficulty_level === level.value ? 'primary' : 'default'}
                            variant={formData.difficulty_level === level.value ? 'filled' : 'outlined'}
                            sx={{ cursor: 'pointer' }}
                          />
                        ))}
                      </Box>
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                        {difficultyLevels.find(l => l.value === formData.difficulty_level)?.description}
                      </Typography>
                    </Grid>

                    {/* Learning Style */}
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" gutterBottom>
                        Learning Style
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {learningStyles.map((style) => (
                          <Chip
                            key={style.value}
                            label={style.label}
                            onClick={() => handleInputChange('learning_style', style.value)}
                            color={formData.learning_style === style.value ? 'secondary' : 'default'}
                            variant={formData.learning_style === style.value ? 'filled' : 'outlined'}
                            sx={{ cursor: 'pointer' }}
                          />
                        ))}
                      </Box>
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                        {learningStyles.find(s => s.value === formData.learning_style)?.description}
                      </Typography>
                    </Grid>

                    {/* Submit Button */}
                    <Grid item xs={12}>
                      <Button
                        fullWidth
                        variant="contained"
                        size="large"
                        onClick={handleExplainConcept}
                        disabled={loading || !formData.subject || !formData.topic}
                        startIcon={loading ? <CircularProgress size={20} /> : <LightbulbIcon />}
                        sx={{ mt: 2 }}
                      >
                        {loading ? 'Generating Explanation...' : 'Explain This Concept'}
                      </Button>
                    </Grid>
                  </Grid>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Explanation Display */}
        <Grid item xs={12} lg={7}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card sx={{ height: 'fit-content', minHeight: '400px' }}>
              <CardContent>
                {loading ? (
                  <Box sx={{ textAlign: 'center', py: 8 }}>
                    <CircularProgress size={60} />
                    <Typography variant="h6" sx={{ mt: 2 }}>
                      Generating explanation...
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Our AI tutor is preparing a personalized explanation for you
                    </Typography>
                  </Box>
                ) : error ? (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                  </Alert>
                ) : explanation ? (
                  <Box>
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="h5" fontWeight="bold" gutterBottom>
                        {explanation.topic} in {explanation.subject}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                        <Chip label={explanation.difficulty_level} size="small" color="primary" />
                        <Chip label={explanation.learning_style} size="small" color="secondary" />
                      </Box>
                    </Box>
                    
                    <Divider sx={{ mb: 3 }} />
                    
                    <Box
                      sx={{
                        '& h1, & h2, & h3': { 
                          color: 'primary.main',
                          fontWeight: 'bold',
                          mb: 2,
                        },
                        '& p': { 
                          mb: 2,
                          lineHeight: 1.6,
                        },
                        '& ul, & ol': { 
                          mb: 2,
                          pl: 3,
                        },
                        '& li': { 
                          mb: 1,
                        },
                        '& code': {
                          bgcolor: 'grey.100',
                          px: 1,
                          py: 0.5,
                          borderRadius: 1,
                          fontSize: '0.875rem',
                        },
                        '& pre': {
                          bgcolor: 'grey.100',
                          p: 2,
                          borderRadius: 1,
                          overflow: 'auto',
                        },
                      }}
                    >
                      <ReactMarkdown>{explanation.explanation}</ReactMarkdown>
                    </Box>
                  </Box>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 8 }}>
                    <BookIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                      Ready to Learn Something New?
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Select a subject and topic to get started with your personalized explanation.
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Quick Topic Suggestions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Popular Topics to Explore
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {[
                { subject: 'Mathematics', topic: 'Quadratic Equations' },
                { subject: 'Physics', topic: 'Newton\'s Laws' },
                { subject: 'Chemistry', topic: 'Periodic Table' },
                { subject: 'Biology', topic: 'Cell Division' },
                { subject: 'Mathematics', topic: 'Derivatives' },
                { subject: 'Physics', topic: 'Electromagnetic Waves' },
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

export default ConceptLearning; 