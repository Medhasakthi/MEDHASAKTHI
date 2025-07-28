import React, { useEffect, useState } from 'react';
import { Box, Typography, CircularProgress, Fade, Zoom } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';

interface SplashScreenProps {
  onComplete?: () => void;
  duration?: number;
  showProgress?: boolean;
  title?: string;
  subtitle?: string;
  variant?: 'default' | 'minimal' | 'loading' | 'auth';
}

const SplashScreen: React.FC<SplashScreenProps> = ({
  onComplete,
  duration = 3000,
  showProgress = true,
  title = 'MEDHASAKTHI',
  subtitle = 'Educational Excellence Platform',
  variant = 'default'
}) => {
  const [progress, setProgress] = useState(0);
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    // Show content after initial delay
    const contentTimer = setTimeout(() => {
      setShowContent(true);
    }, 200);

    // Progress animation
    const progressTimer = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(progressTimer);
          return 100;
        }
        return prev + (100 / (duration / 100));
      });
    }, 100);

    // Auto-complete after duration
    const completeTimer = setTimeout(() => {
      if (onComplete) {
        onComplete();
      }
    }, duration);

    return () => {
      clearTimeout(contentTimer);
      clearTimeout(completeTimer);
      clearInterval(progressTimer);
    };
  }, [duration, onComplete]);

  const getVariantStyles = () => {
    switch (variant) {
      case 'minimal':
        return {
          background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
          minHeight: '200px',
        };
      case 'loading':
        return {
          background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 50%, #1565c0 100%)',
          minHeight: '100vh',
        };
      case 'auth':
        return {
          background: 'linear-gradient(135deg, #0d47a1 0%, #1976d2 50%, #42a5f5 100%)',
          minHeight: '100vh',
        };
      default:
        return {
          background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 50%, #0d47a1 100%)',
          minHeight: '100vh',
        };
    }
  };

  const logoVariants = {
    hidden: { scale: 0, opacity: 0, rotate: -180 },
    visible: { 
      scale: 1, 
      opacity: 1, 
      rotate: 0,
      transition: {
        type: "spring" as const,
        stiffness: 260,
        damping: 20,
        duration: 1.2
      }
    },
    exit: { 
      scale: 0.8, 
      opacity: 0,
      transition: { duration: 0.5 }
    }
  };

  const textVariants = {
    hidden: { y: 50, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        delay: 0.5,
        duration: 0.8,
        ease: [0.17, 0.67, 0.83, 0.67] as const // Type assertion for cubic-bezier array
      }
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: {
        staggerChildren: 0.3
      }
    },
    exit: { 
      opacity: 0,
      transition: { duration: 0.5 }
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial="hidden"
        animate="visible"
        exit="exit"
        variants={containerVariants}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            ...getVariantStyles(),
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* Background Animation */}
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: `
                radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.05) 0%, transparent 50%)
              `,
              animation: 'pulse 4s ease-in-out infinite',
            }}
          />

          {/* Main Content */}
          <Fade in={showContent} timeout={800}>
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                zIndex: 1,
              }}
            >
              {/* Logo */}
              <motion.div variants={logoVariants}>
                <Box
                  sx={{
                    width: { xs: 80, sm: 100, md: 120 },
                    height: { xs: 80, sm: 100, md: 120 },
                    borderRadius: '50%',
                    background: 'rgba(255, 255, 255, 0.1)',
                    backdropFilter: 'blur(10px)',
                    border: '2px solid rgba(255, 255, 255, 0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mb: 3,
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                >
                  {/* Logo placeholder - replace with actual logo */}
                  <Typography
                    variant="h3"
                    sx={{
                      color: 'white',
                      fontWeight: 'bold',
                      fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' },
                    }}
                  >
                    M
                  </Typography>
                  
                  {/* Shimmer effect */}
                  <Box
                    sx={{
                      position: 'absolute',
                      top: '-50%',
                      left: '-50%',
                      width: '200%',
                      height: '200%',
                      background: 'linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.3) 50%, transparent 70%)',
                      animation: 'shimmer 3s ease-in-out infinite',
                    }}
                  />
                </Box>
              </motion.div>

              {/* Title */}
              <motion.div variants={textVariants}>
                <Typography
                  variant="h3"
                  component="h1"
                  sx={{
                    color: 'white',
                    fontWeight: 'bold',
                    textAlign: 'center',
                    mb: 1,
                    fontSize: { xs: '1.8rem', sm: '2.5rem', md: '3rem' },
                    letterSpacing: '0.1em',
                    textShadow: '0 2px 4px rgba(0,0,0,0.3)',
                  }}
                >
                  {title}
                </Typography>
              </motion.div>

              {/* Subtitle */}
              <motion.div variants={textVariants}>
                <Typography
                  variant="h6"
                  sx={{
                    color: 'rgba(255, 255, 255, 0.9)',
                    textAlign: 'center',
                    mb: 4,
                    fontSize: { xs: '0.9rem', sm: '1.1rem', md: '1.25rem' },
                    fontWeight: 300,
                  }}
                >
                  {subtitle}
                </Typography>
              </motion.div>

              {/* Progress Indicator */}
              {showProgress && (
                <motion.div
                  variants={textVariants}
                  style={{ width: '100%', maxWidth: '300px' }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <CircularProgress
                      variant="determinate"
                      value={progress}
                      size={40}
                      thickness={4}
                      sx={{
                        color: 'white',
                        '& .MuiCircularProgress-circle': {
                          strokeLinecap: 'round',
                        },
                      }}
                    />
                    <Typography
                      variant="body2"
                      sx={{
                        color: 'rgba(255, 255, 255, 0.8)',
                        minWidth: '60px',
                      }}
                    >
                      {Math.round(progress)}%
                    </Typography>
                  </Box>
                  
                  {/* Loading text */}
                  <Typography
                    variant="caption"
                    sx={{
                      color: 'rgba(255, 255, 255, 0.7)',
                      textAlign: 'center',
                      display: 'block',
                      mt: 2,
                    }}
                  >
                    Loading your educational experience...
                  </Typography>
                </motion.div>
              )}
            </Box>
          </Fade>

          {/* Floating particles effect */}
          {variant === 'default' && (
            <>
              {[...Array(6)].map((_, i) => (
                <Box
                  key={i}
                  sx={{
                    position: 'absolute',
                    width: '4px',
                    height: '4px',
                    borderRadius: '50%',
                    background: 'rgba(255, 255, 255, 0.6)',
                    animation: `float ${3 + i * 0.5}s ease-in-out infinite`,
                    animationDelay: `${i * 0.5}s`,
                    left: `${20 + i * 15}%`,
                    top: `${30 + (i % 3) * 20}%`,
                  }}
                />
              ))}
            </>
          )}
        </Box>
      </motion.div>

      {/* CSS Animations */}
      <style>
        {`
          @keyframes shimmer {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
          }
          
          @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.7; }
            50% { transform: translateY(-20px) rotate(180deg); opacity: 1; }
          }
          
          @keyframes pulse {
            0%, 100% { opacity: 0.8; }
            50% { opacity: 1; }
          }
        `}
      </style>
    </AnimatePresence>
  );
};

export default SplashScreen;
