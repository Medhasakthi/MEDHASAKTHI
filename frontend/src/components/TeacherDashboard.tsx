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
  Divider,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  People as UsersIcon,
  School as AcademicCapIcon,
  BarChart as ChartBarIcon,
  MenuBook as BookOpenIcon,
  Schedule as ClockIcon,
  EmojiEvents as TrophyIcon,
  Chat as ChatBubbleLeftRightIcon,
  Description as DocumentTextIcon
} from '@mui/icons-material';

// Import splash screen components
import PageSplashScreen from './PageSplashScreen';
import { useRouteSplashScreen } from '../hooks/useSplashScreen';

interface TeacherStats {
  total_students: number;
  classes_handled: number;
  subjects_taught: number;
  recent_exams: number;
  average_class_performance: number;
  total_messages_sent: number;
}

interface ClassInfo {
  class_id: string;
  class_name: string;
  section: string;
  subject: string;
  total_students: number;
  average_performance: number;
  recent_activity: string;
}

interface StudentPerformance {
  student_id: string;
  student_name: string;
  class_section: string;
  average_score: number;
  total_exams: number;
  last_exam_score?: number;
  improvement_trend: 'up' | 'down' | 'stable';
}

interface TeacherProfile {
  teacher_id: string;
  name: string;
  employee_id: string;
  department: string;
  subjects: string[];
  classes_assigned: string[];
  is_class_teacher: boolean;
  class_teacher_of?: string;
  institute_name: string;
}

