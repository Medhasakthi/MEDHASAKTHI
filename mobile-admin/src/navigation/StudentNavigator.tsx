/**
 * Student App Navigator with Custom Top App Bar
 */
import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { colors, typography } from '../theme';
import { StudentStackParamList, StudentTabParamList } from '../types';
import StudentTopAppBar from '../components/common/StudentTopAppBar';

// Student Screens (you'll need to create these)
import StudentDashboardScreen from '../components/student/StudentDashboardScreen';
import ExamsScreen from '../components/student/ExamsScreen';
import ResultsScreen from '../components/student/ResultsScreen';
import ProfileScreen from '../components/student/ProfileScreen';
import NotificationsScreen from '../components/student/NotificationsScreen';

const Stack = createStackNavigator<StudentStackParamList>();
const Tab = createBottomTabNavigator<StudentTabParamList>();

interface StudentTabsProps {
  instituteName?: string;
  instituteLogo?: string;
  studentName?: string;
  notificationCount?: number;
}

function StudentTabs({ 
  instituteName, 
  instituteLogo, 
  studentName,
  notificationCount = 0 
}: StudentTabsProps) {
  const handleNotificationPress = () => {
    // Navigate to notifications screen
    console.log('Notification pressed');
  };

  const handleProfilePress = () => {
    // Navigate to profile screen
    console.log('Profile pressed');
  };

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          switch (route.name) {
            case 'Dashboard':
              iconName = 'dashboard';
              break;
            case 'Exams':
              iconName = 'quiz';
              break;
            case 'Results':
              iconName = 'assessment';
              break;
            case 'Profile':
              iconName = 'person';
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
        header: () => (
          <StudentTopAppBar
            instituteName={instituteName}
            instituteLogo={instituteLogo}
            onNotificationPress={handleNotificationPress}
            onProfilePress={handleProfilePress}
            notificationCount={notificationCount}
          />
        ),
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={StudentDashboardScreen}
        options={{
          title: 'Home',
        }}
      />
      <Tab.Screen 
        name="Exams" 
        component={ExamsScreen}
        options={{
          title: 'Exams',
        }}
      />
      <Tab.Screen 
        name="Results" 
        component={ResultsScreen}
        options={{
          title: 'Results',
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          title: 'Profile',
        }}
      />
    </Tab.Navigator>
  );
}

interface StudentNavigatorProps {
  instituteName?: string;
  instituteLogo?: string;
  studentName?: string;
  notificationCount?: number;
}

export default function StudentNavigator({
  instituteName = 'Demo Institute',
  instituteLogo,
  studentName = 'Student',
  notificationCount = 0,
}: StudentNavigatorProps) {
  const handleNotificationPress = () => {
    // Navigate to notifications
    console.log('Navigate to notifications');
  };

  const handleProfilePress = () => {
    // Navigate to profile
    console.log('Navigate to profile');
  };

  const handleBackPress = () => {
    // Handle back navigation
    console.log('Back pressed');
  };

  return (
    <Stack.Navigator
      screenOptions={{
        cardStyle: { backgroundColor: colors.background },
      }}
    >
      <Stack.Screen 
        name="StudentTabs" 
        options={{ headerShown: false }}
      >
        {() => (
          <StudentTabs
            instituteName={instituteName}
            instituteLogo={instituteLogo}
            studentName={studentName}
            notificationCount={notificationCount}
          />
        )}
      </Stack.Screen>
      
      {/* Additional Stack Screens with Custom Headers */}
      <Stack.Screen 
        name="Notifications"
        component={NotificationsScreen}
        options={{
          header: () => (
            <StudentTopAppBar
              title="Notifications"
              showBackButton={true}
              onBackPress={handleBackPress}
              onProfilePress={handleProfilePress}
              instituteName={instituteName}
              instituteLogo={instituteLogo}
            />
          ),
        }}
      />
      
      {/* Add more screens as needed */}
    </Stack.Navigator>
  );
}
