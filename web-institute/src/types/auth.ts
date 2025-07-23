/**
 * Authentication types for Institute Portal
 */

export interface User {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  is_2fa_enabled: boolean;
  created_at: string;
  last_login?: string;
  profile?: UserProfile;
}

export interface UserProfile {
  first_name: string;
  last_name: string;
  phone?: string;
  profile_picture_url?: string;
  timezone: string;
  language: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  totp_code?: string;
  remember_me?: boolean;
  device_info?: DeviceInfo;
}

export interface RegisterData {
  email: string;
  password: string;
  confirm_password: string;
  role: string;
  first_name: string;
  last_name: string;
  phone?: string;
  institute_code?: string;
  employee_id?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface DeviceInfo {
  device_type: string;
  os: string;
  browser: string;
  app_version?: string;
  device_id?: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordReset {
  token: string;
  new_password: string;
  confirm_password: string;
}

export interface PasswordChange {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  register: (data: RegisterData) => Promise<void>;
  refreshAuth: () => Promise<void>;
  clearError: () => void;
}

export enum UserRole {
  SUPER_ADMIN = 'super_admin',
  INSTITUTE_ADMIN = 'institute_admin',
  TEACHER = 'teacher',
  STUDENT = 'student',
  PARENT = 'parent',
}
