/**
 * API service for MEDHASAKTHI Institute Portal
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { toast } from 'react-hot-toast';

// Types
import { 
  LoginCredentials, 
  RegisterData, 
  AuthResponse, 
  User,
  PasswordResetRequest,
  PasswordReset,
  PasswordChange 
} from '../types/auth';
import {
  QuestionGenerationRequest,
  QuestionGenerationResponse,
  Subject,
  Topic,
  Question,
  QuestionSearchParams,
  QuestionSearchResponse,
  AIGenerationStats,
  QuestionValidation
} from '../types/question';

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = this.getToken();
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
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            await this.refreshToken();
            const token = this.getToken();
            if (token) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return this.api(originalRequest);
            }
          } catch (refreshError) {
            this.logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        // Handle different error types
        if (error.response) {
          const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
          toast.error(message);
        } else if (error.request) {
          toast.error('Network error. Please check your connection.');
        } else {
          toast.error('An unexpected error occurred.');
        }

        return Promise.reject(error);
      }
    );
  }

  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }
    return null;
  }

  private setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  private getRefreshToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('refresh_token');
    }
    return null;
  }

  private setRefreshToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('refresh_token', token);
    }
  }

  private clearTokens(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  }

  // Authentication methods
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>('/api/v1/auth/login', credentials);
    const { access_token, refresh_token, user } = response.data;
    
    this.setToken(access_token);
    this.setRefreshToken(refresh_token);
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user));
    }
    
    return response.data;
  }

  async register(data: RegisterData): Promise<{ message: string }> {
    const response = await this.api.post('/api/v1/auth/register', data);
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.api.post('/api/v1/auth/logout');
    } catch (error) {
      // Continue with logout even if API call fails
    } finally {
      this.clearTokens();
    }
  }

  async refreshToken(): Promise<AuthResponse> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.api.post<AuthResponse>('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    });

    const { access_token, refresh_token: newRefreshToken, user } = response.data;
    
    this.setToken(access_token);
    this.setRefreshToken(newRefreshToken);
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user));
    }

    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get<User>('/api/v1/auth/me');
    return response.data;
  }

  async requestPasswordReset(data: PasswordResetRequest): Promise<{ message: string }> {
    const response = await this.api.post('/api/v1/auth/request-password-reset', data);
    return response.data;
  }

  async resetPassword(data: PasswordReset): Promise<{ message: string }> {
    const response = await this.api.post('/api/v1/auth/reset-password', data);
    return response.data;
  }

  async changePassword(data: PasswordChange): Promise<{ message: string }> {
    const response = await this.api.post('/api/v1/auth/change-password', data);
    return response.data;
  }

  // AI Question Generation methods
  async generateQuestions(request: QuestionGenerationRequest): Promise<QuestionGenerationResponse> {
    const response = await this.api.post<QuestionGenerationResponse>(
      '/api/v1/ai/generate-questions', 
      request
    );
    return response.data;
  }

  async getSubjects(): Promise<Subject[]> {
    const response = await this.api.get<Subject[]>('/api/v1/ai/subjects');
    return response.data;
  }

  async createSubject(data: Partial<Subject>): Promise<Subject> {
    const response = await this.api.post<Subject>('/api/v1/ai/subjects', data);
    return response.data;
  }

  async getTopics(subjectId: string): Promise<Topic[]> {
    const response = await this.api.get<Topic[]>(`/api/v1/ai/subjects/${subjectId}/topics`);
    return response.data;
  }

  async createTopic(data: Partial<Topic>): Promise<Topic> {
    const response = await this.api.post<Topic>('/api/v1/ai/topics', data);
    return response.data;
  }

  async searchQuestions(params: QuestionSearchParams): Promise<QuestionSearchResponse> {
    const response = await this.api.post<QuestionSearchResponse>('/api/v1/ai/questions/search', params);
    return response.data;
  }

  async getGenerationStats(): Promise<AIGenerationStats> {
    const response = await this.api.get<AIGenerationStats>('/api/v1/ai/generation-stats');
    return response.data;
  }

  async validateQuestion(questionData: any): Promise<QuestionValidation> {
    const response = await this.api.post<QuestionValidation>('/api/v1/ai/validate-question', {
      question_data: questionData,
    });
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: number; version: string }> {
    const response = await this.api.get('/health');
    return response.data;
  }

  // Utility methods
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getCurrentUserFromStorage(): User | null {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    }
    return null;
  }
}

// Create singleton instance
export const apiService = new ApiService();
export default apiService;
