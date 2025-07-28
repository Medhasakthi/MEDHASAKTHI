import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Avatar,
  Tooltip,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Switch,
  FormControlLabel,
  Divider
} from '@mui/material';
import {
  Quiz as QuizIcon,
  Schedule as ScheduleIcon,
  Assessment as AssessmentIcon,
  Analytics as AnalyticsIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  PlayArrow as StartIcon,
  Timer as TimerIcon,
  Group as GroupIcon,
  Security as SecurityIcon,
  Settings as SettingsIcon,
  Assignment as AssignmentIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';

// Import splash screen components
import PageSplashScreen from './PageSplashScreen';
import { useRouteSplashScreen } from '../hooks/useSplashScreen';
import { getSplashConfig } from '../config/splashConfig';

interface Exam {
  id: string;
  title: string;
  description: string;
  subject: string;
  duration: number;
  totalQuestions: number;
  totalMarks: number;
  startTime: string;
  endTime: string;
  status: 'draft' | 'scheduled' | 'active' | 'completed';
  enrolledStudents: number;
  completedStudents: number;
  averageScore: number;
  difficulty: 'easy' | 'medium' | 'hard';
  examType: 'practice' | 'assessment' | 'final' | 'talent';
  proctoring: boolean;
  randomizeQuestions: boolean;
}

const ExamManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [exams, setExams] = useState<Exam[]>([]);
  const [selectedExam, setSelectedExam] = useState<Exam | null>(null);
  const [createDialog, setCreateDialog] = useState(false);

  // Exam management splash screen
  const splashConfig = getSplashConfig('exam-management');
  const splash = useRouteSplashScreen('exam-management', splashConfig.duration);
  const [activeStep, setActiveStep] = useState(0);
  const [newExam, setNewExam] = useState<Partial<Exam>>({
    proctoring: false,
    randomizeQuestions: true
  });

  useEffect(() => {
    loadExamData();
  }, []);

  const loadExamData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/talent-exams', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setExams(data);
    } catch (error) {
      console.error('Error loading exam data:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard: React.FC<{ title: string; value: string | number; icon: React.ReactNode; color: string }> = 
    ({ title, value, icon, color }) => (
    <motion.div whileHover={{ scale: 1.02 }}>
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box>
              <Typography color="textSecondary" gutterBottom variant="body2">
                {title}
              </Typography>
              <Typography variant="h4" component="div" fontWeight="bold">
                {value}
              </Typography>
            </Box>
            <Avatar sx={{ bgcolor: color, width: 48, height: 48 }}>
              {icon}
            </Avatar>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  const ExamCard: React.FC<{ exam: Exam }> = ({ exam }) => (
    <motion.div whileHover={{ scale: 1.02 }}>
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              {exam.title}
            </Typography>
            <Chip label={exam.status} color="primary" size="small" />
          </Box>
          
          <Typography variant="body2" color="textSecondary" mb={2}>
            {exam.description}
          </Typography>

          <Box display="flex" gap={1} mb={2} flexWrap="wrap">
            <Chip label={exam.subject} size="small" />
            <Chip label={exam.difficulty} color="warning" size="small" />
            <Chip label={exam.examType} variant="outlined" size="small" />
          </Box>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: 2,
              mb: 2
            }}
          >
            <Box display="flex" alignItems="center">
              <TimerIcon fontSize="small" sx={{ mr: 1 }} />
              <Typography variant="body2">{exam.duration} min</Typography>
            </Box>
            <Box display="flex" alignItems="center">
              <QuizIcon fontSize="small" sx={{ mr: 1 }} />
              <Typography variant="body2">{exam.totalQuestions} questions</Typography>
            </Box>
            <Box display="flex" alignItems="center">
              <GroupIcon fontSize="small" sx={{ mr: 1 }} />
              <Typography variant="body2">{exam.enrolledStudents} enrolled</Typography>
            </Box>
            <Box display="flex" alignItems="center">
              <AssessmentIcon fontSize="small" sx={{ mr: 1 }} />
              <Typography variant="body2">{exam.totalMarks} marks</Typography>
            </Box>
          </Box>

          {exam.completedStudents > 0 && (
            <Box mb={2}>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="body2">Completion</Typography>
                <Typography variant="body2">
                  {Math.round((exam.completedStudents / exam.enrolledStudents) * 100)}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={(exam.completedStudents / exam.enrolledStudents) * 100}
                sx={{ height: 6, borderRadius: 3 }}
              />
            </Box>
          )}

          <Box display="flex" gap={1} justifyContent="flex-end">
            <Tooltip title="View Details">
              <IconButton size="small">
                <ViewIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Edit">
              <IconButton size="small">
                <EditIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Analytics">
              <IconButton size="small">
                <AnalyticsIcon />
              </IconButton>
            </Tooltip>
            {exam.status === 'draft' && (
              <Tooltip title="Start Exam">
                <IconButton size="small" color="success">
                  <StartIcon />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  const createSteps = [
    'Basic Information',
    'Exam Settings',
    'Questions & Timing',
    'Review & Create'
  ];

  // Show splash screen on first visit to exam management
  if (splash.isVisible) {
    return (
      <PageSplashScreen
        title={splashConfig.title}
        subtitle={splashConfig.subtitle}
        icon={<AssignmentIcon sx={{ fontSize: 32 }} />}
        color={splashConfig.color}
        onComplete={splash.hide}
      />
    );
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Exam Management
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Create, manage, and monitor exams and assessments
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialog(true)}
          size="large"
        >
          Create Exam
        </Button>
      </Box>

      {/* Statistics */}
      <Box
        sx={{
          mb: 4,
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(4, 1fr)'
          },
          gap: 3
        }}
      >
        <StatCard
          title="Total Exams"
          value={exams.length}
          icon={<QuizIcon />}
          color="#1976d2"
        />
        <StatCard
          title="Active Exams"
          value={exams.filter(e => e.status === 'active').length}
          icon={<ScheduleIcon />}
          color="#2e7d32"
        />
        <StatCard
          title="Total Students"
          value={exams.reduce((sum, exam) => sum + exam.enrolledStudents, 0)}
          icon={<GroupIcon />}
          color="#ed6c02"
        />
        <StatCard
          title="Avg Score"
          value={`${Math.round(exams.reduce((sum, exam) => sum + exam.averageScore, 0) / exams.length || 0)}%`}
          icon={<AssessmentIcon />}
          color="#9c27b0"
        />
      </Box>

      {/* Tabs */}
      <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="All Exams" />
        <Tab label="Scheduled" />
        <Tab label="Active" />
        <Tab label="Completed" />
      </Tabs>

      {/* Exams Grid */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(3, 1fr)'
          },
          gap: 3
        }}
      >
        {exams
          .filter(exam => {
            if (activeTab === 0) return true;
            if (activeTab === 1) return exam.status === 'scheduled';
            if (activeTab === 2) return exam.status === 'active';
            if (activeTab === 3) return exam.status === 'completed';
            return true;
          })
          .map((exam) => (
            <ExamCard key={exam.id} exam={exam} />
          ))}
      </Box>

      {/* Create Exam Dialog */}
      <Dialog open={createDialog} onClose={() => setCreateDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Exam</DialogTitle>
        <DialogContent>
          <Stepper activeStep={activeStep} orientation="vertical">
            {createSteps.map((label, index) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
                <StepContent>
                  {index === 0 && (
                    <Box sx={{ mt: 2 }}>
                      <TextField
                        fullWidth
                        label="Exam Title"
                        value={newExam.title || ''}
                        onChange={(e) => setNewExam({ ...newExam, title: e.target.value })}
                        margin="normal"
                      />
                      <TextField
                        fullWidth
                        label="Description"
                        multiline
                        rows={3}
                        value={newExam.description || ''}
                        onChange={(e) => setNewExam({ ...newExam, description: e.target.value })}
                        margin="normal"
                      />
                      <FormControl fullWidth margin="normal">
                        <InputLabel>Subject</InputLabel>
                        <Select
                          value={newExam.subject || ''}
                          onChange={(e) => setNewExam({ ...newExam, subject: e.target.value })}
                        >
                          <MenuItem value="Mathematics">Mathematics</MenuItem>
                          <MenuItem value="Science">Science</MenuItem>
                          <MenuItem value="English">English</MenuItem>
                          <MenuItem value="History">History</MenuItem>
                        </Select>
                      </FormControl>
                    </Box>
                  )}
                  
                  {index === 1 && (
                    <Box sx={{ mt: 2 }}>
                      <FormControl fullWidth margin="normal">
                        <InputLabel>Exam Type</InputLabel>
                        <Select
                          value={newExam.examType || ''}
                          onChange={(e) => setNewExam({ ...newExam, examType: e.target.value as any })}
                        >
                          <MenuItem value="practice">Practice Test</MenuItem>
                          <MenuItem value="assessment">Assessment</MenuItem>
                          <MenuItem value="final">Final Exam</MenuItem>
                          <MenuItem value="talent">Talent Exam</MenuItem>
                        </Select>
                      </FormControl>
                      
                      <FormControl fullWidth margin="normal">
                        <InputLabel>Difficulty</InputLabel>
                        <Select
                          value={newExam.difficulty || ''}
                          onChange={(e) => setNewExam({ ...newExam, difficulty: e.target.value as any })}
                        >
                          <MenuItem value="easy">Easy</MenuItem>
                          <MenuItem value="medium">Medium</MenuItem>
                          <MenuItem value="hard">Hard</MenuItem>
                        </Select>
                      </FormControl>

                      <FormControlLabel
                        control={
                          <Switch
                            checked={newExam.proctoring || false}
                            onChange={(e) => setNewExam({ ...newExam, proctoring: e.target.checked })}
                          />
                        }
                        label="Enable Proctoring"
                      />
                      
                      <FormControlLabel
                        control={
                          <Switch
                            checked={newExam.randomizeQuestions || false}
                            onChange={(e) => setNewExam({ ...newExam, randomizeQuestions: e.target.checked })}
                          />
                        }
                        label="Randomize Questions"
                      />
                    </Box>
                  )}

                  {index === 2 && (
                    <Box sx={{ mt: 2 }}>
                      <TextField
                        fullWidth
                        label="Duration (minutes)"
                        type="number"
                        value={newExam.duration || ''}
                        onChange={(e) => setNewExam({ ...newExam, duration: Number(e.target.value) })}
                        margin="normal"
                      />
                      <TextField
                        fullWidth
                        label="Total Questions"
                        type="number"
                        value={newExam.totalQuestions || ''}
                        onChange={(e) => setNewExam({ ...newExam, totalQuestions: Number(e.target.value) })}
                        margin="normal"
                      />
                      <TextField
                        fullWidth
                        label="Total Marks"
                        type="number"
                        value={newExam.totalMarks || ''}
                        onChange={(e) => setNewExam({ ...newExam, totalMarks: Number(e.target.value) })}
                        margin="normal"
                      />
                    </Box>
                  )}

                  {index === 3 && (
                    <Box sx={{ mt: 2 }}>
                      <Alert severity="info" sx={{ mb: 2 }}>
                        Review your exam settings before creating.
                      </Alert>
                      <Typography variant="h6">{newExam.title}</Typography>
                      <Typography variant="body2" color="textSecondary" paragraph>
                        {newExam.description}
                      </Typography>
                      <Divider sx={{ my: 2 }} />
                      <Box
                        sx={{
                          display: 'grid',
                          gridTemplateColumns: 'repeat(2, 1fr)',
                          gap: 2
                        }}
                      >
                        <Typography variant="body2"><strong>Subject:</strong> {newExam.subject}</Typography>
                        <Typography variant="body2"><strong>Type:</strong> {newExam.examType}</Typography>
                        <Typography variant="body2"><strong>Duration:</strong> {newExam.duration} min</Typography>
                        <Typography variant="body2"><strong>Questions:</strong> {newExam.totalQuestions}</Typography>
                      </Box>
                    </Box>
                  )}

                  <Box sx={{ mb: 2, mt: 2 }}>
                    <Button
                      variant="contained"
                      onClick={() => {
                        if (index === createSteps.length - 1) {
                          // Create exam
                          setCreateDialog(false);
                          setActiveStep(0);
                        } else {
                          setActiveStep(index + 1);
                        }
                      }}
                      sx={{ mt: 1, mr: 1 }}
                    >
                      {index === createSteps.length - 1 ? 'Create Exam' : 'Continue'}
                    </Button>
                    <Button
                      disabled={index === 0}
                      onClick={() => setActiveStep(index - 1)}
                      sx={{ mt: 1, mr: 1 }}
                    >
                      Back
                    </Button>
                  </Box>
                </StepContent>
              </Step>
            ))}
          </Stepper>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialog(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ExamManagement;
