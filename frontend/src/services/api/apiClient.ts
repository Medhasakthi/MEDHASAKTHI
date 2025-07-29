import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { store } from '../../store/store';
import { refreshAccessToken, clearAuthState } from '../../store/slices/authSlice';
import toast from 'react-hot-toast';

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 30000; // 30 seconds

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add auth token to requests
    const state = store.getState();
    const token = state.auth.token;
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add request timestamp for performance monitoring
    (config as any).metadata = { startTime: new Date() };

    // Add correlation ID for request tracking
    config.headers = {
      ...config.headers,
      'X-Correlation-ID': generateCorrelationId(),
    };

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response time for performance monitoring
    const config = response.config as any;
    if (config.metadata?.startTime) {
      const duration = new Date().getTime() - config.metadata.startTime.getTime();
      console.debug(`API Request to ${config.url} took ${duration}ms`);
    }

    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    // Handle token expiration
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const state = store.getState();
        const refreshToken = state.auth.refreshToken;

        if (refreshToken) {
          // Attempt to refresh token
          await store.dispatch(refreshAccessToken());
          
          // Retry original request with new token
          const newState = store.getState();
          const newToken = newState.auth.token;
          
          if (newToken && originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return apiClient(originalRequest);
          }
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        store.dispatch(clearAuthState());
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // Handle different error types
    handleApiError(error);

    return Promise.reject(error);
  }
);

// Error handling function
const handleApiError = (error: AxiosError) => {
  const status = error.response?.status;
  const data = error.response?.data as any;
  const message = data?.detail || data?.message || error.message;

  switch (status) {
    case 400:
      toast.error(`Bad Request: ${message}`);
      break;
    case 401:
      toast.error('Authentication required. Please login again.');
      break;
    case 403:
      toast.error('Access denied. You do not have permission to perform this action.');
      break;
    case 404:
      toast.error('Resource not found.');
      break;
    case 409:
      toast.error(`Conflict: ${message}`);
      break;
    case 422:
      // Validation errors
      if (data?.errors) {
        const validationErrors = Object.values(data.errors).flat();
        validationErrors.forEach((err: any) => toast.error(err));
      } else {
        toast.error(`Validation Error: ${message}`);
      }
      break;
    case 429:
      toast.error('Too many requests. Please try again later.');
      break;
    case 500:
      toast.error('Internal server error. Please try again later.');
      break;
    case 502:
      toast.error('Service temporarily unavailable. Please try again later.');
      break;
    case 503:
      toast.error('Service unavailable. Please try again later.');
      break;
    default:
      if (error.code === 'NETWORK_ERROR' || error.code === 'ECONNABORTED') {
        toast.error('Network error. Please check your connection.');
      } else {
        toast.error(`An error occurred: ${message}`);
      }
  }
};

// Utility functions
const generateCorrelationId = (): string => {
  return 'xxxx-xxxx-4xxx-yxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

// API client wrapper with additional features
export class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = apiClient;
  }

  // GET request with caching support
  async get<T = any>(
    url: string, 
    config?: AxiosRequestConfig & { cache?: boolean; cacheTime?: number }
  ): Promise<AxiosResponse<T>> {
    const cacheKey = `api_cache_${url}_${JSON.stringify(config?.params || {})}`;
    
    // Check cache if enabled
    if (config?.cache) {
      const cached = this.getFromCache(cacheKey);
      if (cached) {
        return Promise.resolve(cached);
      }
    }

    const response = await this.client.get<T>(url, config);

    // Store in cache if enabled
    if (config?.cache) {
      this.setCache(cacheKey, response, config.cacheTime || 300000); // 5 minutes default
    }

    return response;
  }

  // POST request
  async post<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.post<T>(url, data, config);
  }

  // PUT request
  async put<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.put<T>(url, data, config);
  }

  // PATCH request
  async patch<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.patch<T>(url, data, config);
  }

  // DELETE request
  async delete<T = any>(
    url: string, 
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.delete<T>(url, config);
  }

  // File upload with progress
  async uploadFile<T = any>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void,
    additionalData?: Record<string, any>
  ): Promise<AxiosResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    return this.client.post<T>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });
  }

  // Download file
  async downloadFile(
    url: string,
    filename?: string,
    onProgress?: (progress: number) => void
  ): Promise<void> {
    const response = await this.client.get(url, {
      responseType: 'blob',
      onDownloadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    // Create download link
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }

  // Batch requests
  async batch<T = any>(requests: Array<() => Promise<AxiosResponse<T>>>): Promise<AxiosResponse<T>[]> {
    return Promise.all(requests.map(request => request()));
  }

  // Request with retry
  async requestWithRetry<T = any>(
    requestFn: () => Promise<AxiosResponse<T>>,
    maxRetries: number = 3,
    delay: number = 1000
  ): Promise<AxiosResponse<T>> {
    let lastError: any;

    for (let i = 0; i <= maxRetries; i++) {
      try {
        return await requestFn();
      } catch (error) {
        lastError = error;
        
        if (i < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
        }
      }
    }

    throw lastError;
  }

  // Cache management
  private getFromCache(key: string): AxiosResponse | null {
    try {
      const cached = localStorage.getItem(key);
      if (cached) {
        const { data, timestamp, ttl } = JSON.parse(cached);
        if (Date.now() - timestamp < ttl) {
          return data;
        } else {
          localStorage.removeItem(key);
        }
      }
    } catch (error) {
      console.warn('Cache retrieval error:', error);
    }
    return null;
  }

  private setCache(key: string, data: AxiosResponse, ttl: number): void {
    try {
      const cacheData = {
        data,
        timestamp: Date.now(),
        ttl,
      };
      localStorage.setItem(key, JSON.stringify(cacheData));
    } catch (error) {
      console.warn('Cache storage error:', error);
    }
  }

  // Clear all cache
  clearCache(): void {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith('api_cache_')) {
        localStorage.removeItem(key);
      }
    });
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      await this.client.get('/health');
      return true;
    } catch {
      return false;
    }
  }

  // Get API status
  async getApiStatus(): Promise<any> {
    const response = await this.client.get('/');
    return response.data;
  }
}

// Export both the raw axios instance and the wrapper
export { apiClient };
export const api = new APIClient();
