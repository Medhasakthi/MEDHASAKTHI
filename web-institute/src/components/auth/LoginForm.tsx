/**
 * Login Form Component for Institute Portal
 */
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Link,
  Alert,
  InputAdornment,
  IconButton,
  Checkbox,
  FormControlLabel,
  Divider,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  School,
} from '@mui/icons-material';
import { toast } from 'react-hot-toast';

import { useAuth } from '../../contexts/AuthContext';
import { LoginCredentials } from '../../types/auth';

// Validation schema
const loginSchema = yup.object({
  email: yup
    .string()
    .email('Please enter a valid email address')
    .required('Email is required'),
  password: yup
    .string()
    .min(8, 'Password must be at least 8 characters')
    .required('Password is required'),
  totp_code: yup
    .string()
    .matches(/^\d{6}$/, 'TOTP code must be 6 digits')
    .optional(),
  remember_me: yup.boolean().optional(),
});

type LoginFormData = yup.InferType<typeof loginSchema>;

export default function LoginForm() {
  const router = useRouter();
  const { login, isLoading, error, clearError } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [show2FA, setShow2FA] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
  } = useForm<LoginFormData>({
    resolver: yupResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      totp_code: '',
      remember_me: false,
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      clearError();
      
      const credentials: LoginCredentials = {
        email: data.email,
        password: data.password,
        totp_code: data.totp_code || undefined,
        remember_me: data.remember_me,
        device_info: {
          device_type: 'desktop',
          os: navigator.platform,
          browser: navigator.userAgent.split(' ').pop() || 'Unknown',
          app_version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
        },
      };

      await login(credentials);
      router.push('/dashboard');
    } catch (error: any) {
      if (error.response?.data?.detail?.includes('2FA')) {
        setShow2FA(true);
        toast.error('Please enter your 2FA code');
      }
    }
  };

  const handleTogglePassword = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: 2,
      }}
    >
      <Card
        sx={{
          maxWidth: 450,
          width: '100%',
          boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
          borderRadius: 3,
        }}
      >
        <CardContent sx={{ padding: 4 }}>
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <School sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
              MEDHASAKTHI
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Institute Portal
            </Typography>
          </Box>

          {/* Error Alert */}
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit(onSubmit)}>
            <TextField
              {...register('email')}
              fullWidth
              label="Email Address"
              type="email"
              error={!!errors.email}
              helperText={errors.email?.message}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Email color="action" />
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 3 }}
            />

            <TextField
              {...register('password')}
              fullWidth
              label="Password"
              type={showPassword ? 'text' : 'password'}
              error={!!errors.password}
              helperText={errors.password?.message}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={handleTogglePassword} edge="end">
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{ mb: show2FA ? 2 : 3 }}
            />

            {/* 2FA Code Field */}
            {show2FA && (
              <TextField
                {...register('totp_code')}
                fullWidth
                label="2FA Code"
                placeholder="Enter 6-digit code"
                error={!!errors.totp_code}
                helperText={errors.totp_code?.message || 'Enter the 6-digit code from your authenticator app'}
                sx={{ mb: 3 }}
              />
            )}

            {/* Remember Me */}
            <FormControlLabel
              control={
                <Checkbox
                  {...register('remember_me')}
                  color="primary"
                />
              }
              label="Remember me"
              sx={{ mb: 3 }}
            />

            {/* Login Button */}
            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isLoading}
              sx={{
                mb: 3,
                py: 1.5,
                background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                '&:hover': {
                  background: 'linear-gradient(45deg, #5a6fd8 30%, #6a4190 90%)',
                },
              }}
            >
              {isLoading ? 'Signing In...' : 'Sign In'}
            </Button>

            <Divider sx={{ mb: 3 }}>
              <Typography variant="body2" color="text.secondary">
                OR
              </Typography>
            </Divider>

            {/* Links */}
            <Box sx={{ textAlign: 'center' }}>
              <Link
                href="/forgot-password"
                variant="body2"
                sx={{ display: 'block', mb: 2 }}
              >
                Forgot your password?
              </Link>
              
              <Typography variant="body2" color="text.secondary">
                Don't have an account?{' '}
                <Link href="/register" color="primary">
                  Contact your administrator
                </Link>
              </Typography>
            </Box>
          </form>

          {/* Demo Credentials */}
          {process.env.NODE_ENV === 'development' && (
            <Box sx={{ mt: 4, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
              <Typography variant="caption" display="block" gutterBottom>
                Demo Credentials:
              </Typography>
              <Typography variant="caption" display="block">
                Admin: admin@demo-school.edu / admin123!
              </Typography>
              <Typography variant="caption" display="block">
                Teacher: teacher@demo-school.edu / teacher123!
              </Typography>
              <Button
                size="small"
                onClick={() => {
                  setValue('email', 'admin@demo-school.edu');
                  setValue('password', 'admin123!');
                }}
                sx={{ mt: 1, mr: 1 }}
              >
                Use Admin
              </Button>
              <Button
                size="small"
                onClick={() => {
                  setValue('email', 'teacher@demo-school.edu');
                  setValue('password', 'teacher123!');
                }}
                sx={{ mt: 1 }}
              >
                Use Teacher
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
