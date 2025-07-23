/**
 * API Service for Mobile Admin App
 */
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import DeviceInfo from 'react-native-device-info';
import Toast from 'react-native-toast-message';

import {
  LoginCredentials,
  AuthResponse,
  User,
  Institute,
  InstituteStats,
  PlatformAnalytics,
  SupportTicket,
  SystemConfig,
  Notification,
  ApiResponse,
  PaginatedResponse,
  InstituteFilters,
  TicketFilters,
  DeviceInfo as DeviceInfoType,
} from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = __DEV__ 
      ? 'http://localhost:8000' 
      : 'https://api.medhasakthi.com';
    
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
    // Request interceptor
    this.api.interceptors.request.use(
      async (config) => {
        const token = await this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            await this.refreshToken();
            const token = await this.getToken();
            if (token) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return this.api(originalRequest);
            }
          } catch (refreshError) {
            await this.logout();
            // Navigate to login screen
            return Promise.reject(refreshError);
          }
        }

        // Show error toast
        const message = error.response?.data?.detail || 
                       error.response?.data?.message || 
                       'Network error occurred';
        
        Toast.show({
          type: 'error',
          text1: 'Error',
          text2: message,
        });

        return Promise.reject(error);
      }
    );
  }

  // Token management
  private async getToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem('access_token');
    } catch (error) {
      return null;
    }
  }

  private async setToken(token: string): Promise<void> {
    await AsyncStorage.setItem('access_token', token);
  }

  private async getRefreshToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem('refresh_token');
    } catch (error) {
      return null;
    }
  }

  private async setRefreshToken(token: string): Promise<void> {
    await AsyncStorage.setItem('refresh_token', token);
  }

  private async clearTokens(): Promise<void> {
    await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
  }

  // Device info helper
  private async getDeviceInfo(): Promise<DeviceInfoType> {
    const [deviceId, deviceName, systemVersion, appVersion] = await Promise.all([
      DeviceInfo.getUniqueId(),
      DeviceInfo.getDeviceName(),
      DeviceInfo.getSystemVersion(),
      DeviceInfo.getVersion(),
    ]);

    return {
      device_type: 'mobile',
      os: `${DeviceInfo.getSystemName()} ${systemVersion}`,
      app_version: appVersion,
      device_id: deviceId,
      device_name: deviceName,
    };
  }

  // Authentication methods
  async login(credentials: Omit<LoginCredentials, 'device_info'>): Promise<AuthResponse> {
    const deviceInfo = await this.getDeviceInfo();
    const loginData = { ...credentials, device_info: deviceInfo };
    
    const response = await this.api.post<AuthResponse>('/api/v1/auth/login', loginData);
    const { access_token, refresh_token, user } = response.data;
    
    await this.setToken(access_token);
    await this.setRefreshToken(refresh_token);
    await AsyncStorage.setItem('user', JSON.stringify(user));
    
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.api.post('/api/v1/auth/logout');
    } catch (error) {
      // Continue with logout even if API call fails
    } finally {
      await this.clearTokens();
    }
  }

  async refreshToken(): Promise<AuthResponse> {
    const refreshToken = await this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.api.post<AuthResponse>('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    });

    const { access_token, refresh_token: newRefreshToken, user } = response.data;
    
    await this.setToken(access_token);
    await this.setRefreshToken(newRefreshToken);
    await AsyncStorage.setItem('user', JSON.stringify(user));

    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get<User>('/api/v1/auth/me');
    return response.data;
  }

  // Institute management
  async getInstitutes(filters?: InstituteFilters): Promise<PaginatedResponse<Institute>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }
    
    const response = await this.api.get<PaginatedResponse<Institute>>(
      `/api/v1/admin/institutes?${params.toString()}`
    );
    return response.data;
  }

  async getInstitute(id: string): Promise<Institute> {
    const response = await this.api.get<Institute>(`/api/v1/admin/institutes/${id}`);
    return response.data;
  }

  async createInstitute(data: any): Promise<Institute> {
    const response = await this.api.post<Institute>('/api/v1/admin/institutes', data);
    return response.data;
  }

  async updateInstitute(id: string, data: any): Promise<Institute> {
    const response = await this.api.put<Institute>(`/api/v1/admin/institutes/${id}`, data);
    return response.data;
  }

  async deleteInstitute(id: string): Promise<void> {
    await this.api.delete(`/api/v1/admin/institutes/${id}`);
  }

  async verifyInstitute(id: string): Promise<Institute> {
    const response = await this.api.post<Institute>(`/api/v1/admin/institutes/${id}/verify`);
    return response.data;
  }

  async suspendInstitute(id: string, reason: string): Promise<Institute> {
    const response = await this.api.post<Institute>(`/api/v1/admin/institutes/${id}/suspend`, {
      reason,
    });
    return response.data;
  }

  // Analytics and statistics
  async getInstituteStats(): Promise<InstituteStats> {
    const response = await this.api.get<InstituteStats>('/api/v1/admin/stats/institutes');
    return response.data;
  }

  async getPlatformAnalytics(period?: string): Promise<PlatformAnalytics> {
    const params = period ? `?period=${period}` : '';
    const response = await this.api.get<PlatformAnalytics>(`/api/v1/admin/analytics${params}`);
    return response.data;
  }

  // Support tickets
  async getSupportTickets(filters?: TicketFilters): Promise<PaginatedResponse<SupportTicket>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }
    
    const response = await this.api.get<PaginatedResponse<SupportTicket>>(
      `/api/v1/admin/support/tickets?${params.toString()}`
    );
    return response.data;
  }

  async getSupportTicket(id: string): Promise<SupportTicket> {
    const response = await this.api.get<SupportTicket>(`/api/v1/admin/support/tickets/${id}`);
    return response.data;
  }

  async updateTicketStatus(id: string, status: string): Promise<SupportTicket> {
    const response = await this.api.patch<SupportTicket>(`/api/v1/admin/support/tickets/${id}`, {
      status,
    });
    return response.data;
  }

  async assignTicket(id: string, assignedTo: string): Promise<SupportTicket> {
    const response = await this.api.patch<SupportTicket>(`/api/v1/admin/support/tickets/${id}`, {
      assigned_to: assignedTo,
    });
    return response.data;
  }

  async addTicketMessage(id: string, message: string, isInternal: boolean = false): Promise<void> {
    await this.api.post(`/api/v1/admin/support/tickets/${id}/messages`, {
      message,
      is_internal: isInternal,
    });
  }

  // System configuration
  async getSystemConfig(): Promise<SystemConfig> {
    const response = await this.api.get<SystemConfig>('/api/v1/admin/system/config');
    return response.data;
  }

  async updateSystemConfig(config: Partial<SystemConfig>): Promise<SystemConfig> {
    const response = await this.api.put<SystemConfig>('/api/v1/admin/system/config', config);
    return response.data;
  }

  // Notifications
  async getNotifications(): Promise<Notification[]> {
    const response = await this.api.get<Notification[]>('/api/v1/admin/notifications');
    return response.data;
  }

  async markNotificationAsRead(id: string): Promise<void> {
    await this.api.patch(`/api/v1/admin/notifications/${id}/read`);
  }

  async markAllNotificationsAsRead(): Promise<void> {
    await this.api.patch('/api/v1/admin/notifications/read-all');
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: number; version: string }> {
    const response = await this.api.get('/health');
    return response.data;
  }

  // Utility methods
  async isAuthenticated(): Promise<boolean> {
    const token = await this.getToken();
    return !!token;
  }

  async getCurrentUserFromStorage(): Promise<User | null> {
    try {
      const userStr = await AsyncStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      return null;
    }
  }
}

// Create singleton instance
export const apiService = new ApiService();
export default apiService;
