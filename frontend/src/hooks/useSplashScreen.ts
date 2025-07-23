import { useState, useEffect } from 'react';

interface UseSplashScreenOptions {
  duration?: number;
  showOnFirstVisit?: boolean;
  showOnRouteChange?: boolean;
  minDisplayTime?: number;
  storageKey?: string;
}

interface SplashScreenState {
  isVisible: boolean;
  isLoading: boolean;
  progress: number;
  hide: () => void;
  show: () => void;
  reset: () => void;
}

export const useSplashScreen = (options: UseSplashScreenOptions = {}): SplashScreenState => {
  const {
    duration = 3000,
    showOnFirstVisit = true,
    showOnRouteChange = false,
    minDisplayTime = 1000,
    storageKey = 'medhasakthi_splash_shown'
  } = options;

  const [isVisible, setIsVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [progress, setProgress] = useState(0);
  const [startTime, setStartTime] = useState<number>(0);

  useEffect(() => {
    const shouldShow = () => {
      if (showOnRouteChange) return true;
      
      if (showOnFirstVisit) {
        const hasShown = localStorage.getItem(storageKey);
        return !hasShown;
      }
      
      return true;
    };

    if (shouldShow()) {
      setIsVisible(true);
      setStartTime(Date.now());
      
      // Progress animation
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            clearInterval(progressInterval);
            return 100;
          }
          return prev + (100 / (duration / 100));
        });
      }, 100);

      // Auto-hide after duration
      const hideTimer = setTimeout(() => {
        hide();
      }, duration);

      return () => {
        clearInterval(progressInterval);
        clearTimeout(hideTimer);
      };
    } else {
      setIsLoading(false);
    }
  }, [duration, showOnFirstVisit, showOnRouteChange, storageKey]);

  const hide = () => {
    const elapsed = Date.now() - startTime;
    const remainingTime = Math.max(0, minDisplayTime - elapsed);

    setTimeout(() => {
      setIsVisible(false);
      setIsLoading(false);
      
      if (showOnFirstVisit) {
        localStorage.setItem(storageKey, 'true');
      }
    }, remainingTime);
  };

  const show = () => {
    setIsVisible(true);
    setIsLoading(true);
    setProgress(0);
    setStartTime(Date.now());
  };

  const reset = () => {
    localStorage.removeItem(storageKey);
    setProgress(0);
    show();
  };

  return {
    isVisible,
    isLoading,
    progress,
    hide,
    show,
    reset
  };
};

// Hook for route-based splash screens
export const useRouteSplashScreen = (routeName: string, duration: number = 2000) => {
  return useSplashScreen({
    duration,
    showOnRouteChange: true,
    showOnFirstVisit: false,
    storageKey: `medhasakthi_splash_${routeName}`
  });
};

// Hook for component-level loading splash
export const useLoadingSplash = (isLoading: boolean, minDisplayTime: number = 1000) => {
  const [showSplash, setShowSplash] = useState(isLoading);

  useEffect(() => {
    if (isLoading) {
      setShowSplash(true);
    } else {
      const timer = setTimeout(() => {
        setShowSplash(false);
      }, minDisplayTime);

      return () => clearTimeout(timer);
    }
  }, [isLoading, minDisplayTime]);

  return showSplash;
};
