import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { authAPI } from '../../services/api/authAPI';

// Types
export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'institute_admin' | 'institute_staff' | 'teacher' | 'student';
  is_active: boolean;
  is_2fa_enabled: boolean;
  profile_picture?: string;
  institute_id?: string;
  institute_name?: string;
  permissions?: string[];
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  loginAttempts: number;
  lastLoginAttempt: number | null;
  deviceSession: string | null;
  requires2FA: boolean;
  requiresDeviceVerification: boolean;
}

const initialState: AuthState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  loginAttempts: 0,
  lastLoginAttempt: null,
  deviceSession: null,
  requires2FA: false,
  requiresDeviceVerification: false,
};

// Async thunks
export const loginUser = createAsyncThunk(
  'auth/login',
  async (
    credentials: {
      email: string;
      password: string;
      totpCode?: string;
      deviceInfo: any;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await authAPI.login(credentials);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Login failed');
    }
  }
);

export const registerUser = createAsyncThunk(
  'auth/register',
  async (
    userData: {
      email: string;
      password: string;
      full_name: string;
      role: string;
      institute_code?: string;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await authAPI.register(userData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Registration failed');
    }
  }
);

export const refreshAccessToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState() as { auth: AuthState };
      const refreshToken = state.auth.refreshToken;
      
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await authAPI.refreshToken(refreshToken);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Token refresh failed');
    }
  }
);

export const logoutUser = createAsyncThunk(
  'auth/logout',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState() as { auth: AuthState };
      const token = state.auth.token;
      
      if (token) {
        await authAPI.logout();
      }
      
      return {};
    } catch (error: any) {
      // Even if logout API fails, we should clear local state
      return {};
    }
  }
);

export const getCurrentUser = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authAPI.getCurrentUser();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to get user');
    }
  }
);

export const updateProfile = createAsyncThunk(
  'auth/updateProfile',
  async (
    profileData: {
      full_name?: string;
      profile_picture?: string;
      phone?: string;
      address?: string;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await authAPI.updateProfile(profileData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Profile update failed');
    }
  }
);

export const changePassword = createAsyncThunk(
  'auth/changePassword',
  async (
    passwordData: {
      current_password: string;
      new_password: string;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await authAPI.changePassword(passwordData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Password change failed');
    }
  }
);

export const setup2FA = createAsyncThunk(
  'auth/setup2FA',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authAPI.setup2FA();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '2FA setup failed');
    }
  }
);

export const verify2FA = createAsyncThunk(
  'auth/verify2FA',
  async (
    verificationData: {
      totp_code: string;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await authAPI.verify2FA(verificationData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '2FA verification failed');
    }
  }
);

export const disable2FA = createAsyncThunk(
  'auth/disable2FA',
  async (
    verificationData: {
      totp_code: string;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await authAPI.disable2FA(verificationData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '2FA disable failed');
    }
  }
);

// Auth slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearAuthState: (state) => {
      return { ...initialState };
    },
    setToken: (state, action: PayloadAction<string>) => {
      state.token = action.payload;
    },
    incrementLoginAttempts: (state) => {
      state.loginAttempts += 1;
      state.lastLoginAttempt = Date.now();
    },
    resetLoginAttempts: (state) => {
      state.loginAttempts = 0;
      state.lastLoginAttempt = null;
    },
    setRequires2FA: (state, action: PayloadAction<boolean>) => {
      state.requires2FA = action.payload;
    },
    setRequiresDeviceVerification: (state, action: PayloadAction<boolean>) => {
      state.requiresDeviceVerification = action.payload;
    },
    updateUserProfile: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        
        if (action.payload.requires_2fa) {
          state.requires2FA = true;
          state.error = null;
        } else if (action.payload.requires_device_verification) {
          state.requiresDeviceVerification = true;
          state.error = null;
        } else {
          state.user = action.payload.user;
          state.token = action.payload.access_token;
          state.refreshToken = action.payload.refresh_token;
          state.deviceSession = action.payload.device_session_id;
          state.isAuthenticated = true;
          state.requires2FA = false;
          state.requiresDeviceVerification = false;
          state.loginAttempts = 0;
          state.lastLoginAttempt = null;
        }
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        state.loginAttempts += 1;
        state.lastLoginAttempt = Date.now();
      });

    // Register
    builder
      .addCase(registerUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.isLoading = false;
        // Registration successful, but user needs to verify email
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Refresh token
    builder
      .addCase(refreshAccessToken.fulfilled, (state, action) => {
        state.token = action.payload.access_token;
        if (action.payload.refresh_token) {
          state.refreshToken = action.payload.refresh_token;
        }
      })
      .addCase(refreshAccessToken.rejected, (state) => {
        // Token refresh failed, logout user
        return { ...initialState };
      });

    // Logout
    builder
      .addCase(logoutUser.fulfilled, (state) => {
        return { ...initialState };
      });

    // Get current user
    builder
      .addCase(getCurrentUser.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.user;
        state.isAuthenticated = true;
      })
      .addCase(getCurrentUser.rejected, (state) => {
        state.isLoading = false;
        // If getting current user fails, logout
        return { ...initialState };
      });

    // Update profile
    builder
      .addCase(updateProfile.fulfilled, (state, action) => {
        if (state.user) {
          state.user = { ...state.user, ...action.payload.user };
        }
      });

    // 2FA setup
    builder
      .addCase(setup2FA.fulfilled, (state, action) => {
        // 2FA setup data returned for QR code display
      });

    // 2FA verification
    builder
      .addCase(verify2FA.fulfilled, (state, action) => {
        if (state.user) {
          state.user.is_2fa_enabled = true;
        }
      });

    // 2FA disable
    builder
      .addCase(disable2FA.fulfilled, (state, action) => {
        if (state.user) {
          state.user.is_2fa_enabled = false;
        }
      });
  },
});

export const {
  clearError,
  clearAuthState,
  setToken,
  incrementLoginAttempts,
  resetLoginAttempts,
  setRequires2FA,
  setRequiresDeviceVerification,
  updateUserProfile,
} = authSlice.actions;

export default authSlice.reducer;
