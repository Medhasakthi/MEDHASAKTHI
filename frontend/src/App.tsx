import React, { Suspense, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { Toaster } from 'react-hot-toast';

// Import splash screen components
import SplashScreen from './components/SplashScreen';
import { useSplashScreen } from './hooks/useSplashScreen';
import SplashProvider from './providers/SplashProvider';

// Import our actual components
import EnhancedLandingPage from './components/EnhancedLandingPage';
import AuthenticationPages from './components/AuthenticationPages';
import StudentDashboard from './components/StudentDashboard';
import TeacherDashboard from './components/TeacherDashboard';
import AdminDashboard from './components/AdminDashboard';
import IndependentLearnerDashboard from './components/IndependentLearnerDashboard';
import InstituteManagement from './components/InstituteManagement';
import ExamManagement from './components/ExamManagement';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import SystemSettings from './components/SystemSettings';
import CertificateManagement from './components/CertificateManagement';
import AIQuestionGenerator from './components/AIQuestionGenerator';
import UPIPayment from './components/UPIPayment';
import UserFeedbackSystem from './components/UserFeedbackSystem';



// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

// User interface
interface User {
  id: string;
  name: string;
  email: string;
  userType: string;
}

// Main App component
const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);

  // Global splash screen for first visit
  const splash = useSplashScreen({
    duration: 3000,
    showOnFirstVisit: true,
    showOnRouteChange: false
  });

  const handleLogin = async (credentials: { email: string; password: string }) => {
    setLoading(true);
    try {
      // Simulate login API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setCurrentUser({
        id: '1',
        name: 'Test User',
        email: credentials.email,
        userType: 'student'
      });
    } catch (error) {
      // Handle login error in production
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (userData: { name: string; email: string; userType: string }) => {
    setLoading(true);
    try {
      // Simulate register API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setCurrentUser({
        id: '1',
        name: userData.name,
        email: userData.email,
        userType: userData.userType
      });
    } catch (error) {
      // Handle registration error in production
      // Error handling can be implemented here
    } finally {
      setLoading(false);
    }
  };

  const renderDashboard = () => {
    if (!currentUser) {
      return null;
    }

    switch (currentUser.userType) {
      case 'student':
        return <StudentDashboard />;
      case 'teacher':
        return <TeacherDashboard />;
      case 'super_admin':
      case 'institute_admin':
        return <AdminDashboard />;
      case 'independent_learner':
        return <IndependentLearnerDashboard />;
      default:
        return <StudentDashboard />;
    }
  };

  // Show splash screen on first visit
  if (splash.isVisible) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <SplashScreen
          onComplete={splash.hide}
          duration={3000}
          title="MEDHASAKTHI"
          subtitle="Educational Excellence Platform"
          variant="default"
        />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SplashProvider enableRouteBasedSplash={true} globalSplashDuration={3000}>
        <Router>
          <Box sx={{ minHeight: '100vh' }}>
            <Suspense fallback={
              <SplashScreen
                variant="loading"
                title="Loading..."
                subtitle="Please wait while we prepare your content"
                showProgress={true}
              />
            }>
            <Routes>
              {/* Public Routes */}
              <Route
                path="/"
                element={currentUser ? <Navigate to="/dashboard" /> : <EnhancedLandingPage />}
              />
              <Route
                path="/auth"
                element={
                  currentUser ?
                    <Navigate to="/dashboard" /> :
                    <AuthenticationPages
                      onLogin={handleLogin}
                      onRegister={handleRegister}
                      loading={loading}
                    />
                }
              />

              {/* Protected Routes */}
              <Route
                path="/dashboard"
                element={currentUser ? renderDashboard() : <Navigate to="/auth" />}
              />
              <Route
                path="/institute-management"
                element={currentUser ? <InstituteManagement /> : <Navigate to="/auth" />}
              />
              <Route
                path="/exam-management"
                element={currentUser ? <ExamManagement /> : <Navigate to="/auth" />}
              />
              <Route
                path="/analytics"
                element={currentUser ? <AnalyticsDashboard /> : <Navigate to="/auth" />}
              />
              <Route
                path="/settings"
                element={currentUser ? <SystemSettings /> : <Navigate to="/auth" />}
              />
              <Route
                path="/certificates"
                element={currentUser ? <CertificateManagement /> : <Navigate to="/auth" />}
              />
              <Route
                path="/ai-questions"
                element={currentUser ? <AIQuestionGenerator /> : <Navigate to="/auth" />}
              />
              <Route
                path="/payment"
                element={currentUser ? <UPIPayment amount={500} onSuccess={() => {}} onCancel={() => {}} /> : <Navigate to="/auth" />}
              />



              {/* Catch all route */}
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </Suspense>
        </Box>
      </Router>
      </SplashProvider>

      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />

      {/* User Feedback System */}
      <UserFeedbackSystem />
    </ThemeProvider>
  );
};

export default App;
