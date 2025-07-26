import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const message = error.response?.data?.error || error.message || 'An error occurred';
    
    // Don't show toast for certain errors
    if (error.response?.status !== 404) {
      toast.error(message);
    }
    
    return Promise.reject(error);
  }
);

// Test Sessions API
export const createTestSession = async (testData) => {
  return api.post('/tests/create', testData);
};

export const executeTestSession = async (sessionId) => {
  return api.post(`/tests/execute/${sessionId}`);
};

export const getTestSession = async (sessionId) => {
  return api.get(`/tests/${sessionId}`);
};

export const getTestSessions = async () => {
  return api.get('/tests');
};

export const deleteTestSession = async (sessionId) => {
  return api.delete(`/tests/${sessionId}`);
};

// Health check
export const healthCheck = async () => {
  return api.get('/health');
};

export default api;
