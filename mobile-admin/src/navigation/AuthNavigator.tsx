/**
 * Authentication Navigator
 */
import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';

import { AuthStackParamList } from '../types';
import { colors } from '../theme';

// Auth Screens
import LoginScreen from '../components/auth/LoginScreen';
import ForgotPasswordScreen from '../components/auth/ForgotPasswordScreen';
import ResetPasswordScreen from '../components/auth/ResetPasswordScreen';

const Stack = createStackNavigator<AuthStackParamList>();

export default function AuthNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        cardStyle: { backgroundColor: colors.background },
      }}
    >
      <Stack.Screen 
        name="Login" 
        component={LoginScreen}
        options={{
          title: 'Sign In',
        }}
      />
      <Stack.Screen 
        name="ForgotPassword" 
        component={ForgotPasswordScreen}
        options={{
          title: 'Forgot Password',
          headerShown: true,
          headerStyle: {
            backgroundColor: colors.primary,
          },
          headerTintColor: colors.white,
        }}
      />
      <Stack.Screen 
        name="ResetPassword" 
        component={ResetPasswordScreen}
        options={{
          title: 'Reset Password',
          headerShown: true,
          headerStyle: {
            backgroundColor: colors.primary,
          },
          headerTintColor: colors.white,
        }}
      />
    </Stack.Navigator>
  );
}
