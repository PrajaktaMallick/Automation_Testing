import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
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
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    
    // Don't show toast for certain errors
    if (error.response?.status !== 404 && !error.config?.skipErrorToast) {
      toast.error(message);
    }
    
    return Promise.reject(error);
  }
);

// API methods
export const api = {
  // Health check
  healthCheck: () => apiClient.get('/health'),

  // Test management
  createTest: (data) => apiClient.post('/tests/create', data),
  executeTest: (sessionId, options = {}) => apiClient.post('/tests/execute', { session_id: sessionId, options }),
  getTest: (sessionId) => apiClient.get(`/tests/${sessionId}`),
  getTests: (params = {}) => apiClient.get('/tests', { params }),
  deleteTest: (sessionId) => apiClient.delete(`/tests/${sessionId}`),
  stopTest: (sessionId) => apiClient.post(`/tests/${sessionId}/stop`),
  
  // Test status and monitoring
  getTestStatus: (sessionId) => apiClient.get(`/tests/${sessionId}/status`),
  getTestScreenshots: (sessionId) => apiClient.get(`/tests/${sessionId}/screenshots`),
  
  // Analytics and stats
  getStats: () => apiClient.get('/stats'),
  
  // Website analysis
  analyzeWebsite: (url) => apiClient.post('/analyze-website', { url }),
};

// WebSocket connection for real-time updates
export class TestWebSocket {
  constructor(sessionId, onMessage, onError) {
    this.sessionId = sessionId;
    this.onMessage = onMessage;
    this.onError = onError;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    try {
      const wsUrl = `ws://localhost:8000/ws/test/${this.sessionId}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.onMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (this.onError) {
          this.onError(error);
        }
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      if (this.onError) {
        this.onError(error);
      }
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect();
      }, 1000 * this.reconnectAttempts);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}

export default apiClient;
