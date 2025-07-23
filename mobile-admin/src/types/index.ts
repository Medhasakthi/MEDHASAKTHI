/**
 * TypeScript types for Mobile Admin App
 */

// User and Authentication Types
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
  institute?: {
    id: string;
    name: string;
    logo?: string;
  };
  unreadNotifications?: number;
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
  app_version: string;
  device_id: string;
  device_name: string;
}

// Institute Management Types
export interface Institute {
  id: string;
  name: string;
  code: string;
  admin_user_id: string;
  description?: string;
  website?: string;
  phone?: string;
  email?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  subscription_plan: string;
  subscription_expires_at?: string;
  max_students: number;
  max_teachers: number;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at?: string;
  admin?: User;
  student_count?: number;
  teacher_count?: number;
  exam_count?: number;
}

export interface InstituteStats {
  total_institutes: number;
  active_institutes: number;
  pending_verification: number;
  total_students: number;
  total_teachers: number;
  total_exams: number;
  monthly_growth: number;
  revenue: number;
}

// Platform Analytics Types
export interface PlatformAnalytics {
  overview: {
    total_users: number;
    total_institutes: number;
    total_questions_generated: number;
    total_exams_conducted: number;
    platform_uptime: number;
    api_response_time: number;
  };
  user_growth: Array<{
    date: string;
    new_users: number;
    active_users: number;
  }>;
  institute_growth: Array<{
    date: string;
    new_institutes: number;
    active_institutes: number;
  }>;
  ai_usage: {
    total_generations: number;
    success_rate: number;
    average_cost: number;
    popular_subjects: Array<{
      subject: string;
      count: number;
    }>;
  };
  revenue: {
    total_revenue: number;
    monthly_recurring_revenue: number;
    average_revenue_per_user: number;
    churn_rate: number;
  };
  system_health: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    active_connections: number;
    error_rate: number;
  };
}

// Subscription and Billing Types
export interface SubscriptionPlan {
  id: string;
  name: string;
  description: string;
  price_monthly: number;
  price_yearly: number;
  max_students: number;
  max_teachers: number;
  max_exams_per_month: number;
  ai_questions_per_month: number;
  features: string[];
  is_popular: boolean;
  is_active: boolean;
}

export interface BillingInfo {
  institute_id: string;
  subscription_plan: string;
  billing_cycle: 'monthly' | 'yearly';
  amount: number;
  currency: string;
  next_billing_date: string;
  payment_method: string;
  billing_history: Array<{
    date: string;
    amount: number;
    status: string;
    invoice_url?: string;
  }>;
}

// Support and Tickets Types
export interface SupportTicket {
  id: string;
  institute_id: string;
  user_id: string;
  title: string;
  description: string;
  category: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  assigned_to?: string;
  created_at: string;
  updated_at?: string;
  resolved_at?: string;
  institute?: Institute;
  user?: User;
  messages?: SupportMessage[];
}

export interface SupportMessage {
  id: string;
  ticket_id: string;
  user_id: string;
  message: string;
  is_internal: boolean;
  attachments?: string[];
  created_at: string;
  user?: User;
}

// System Configuration Types
export interface SystemConfig {
  app_settings: {
    maintenance_mode: boolean;
    registration_enabled: boolean;
    ai_generation_enabled: boolean;
    max_file_upload_size: number;
    session_timeout_minutes: number;
  };
  email_settings: {
    smtp_host: string;
    smtp_port: number;
    smtp_username: string;
    from_email: string;
    from_name: string;
  };
  ai_settings: {
    openai_enabled: boolean;
    huggingface_enabled: boolean;
    default_model: string;
    max_questions_per_request: number;
    cost_per_question: number;
  };
  security_settings: {
    password_min_length: number;
    require_2fa: boolean;
    session_timeout: number;
    max_login_attempts: number;
    lockout_duration_minutes: number;
  };
}

// Notification Types
export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  category: string;
  is_read: boolean;
  created_at: string;
  action_url?: string;
  metadata?: Record<string, any>;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  pagination?: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// Navigation Types
export type RootStackParamList = {
  Auth: undefined;
  AdminApp: undefined;
  StudentApp: undefined;
};

export type AuthStackParamList = {
  Login: undefined;
  ForgotPassword: undefined;
  ResetPassword: { token: string };
};

export type AdminStackParamList = {
  Dashboard: undefined;
  Institutes: undefined;
  InstituteDetails: { instituteId: string };
  Analytics: undefined;
  Support: undefined;
  TicketDetails: { ticketId: string };
  Settings: undefined;
  Profile: undefined;
  Notifications: undefined;
};

export type TabParamList = {
  Dashboard: undefined;
  Institutes: undefined;
  Analytics: undefined;
  Support: undefined;
  Settings: undefined;
};

// Student Navigation Types
export type StudentStackParamList = {
  StudentTabs: undefined;
  Notifications: undefined;
  ExamDetails: { examId: string };
  TakeExam: { examId: string };
  ExamResult: { resultId: string };
  EditProfile: undefined;
};

export type StudentTabParamList = {
  Dashboard: undefined;
  Exams: undefined;
  Results: undefined;
  Profile: undefined;
};

// Form Types
export interface InstituteFormData {
  name: string;
  code: string;
  description?: string;
  admin_email: string;
  admin_first_name: string;
  admin_last_name: string;
  admin_phone?: string;
  website?: string;
  phone?: string;
  email?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  subscription_plan: string;
  max_students: number;
  max_teachers: number;
}

export interface TicketFormData {
  title: string;
  description: string;
  category: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

// Filter and Search Types
export interface InstituteFilters {
  search?: string;
  subscription_plan?: string;
  is_active?: boolean;
  is_verified?: boolean;
  country?: string;
  created_after?: string;
  created_before?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface TicketFilters {
  search?: string;
  status?: string;
  priority?: string;
  category?: string;
  institute_id?: string;
  assigned_to?: string;
  created_after?: string;
  created_before?: string;
}

// Chart Data Types
export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface TimeSeriesData {
  date: string;
  value: number;
  label?: string;
}

export interface MultiSeriesData {
  date: string;
  [key: string]: number | string;
}
