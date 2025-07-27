import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  Avatar,
  Divider
} from '@mui/material';
import {
  School as AcademicCapIcon,
  BarChart as ChartBarIcon,
  Description as DocumentTextIcon,
  Person as UserIcon,
  Schedule as ClockIcon,
  EmojiEvents as TrophyIcon,
  Warning as ExclamationTriangleIcon
} from '@mui/icons-material';

// Import splash screen components
import PageSplashScreen from './PageSplashScreen';
import { useRouteSplashScreen } from '../hooks/useSplashScreen';

interface StudentStats {
  total_exams_registered: number;
  exams_completed: number;
  average_score: number;
  certificates_earned: number;
  current_rank: number;
  improvement_percentage: number;
}

interface ExamRegistration {
  id: string;
  exam_name: string;
  exam_date: string;
  exam_time: string;
  status: string;
  score?: number;
  result?: string;
  certificate_available: boolean;
}

interface StudentProfile {
  student_id: string;
  name: string;
  class_level: string;
  section: string;
  institute_name: string;
  email: string;
  phone?: string;
  guardian_email?: string;
}

const StudentDashboard: React.FC = () => {
  const [stats, setStats] = useState<StudentStats | null>(null);
  const [recentExams, setRecentExams] = useState<ExamRegistration[]>([]);
  const [upcomingExams, setUpcomingExams] = useState<ExamRegistration[]>([]);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Page splash screen
  const splash = useRouteSplashScreen('student-dashboard', 2000);
  const [activeTab, setActiveTab] = useState<'overview' | 'exams' | 'results' | 'profile'>('overview');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch dashboard data
      const dashboardResponse = await fetch('/api/v1/student/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const dashboardData = await dashboardResponse.json();
      
      if (dashboardData.status === 'success') {
        setStats(dashboardData.data.statistics);
        setRecentExams(dashboardData.data.recent_exams);
        setUpcomingExams(dashboardData.data.upcoming_exams);
        setProfile(dashboardData.data.student_info);
      }
    } catch (error) {
      // Handle dashboard data fetch error in production
      setError('Failed to load dashboard data. Please refresh the page.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'registered': return 'text-blue-600 bg-blue-100';
      case 'upcoming': return 'text-yellow-600 bg-yellow-100';
      case 'missed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getResultColor = (result: string) => {
    switch (result?.toLowerCase()) {
      case 'pass': return 'text-green-600';
      case 'fail': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  // Show splash screen on first visit to dashboard
  if (splash.isVisible) {
    return (
      <PageSplashScreen
        title="Student Dashboard"
        subtitle="Your Learning Journey Awaits"
        icon={<AcademicCapIcon sx={{ fontSize: 32 }} />}
        color="#1976d2"
        onComplete={splash.hide}
      />
    );
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, bgcolor: 'background.default', minHeight: '100vh' }}>
      {/* Header */}
      <Paper elevation={1} sx={{ mb: 3 }}>
        <Box sx={{ maxWidth: 1200, mx: 'auto', px: 3, py: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
                Student Dashboard
              </Typography>
              {profile && (
                <Typography variant="body2" color="text.secondary">
                  Welcome back, {profile.name} - {profile.class_level} {profile.section}
                </Typography>
              )}
            </Box>
            <Box display="flex" alignItems="center">
              <Typography variant="body2" color="text.secondary">
                {profile?.institute_name}
              </Typography>
            </Box>
          </Box>
        </Box>
      </Paper>

      {/* Navigation Tabs */}
      <Box sx={{ maxWidth: 1200, mx: 'auto', px: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab
            value="overview"
            label="Overview"
            icon={<ChartBarIcon />}
            iconPosition="start"
          />
          <Tab
            value="exams"
            label="My Exams"
            icon={<DocumentTextIcon />}
            iconPosition="start"
          />
          <Tab
            value="results"
            label="Results"
            icon={<TrophyIcon />}
            iconPosition="start"
          />
          <Tab
            value="profile"
            label="Profile"
            icon={<UserIcon />}
            iconPosition="start"
          />
        </Tabs>
      </Box>

      <Box sx={{ maxWidth: 1200, mx: 'auto', px: 3, py: 3 }}>
        {/* Overview Tab */}
        {activeTab === 'overview' && stats && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Stats Cards */}
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center">
                      <DocumentTextIcon sx={{ fontSize: 32, color: 'primary.main', mr: 2 }} />
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Total Exams
                        </Typography>
                        <Typography variant="h4" component="div">
                          {stats.total_exams_registered}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center">
                      <AcademicCapIcon sx={{ fontSize: 32, color: 'success.main', mr: 2 }} />
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Completed
                        </Typography>
                        <Typography variant="h4" component="div">
                          {stats.exams_completed}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center">
                      <ChartBarIcon sx={{ fontSize: 32, color: 'secondary.main', mr: 2 }} />
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Average Score
                        </Typography>
                        <Typography variant="h4" component="div">
                          {stats.average_score}%
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center">
                      <TrophyIcon sx={{ fontSize: 32, color: 'warning.main', mr: 2 }} />
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Certificates
                        </Typography>
                        <Typography variant="h4" component="div">
                          {stats.certificates_earned}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Recent Activity */}
            <Grid container spacing={3}>
              {/* Recent Exams */}
              <Grid item xs={12} lg={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Recent Exams
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    {recentExams.length > 0 ? (
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {recentExams.slice(0, 5).map((exam) => (
                          <Box key={exam.id} display="flex" justifyContent="space-between" alignItems="center">
                            <Box>
                              <Typography variant="body2" fontWeight="medium">
                                {exam.exam_name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {exam.exam_date}
                              </Typography>
                            </Box>
                            <Box textAlign="right">
                              <Chip
                                label={exam.status}
                                size="small"
                                color={exam.status === 'completed' ? 'success' : 'default'}
                              />
                              {exam.score && (
                                <Typography variant="body2" fontWeight="medium" sx={{ mt: 0.5 }}>
                                  {exam.score}%
                                </Typography>
                              )}
                            </Box>
                          </Box>
                        ))}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary" textAlign="center" sx={{ py: 2 }}>
                        No recent exams
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              {/* Upcoming Exams */}
              <Grid item xs={12} lg={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Upcoming Exams
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    {upcomingExams.length > 0 ? (
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {upcomingExams.slice(0, 5).map((exam) => (
                          <Box key={exam.id} display="flex" justifyContent="space-between" alignItems="center">
                            <Box>
                              <Typography variant="body2" fontWeight="medium">
                                {exam.exam_name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {exam.exam_date} at {exam.exam_time}
                              </Typography>
                            </Box>
                            <ClockIcon sx={{ fontSize: 20, color: 'warning.main' }} />
                          </Box>
                        ))}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary" textAlign="center" sx={{ py: 2 }}>
                        No upcoming exams
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Exams Tab */}
        {activeTab === 'exams' && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                My Exam Registrations
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Exam Name</TableCell>
                      <TableCell>Date & Time</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {[...recentExams, ...upcomingExams].map((exam) => (
                      <TableRow key={exam.id}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {exam.exam_name}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {exam.exam_date} {exam.exam_time && `at ${exam.exam_time}`}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={exam.status}
                            size="small"
                            color={exam.status === 'completed' ? 'success' : exam.status === 'upcoming' ? 'primary' : 'default'}
                          />
                        </TableCell>
                        <TableCell>
                          <Box display="flex" gap={1}>
                            {exam.status === 'upcoming' && (
                              <Button size="small" variant="contained">
                                Take Exam
                              </Button>
                            )}
                            {exam.certificate_available && (
                              <Button size="small" variant="outlined" color="success">
                                Download Certificate
                              </Button>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        )}

        {/* Results Tab */}
        {activeTab === 'results' && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Exam Results
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Exam Name</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Score</TableCell>
                      <TableCell>Result</TableCell>
                      <TableCell>Certificate</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentExams.filter(exam => exam.score !== undefined).map((exam) => (
                      <TableRow key={exam.id}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {exam.exam_name}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {exam.exam_date}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {exam.score}%
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={exam.result?.toUpperCase() || 'N/A'}
                            size="small"
                            color={exam.result === 'pass' ? 'success' : exam.result === 'fail' ? 'error' : 'default'}
                          />
                        </TableCell>
                        <TableCell>
                          {exam.certificate_available ? (
                            <Button size="small" variant="outlined" color="success">
                              Download
                            </Button>
                          ) : (
                            <Typography variant="body2" color="text.disabled">
                              Not Available
                            </Typography>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        )}

        {/* Profile Tab */}
        {activeTab === 'profile' && profile && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Student Profile
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Student ID
                  </Typography>
                  <Typography variant="body1">
                    {profile.student_id}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Full Name
                  </Typography>
                  <Typography variant="body1">
                    {profile.name}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Class
                  </Typography>
                  <Typography variant="body1">
                    {profile.class_level} {profile.section}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Institute
                  </Typography>
                  <Typography variant="body1">
                    {profile.institute_name}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Email
                  </Typography>
                  <Typography variant="body1">
                    {profile.email}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Phone
                  </Typography>
                  <Typography variant="body1">
                    {profile.phone || 'Not provided'}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Guardian Email
                  </Typography>
                  <Typography variant="body1">
                    {profile.guardian_email || 'Not provided'}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        )}
      </Box>
    </Box>
  );
};

export default StudentDashboard;
