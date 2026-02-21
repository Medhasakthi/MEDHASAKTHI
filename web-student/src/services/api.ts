import axios, { AxiosInstance, AxiosResponse } from 'axios';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
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

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Service
export const apiService = {
  // Auth endpoints
  auth: {
    login: (credentials: { email: string; password: string }) =>
      apiClient.post('/auth/login', credentials),
    logout: () => apiClient.post('/auth/logout'),
    register: (userData: any) => apiClient.post('/auth/register', userData),
    refreshToken: () => apiClient.post('/auth/refresh'),
  },

  // Exam endpoints
  exams: {
    getAll: () => apiClient.get('/exams'),
    getById: (id: string) => apiClient.get(`/exams/${id}`),
    start: (id: string) => apiClient.post(`/exams/${id}/start`),
    submit: (id: string, answers: any) => apiClient.post(`/exams/${id}/submit`, answers),
    getQuestions: (id: string) => apiClient.get(`/exams/${id}/questions`),
  },

  // Student endpoints
  student: {
    getProfile: () => apiClient.get('/student/profile'),
    updateProfile: (data: any) => apiClient.put('/student/profile', data),
    getResults: () => apiClient.get('/student/results'),
    getExamHistory: () => apiClient.get('/student/exam-history'),
  },

  // Proctoring endpoints
  proctoring: {
    startSession: (examId: string) => apiClient.post(`/proctoring/${examId}/start`),
    endSession: (examId: string) => apiClient.post(`/proctoring/${examId}/end`),
    reportViolation: (examId: string, violation: any) => 
      apiClient.post(`/proctoring/${examId}/violation`, violation),
  },
};

export default apiService;
