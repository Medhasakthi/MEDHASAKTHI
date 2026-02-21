/**
 * Theme configuration for Mobile Admin App
 */

export const colors = {
  // Primary colors
  primary: '#667eea',
  primaryLight: '#9bb5ff',
  primaryDark: '#3f51b5',
  secondary: '#764ba2',
  secondaryLight: '#a478d4',
  secondaryDark: '#4a2c73',

  // Neutral colors
  white: '#ffffff',
  black: '#000000',
  gray: '#666666',
  lightGray: '#e0e0e0',
  darkGray: '#333333',
  background: '#f5f5f5',
  surface: '#ffffff',

  // Status colors
  success: '#4caf50',
  successLight: '#81c784',
  successDark: '#388e3c',
  warning: '#ff9800',
  warningLight: '#ffb74d',
  warningDark: '#f57c00',
  error: '#f44336',
  errorLight: '#ffebee',
  errorDark: '#d32f2f',
  info: '#2196f3',
  infoLight: '#64b5f6',
  infoDark: '#1976d2',

  // Text colors
  text: '#333333',
  textSecondary: '#666666',
  textLight: '#999999',
  textInverse: '#ffffff',

  // Border colors
  border: '#e0e0e0',
  borderLight: '#f0f0f0',
  borderDark: '#cccccc',

  // Shadow colors
  shadow: 'rgba(0, 0, 0, 0.1)',
  shadowDark: 'rgba(0, 0, 0, 0.2)',

  // Gradient colors
  gradientPrimary: ['#667eea', '#764ba2'],
  gradientSuccess: ['#4caf50', '#81c784'],
  gradientWarning: ['#ff9800', '#ffb74d'],
  gradientError: ['#f44336', '#ef5350'],
};

export const typography = {
  sizes: {
    xs: 10,
    sm: 12,
    md: 14,
    lg: 16,
    xl: 18,
    xxl: 24,
    xxxl: 32,
  },
  weights: {
    light: '300' as const,
    regular: '400' as const,
    medium: '500' as const,
    semibold: '600' as const,
    bold: '700' as const,
  },
  lineHeights: {
    tight: 1.2,
    normal: 1.4,
    relaxed: 1.6,
  },
  families: {
    regular: 'System',
    medium: 'System',
    bold: 'System',
  },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
  xxxl: 64,
};

export const borderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  xxl: 24,
  round: 50,
};

export const shadows = {
  sm: {
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  md: {
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
  lg: {
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.2,
    shadowRadius: 16,
    elevation: 8,
  },
};

export const layout = {
  window: {
    width: 0, // Will be set dynamically
    height: 0, // Will be set dynamically
  },
  isSmallDevice: false, // Will be set dynamically
  headerHeight: 60,
  tabBarHeight: 80,
  statusBarHeight: 0, // Will be set dynamically
};

export const animations = {
  timing: {
    fast: 200,
    normal: 300,
    slow: 500,
  },
  easing: {
    easeInOut: 'ease-in-out',
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    linear: 'linear',
  },
};

// Component-specific styles
export const components = {
  button: {
    height: 48,
    borderRadius: borderRadius.lg,
    paddingHorizontal: spacing.lg,
  },
  input: {
    height: 48,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  card: {
    borderRadius: borderRadius.lg,
    backgroundColor: colors.surface,
    padding: spacing.lg,
    ...shadows.md,
  },
  header: {
    height: layout.headerHeight,
    backgroundColor: colors.surface,
    ...shadows.sm,
  },
};

// Status bar styles
export const statusBarStyles = {
  light: {
    backgroundColor: colors.primary,
    barStyle: 'light-content' as const,
  },
  dark: {
    backgroundColor: colors.surface,
    barStyle: 'dark-content' as const,
  },
};

// Chart colors
export const chartColors = [
  colors.primary,
  colors.secondary,
  colors.success,
  colors.warning,
  colors.error,
  colors.info,
  colors.primaryLight,
  colors.secondaryLight,
  colors.successLight,
  colors.warningLight,
];

// Theme object
export const theme = {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  layout,
  animations,
  components,
  statusBarStyles,
  chartColors,
};

export type Theme = typeof theme;
export default theme;
