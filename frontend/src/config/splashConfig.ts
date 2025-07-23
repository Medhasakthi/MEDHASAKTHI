// MEDHASAKTHI Splash Screen Configuration
// Centralized configuration for all splash screens across the platform

export interface SplashConfig {
  title: string;
  subtitle: string;
  color: string;
  duration: number;
  icon?: string;
  showProgress?: boolean;
  variant?: 'default' | 'minimal' | 'loading' | 'auth';
}

export const SPLASH_CONFIGS: Record<string, SplashConfig> = {
  // Main Application
  app: {
    title: 'MEDHASAKTHI',
    subtitle: 'Educational Excellence Platform',
    color: '#1976d2',
    duration: 3000,
    showProgress: true,
    variant: 'default'
  },

  // Authentication
  auth: {
    title: 'MEDHASAKTHI',
    subtitle: 'Secure Authentication Portal',
    color: '#0d47a1',
    duration: 2500,
    showProgress: true,
    variant: 'auth'
  },

  // Student Dashboard
  'student-dashboard': {
    title: 'Student Dashboard',
    subtitle: 'Your Learning Journey Awaits',
    color: '#1976d2',
    duration: 2000,
    showProgress: false,
    variant: 'minimal'
  },

  // Teacher Dashboard
  'teacher-dashboard': {
    title: 'Teacher Dashboard',
    subtitle: 'Empowering Education Excellence',
    color: '#0d47a1',
    duration: 2000,
    showProgress: false,
    variant: 'minimal'
  },

  // Admin Dashboard
  'admin-dashboard': {
    title: 'Admin Dashboard',
    subtitle: 'System Management Portal',
    color: '#1565c0',
    duration: 2500,
    showProgress: false,
    variant: 'minimal'
  },

  // Independent Learner
  'independent-learner': {
    title: 'Independent Learner',
    subtitle: 'Self-Paced Learning Hub',
    color: '#7b1fa2',
    duration: 2000,
    showProgress: false,
    variant: 'minimal'
  },

  // Exam Management
  'exam-management': {
    title: 'Exam Management',
    subtitle: 'Comprehensive Assessment Tools',
    color: '#d32f2f',
    duration: 1800,
    showProgress: false,
    variant: 'minimal'
  },

  // Analytics Dashboard
  'analytics-dashboard': {
    title: 'Analytics Dashboard',
    subtitle: 'Data-Driven Insights',
    color: '#388e3c',
    duration: 2000,
    showProgress: false,
    variant: 'minimal'
  },

  // Institute Management
  'institute-management': {
    title: 'Institute Management',
    subtitle: 'Institutional Administration',
    color: '#f57c00',
    duration: 2000,
    showProgress: false,
    variant: 'minimal'
  },

  // Certificate Management
  'certificate-management': {
    title: 'Certificate Management',
    subtitle: 'Digital Certification System',
    color: '#5d4037',
    duration: 1800,
    showProgress: false,
    variant: 'minimal'
  },

  // AI Question Generator
  'ai-question-generator': {
    title: 'AI Question Generator',
    subtitle: 'Intelligent Assessment Creation',
    color: '#e91e63',
    duration: 2200,
    showProgress: false,
    variant: 'minimal'
  },

  // System Settings
  'system-settings': {
    title: 'System Settings',
    subtitle: 'Platform Configuration',
    color: '#424242',
    duration: 1500,
    showProgress: false,
    variant: 'minimal'
  },

  // User Feedback
  'user-feedback': {
    title: 'User Feedback',
    subtitle: 'Voice of Our Community',
    color: '#00796b',
    duration: 1800,
    showProgress: false,
    variant: 'minimal'
  },

  // Payment System
  'payment-system': {
    title: 'Payment System',
    subtitle: 'Secure Transaction Portal',
    color: '#1976d2',
    duration: 2000,
    showProgress: false,
    variant: 'minimal'
  },

  // Loading States
  loading: {
    title: 'Loading...',
    subtitle: 'Please wait while we prepare your content',
    color: '#1976d2',
    duration: 0, // Infinite until manually hidden
    showProgress: true,
    variant: 'loading'
  },

  // Error States
  error: {
    title: 'Something went wrong',
    subtitle: 'We\'re working to fix this issue',
    color: '#d32f2f',
    duration: 3000,
    showProgress: false,
    variant: 'minimal'
  }
};

// Helper function to get splash config
export const getSplashConfig = (key: string): SplashConfig => {
  return SPLASH_CONFIGS[key] || SPLASH_CONFIGS.app;
};

// Brand colors for consistency
export const BRAND_COLORS = {
  primary: '#1976d2',
  secondary: '#dc004e',
  success: '#388e3c',
  warning: '#f57c00',
  error: '#d32f2f',
  info: '#0288d1',
  dark: '#0d47a1',
  light: '#42a5f5'
};

// Animation presets
export const ANIMATION_PRESETS = {
  fast: {
    duration: 1000,
    easing: 'ease-out'
  },
  normal: {
    duration: 2000,
    easing: 'ease-in-out'
  },
  slow: {
    duration: 3000,
    easing: 'ease-in'
  }
};

// Logo configuration
export const LOGO_CONFIG = {
  src: '/assets/images/medhasakthi.png',
  alt: 'MEDHASAKTHI Logo',
  fallback: 'M', // Fallback text when logo is not available
  sizes: {
    small: 60,
    medium: 100,
    large: 120
  }
};
