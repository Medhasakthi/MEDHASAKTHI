/**
 * Login Screen for Mobile Admin App
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Image,
} from 'react-native';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialIcons';
import Toast from 'react-native-toast-message';
import { useBiometrics } from 'react-native-biometrics';

import { useAuth } from '../../contexts/AuthContext';
import { LoginCredentials } from '../../types';
import { colors, typography, spacing } from '../../theme';

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
});

type LoginFormData = yup.InferType<typeof loginSchema>;

interface LoginScreenProps {
  navigation: any;
}

export default function LoginScreen({ navigation }: LoginScreenProps) {
  const { login, isLoading, error } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [show2FA, setShow2FA] = useState(false);
  const [biometricsAvailable, setBiometricsAvailable] = useState(false);
  const { isSensorAvailable } = useBiometrics();

  const {
    control,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<LoginFormData>({
    resolver: yupResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      totp_code: '',
    },
  });

  useEffect(() => {
    checkBiometrics();
  }, []);

  const checkBiometrics = async () => {
    try {
      const { available } = await isSensorAvailable();
      setBiometricsAvailable(available);
    } catch (error) {
      setBiometricsAvailable(false);
    }
  };

  const onSubmit = async (data: LoginFormData) => {
    try {
      const credentials: Omit<LoginCredentials, 'device_info'> = {
        email: data.email,
        password: data.password,
        totp_code: data.totp_code || undefined,
        remember_me: true,
      };

      await login(credentials);
      navigation.replace('MainTabs');
    } catch (error: any) {
      if (error.response?.data?.detail?.includes('2FA')) {
        setShow2FA(true);
        Toast.show({
          type: 'info',
          text1: '2FA Required',
          text2: 'Please enter your 2FA code',
        });
      }
    }
  };

  const handleBiometricLogin = async () => {
    try {
      // Implementation for biometric login
      Toast.show({
        type: 'info',
        text1: 'Biometric Login',
        text2: 'Feature coming soon',
      });
    } catch (error) {
      Toast.show({
        type: 'error',
        text1: 'Biometric Login Failed',
        text2: 'Please use email and password',
      });
    }
  };

  const handleForgotPassword = () => {
    Alert.alert(
      'Forgot Password',
      'Please contact MEDHASAKTHI support to reset your password.',
      [{ text: 'OK' }]
    );
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <LinearGradient
        colors={[colors.primary, colors.secondary]}
        style={styles.gradient}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          {/* Header */}
          <View style={styles.header}>
            <Icon name="psychology" size={60} color={colors.white} />
            <Text style={styles.title}>MEDHASAKTHI</Text>
            <Text style={styles.subtitle}>Super Admin Portal</Text>
          </View>

          {/* Login Form */}
          <View style={styles.formContainer}>
            {/* Email Input */}
            <View style={styles.inputContainer}>
              <Icon name="email" size={20} color={colors.gray} style={styles.inputIcon} />
              <Controller
                name="email"
                control={control}
                render={({ field: { onChange, onBlur, value } }) => (
                  <TextInput
                    style={styles.input}
                    placeholder="Email Address"
                    placeholderTextColor={colors.gray}
                    value={value}
                    onChangeText={onChange}
                    onBlur={onBlur}
                    keyboardType="email-address"
                    autoCapitalize="none"
                    autoCorrect={false}
                  />
                )}
              />
            </View>
            {errors.email && (
              <Text style={styles.errorText}>{errors.email.message}</Text>
            )}

            {/* Password Input */}
            <View style={styles.inputContainer}>
              <Icon name="lock" size={20} color={colors.gray} style={styles.inputIcon} />
              <Controller
                name="password"
                control={control}
                render={({ field: { onChange, onBlur, value } }) => (
                  <TextInput
                    style={[styles.input, styles.passwordInput]}
                    placeholder="Password"
                    placeholderTextColor={colors.gray}
                    value={value}
                    onChangeText={onChange}
                    onBlur={onBlur}
                    secureTextEntry={!showPassword}
                    autoCapitalize="none"
                    autoCorrect={false}
                  />
                )}
              />
              <TouchableOpacity
                style={styles.passwordToggle}
                onPress={() => setShowPassword(!showPassword)}
              >
                <Icon
                  name={showPassword ? 'visibility-off' : 'visibility'}
                  size={20}
                  color={colors.gray}
                />
              </TouchableOpacity>
            </View>
            {errors.password && (
              <Text style={styles.errorText}>{errors.password.message}</Text>
            )}

            {/* 2FA Input */}
            {show2FA && (
              <>
                <View style={styles.inputContainer}>
                  <Icon name="security" size={20} color={colors.gray} style={styles.inputIcon} />
                  <Controller
                    name="totp_code"
                    control={control}
                    render={({ field: { onChange, onBlur, value } }) => (
                      <TextInput
                        style={styles.input}
                        placeholder="2FA Code (6 digits)"
                        placeholderTextColor={colors.gray}
                        value={value}
                        onChangeText={onChange}
                        onBlur={onBlur}
                        keyboardType="numeric"
                        maxLength={6}
                      />
                    )}
                  />
                </View>
                {errors.totp_code && (
                  <Text style={styles.errorText}>{errors.totp_code.message}</Text>
                )}
              </>
            )}

            {/* Error Message */}
            {error && (
              <View style={styles.errorContainer}>
                <Icon name="error" size={16} color={colors.error} />
                <Text style={styles.errorMessage}>{error}</Text>
              </View>
            )}

            {/* Login Button */}
            <TouchableOpacity
              style={[styles.loginButton, isLoading && styles.loginButtonDisabled]}
              onPress={handleSubmit(onSubmit)}
              disabled={isLoading}
            >
              <LinearGradient
                colors={[colors.white, colors.lightGray]}
                style={styles.loginButtonGradient}
              >
                <Text style={styles.loginButtonText}>
                  {isLoading ? 'Signing In...' : 'Sign In'}
                </Text>
              </LinearGradient>
            </TouchableOpacity>

            {/* Biometric Login */}
            {biometricsAvailable && (
              <TouchableOpacity
                style={styles.biometricButton}
                onPress={handleBiometricLogin}
              >
                <Icon name="fingerprint" size={24} color={colors.white} />
                <Text style={styles.biometricText}>Use Biometric Login</Text>
              </TouchableOpacity>
            )}

            {/* Forgot Password */}
            <TouchableOpacity
              style={styles.forgotPasswordButton}
              onPress={handleForgotPassword}
            >
              <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
            </TouchableOpacity>

            {/* Demo Credentials */}
            {__DEV__ && (
              <View style={styles.demoContainer}>
                <Text style={styles.demoTitle}>Demo Credentials:</Text>
                <TouchableOpacity
                  style={styles.demoButton}
                  onPress={() => {
                    setValue('email', 'superadmin@medhasakthi.com');
                    setValue('password', 'superadmin123!');
                  }}
                >
                  <Text style={styles.demoButtonText}>Use Super Admin</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </ScrollView>
      </LinearGradient>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradient: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: spacing.lg,
  },
  header: {
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  title: {
    fontSize: typography.sizes.xxl,
    fontWeight: typography.weights.bold,
    color: colors.white,
    marginTop: spacing.md,
  },
  subtitle: {
    fontSize: typography.sizes.md,
    color: colors.white,
    opacity: 0.9,
    marginTop: spacing.xs,
  },
  formContainer: {
    backgroundColor: colors.white,
    borderRadius: 20,
    padding: spacing.xl,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.1,
    shadowRadius: 20,
    elevation: 10,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.lightGray,
    borderRadius: 12,
    marginBottom: spacing.md,
    paddingHorizontal: spacing.md,
    backgroundColor: colors.background,
  },
  inputIcon: {
    marginRight: spacing.sm,
  },
  input: {
    flex: 1,
    height: 50,
    fontSize: typography.sizes.md,
    color: colors.text,
  },
  passwordInput: {
    paddingRight: spacing.xl,
  },
  passwordToggle: {
    position: 'absolute',
    right: spacing.md,
    padding: spacing.xs,
  },
  errorText: {
    color: colors.error,
    fontSize: typography.sizes.sm,
    marginBottom: spacing.sm,
    marginLeft: spacing.xs,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.errorLight,
    padding: spacing.sm,
    borderRadius: 8,
    marginBottom: spacing.md,
  },
  errorMessage: {
    color: colors.error,
    fontSize: typography.sizes.sm,
    marginLeft: spacing.xs,
    flex: 1,
  },
  loginButton: {
    borderRadius: 12,
    marginBottom: spacing.md,
    overflow: 'hidden',
  },
  loginButtonDisabled: {
    opacity: 0.6,
  },
  loginButtonGradient: {
    paddingVertical: spacing.md,
    alignItems: 'center',
  },
  loginButtonText: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
    color: colors.primary,
  },
  biometricButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primaryLight,
    paddingVertical: spacing.md,
    borderRadius: 12,
    marginBottom: spacing.md,
  },
  biometricText: {
    color: colors.white,
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.medium,
    marginLeft: spacing.sm,
  },
  forgotPasswordButton: {
    alignItems: 'center',
    paddingVertical: spacing.sm,
  },
  forgotPasswordText: {
    color: colors.primary,
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.medium,
  },
  demoContainer: {
    marginTop: spacing.lg,
    padding: spacing.md,
    backgroundColor: colors.background,
    borderRadius: 8,
  },
  demoTitle: {
    fontSize: typography.sizes.sm,
    color: colors.gray,
    marginBottom: spacing.sm,
  },
  demoButton: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: 6,
  },
  demoButtonText: {
    color: colors.white,
    fontSize: typography.sizes.sm,
    textAlign: 'center',
  },
});
