import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Avatar,
  LinearProgress,
  Chip,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  School as SchoolIcon,
  Quiz as QuizIcon,
  EmojiEvents as TrophyIcon,
  Assignment as AssignmentIcon,
  TrendingUp as TrendingUpIcon,
  Notifications as NotificationsIcon,
  CalendarToday as CalendarIcon,
  PlayArrow as PlayIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';

import DashboardLayout from '../../components/layout/DashboardLayout';
import StatCard from '../../components/dashboard/StatCard';
import QuickActionCard from '../../components/dashboard/QuickActionCard';
import ProgressChart from '../../components/charts/ProgressChart';
import RecentActivityList from '../../components/dashboard/RecentActivityList';
import UpcomingExamsList from '../../components/dashboard/UpcomingExamsList';
import { useAppSelector } from '../../hooks/redux';
import { studentAPI } from '../../services/api/studentAPI';

const StudentDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAppSelector((state) => state.auth);
  const [selectedTimeRange, setSelectedTimeRange] = useState('week');

  // Fetch dashboard data
  const { data: dashboardData, isLoading } = useQuery(
    ['studentDashboard', selectedTimeRange],
    () => studentAPI.getDashboardData(selectedTimeRange),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  const { data: upcomingExams } = useQuery(
    'upcomingExams',
    () => studentAPI.getUpcomingExams(),
    {
      refetchInterval: 60000, // Refresh every minute
    }
  );

  const { data: recentActivity } = useQuery(
    'recentActivity',
    () => studentAPI.getRecentActivity(),
    {
      refetchInterval: 30000,
    }
  );

  const { data: subjectProgress } = useQuery(
    'subjectProgress',
    () => studentAPI.getSubjectProgress(),
    {
      refetchInterval: 300000, // Refresh every 5 minutes
    }
  );

  const stats = dashboardData?.stats || {};
  const performance = dashboardData?.performance || {};

  const quickActions = [
    {
      title: 'Take Practice Test',
      description: 'Improve your skills with practice questions',
      icon: <QuizIcon />,
      color: 'primary',
      action: () => navigate('/practice'),
    },
    {
      title: 'View Upcoming Exams',
      description: 'Check your scheduled talent exams',
      icon: <CalendarIcon />,
      color: 'secondary',
      action: () => navigate('/exams'),
    },
    {
      title: 'Study Materials',
      description: 'Access subject-wise study resources',
      icon: <SchoolIcon />,
      color: 'success',
      action: () => navigate('/study-materials'),
    },
    {
      title: 'View Results',
      description: 'Check your exam results and certificates',
      icon: <TrophyIcon />,
      color: 'warning',
      action: () => navigate('/results'),
    },
  ];

  return (
    <DashboardLayout title="Student Dashboard">
      <Box sx={{ flexGrow: 1, p: 3 }}>
        {/* Welcome Section */}
        <Paper sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
          <Box display="flex" alignItems="center" color="white">
            <Avatar
              src={user?.profile_picture}
              sx={{ width: 80, height: 80, mr: 3 }}
            >
              {user?.full_name?.charAt(0)}
            </Avatar>
            <Box>
              <Typography variant="h4" gutterBottom>
                Welcome back, {user?.full_name?.split(' ')[0]}!
              </Typography>
              <Typography variant="h6" sx={{ opacity: 0.9 }}>
                Ready to excel in your talent exams today?
              </Typography>
              <Box mt={2}>
                <Chip
                  label={`Class ${stats.current_class || 'N/A'}`}
                  sx={{ mr: 1, bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                />
                <Chip
                  label={`${stats.institute_name || 'Independent'}`}
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                />
              </Box>
            </Box>
          </Box>
        </Paper>

        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Exams Taken"
              value={stats.exams_taken || 0}
              icon={<AssignmentIcon />}
              color="primary"
              trend={stats.exams_trend}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Average Score"
              value={`${stats.average_score || 0}%`}
              icon={<TrendingUpIcon />}
              color="success"
              trend={stats.score_trend}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Certificates Earned"
              value={stats.certificates_earned || 0}
              icon={<TrophyIcon />}
              color="warning"
              trend={stats.certificates_trend}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Study Hours"
              value={`${stats.study_hours || 0}h`}
              icon={<SchoolIcon />}
              color="info"
              trend={stats.study_trend}
            />
          </Grid>
        </Grid>

        {/* Quick Actions */}
        <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
          Quick Actions
        </Typography>
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {quickActions.map((action, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <QuickActionCard {...action} />
            </Grid>
          ))}
        </Grid>

        {/* Main Content Grid */}
        <Grid container spacing={3}>
          {/* Performance Chart */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">Performance Overview</Typography>
                  <Box>
                    {['week', 'month', 'quarter'].map((range) => (
                      <Button
                        key={range}
                        size="small"
                        variant={selectedTimeRange === range ? 'contained' : 'outlined'}
                        onClick={() => setSelectedTimeRange(range)}
                        sx={{ ml: 1 }}
                      >
                        {range.charAt(0).toUpperCase() + range.slice(1)}
                      </Button>
                    ))}
                  </Box>
                </Box>
                <ProgressChart
                  data={performance.chart_data || []}
                  height={300}
                  isLoading={isLoading}
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Subject Progress */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Subject Progress
                </Typography>
                <Box>
                  {subjectProgress?.subjects?.map((subject: any, index: number) => (
                    <Box key={index} sx={{ mb: 2 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2" color="textSecondary">
                          {subject.name}
                        </Typography>
                        <Typography variant="body2" fontWeight="bold">
                          {subject.progress}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={subject.progress}
                        sx={{
                          mt: 0.5,
                          height: 8,
                          borderRadius: 4,
                          bgcolor: 'grey.200',
                          '& .MuiLinearProgress-bar': {
                            borderRadius: 4,
                            bgcolor: subject.color || 'primary.main',
                          },
                        }}
                      />
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Upcoming Exams */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Upcoming Exams
                </Typography>
                <UpcomingExamsList
                  exams={upcomingExams?.exams || []}
                  onRegister={(examId) => navigate(`/exams/${examId}/register`)}
                  onViewDetails={(examId) => navigate(`/exams/${examId}`)}
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Recent Activity */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Activity
                </Typography>
                <RecentActivityList
                  activities={recentActivity?.activities || []}
                  maxItems={5}
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Study Recommendations */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Personalized Study Recommendations
                </Typography>
                <Grid container spacing={2}>
                  {dashboardData?.recommendations?.map((rec: any, index: number) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                      <Paper
                        sx={{
                          p: 2,
                          border: '1px solid',
                          borderColor: 'divider',
                          borderRadius: 2,
                          cursor: 'pointer',
                          '&:hover': {
                            bgcolor: 'action.hover',
                          },
                        }}
                        onClick={() => navigate(rec.link)}
                      >
                        <Box display="flex" alignItems="center" mb={1}>
                          <AssessmentIcon color="primary" sx={{ mr: 1 }} />
                          <Typography variant="subtitle2" fontWeight="bold">
                            {rec.title}
                          </Typography>
                        </Box>
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          {rec.description}
                        </Typography>
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Chip
                            label={rec.priority}
                            size="small"
                            color={rec.priority === 'High' ? 'error' : rec.priority === 'Medium' ? 'warning' : 'default'}
                          />
                          <Button size="small" endIcon={<PlayIcon />}>
                            Start
                          </Button>
                        </Box>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </DashboardLayout>
  );
};

export default StudentDashboard;
