import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Alert,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Speed as SpeedIcon,
  Computer as ServerIcon,
  NetworkCheck as NetworkIcon,
  Timer as TimerIcon,
  Error as ErrorIcon,
  CheckCircle as SuccessIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';

interface ServerMetrics {
  id: number;
  hostname: string;
  ip_address: string;
  server_type: string;
  status: string;
  health_status: string;
  response_time_ms: number;
  cpu_usage_percent: number;
  memory_usage_percent: number;
  requests_per_second: number;
  error_rate_percent: number;
  uptime_percent: number;
  last_updated: string;
}

interface LoadBalancerStats {
  total_requests: number;
  requests_per_second: number;
  average_response_time: number;
  error_rate: number;
  healthy_servers: number;
  total_servers: number;
  traffic_distribution: Array<{
    server: string;
    requests: number;
    percentage: number;
  }>;
}

const LoadBalancerDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<ServerMetrics[]>([]);
  const [stats, setStats] = useState<LoadBalancerStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [timeRange, setTimeRange] = useState('1h');

  // Sample data for demonstration
  const [performanceData, setPerformanceData] = useState([
    { time: '10:00', requests: 120, response_time: 45, errors: 2 },
    { time: '10:05', requests: 135, response_time: 52, errors: 1 },
    { time: '10:10', requests: 148, response_time: 38, errors: 3 },
    { time: '10:15', requests: 162, response_time: 41, errors: 1 },
    { time: '10:20', requests: 178, response_time: 47, errors: 2 },
    { time: '10:25', requests: 195, response_time: 43, errors: 0 },
  ]);

  useEffect(() => {
    loadMetrics();
    
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(loadMetrics, 30000); // Refresh every 30 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, timeRange]);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      
      // Load server metrics
      const metricsResponse = await fetch('/api/v1/load-balancer/status', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (metricsResponse.ok) {
        const data = await metricsResponse.json();
        
        // Transform data to include mock metrics for demonstration
        const transformedMetrics: ServerMetrics[] = data.servers.map((server: any, index: number) => ({
          ...server,
          cpu_usage_percent: Math.floor(Math.random() * 80) + 10,
          memory_usage_percent: Math.floor(Math.random() * 70) + 20,
          requests_per_second: Math.floor(Math.random() * 50) + 10,
          error_rate_percent: Math.floor(Math.random() * 5),
          uptime_percent: Math.floor(Math.random() * 10) + 90,
          last_updated: new Date().toISOString()
        }));
        
        setMetrics(transformedMetrics);
        
        // Calculate aggregate stats
        const totalServers = transformedMetrics.length;
        const healthyServers = transformedMetrics.filter(m => m.health_status === 'healthy').length;
        const avgResponseTime = transformedMetrics.reduce((sum, m) => sum + (m.response_time_ms || 0), 0) / totalServers;
        const totalRPS = transformedMetrics.reduce((sum, m) => sum + m.requests_per_second, 0);
        const avgErrorRate = transformedMetrics.reduce((sum, m) => sum + m.error_rate_percent, 0) / totalServers;
        
        setStats({
          total_requests: totalRPS * 3600, // Estimate hourly requests
          requests_per_second: totalRPS,
          average_response_time: Math.round(avgResponseTime),
          error_rate: Math.round(avgErrorRate * 100) / 100,
          healthy_servers: healthyServers,
          total_servers: totalServers,
          traffic_distribution: transformedMetrics.map(m => ({
            server: m.hostname,
            requests: m.requests_per_second * 60,
            percentage: Math.round((m.requests_per_second / totalRPS) * 100)
          }))
        });
      }
    } catch (error) {
      console.error('Error loading metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return '#4caf50';
      case 'unhealthy': return '#f44336';
      case 'warning': return '#ff9800';
      default: return '#9e9e9e';
    }
  };

  const getUsageColor = (percentage: number) => {
    if (percentage < 50) return 'success';
    if (percentage < 80) return 'warning';
    return 'error';
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Load Balancer Dashboard
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
            }
            label="Auto Refresh"
          />
          <IconButton onClick={loadMetrics} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Key Metrics */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Requests/sec
                    </Typography>
                    <Typography variant="h4" component="div" fontWeight="bold">
                      {stats?.requests_per_second || 0}
                    </Typography>
                  </Box>
                  <SpeedIcon sx={{ fontSize: 40, color: 'primary.main' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Avg Response Time
                    </Typography>
                    <Typography variant="h4" component="div" fontWeight="bold">
                      {stats?.average_response_time || 0}ms
                    </Typography>
                  </Box>
                  <TimerIcon sx={{ fontSize: 40, color: 'info.main' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Error Rate
                    </Typography>
                    <Typography variant="h4" component="div" fontWeight="bold" color="error.main">
                      {stats?.error_rate || 0}%
                    </Typography>
                  </Box>
                  <ErrorIcon sx={{ fontSize: 40, color: 'error.main' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Healthy Servers
                    </Typography>
                    <Typography variant="h4" component="div" fontWeight="bold" color="success.main">
                      {stats?.healthy_servers || 0}/{stats?.total_servers || 0}
                    </Typography>
                  </Box>
                  <SuccessIcon sx={{ fontSize: 40, color: 'success.main' }} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Trends
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <RechartsTooltip />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="requests"
                    stroke="#8884d8"
                    strokeWidth={2}
                    name="Requests"
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="response_time"
                    stroke="#82ca9d"
                    strokeWidth={2}
                    name="Response Time (ms)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Traffic Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={stats?.traffic_distribution || []}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percentage }) => `${name}: ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="percentage"
                  >
                    {(stats?.traffic_distribution || []).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Server Details Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Server Performance Details
          </Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Server</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>CPU Usage</TableCell>
                  <TableCell>Memory Usage</TableCell>
                  <TableCell>RPS</TableCell>
                  <TableCell>Response Time</TableCell>
                  <TableCell>Error Rate</TableCell>
                  <TableCell>Uptime</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {metrics.map((server) => (
                  <TableRow key={server.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {server.hostname}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {server.ip_address}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={server.health_status}
                        size="small"
                        sx={{
                          backgroundColor: getStatusColor(server.health_status),
                          color: 'white'
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          {server.cpu_usage_percent}%
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={server.cpu_usage_percent}
                          color={getUsageColor(server.cpu_usage_percent)}
                          sx={{ mt: 0.5 }}
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          {server.memory_usage_percent}%
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={server.memory_usage_percent}
                          color={getUsageColor(server.memory_usage_percent)}
                          sx={{ mt: 0.5 }}
                        />
                      </Box>
                    </TableCell>
                    <TableCell>{server.requests_per_second}</TableCell>
                    <TableCell>{server.response_time_ms || 'N/A'}ms</TableCell>
                    <TableCell>
                      <Typography
                        color={server.error_rate_percent > 5 ? 'error' : 'textPrimary'}
                      >
                        {server.error_rate_percent}%
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography
                        color={server.uptime_percent > 95 ? 'success.main' : 'warning.main'}
                      >
                        {server.uptime_percent}%
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Health Status Alert */}
      {stats && stats.healthy_servers < stats.total_servers && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          {stats.total_servers - stats.healthy_servers} server(s) are currently unhealthy. 
          Please check the server status and take appropriate action.
        </Alert>
      )}
    </Box>
  );
};

export default LoadBalancerDashboard;
