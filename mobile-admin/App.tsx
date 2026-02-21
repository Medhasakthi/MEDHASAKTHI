/**
 * Main App Component for MEDHASAKTHI Mobile Admin
 */
import React, { useEffect, useState } from 'react';
import { StatusBar, LogBox } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import Toast from 'react-native-toast-message';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { store, persistor } from './src/store';
import { AuthProvider } from './src/contexts/AuthContext';
import AppNavigator from './src/navigation/AppNavigator';
import LoadingSpinner from './src/components/common/LoadingSpinner';
import SplashScreen from './src/components/SplashScreen';
import { colors } from './src/theme';

// Ignore specific warnings
LogBox.ignoreLogs([
  'Non-serializable values were found in the navigation state',
  'VirtualizedLists should never be nested',
]);

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});

export default function App() {
  const [showSplash, setShowSplash] = useState(true);

  useEffect(() => {
    // Set status bar style
    StatusBar.setBarStyle('light-content', true);
    StatusBar.setBackgroundColor(colors.primary, true);
  }, []);

  const handleSplashFinish = () => {
    setShowSplash(false);
  };

  // Show splash screen first
  if (showSplash) {
    return <SplashScreen onFinish={handleSplashFinish} />;
  }

  return (
    <Provider store={store}>
      <PersistGate loading={<LoadingSpinner />} persistor={persistor}>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <NavigationContainer>
              <StatusBar
                barStyle="light-content"
                backgroundColor={colors.primary}
                translucent={false}
              />
              <AppNavigator />
              <Toast />
            </NavigationContainer>
          </AuthProvider>
        </QueryClientProvider>
      </PersistGate>
    </Provider>
  );
}
