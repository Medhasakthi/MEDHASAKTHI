/**
 * Main App Navigator
 */
import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { useAuth } from '../contexts/AuthContext';
import { colors, typography } from '../theme';
import { RootStackParamList, TabParamList } from '../types';

// Auth Screens
import LoginScreen from '../components/auth/LoginScreen';
import LoadingSpinner from '../components/common/LoadingSpinner';

// Main Screens
import DashboardScreen from '../components/dashboard/DashboardScreen';
import InstitutesScreen from '../components/institutes/InstitutesScreen';
import AnalyticsScreen from '../components/analytics/AnalyticsScreen';
import SupportScreen from '../components/support/SupportScreen';
import SettingsScreen from '../components/settings/SettingsScreen';

const Stack = createStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<TabParamList>();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          switch (route.name) {
            case 'Dashboard':
              iconName = 'dashboard';
              break;
            case 'Institutes':
              iconName = 'school';
              break;
            case 'Analytics':
              iconName = 'analytics';
              break;
            case 'Support':
              iconName = 'support-agent';
              break;
            case 'Settings':
              iconName = 'settings';
              break;
            default:
              iconName = 'help';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.border,
          paddingBottom: 5,
          paddingTop: 5,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: typography.sizes.xs,
          fontWeight: typography.weights.medium,
        },
        headerStyle: {
          backgroundColor: colors.primary,
          elevation: 0,
          shadowOpacity: 0,
        },
        headerTintColor: colors.white,
        headerTitleStyle: {
          fontSize: typography.sizes.lg,
          fontWeight: typography.weights.semibold,
        },
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{
          title: 'Dashboard',
          headerTitle: 'MEDHASAKTHI Admin',
        }}
      />
      <Tab.Screen 
        name="Institutes" 
        component={InstitutesScreen}
        options={{
          title: 'Institutes',
          headerTitle: 'Institute Management',
        }}
      />
      <Tab.Screen 
        name="Analytics" 
        component={AnalyticsScreen}
        options={{
          title: 'Analytics',
          headerTitle: 'Platform Analytics',
        }}
      />
      <Tab.Screen 
        name="Support" 
        component={SupportScreen}
        options={{
          title: 'Support',
          headerTitle: 'Support Tickets',
        }}
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{
          title: 'Settings',
          headerTitle: 'System Settings',
        }}
      />
    </Tab.Navigator>
  );
}

export default function AppNavigator() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner message="Initializing..." />;
  }

  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        cardStyle: { backgroundColor: colors.background },
      }}
    >
      {isAuthenticated ? (
        <>
          <Stack.Screen name="MainTabs" component={MainTabs} />
          {/* Add other authenticated screens here */}
        </>
      ) : (
        <Stack.Screen name="Login" component={LoginScreen} />
      )}
    </Stack.Navigator>
  );
}
