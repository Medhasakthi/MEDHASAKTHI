import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Avatar,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Alert,
  AlertTitle,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  School as SchoolIcon,
  Quiz as QuizIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';

import DashboardLayout from '../../components/layout/DashboardLayout';
import StatCard from '../../components/dashboard/StatCard';
import QuickActionCard from '../../components/dashboard/QuickActionCard';
import SystemHealthCard from '../../components/admin/SystemHealthCard';
import RealtimeChart from '../../components/charts/RealtimeChart';
import { useAppSelector } from '../../hooks/redux';
import { adminAPI } from '../../services/api/adminAPI';

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAppSelector((state) => state.auth);
  const [selectedTimeRange, setSelectedTimeRange] = useState('today');

  // Fetch admin dashboard data
  const { data: dashboardData, isLoading, refetch } = useQuery(
    ['adminDashboard', selectedTimeRange],
    () => adminAPI.getDashboardData(selectedTimeRange),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  const { data: systemHealth } = useQuery(
    'systemHealth',
    () => adminAPI.getSystemHealth(),
    {
      refetchInterval: 10000, // Refresh every 10 seconds
    }
  );

  const { data: recentAlerts } = useQuery(
    'recentAlerts',
    () => adminAPI.getRecentAlerts(),
    {
      refetchInterval: 15000, // Refresh every 15 seconds
    }
  );

  const { data: activeUsers } = useQuery(
    'activeUsers',
    () => adminAPI.getActiveUsers(),
    {
      refetchInterval: 60000, // Refresh every minute
    }
  );

  const stats = dashboardData?.stats || {};
  const performance = dashboardData?.performance || {};

  const quickActions = [
    {
      title: 'User Management',
      description: 'Manage users, roles, and permissions',
      icon: <PeopleIcon />,
      color: 'primary',
      action: () => navigate('/admin/users'),
    },
    {
      title: 'Institute Management',
      description: 'Manage educational institutes',
      icon: <SchoolIcon />,
      color: 'secondary',
      action: () => navigate('/admin/institutes'),
    },
    {
      title: 'Exam Management',
      description: 'Create and manage talent exams',
      icon: <QuizIcon />,
      color: 'success',
      action: () => navigate('/admin/exams'),
    },
    {
      title: 'System Monitoring',
      description: 'Monitor system health and performance',
      icon: <TrendingUpIcon />,
      color: 'warning',
      action: () => navigate('/admin/monitoring'),
    },
  ];

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'warning':
        return 'warning';
      case 'critical':
        return 'error';
      default:
        return 'default';
    }
  };

  const getHealthStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon />;
      case 'warning':
        return <WarningIcon />;
      case 'critical':
        return <ErrorIcon />;
      default:
        return <WarningIcon />;
    }
  };

  return (
    <DashboardLayout title="Admin Dashboard">
      <Box sx={{ flexGrow: 1, p: 3 }}>
        {/* Welcome Section */}
        <Paper sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" color="white">
            <Box display="flex" alignItems="center">
              <Avatar
                src={user?.profile_picture}
                sx={{ width: 80, height: 80, mr: 3 }}
              >
                {user?.full_name?.charAt(0)}
              </Avatar>
              <Box>
                <Typography variant="h4" gutterBottom>
                  Admin Dashboard
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9 }}>
                  Welcome back, {user?.full_name}
                </Typography>
                <Typography variant="body1" sx={{ opacity: 0.8, mt: 1 }}>
                  System Status: {systemHealth?.overall_status === 'healthy' ? '🟢 All Systems Operational' : '🟡 Some Issues Detected'}
                </Typography>
              </Box>
            </Box>
            <Box>
              <IconButton
                onClick={() => refetch()}
                sx={{ color: 'white', bgcolor: 'rgba(255,255,255,0.2)' }}
              >
                <RefreshIcon />
              </IconButton>
            </Box>
          </Box>
        </Paper>

        {/* System Alerts */}
        {recentAlerts?.alerts?.length > 0 && (
          <Box sx={{ mb: 3 }}>
            {recentAlerts.alerts.slice(0, 3).map((alert: any, index: number) => (
              <Alert
                key={index}
                severity={alert.severity}
                sx={{ mb: 1 }}
                action={
                  <Button color="inherit" size="small" onClick={() => navigate('/admin/monitoring')}>
                    View Details
                  </Button>
                }
              >
                <AlertTitle>{alert.title}</AlertTitle>
                {alert.description}
              </Alert>
            ))}
          </Box>
        )}

        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Users"
              value={stats.total_users || 0}
              icon={<PeopleIcon />}
              color="primary"
              trend={stats.users_trend}
              subtitle={`${stats.active_users || 0} active today`}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Institutes"
              value={stats.total_institutes || 0}
              icon={<SchoolIcon />}
              color="secondary"
              trend={stats.institutes_trend}
              subtitle={`${stats.active_institutes || 0} active`}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Exams Conducted"
              value={stats.exams_conducted || 0}
              icon={<QuizIcon />}
              color="success"
              trend={stats.exams_trend}
              subtitle={`${stats.ongoing_exams || 0} ongoing`}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="System Uptime"
              value={`${stats.uptime_percentage || 99.9}%`}
              icon={<TrendingUpIcon />}
              color="info"
              trend={stats.uptime_trend}
              subtitle={`${stats.uptime_days || 0} days`}
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
          {/* System Health Overview */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Health Overview
                </Typography>
                <Grid container spacing={2}>
                  {systemHealth?.services?.map((service: any, index: number) => (
                    <Grid item xs={12} sm={6} key={index}>
                      <SystemHealthCard
                        name={service.name}
                        status={service.status}
                        responseTime={service.response_time}
                        lastCheck={service.last_check}
                      />
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Real-time Metrics */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">Real-time Metrics</Typography>
                  <Box>
                    {['1h', '6h', '24h'].map((range) => (
                      <Button
                        key={range}
                        size="small"
                        variant={selectedTimeRange === range ? 'contained' : 'outlined'}
                        onClick={() => setSelectedTimeRange(range)}
                        sx={{ ml: 1 }}
                      >
                        {range}
                      </Button>
                    ))}
                  </Box>
                </Box>
                <RealtimeChart
                  data={performance.realtime_data || []}
                  height={300}
                  isLoading={isLoading}
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Active Users */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Active Users ({activeUsers?.total || 0})
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>User</TableCell>
                        <TableCell>Role</TableCell>
                        <TableCell>Activity</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {activeUsers?.users?.slice(0, 5).map((user: any, index: number) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Box display="flex" alignItems="center">
                              <Avatar sx={{ width: 32, height: 32, mr: 1 }}>
                                {user.name.charAt(0)}
                              </Avatar>
                              <Box>
                                <Typography variant="body2">{user.name}</Typography>
                                <Typography variant="caption" color="textSecondary">
                                  {user.email}
                                </Typography>
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip label={user.role} size="small" />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">{user.current_activity}</Typography>
                            <Typography variant="caption" color="textSecondary">
                              {user.last_seen}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <IconButton
                              size="small"
                              onClick={() => navigate(`/admin/users/${user.id}`)}
                            >
                              <VisibilityIcon />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                {activeUsers?.total > 5 && (
                  <Box mt={2} textAlign="center">
                    <Button
                      variant="outlined"
                      onClick={() => navigate('/admin/users')}
                    >
                      View All Users
                    </Button>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Recent System Events */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent System Events
                </Typography>
                <Box>
                  {dashboardData?.recent_events?.map((event: any, index: number) => (
                    <Box
                      key={index}
                      display="flex"
                      alignItems="center"
                      py={1}
                      borderBottom={index < dashboardData.recent_events.length - 1 ? 1 : 0}
                      borderColor="divider"
                    >
                      <Box
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          bgcolor: getHealthStatusColor(event.type),
                          mr: 2,
                        }}
                      />
                      <Box flexGrow={1}>
                        <Typography variant="body2">{event.message}</Typography>
                        <Typography variant="caption" color="textSecondary">
                          {event.timestamp}
                        </Typography>
                      </Box>
                      <Chip
                        label={event.type}
                        size="small"
                        color={getHealthStatusColor(event.type) as any}
                        variant="outlined"
                      />
                    </Box>
                  ))}
                </Box>
                <Box mt={2} textAlign="center">
                  <Button
                    variant="outlined"
                    onClick={() => navigate('/admin/monitoring')}
                  >
                    View All Events
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Performance Summary */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance Summary
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">
                        {performance.avg_response_time || 0}ms
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Avg Response Time
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="success.main">
                        {performance.cache_hit_rate || 0}%
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Cache Hit Rate
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="warning.main">
                        {performance.error_rate || 0}%
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Error Rate
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="info.main">
                        {performance.throughput || 0}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Requests/min
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </DashboardLayout>
  );
};

export default AdminDashboard;
