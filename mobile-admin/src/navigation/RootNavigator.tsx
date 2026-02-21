/**
 * Root Navigator - Handles authentication and user role routing
 */
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

import { RootStackParamList } from '../types';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/common/LoadingSpinner';

// Navigators
import AuthNavigator from './AuthNavigator';
import AppNavigator from './AppNavigator'; // Admin/Super Admin Navigator
import StudentNavigator from './StudentNavigator';

const Stack = createStackNavigator<RootStackParamList>();

export default function RootNavigator() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {!user ? (
          // User is not authenticated - show auth screens
          <Stack.Screen name="Auth" component={AuthNavigator} />
        ) : (
          // User is authenticated - route based on role
          <>
            {user.role === 'student' ? (
              // Student user - show student interface
              <Stack.Screen name="StudentApp">
                {() => (
                  <StudentNavigator
                    instituteName={user.institute?.name}
                    instituteLogo={user.institute?.logo}
                    studentName={`${user.profile?.first_name} ${user.profile?.last_name}`}
                    notificationCount={user.unreadNotifications || 0}
                  />
                )}
              </Stack.Screen>
            ) : (
              // Admin/Super Admin user - show admin interface
              <Stack.Screen name="AdminApp" component={AppNavigator} />
            )}
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
