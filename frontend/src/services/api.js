import axios from 'axios';
import toast from 'react-hot-toast';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`🔹 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('🔸 API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error);
    
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    
    // Don't show toast for certain endpoints
    const skipToast = ['/api/sessions/', '/health'].some(endpoint => 
      error.config?.url?.includes(endpoint)
    );
    
    if (!skipToast) {
      toast.error(message);
    }
    
    return Promise.reject(error);
  }
);

// API service functions
export const apiService = {
  // Health check
  async healthCheck() {
    const response = await api.get('/');
    return response.data;
  },

  // Session management
  async createSession(studentId = null) {
    const response = await api.post('/api/sessions', {
      student_id: studentId
    });
    return response.data;
  },

  async getSession(sessionId) {
    const response = await api.get(`/api/sessions/${sessionId}`);
    return response.data;
  },

  async deleteSession(sessionId) {
    const response = await api.delete(`/api/sessions/${sessionId}`);
    return response.data;
  },

  // Concept learning
  async explainConcept(sessionId, data) {
    const response = await api.post(`/api/sessions/${sessionId}/concepts/explain`, data);
    return response.data;
  },

  // Practice problems
  async generateProblems(sessionId, data) {
    const response = await api.post(`/api/sessions/${sessionId}/problems/generate`, data);
    return response.data;
  },

  async evaluateSolution(sessionId, data) {
    const response = await api.post(`/api/sessions/${sessionId}/problems/evaluate`, data);
    return response.data;
  },

  // Progress and analytics
  async getProgressReport(sessionId) {
    const response = await api.get(`/api/sessions/${sessionId}/progress`);
    return response.data;
  },

  async getStudentAnalytics(studentId) {
    const response = await api.get(`/api/students/${studentId}/analytics`);
    return response.data;
  },

  async getDashboardData(studentId) {
    const response = await api.get(`/api/students/${studentId}/dashboard`);
    return response.data;
  },

  // User profile
  async getUserProfile(studentId) {
    const response = await api.get(`/api/students/${studentId}/profile`);
    return response.data;
  },

  async updateUserProfile(studentId, data) {
    const response = await api.put(`/api/students/${studentId}/profile`, data);
    return response.data;
  },

  // Conversation history
  async getConversationHistory(sessionId, limit = 50) {
    const response = await api.get(`/api/sessions/${sessionId}/conversation`, {
      params: { limit }
    });
    return response.data;
  },

  // Utility endpoints
  async getSubjects() {
    const response = await api.get('/api/subjects');
    return response.data;
  },

  async getTopics(subject) {
    const response = await api.get(`/api/subjects/${subject}/topics`);
    return response.data;
  },
};

// Helper functions
export const handleApiError = (error, defaultMessage = 'An error occurred') => {
  const message = error.response?.data?.detail || error.message || defaultMessage;
  console.error('API Error:', message);
  return message;
};

export const isApiError = (error) => {
  return error.response && error.response.status;
};

export default api; 