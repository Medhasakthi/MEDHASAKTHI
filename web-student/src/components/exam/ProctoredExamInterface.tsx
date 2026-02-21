/**
 * Proctored Exam Interface with Real-time Monitoring
 */
'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Videocam,
  VideocamOff,
  Mic,
  MicOff,
  ScreenShare,
  Warning,
  Security,
  Timer,
} from '@mui/icons-material';
import { useTimer } from 'react-timer-hook';
import Webcam from 'react-webcam';

import { apiService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

interface ProctoredExamInterfaceProps {
  examId: string;
  examTitle: string;
  duration: number; // in minutes
  questions: any[];
  onSubmit: (answers: any) => void;
}

interface ProctoringStatus {
  cameraEnabled: boolean;
  microphoneEnabled: boolean;
  screenShareEnabled: boolean;
  fullscreenActive: boolean;
  violationCount: number;
  warnings: string[];
}

export default function ProctoredExamInterface({
  examId,
  examTitle,
  duration,
  questions,
  onSubmit,
}: ProctoredExamInterfaceProps) {
  const { user } = useAuth();
  const webcamRef = useRef<Webcam>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const screenCaptureRef = useRef<MediaStream | null>(null);
  
  const [proctoringStatus, setProctoringStatus] = useState<ProctoringStatus>({
    cameraEnabled: false,
    microphoneEnabled: false,
    screenShareEnabled: false,
    fullscreenActive: false,
    violationCount: 0,
    warnings: [],
  });
  
  const [examStarted, setExamStarted] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<number, any>>({});
  const [showWarningDialog, setShowWarningDialog] = useState(false);
  const [warningMessage, setWarningMessage] = useState('');
  const [examTerminated, setExamTerminated] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Timer setup
  const expiryTimestamp = new Date();
  expiryTimestamp.setMinutes(expiryTimestamp.getMinutes() + duration);
  
  const {
    seconds,
    minutes,
    hours,
    isRunning,
    start,
    pause,
    resume,
    restart,
  } = useTimer({
    expiryTimestamp,
    onExpire: () => handleTimeUp(),
  });

  // Initialize proctoring system
  useEffect(() => {
    initializeProctoring();
    return () => {
      cleanup();
    };
  }, []);

  // Monitor browser events
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden && examStarted) {
        sendBrowserEvent('WINDOW_BLUR', { timestamp: Date.now() });
      }
    };

    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (examStarted) {
        e.preventDefault();
        e.returnValue = 'Are you sure you want to leave the exam?';
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      // Prevent common cheating shortcuts
      if (examStarted) {
        if (
          (e.ctrlKey && (e.key === 'c' || e.key === 'v' || e.key === 'a')) ||
          e.key === 'F12' ||
          (e.ctrlKey && e.shiftKey && e.key === 'I')
        ) {
          e.preventDefault();
          sendBrowserEvent('PROHIBITED_SHORTCUT', { key: e.key, ctrlKey: e.ctrlKey });
        }
      }
    };

    const handleContextMenu = (e: MouseEvent) => {
      if (examStarted) {
        e.preventDefault();
        sendBrowserEvent('RIGHT_CLICK', { timestamp: Date.now() });
      }
    };

    const handleFullscreenChange = () => {
      const isFullscreen = !!document.fullscreenElement;
      setProctoringStatus(prev => ({ ...prev, fullscreenActive: isFullscreen }));
      
      if (!isFullscreen && examStarted) {
        sendBrowserEvent('FULLSCREEN_EXIT', { timestamp: Date.now() });
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('beforeunload', handleBeforeUnload);
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('contextmenu', handleContextMenu);
    document.addEventListener('fullscreenchange', handleFullscreenChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('beforeunload', handleBeforeUnload);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('contextmenu', handleContextMenu);
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, [examStarted]);

  const initializeProctoring = async () => {
    try {
      // Request camera and microphone permissions
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });

      setProctoringStatus(prev => ({
        ...prev,
        cameraEnabled: true,
        microphoneEnabled: true,
      }));

      // Initialize WebSocket connection for real-time monitoring
      const wsUrl = `ws://localhost:8000/ws/proctoring/${examId}`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('Proctoring WebSocket connected');
      };

      wsRef.current.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleProctoringMessage(message);
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      // Start screen capture
      await startScreenCapture();

    } catch (error) {
      console.error('Failed to initialize proctoring:', error);
      alert('Camera and microphone access is required for this exam.');
    }
  };

  const startScreenCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: false,
      });

      screenCaptureRef.current = stream;
      setProctoringStatus(prev => ({ ...prev, screenShareEnabled: true }));

      // Monitor screen capture
      stream.getVideoTracks()[0].addEventListener('ended', () => {
        setProctoringStatus(prev => ({ ...prev, screenShareEnabled: false }));
        sendBrowserEvent('SCREEN_SHARE_STOPPED', { timestamp: Date.now() });
      });

    } catch (error) {
      console.error('Failed to start screen capture:', error);
    }
  };

  const sendBrowserEvent = (eventType: string, eventData: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'BROWSER_EVENT',
        event_type: eventType,
        event_data: eventData,
      }));
    }
  };

  const handleProctoringMessage = (message: any) => {
    switch (message.type) {
      case 'WARNING':
        setWarningMessage(message.message);
        setShowWarningDialog(true);
        setProctoringStatus(prev => ({
          ...prev,
          violationCount: prev.violationCount + 1,
          warnings: [...prev.warnings, message.message],
        }));
        break;

      case 'EXAM_TERMINATED':
        setExamTerminated(true);
        setExamStarted(false);
        pause();
        alert('Exam has been terminated due to multiple violations.');
        break;

      default:
        console.log('Unknown proctoring message:', message);
    }
  };

  const startExam = async () => {
    try {
      // Enter fullscreen mode
      await document.documentElement.requestFullscreen();
      
      // Start the exam
      setExamStarted(true);
      start();
      
      // Start video monitoring
      startVideoMonitoring();
      
    } catch (error) {
      console.error('Failed to start exam:', error);
    }
  };

  const startVideoMonitoring = () => {
    const captureFrame = () => {
      if (webcamRef.current && examStarted) {
        const imageSrc = webcamRef.current.getScreenshot();
        if (imageSrc && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          // Convert base64 to blob and send
          fetch(imageSrc)
            .then(res => res.blob())
            .then(blob => {
              const reader = new FileReader();
              reader.onload = () => {
                wsRef.current?.send(JSON.stringify({
                  type: 'VIDEO_FRAME',
                  data: reader.result,
                }));
              };
              reader.readAsDataURL(blob);
            });
        }
      }
    };

    // Capture frame every 5 seconds
    const interval = setInterval(captureFrame, 5000);
    
    return () => clearInterval(interval);
  };

  const handleAnswerChange = (questionIndex: number, answer: any) => {
    setAnswers(prev => ({
      ...prev,
      [questionIndex]: answer,
    }));
  };

  const handleTimeUp = () => {
    alert('Time is up! Submitting your exam...');
    handleSubmitExam();
  };

  const handleSubmitExam = async () => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    
    try {
      // Submit answers
      await onSubmit(answers);
      
      // End proctoring session
      if (wsRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'END_PROCTORING',
        }));
      }
      
      setExamStarted(false);
      
    } catch (error) {
      console.error('Failed to submit exam:', error);
      alert('Failed to submit exam. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const cleanup = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    
    if (screenCaptureRef.current) {
      screenCaptureRef.current.getTracks().forEach(track => track.stop());
    }
    
    // Exit fullscreen
    if (document.fullscreenElement) {
      document.exitFullscreen();
    }
  };

  const formatTime = (hours: number, minutes: number, seconds: number) => {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  if (examTerminated) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="h6">Exam Terminated</Typography>
          <Typography>
            Your exam has been terminated due to multiple proctoring violations.
            Please contact your instructor for further assistance.
          </Typography>
        </Alert>
      </Box>
    );
  }

  if (!examStarted) {
    return (
      <Box sx={{ p: 4 }}>
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h4" gutterBottom>
            {examTitle}
          </Typography>
          
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Proctored Examination
          </Typography>
          
          <Box sx={{ my: 4 }}>
            <Typography variant="body1" paragraph>
              This is a proctored exam. Your camera, microphone, and screen will be monitored
              throughout the examination period.
            </Typography>
            
            <Typography variant="body2" color="text.secondary" paragraph>
              Duration: {duration} minutes | Questions: {questions.length}
            </Typography>
          </Box>

          {/* Proctoring Status */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Proctoring Status
            </Typography>
            
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mb: 2 }}>
              <Chip
                icon={proctoringStatus.cameraEnabled ? <Videocam /> : <VideocamOff />}
                label="Camera"
                color={proctoringStatus.cameraEnabled ? 'success' : 'error'}
              />
              <Chip
                icon={proctoringStatus.microphoneEnabled ? <Mic /> : <MicOff />}
                label="Microphone"
                color={proctoringStatus.microphoneEnabled ? 'success' : 'error'}
              />
              <Chip
                icon={<ScreenShare />}
                label="Screen Share"
                color={proctoringStatus.screenShareEnabled ? 'success' : 'error'}
              />
            </Box>

            {/* Camera Preview */}
            <Box sx={{ width: 320, height: 240, mx: 'auto', mb: 2 }}>
              <Webcam
                ref={webcamRef}
                audio={false}
                width={320}
                height={240}
                screenshotFormat="image/jpeg"
                style={{ borderRadius: 8 }}
              />
            </Box>
          </Box>

          <Alert severity="warning" sx={{ mb: 4 }}>
            <Typography variant="body2">
              <strong>Important:</strong> Do not switch tabs, leave fullscreen mode, or use
              prohibited shortcuts during the exam. Violations will be recorded and may
              result in exam termination.
            </Typography>
          </Alert>

          <Button
            variant="contained"
            size="large"
            onClick={startExam}
            disabled={!proctoringStatus.cameraEnabled || !proctoringStatus.microphoneEnabled}
            sx={{ px: 4, py: 2 }}
          >
            Start Exam
          </Button>
        </Paper>
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Exam Header */}
      <Paper sx={{ p: 2, borderRadius: 0 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">{examTitle}</Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {/* Timer */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Timer />
              <Typography variant="h6" color={minutes < 10 ? 'error' : 'inherit'}>
                {formatTime(hours, minutes, seconds)}
              </Typography>
            </Box>
            
            {/* Proctoring Indicators */}
            <Tooltip title="Camera Active">
              <IconButton size="small" color="success">
                <Videocam />
              </IconButton>
            </Tooltip>
            
            {proctoringStatus.violationCount > 0 && (
              <Tooltip title={`${proctoringStatus.violationCount} violations`}>
                <IconButton size="small" color="warning">
                  <Warning />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        </Box>
        
        {/* Progress Bar */}
        <LinearProgress
          variant="determinate"
          value={(currentQuestion / questions.length) * 100}
          sx={{ mt: 1 }}
        />
      </Paper>

      {/* Exam Content */}
      <Box sx={{ flex: 1, p: 3, overflow: 'auto' }}>
        {/* Question content would go here */}
        <Typography variant="h6" gutterBottom>
          Question {currentQuestion + 1} of {questions.length}
        </Typography>
        
        {/* Question rendering logic would be implemented here */}
      </Box>

      {/* Navigation */}
      <Paper sx={{ p: 2, borderRadius: 0 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button
            variant="outlined"
            onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
            disabled={currentQuestion === 0}
          >
            Previous
          </Button>
          
          {currentQuestion === questions.length - 1 ? (
            <Button
              variant="contained"
              color="primary"
              onClick={handleSubmitExam}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Exam'}
            </Button>
          ) : (
            <Button
              variant="contained"
              onClick={() => setCurrentQuestion(Math.min(questions.length - 1, currentQuestion + 1))}
            >
              Next
            </Button>
          )}
        </Box>
      </Paper>

      {/* Warning Dialog */}
      <Dialog open={showWarningDialog} onClose={() => setShowWarningDialog(false)}>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Warning color="warning" />
            Proctoring Warning
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography>{warningMessage}</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Violation count: {proctoringStatus.violationCount}/3
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowWarningDialog(false)} variant="contained">
            I Understand
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
