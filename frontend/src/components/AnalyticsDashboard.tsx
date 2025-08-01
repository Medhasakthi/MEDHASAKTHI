import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Avatar,
  LinearProgress,
  CircularProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  People as PeopleIcon,
  School as SchoolIcon,
  Assessment as AssessmentIcon,
  MonetizationOn as MoneyIcon,
  Analytics as AnalyticsIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  DateRange as DateRangeIcon,
  Star as StarIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface AnalyticsData {
  userGrowth: Array<{ date: string; users: number }>;
  revenueData: Array<{ date: string; revenue: number }>;
  examPerformance: Array<{ exam: string; score: number }>;
  categoryDistribution: Array<{ category: string; count: number }>;
  topPerformers: Array<{ name: string; score: number }>;
  recentActivities: Array<{ activity: string; action: string; timestamp: string }>;
  kpis: {
    totalUsers: number;
    totalRevenue: number;
    activeExams: number;
    completionRate: number;
    userGrowthRate: number;
    revenueGrowthRate: number;
  };
}

const AnalyticsDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);

  const loadAnalyticsData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/admin/analytics?range=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setAnalyticsData(data);
    } catch (error) {
      // Handle error silently in production
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    loadAnalyticsData();
  }, [loadAnalyticsData]);

  const KPICard: React.FC<{ 
    title: string; 
    value: string | number; 
    change: number;
    icon: React.ReactNode; 
    color: string;
  }> = ({ title, value, change, icon, color }) => (
    <motion.div whileHover={{ scale: 1.02 }}>
      <Card sx={{ height: '100%', position: 'relative', overflow: 'hidden' }}>
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            right: 0,
            width: 80,
            height: 80,
            background: `linear-gradient(135deg, ${color}20, ${color}40)`,
            borderRadius: '0 0 0 100%'
          }}
        />
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box>
              <Typography color="textSecondary" gutterBottom variant="body2">
                {title}
              </Typography>
              <Typography variant="h4" component="div" fontWeight="bold">
                {value}
              </Typography>
              <Box display="flex" alignItems="center" mt={1}>
                {change > 0 ? (
                  <TrendingUpIcon color="success" fontSize="small" />
                ) : (
                  <TrendingDownIcon color="error" fontSize="small" />
                )}
                <Typography 
                  variant="body2" 
                  color={change > 0 ? 'success.main' : 'error.main'}
                  sx={{ ml: 0.5 }}
                >
                  {change > 0 ? '+' : ''}{change}%
                </Typography>
              </Box>
            </Box>
            <Avatar sx={{ bgcolor: color, width: 56, height: 56 }}>
              {icon}
            </Avatar>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

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
            Analytics Dashboard
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Comprehensive insights and performance metrics
          </Typography>
        </Box>
        <Box display="flex" gap={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              startAdornment={<DateRangeIcon sx={{ mr: 1 }} />}
            >
              <MenuItem value="7d">Last 7 days</MenuItem>
              <MenuItem value="30d">Last 30 days</MenuItem>
              <MenuItem value="90d">Last 3 months</MenuItem>
              <MenuItem value="1y">Last year</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadAnalyticsData}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
          >
            Export
          </Button>
        </Box>
      </Box>

      {/* KPI Cards */}
      <Box
        sx={{
          mb: 4,
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(5, 1fr)'
          },
          gap: 3
        }}
      >
        <KPICard
          title="Total Users"
          value={analyticsData?.kpis.totalUsers.toLocaleString() || '0'}
          change={analyticsData?.kpis.userGrowthRate || 0}
          icon={<PeopleIcon />}
          color="#1976d2"
        />
        <KPICard
          title="Total Revenue"
          value={`₹${analyticsData?.kpis.totalRevenue.toLocaleString() || '0'}`}
          change={analyticsData?.kpis.revenueGrowthRate || 0}
          icon={<MoneyIcon />}
          color="#2e7d32"
        />
        <KPICard
          title="Active Exams"
          value={analyticsData?.kpis.activeExams || 0}
          change={15}
          icon={<AssessmentIcon />}
          color="#ed6c02"
        />
        <KPICard
          title="Completion Rate"
          value={`${analyticsData?.kpis.completionRate || 0}%`}
          change={8}
          icon={<CheckCircleIcon />}
          color="#9c27b0"
        />
        <KPICard
          title="Active Institutes"
          value="125"
          change={12}
          icon={<SchoolIcon />}
          color="#1565c0"
        />
      </Box>

      {/* Tabs */}
      <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Overview" />
        <Tab label="User Analytics" />
        <Tab label="Revenue" />
        <Tab label="Performance" />
      </Tabs>

      {/* Overview Tab */}
      {activeTab === 0 && (
        <Box>
          {/* First row with User Growth Chart and Category Distribution */}
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' },
              gap: 3,
              mb: 3
            }}
          >
            {/* User Growth Chart */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  User Growth Trend
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={analyticsData?.userGrowth || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area
                      type="monotone"
                      dataKey="users"
                      stroke="#1976d2"
                      fill="#1976d220"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Category Distribution */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  User Categories
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analyticsData?.categoryDistribution || []}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label
                    >
                      {(analyticsData?.categoryDistribution || []).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Box>

          {/* Second row with Top Performers and Recent Activities */}
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
              gap: 3
            }}
          >
            {/* Top Performers */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Top Performers
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Student</TableCell>
                        <TableCell>Score</TableCell>
                        <TableCell>Rank</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {(analyticsData?.topPerformers || []).slice(0, 5).map((performer, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Box display="flex" alignItems="center">
                              <Avatar sx={{ width: 32, height: 32, mr: 1 }}>
                                {performer.name?.charAt(0)}
                              </Avatar>
                              {performer.name}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={`${performer.score}%`}
                              color="success"
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Box display="flex" alignItems="center">
                              <StarIcon color="warning" fontSize="small" sx={{ mr: 0.5 }} />
                              #{index + 1}
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>

            {/* Recent Activities */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Activities
                </Typography>
                <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                  {(analyticsData?.recentActivities || []).map((activity, index) => (
                    <Box key={index} display="flex" alignItems="center" mb={2}>
                      <Avatar sx={{ width: 32, height: 32, mr: 2, bgcolor: 'primary.main' }}>
                        <AnalyticsIcon fontSize="small" />
                      </Avatar>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {activity.action}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {activity.timestamp}
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Box>
      )}

      {/* Revenue Tab */}
      {activeTab === 2 && (
        <Box>
          {/* Revenue Analytics Chart */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Revenue Analytics
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={analyticsData?.revenueData || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="revenue" fill="#2e7d32" />
                  <Bar dataKey="target" fill="#81c784" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Revenue Breakdown and Payment Methods */}
          <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Revenue Summary
            </Typography>
            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: { xs: '1fr', md: '1fr 2fr' },
                gap: 3
              }}
            >
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Revenue Breakdown
                </Typography>
                <Box mb={2}>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">UPI Payments</Typography>
                    <Typography variant="body2" fontWeight="bold">₹2,50,000</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={75} sx={{ height: 8 }} />
                </Box>
                <Box mb={2}>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">Subscriptions</Typography>
                    <Typography variant="body2" fontWeight="bold">₹1,80,000</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={60} sx={{ height: 8 }} />
                </Box>
                <Box mb={2}>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">Certifications</Typography>
                    <Typography variant="body2" fontWeight="bold">₹95,000</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={40} sx={{ height: 8 }} />
                </Box>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Payment Methods Performance
                </Typography>
                <Alert severity="success" sx={{ mb: 2 }}>
                  UPI payments have 0% transaction fees, saving ₹15,000 this month!
                </Alert>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Payment Method</TableCell>
                        <TableCell>Transactions</TableCell>
                        <TableCell>Amount</TableCell>
                        <TableCell>Fees Saved</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell>UPI (PhonePe, GPay, etc.)</TableCell>
                        <TableCell>1,250</TableCell>
                        <TableCell>₹3,75,000</TableCell>
                        <TableCell>
                          <Chip label="₹11,250 saved" color="success" size="small" />
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Credit/Debit Cards</TableCell>
                        <TableCell>180</TableCell>
                        <TableCell>₹54,000</TableCell>
                        <TableCell>
                          <Chip label="₹1,620 fees" color="error" size="small" />
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
            </Box>
          </Paper>
        </Box>
      )}

      {/* Performance Tab */}
      {activeTab === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Exam Performance Trends
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={analyticsData?.examPerformance || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="averageScore" stroke="#1976d2" strokeWidth={2} />
                <Line type="monotone" dataKey="completionRate" stroke="#2e7d32" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default AnalyticsDashboard;
