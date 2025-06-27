import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Avatar,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Person as PersonIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  School as SchoolIcon,
  Psychology as PsychologyIcon,
  History as HistoryIcon,
  Visibility as VisibilityIcon,
  VolumeUp as VolumeUpIcon,
  TouchApp as TouchAppIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

import { useAppContext } from '../../context/AppContext';
import { apiService } from '../../services/api';

const UserProfile = () => {
  const { currentSession, studentId } = useAppContext();
  
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [profile, setProfile] = useState({
    student_id: studentId,
    name: 'Demo Student',
    email: 'demo@example.com',
    grade_level: 'High School',
    preferred_subjects: ['Mathematics', 'Physics'],
    learning_preferences: {
      difficulty_level: 'medium',
      learning_style: 'visual',
      session_duration: 30,
      reminder_notifications: true,
      progress_tracking: true,
    },
    personal_info: {
      bio: 'I am a passionate learner who loves exploring new concepts in STEM fields.',
      goals: 'To master calculus and prepare for college-level physics courses.',
      timezone: 'UTC',
    }
  });

  const handleInputChange = (field, value, nested = null) => {
    if (nested) {
      setProfile(prev => ({
        ...prev,
        [nested]: {
          ...prev[nested],
          [field]: value,
        }
      }));
    } else {
      setProfile(prev => ({
        ...prev,
        [field]: value,
      }));
    }
  };

  const handleSaveProfile = async () => {
    try {
      setLoading(true);
      // In a real app, this would call the API
      // await apiService.updateUserProfile(studentId, profile);
      setEditing(false);
      toast.success('Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const learningStyles = [
    { value: 'visual', label: 'Visual', icon: <VisibilityIcon />, description: 'Learn through diagrams and visual aids' },
    { value: 'auditory', label: 'Auditory', icon: <VolumeUpIcon />, description: 'Learn through spoken explanations' },
    { value: 'kinesthetic', label: 'Kinesthetic', icon: <TouchAppIcon />, description: 'Learn through hands-on practice' },
  ];

  const difficultyLevels = [
    { value: 'easy', label: 'Easy', color: 'success' },
    { value: 'medium', label: 'Medium', color: 'warning' },
    { value: 'hard', label: 'Hard', color: 'error' },
  ];

  const subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'Computer Science', 'English', 'History'];

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
              User Profile 👤
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Manage your profile and learning preferences for a personalized experience.
            </Typography>
          </Box>
          <Box>
            {editing ? (
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSaveProfile}
                  disabled={loading}
                >
                  Save
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<CancelIcon />}
                  onClick={() => setEditing(false)}
                >
                  Cancel
                </Button>
              </Box>
            ) : (
              <Button
                variant="outlined"
                startIcon={<EditIcon />}
                onClick={() => setEditing(true)}
              >
                Edit Profile
              </Button>
            )}
          </Box>
        </Box>
      </motion.div>

      <Grid container spacing={3}>
        {/* Profile Overview */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Avatar
                  sx={{
                    width: 100,
                    height: 100,
                    margin: '0 auto',
                    mb: 2,
                    bgcolor: 'primary.main',
                    fontSize: '2rem',
                  }}
                >
                  {profile.name?.charAt(0)?.toUpperCase() || 'S'}
                </Avatar>
                
                {editing ? (
                  <TextField
                    fullWidth
                    label="Name"
                    value={profile.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    sx={{ mb: 2 }}
                  />
                ) : (
                  <Typography variant="h5" fontWeight="bold" gutterBottom>
                    {profile.name}
                  </Typography>
                )}

                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Student ID: {studentId}
                </Typography>

                {editing ? (
                  <TextField
                    fullWidth
                    label="Email"
                    type="email"
                    value={profile.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    sx={{ mb: 2 }}
                  />
                ) : (
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {profile.email}
                  </Typography>
                )}

                {profile.grade_level && (
                  <Chip
                    label={profile.grade_level}
                    color="primary"
                    variant="outlined"
                    sx={{ mb: 2 }}
                  />
                )}

                <Divider sx={{ my: 2 }} />
                
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    About Me
                  </Typography>
                  {editing ? (
                    <TextField
                      fullWidth
                      multiline
                      rows={3}
                      value={profile.personal_info?.bio || ''}
                      onChange={(e) => handleInputChange('bio', e.target.value, 'personal_info')}
                      placeholder="Tell us about yourself..."
                    />
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      {profile.personal_info?.bio}
                    </Typography>
                  )}
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Profile Details */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={3}>
            {/* Learning Preferences */}
            <Grid item xs={12}>
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <Card>
                  <CardContent>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      <PsychologyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Learning Preferences
                    </Typography>

                    <Grid container spacing={3}>
                      {/* Learning Style */}
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" gutterBottom>
                          Learning Style
                        </Typography>
                        {editing ? (
                          <FormControl fullWidth>
                            <InputLabel>Learning Style</InputLabel>
                            <Select
                              value={profile.learning_preferences?.learning_style || 'visual'}
                              label="Learning Style"
                              onChange={(e) => handleInputChange('learning_style', e.target.value, 'learning_preferences')}
                            >
                              {learningStyles.map((style) => (
                                <MenuItem key={style.value} value={style.value}>
                                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                    {style.icon}
                                    <Box sx={{ ml: 2 }}>
                                      <Typography>{style.label}</Typography>
                                      <Typography variant="caption" color="text.secondary">
                                        {style.description}
                                      </Typography>
                                    </Box>
                                  </Box>
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        ) : (
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {learningStyles.find(s => s.value === profile.learning_preferences?.learning_style)?.icon}
                            <Typography sx={{ ml: 1 }}>
                              {learningStyles.find(s => s.value === profile.learning_preferences?.learning_style)?.label || 'Visual'}
                            </Typography>
                          </Box>
                        )}
                      </Grid>

                      {/* Difficulty Level */}
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" gutterBottom>
                          Preferred Difficulty
                        </Typography>
                        {editing ? (
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            {difficultyLevels.map((level) => (
                              <Chip
                                key={level.value}
                                label={level.label}
                                onClick={() => handleInputChange('difficulty_level', level.value, 'learning_preferences')}
                                color={profile.learning_preferences?.difficulty_level === level.value ? level.color : 'default'}
                                variant={profile.learning_preferences?.difficulty_level === level.value ? 'filled' : 'outlined'}
                                sx={{ cursor: 'pointer' }}
                              />
                            ))}
                          </Box>
                        ) : (
                          <Chip
                            label={difficultyLevels.find(d => d.value === profile.learning_preferences?.difficulty_level)?.label || 'Medium'}
                            color={difficultyLevels.find(d => d.value === profile.learning_preferences?.difficulty_level)?.color || 'warning'}
                          />
                        )}
                      </Grid>

                      {/* Session Duration */}
                      <Grid item xs={12} md={6}>
                        {editing ? (
                          <TextField
                            fullWidth
                            label="Preferred Session Duration (minutes)"
                            type="number"
                            value={profile.learning_preferences?.session_duration || 30}
                            onChange={(e) => handleInputChange('session_duration', parseInt(e.target.value), 'learning_preferences')}
                            inputProps={{ min: 15, max: 120 }}
                          />
                        ) : (
                          <Box>
                            <Typography variant="subtitle2" gutterBottom>
                              Session Duration
                            </Typography>
                            <Typography>
                              {profile.learning_preferences?.session_duration || 30} minutes
                            </Typography>
                          </Box>
                        )}
                      </Grid>

                      {/* Settings */}
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" gutterBottom>
                          Preferences
                        </Typography>
                        <FormControlLabel
                          control={
                            <Switch
                              checked={profile.learning_preferences?.reminder_notifications !== false}
                              onChange={(e) => handleInputChange('reminder_notifications', e.target.checked, 'learning_preferences')}
                              disabled={!editing}
                            />
                          }
                          label="Reminder Notifications"
                        />
                        <br />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={profile.learning_preferences?.progress_tracking !== false}
                              onChange={(e) => handleInputChange('progress_tracking', e.target.checked, 'learning_preferences')}
                              disabled={!editing}
                            />
                          }
                          label="Progress Tracking"
                        />
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* Preferred Subjects */}
            <Grid item xs={12}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
              >
                <Card>
                  <CardContent>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      <SchoolIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Preferred Subjects
                    </Typography>

                    {editing ? (
                      <FormControl fullWidth>
                        <InputLabel>Select Subjects</InputLabel>
                        <Select
                          multiple
                          value={profile.preferred_subjects || []}
                          label="Select Subjects"
                          onChange={(e) => handleInputChange('preferred_subjects', e.target.value)}
                          renderValue={(selected) => (
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                              {selected.map((value) => (
                                <Chip key={value} label={value} size="small" />
                              ))}
                            </Box>
                          )}
                        >
                          {subjects.map((subject) => (
                            <MenuItem key={subject} value={subject}>
                              {subject}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    ) : (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {profile.preferred_subjects?.map((subject) => (
                          <Chip
                            key={subject}
                            label={subject}
                            color="primary"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* Learning Goals */}
            <Grid item xs={12}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                <Card>
                  <CardContent>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      Learning Goals
                    </Typography>

                    {editing ? (
                      <TextField
                        fullWidth
                        label="Learning Goals"
                        multiline
                        rows={4}
                        value={profile.personal_info?.goals || ''}
                        onChange={(e) => handleInputChange('goals', e.target.value, 'personal_info')}
                        placeholder="What are your learning goals and objectives?"
                      />
                    ) : (
                      <Typography variant="body2">
                        {profile.personal_info?.goals}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* Recent Activity */}
            <Grid item xs={12}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.5 }}
              >
                <Card>
                  <CardContent>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      <HistoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Recent Activity
                    </Typography>

                    <List>
                      <ListItem>
                        <ListItemIcon>
                          <PersonIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Solved quadratic equation problems"
                          secondary="You • 2 hours ago"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          <PersonIcon color="secondary" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Learned about Newton's laws of motion"
                          secondary="AI Tutor • 1 day ago"
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
};

export default UserProfile; 