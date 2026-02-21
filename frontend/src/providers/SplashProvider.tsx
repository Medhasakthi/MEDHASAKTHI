import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useLocation } from 'react-router-dom';
import SplashScreen from '../components/SplashScreen';
import { getSplashConfig, SplashConfig } from '../config/splashConfig';

interface SplashContextType {
  showSplash: (key: string, config?: Partial<SplashConfig>) => void;
  hideSplash: () => void;
  isVisible: boolean;
  currentConfig: SplashConfig | null;
}

const SplashContext = createContext<SplashContextType | undefined>(undefined);

interface SplashProviderProps {
  children: ReactNode;
  enableRouteBasedSplash?: boolean;
  globalSplashDuration?: number;
}

export const SplashProvider: React.FC<SplashProviderProps> = ({
  children,
  enableRouteBasedSplash = false,
  globalSplashDuration = 3000
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [currentConfig, setCurrentConfig] = useState<SplashConfig | null>(null);
  const [splashKey, setSplashKey] = useState<string>('');
  const location = useLocation();

  // Route-based splash screen mapping
  const routeSplashMap: Record<string, string> = {
    '/': 'app',
    '/auth': 'auth',
    '/login': 'auth',
    '/register': 'auth',
    '/student': 'student-dashboard',
    '/student/dashboard': 'student-dashboard',
    '/teacher': 'teacher-dashboard',
    '/teacher/dashboard': 'teacher-dashboard',
    '/admin': 'admin-dashboard',
    '/admin/dashboard': 'admin-dashboard',
    '/independent': 'independent-learner',
    '/independent/dashboard': 'independent-learner',
    '/exams': 'exam-management',
    '/exam-management': 'exam-management',
    '/analytics': 'analytics-dashboard',
    '/institute': 'institute-management',
    '/certificates': 'certificate-management',
    '/ai-questions': 'ai-question-generator',
    '/settings': 'system-settings',
    '/feedback': 'user-feedback',
    '/payments': 'payment-system'
  };

  // Show splash screen based on route
  useEffect(() => {
    if (enableRouteBasedSplash) {
      const currentPath = location.pathname;
      const splashConfigKey = routeSplashMap[currentPath] || 'app';
      
      // Check if we should show splash for this route
      const storageKey = `medhasakthi_splash_${splashConfigKey}`;
      const hasShown = localStorage.getItem(storageKey);
      
      if (!hasShown) {
        showSplash(splashConfigKey);
      }
    }
  }, [location.pathname, enableRouteBasedSplash]);

  const showSplash = (key: string, customConfig?: Partial<SplashConfig>) => {
    const baseConfig = getSplashConfig(key);
    const finalConfig = { ...baseConfig, ...customConfig };
    
    setCurrentConfig(finalConfig);
    setSplashKey(key);
    setIsVisible(true);

    // Auto-hide after duration (if duration > 0)
    if (finalConfig.duration > 0) {
      setTimeout(() => {
        hideSplash();
      }, finalConfig.duration);
    }
  };

  const hideSplash = () => {
    setIsVisible(false);
    
    // Mark as shown in localStorage
    if (splashKey) {
      const storageKey = `medhasakthi_splash_${splashKey}`;
      localStorage.setItem(storageKey, 'true');
    }
    
    // Clear config after animation
    setTimeout(() => {
      setCurrentConfig(null);
      setSplashKey('');
    }, 500);
  };

  const contextValue: SplashContextType = {
    showSplash,
    hideSplash,
    isVisible,
    currentConfig
  };

  return (
    <SplashContext.Provider value={contextValue}>
      {children}
      
      {/* Global Splash Screen Overlay */}
      {isVisible && currentConfig && (
        <SplashScreen
          title={currentConfig.title}
          subtitle={currentConfig.subtitle}
          variant={currentConfig.variant}
          showProgress={currentConfig.showProgress}
          duration={currentConfig.duration}
          onComplete={hideSplash}
        />
      )}
    </SplashContext.Provider>
  );
};

// Hook to use splash context
export const useSplashContext = (): SplashContextType => {
  const context = useContext(SplashContext);
  if (!context) {
    throw new Error('useSplashContext must be used within a SplashProvider');
  }
  return context;
};

// Higher-order component for automatic splash screens
export const withSplash = <P extends object>(
  Component: React.ComponentType<P>,
  splashKey: string,
  customConfig?: Partial<SplashConfig>
) => {
  return (props: P) => {
    const { showSplash } = useSplashContext();
    const [hasShown, setHasShown] = useState(false);

    useEffect(() => {
      const storageKey = `medhasakthi_splash_${splashKey}`;
      const shown = localStorage.getItem(storageKey);
      
      if (!shown && !hasShown) {
        showSplash(splashKey, customConfig);
        setHasShown(true);
      }
    }, [showSplash, splashKey, hasShown]);

    return <Component {...props} />;
  };
};

// Utility functions for manual splash control
export const splashUtils = {
  // Show splash for specific page
  showPageSplash: (key: string, config?: Partial<SplashConfig>) => {
    const event = new CustomEvent('show-splash', { 
      detail: { key, config } 
    });
    window.dispatchEvent(event);
  },

  // Hide current splash
  hideSplash: () => {
    const event = new CustomEvent('hide-splash');
    window.dispatchEvent(event);
  },

  // Reset splash for specific key (will show again)
  resetSplash: (key: string) => {
    const storageKey = `medhasakthi_splash_${key}`;
    localStorage.removeItem(storageKey);
  },

  // Reset all splashes
  resetAllSplashes: () => {
    const keys = Object.keys(localStorage).filter(key => 
      key.startsWith('medhasakthi_splash_')
    );
    keys.forEach(key => localStorage.removeItem(key));
  },

  // Check if splash has been shown
  hasSplashBeenShown: (key: string): boolean => {
    const storageKey = `medhasakthi_splash_${key}`;
    return !!localStorage.getItem(storageKey);
  }
};

export default SplashProvider;
