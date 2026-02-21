import axios, { AxiosResponse } from 'axios';
import { apiClient } from './apiClient';

// Types
interface LoginCredentials {
  email: string;
  password: string;
  totpCode?: string;
  deviceInfo: {
    fingerprint: string;
    user_agent: string;
    ip_address?: string;
    location?: any;
  };
}

interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  role: string;
  institute_code?: string;
}

interface LoginResponse {
  access_token?: string;
  refresh_token?: string;
  token_type?: string;
  expires_in?: number;
  user?: any;
  device_session_id?: string;
  requires_2fa?: boolean;
  requires_device_verification?: boolean;
  message?: string;
}

interface ProfileUpdateData {
  full_name?: string;
  profile_picture?: string;
  phone?: string;
  address?: string;
}

interface PasswordChangeData {
  current_password: string;
  new_password: string;
}

interface TwoFAVerificationData {
  totp_code: string;
}

// Device fingerprinting utility
const generateDeviceFingerprint = (): string => {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  if (ctx) {
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('Device fingerprint', 2, 2);
  }
  
  const fingerprint = [
    navigator.userAgent,
    navigator.language,
    screen.width + 'x' + screen.height,
    new Date().getTimezoneOffset(),
    canvas.toDataURL(),
    navigator.hardwareConcurrency || 'unknown',
    (navigator as any).deviceMemory || 'unknown'
  ].join('|');
  
  // Simple hash function
  let hash = 0;
  for (let i = 0; i < fingerprint.length; i++) {
    const char = fingerprint.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  return Math.abs(hash).toString(16);
};

// Get device information
const getDeviceInfo = () => ({
  fingerprint: generateDeviceFingerprint(),
  user_agent: navigator.userAgent,
  ip_address: '', // Will be detected by backend
  location: null, // Can be added with geolocation API
});

// Auth API class
export class AuthAPI {
  private baseURL = '/api/v1/auth';

  async login(credentials: Omit<LoginCredentials, 'deviceInfo'>): Promise<AxiosResponse<LoginResponse>> {
    const deviceInfo = getDeviceInfo();
    
    return apiClient.post(`${this.baseURL}/login`, {
      ...credentials,
      device_info: deviceInfo,
    });
  }

  async register(userData: RegisterData): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/register`, userData);
  }

  async logout(): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/logout`);
  }

  async refreshToken(refreshToken: string): Promise<AxiosResponse<LoginResponse>> {
    return apiClient.post(`${this.baseURL}/refresh`, {
      refresh_token: refreshToken,
    });
  }

  async getCurrentUser(): Promise<AxiosResponse<any>> {
    return apiClient.get(`${this.baseURL}/me`);
  }

  async updateProfile(profileData: ProfileUpdateData): Promise<AxiosResponse<any>> {
    return apiClient.put(`${this.baseURL}/profile`, profileData);
  }

  async changePassword(passwordData: PasswordChangeData): Promise<AxiosResponse<any>> {
    return apiClient.put(`${this.baseURL}/change-password`, passwordData);
  }

  async forgotPassword(email: string): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/forgot-password`, { email });
  }

  async resetPassword(token: string, newPassword: string): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/reset-password`, {
      token,
      new_password: newPassword,
    });
  }

  async verifyEmail(token: string): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/verify-email`, { token });
  }

  async resendVerificationEmail(email: string): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/resend-verification`, { email });
  }

  // Two-Factor Authentication
  async setup2FA(): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/2fa/setup`);
  }

  async verify2FA(verificationData: TwoFAVerificationData): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/2fa/verify`, verificationData);
  }

  async disable2FA(verificationData: TwoFAVerificationData): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/2fa/disable`, verificationData);
  }

  async generateBackupCodes(): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/2fa/backup-codes`);
  }

  // Device Management
  async getDevices(): Promise<AxiosResponse<any>> {
    return apiClient.get(`${this.baseURL}/devices`);
  }

  async revokeDevice(deviceId: string): Promise<AxiosResponse<any>> {
    return apiClient.delete(`${this.baseURL}/devices/${deviceId}`);
  }

  async verifyDevice(token: string): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/verify-device`, { token });
  }

  // Security
  async getSecurityLogs(): Promise<AxiosResponse<any>> {
    return apiClient.get(`${this.baseURL}/security-logs`);
  }

  async reportSuspiciousActivity(details: any): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/report-suspicious`, details);
  }

  // Biometric Authentication (if supported)
  async registerBiometric(biometricData: any): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/biometric/register`, biometricData);
  }

  async verifyBiometric(biometricData: any): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/biometric/verify`, biometricData);
  }

  async removeBiometric(biometricId: string): Promise<AxiosResponse<any>> {
    return apiClient.delete(`${this.baseURL}/biometric/${biometricId}`);
  }

  // Session Management
  async getSessions(): Promise<AxiosResponse<any>> {
    return apiClient.get(`${this.baseURL}/sessions`);
  }

  async revokeSession(sessionId: string): Promise<AxiosResponse<any>> {
    return apiClient.delete(`${this.baseURL}/sessions/${sessionId}`);
  }

  async revokeAllSessions(): Promise<AxiosResponse<any>> {
    return apiClient.delete(`${this.baseURL}/sessions/all`);
  }

  // Account Management
  async deleteAccount(password: string): Promise<AxiosResponse<any>> {
    return apiClient.delete(`${this.baseURL}/account`, {
      data: { password }
    });
  }

  async exportData(): Promise<AxiosResponse<any>> {
    return apiClient.get(`${this.baseURL}/export-data`);
  }

  // Admin functions
  async impersonateUser(userId: string): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/admin/impersonate`, { user_id: userId });
  }

  async stopImpersonation(): Promise<AxiosResponse<any>> {
    return apiClient.post(`${this.baseURL}/admin/stop-impersonate`);
  }

  // Utility methods
  isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  }

  getTokenPayload(token: string): any {
    try {
      return JSON.parse(atob(token.split('.')[1]));
    } catch {
      return null;
    }
  }

  // Password strength checker
  checkPasswordStrength(password: string): {
    score: number;
    feedback: string[];
    isStrong: boolean;
  } {
    const feedback: string[] = [];
    let score = 0;

    // Length check
    if (password.length >= 8) score += 1;
    else feedback.push('Password should be at least 8 characters long');

    if (password.length >= 12) score += 1;

    // Character variety checks
    if (/[a-z]/.test(password)) score += 1;
    else feedback.push('Include lowercase letters');

    if (/[A-Z]/.test(password)) score += 1;
    else feedback.push('Include uppercase letters');

    if (/[0-9]/.test(password)) score += 1;
    else feedback.push('Include numbers');

    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    else feedback.push('Include special characters');

    // Common patterns check
    const commonPatterns = [
      /123456/,
      /password/i,
      /qwerty/i,
      /abc123/i,
    ];

    if (commonPatterns.some(pattern => pattern.test(password))) {
      score -= 2;
      feedback.push('Avoid common patterns');
    }

    return {
      score: Math.max(0, score),
      feedback,
      isStrong: score >= 5 && feedback.length === 0,
    };
  }
}

// Export singleton instance
export const authAPI = new AuthAPI();
