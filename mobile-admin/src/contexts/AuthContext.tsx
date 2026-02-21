/**
 * Authentication Context for Mobile Admin App
 */
import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Toast from 'react-native-toast-message';

import { apiService } from '../services/ApiService';
import { User, LoginCredentials } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: Omit<LoginCredentials, 'device_info'>) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

// Initial state
const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Action types
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'SET_LOADING'; payload: boolean };

// Reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    
    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
    
    case 'AUTH_LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    
    default:
      return state;
  }
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize auth state
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      const [token, userStr] = await Promise.all([
        AsyncStorage.getItem('access_token'),
        AsyncStorage.getItem('user'),
      ]);

      if (token && userStr) {
        const user = JSON.parse(userStr);
        
        // Verify token is still valid
        try {
          const currentUser = await apiService.getCurrentUser();
          dispatch({
            type: 'AUTH_SUCCESS',
            payload: {
              user: currentUser,
              token,
            },
          });
        } catch (error) {
          // Token might be expired, try to refresh
          try {
            const authResponse = await apiService.refreshToken();
            dispatch({
              type: 'AUTH_SUCCESS',
              payload: {
                user: authResponse.user,
                token: authResponse.access_token,
              },
            });
          } catch (refreshError) {
            // Refresh failed, clear auth state
            await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
            dispatch({ type: 'AUTH_LOGOUT' });
          }
        }
      } else {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Login function
  const login = async (credentials: Omit<LoginCredentials, 'device_info'>) => {
    try {
      dispatch({ type: 'AUTH_START' });
      
      const authResponse = await apiService.login(credentials);
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user: authResponse.user,
          token: authResponse.access_token,
        },
      });

      Toast.show({
        type: 'success',
        text1: 'Login Successful',
        text2: `Welcome back, ${authResponse.user.profile?.first_name || authResponse.user.email}!`,
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Login failed';
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await apiService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      dispatch({ type: 'AUTH_LOGOUT' });
      Toast.show({
        type: 'success',
        text1: 'Logged Out',
        text2: 'You have been successfully logged out',
      });
    }
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const contextValue: AuthContextType = {
    user: state.user,
    token: state.token,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    error: state.error,
    login,
    logout,
    clearError,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook to use auth context
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
