import React from 'react';
import { Box, Typography, Fade } from '@mui/material';
import { motion } from 'framer-motion';

interface PageSplashScreenProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  color?: string;
  duration?: number;
  onComplete?: () => void;
}

const PageSplashScreen: React.FC<PageSplashScreenProps> = ({
  title,
  subtitle,
  icon,
  color = '#1976d2',
  duration = 1500,
  onComplete
}) => {
  React.useEffect(() => {
    if (onComplete) {
      const timer = setTimeout(onComplete, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onComplete]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `linear-gradient(135deg, ${color} 0%, ${color}dd 100%)`,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
        }}
      >
        {/* Logo */}
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: "spring", stiffness: 260, damping: 20 }}
        >
          <Box
            sx={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              background: 'rgba(255, 255, 255, 0.2)',
              backdropFilter: 'blur(10px)',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 2,
            }}
          >
            {icon || (
              <Typography
                variant="h3"
                sx={{
                  color: 'white',
                  fontWeight: 'bold',
                }}
              >
                M
              </Typography>
            )}
          </Box>
        </motion.div>

        {/* Title */}
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <Typography
            variant="h4"
            sx={{
              color: 'white',
              fontWeight: 'bold',
              textAlign: 'center',
              mb: 1,
            }}
          >
            {title}
          </Typography>
        </motion.div>

        {/* Subtitle */}
        {subtitle && (
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.6 }}
          >
            <Typography
              variant="body1"
              sx={{
                color: 'rgba(255, 255, 255, 0.9)',
                textAlign: 'center',
              }}
            >
              {subtitle}
            </Typography>
          </motion.div>
        )}
      </Box>
    </motion.div>
  );
};

export default PageSplashScreen;