const TeacherDashboard: React.FC = () => {
  const [stats, setStats] = useState<TeacherStats | null>(null);
  const [classes, setClasses] = useState<ClassInfo[]>([]);
  const [topPerformers, setTopPerformers] = useState<StudentPerformance[]>([]);
  const [needsAttention, setNeedsAttention] = useState<StudentPerformance[]>([]);
  const [profile, setProfile] = useState<TeacherProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Page splash screen for teacher dashboard
  const splash = useRouteSplashScreen('teacher-dashboard', 2000);
  const [activeTab, setActiveTab] = useState<'overview' | 'classes' | 'students' | 'analytics' | 'profile'>('overview');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch teacher dashboard data
      const dashboardResponse = await fetch('/api/v1/teacher/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const dashboardData = await dashboardResponse.json();
      
      if (dashboardData.status === 'success') {
        setStats(dashboardData.data.statistics);
        setClasses(dashboardData.data.assigned_classes);
        setTopPerformers(dashboardData.data.top_performers);
        setNeedsAttention(dashboardData.data.needs_attention);
        setProfile(dashboardData.data.teacher_info);
      }
    } catch (error) {
      // Handle dashboard data fetch error in production
      setError('Failed to load dashboard data. Please refresh the page.');
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return '📈';
      case 'down': return '📉';
      default: return '➡️';
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up': return 'text-green-600';
      case 'down': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  // Show splash screen on first visit to teacher dashboard
  if (splash.isVisible) {
    return (
      <PageSplashScreen
        title="Teacher Dashboard"
        subtitle="Empowering Education Excellence"
        icon={<AcademicCapIcon sx={{ fontSize: 32 }} />}
        color="#0d47a1"
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
                Teacher Dashboard
              </Typography>
              {profile && (
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography variant="body2" color="text.secondary">
                    Welcome back, {profile.name} - {profile.department}
                  </Typography>
                  {profile.is_class_teacher && profile.class_teacher_of && (
                    <Chip
                      label={`Class Teacher: ${profile.class_teacher_of}`}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  )}
                </Box>
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
            value="classes"
            label="My Classes"
            icon={<AcademicCapIcon />}
            iconPosition="start"
          />
          <Tab
            value="students"
            label="Students"
            icon={<UsersIcon />}
            iconPosition="start"
          />
          <Tab
            value="analytics"
            label="Analytics"
            icon={<DocumentTextIcon />}
            iconPosition="start"
          />
          <Tab
            value="profile"
            label="Profile"
            icon={<BookOpenIcon />}
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
                      <UsersIcon sx={{ fontSize: 32, color: 'primary.main', mr: 2 }} />
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Total Students
                        </Typography>
                        <Typography variant="h4" component="div">
                          {stats.total_students}
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
                          Classes
                        </Typography>
                        <Typography variant="h4" component="div">
                          {stats.classes_handled}
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
                      <BookOpenIcon sx={{ fontSize: 32, color: 'secondary.main', mr: 2 }} />
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Subjects
                        </Typography>
                        <Typography variant="h4" component="div">
                          {stats.subjects_taught}
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
                      <ChartBarIcon sx={{ fontSize: 32, color: 'warning.main', mr: 2 }} />
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Avg Performance
                        </Typography>
                        <Typography variant="h4" component="div">
                          {stats.average_class_performance}%
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Quick Actions */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quick Actions
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <Button
                      variant="outlined"
                      fullWidth
                      startIcon={<ChatBubbleLeftRightIcon />}
                      sx={{ py: 2, justifyContent: 'flex-start' }}
                    >
                      Send Message to Class
                    </Button>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Button
                      variant="outlined"
                      fullWidth
                      startIcon={<DocumentTextIcon />}
                      sx={{ py: 2, justifyContent: 'flex-start' }}
                    >
                      Create Assignment
                    </Button>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Button
                      variant="outlined"
                      fullWidth
                      startIcon={<TrophyIcon />}
                      sx={{ py: 2, justifyContent: 'flex-start' }}
                    >
                      View Results
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Student Performance Overview */}
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 3 }}>
              {/* Top Performers */}
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Top Performers
                  </Typography>
                  <Box>
                  {topPerformers.length > 0 ? (
                    <div className="space-y-4">
                      {topPerformers.slice(0, 5).map((student, index) => (
                        <div key={student.student_id} className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="flex-shrink-0">
                              <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                                <span className="text-sm font-medium text-yellow-800">#{index + 1}</span>
                              </div>
                            </div>
                            <div className="ml-3">
                              <p className="text-sm font-medium text-gray-900">{student.student_name}</p>
                              <p className="text-xs text-gray-500">{student.class_section}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-gray-900">{student.average_score}%</p>
                            <p className={`text-xs ${getTrendColor(student.improvement_trend)}`}>
                              {getTrendIcon(student.improvement_trend)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 2 }}>
                      No performance data available
                    </Typography>
                  )}
                  </Box>
                </CardContent>
              </Card>

              {/* Students Needing Attention */}
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Needs Attention
                  </Typography>
                  <Box>
                  {needsAttention.length > 0 ? (
                    <div className="space-y-4">
                      {needsAttention.slice(0, 5).map((student) => (
                        <div key={student.student_id} className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{student.student_name}</p>
                            <p className="text-xs text-gray-500">{student.class_section}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-red-600">{student.average_score}%</p>
                            <button className="text-xs text-blue-600 hover:text-blue-800">
                              Send Message
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 2 }}>
                      All students performing well!
                    </Typography>
                  )}
                  </Box>
                </CardContent>
              </Card>
            </Box>
          </Box>
        )}

        {/* Classes Tab */}
        {activeTab === 'classes' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {classes.map((classInfo) => (
                <div key={classInfo.class_id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      {classInfo.class_name} {classInfo.section}
                    </h3>
                    <span className="text-sm text-gray-500">{classInfo.subject}</span>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Students:</span>
                      <span className="text-sm font-medium">{classInfo.total_students}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Avg Performance:</span>
                      <span className="text-sm font-medium">{classInfo.average_performance}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Recent Activity:</span>
                      <span className="text-sm text-gray-500">{classInfo.recent_activity}</span>
                    </div>
                  </div>
                  
                  <div className="mt-4 flex space-x-2">
                    <button className="flex-1 bg-blue-600 text-white text-sm py-2 px-3 rounded hover:bg-blue-700">
                      View Details
                    </button>
                    <button className="flex-1 bg-gray-100 text-gray-700 text-sm py-2 px-3 rounded hover:bg-gray-200">
                      Send Message
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Students Tab */}
        {activeTab === 'students' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">All Students</h3>
              <div className="flex space-x-2">
                <input
                  type="text"
                  placeholder="Search students..."
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                />
                <select className="px-3 py-2 border border-gray-300 rounded-md text-sm">
                  <option value="">All Classes</option>
                  {classes.map((cls) => (
                    <option key={cls.class_id} value={cls.class_id}>
                      {cls.class_name} {cls.section}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Student
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Class
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Average Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total Exams
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Trend
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {[...topPerformers, ...needsAttention].map((student) => (
                    <tr key={student.student_id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{student.student_name}</div>
                        <div className="text-sm text-gray-500">{student.student_id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {student.class_section}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {student.average_score}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {student.total_exams}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-sm ${getTrendColor(student.improvement_trend)}`}>
                          {getTrendIcon(student.improvement_trend)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button className="text-blue-600 hover:text-blue-900 mr-4">
                          View Profile
                        </button>
                        <button className="text-green-600 hover:text-green-900">
                          Send Message
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Analytics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Class Performance Trends</h4>
                  <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                    <span className="text-gray-500">Chart will be rendered here</span>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Subject-wise Performance</h4>
                  <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                    <span className="text-gray-500">Chart will be rendered here</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Profile Tab */}
        {activeTab === 'profile' && profile && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Teacher Profile</h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Teacher ID</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.teacher_id}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Employee ID</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.employee_id}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Full Name</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Department</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.department}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Subjects</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.subjects.join(', ')}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Classes Assigned</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.classes_assigned.join(', ')}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Class Teacher</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {profile.is_class_teacher ? `Yes - ${profile.class_teacher_of}` : 'No'}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Institute</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.institute_name}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Other tabs can be implemented similarly */}
        {activeTab !== 'overview' && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {activeTab === 'classes' && 'My Classes'}
                {activeTab === 'students' && 'Students Management'}
                {activeTab === 'analytics' && 'Performance Analytics'}
                {activeTab === 'profile' && 'Teacher Profile'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                This section is under development. Please check back later.
              </Typography>
            </CardContent>
          </Card>
        )}
      </Box>
    </Box>
  );
};

export default TeacherDashboard;
