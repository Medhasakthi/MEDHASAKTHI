import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
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
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Slider,
  Switch,
  FormControlLabel,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Analytics as AnalyticsIcon,
  PieChart as PieChartIcon,
  BarChart as BarChartIcon,
  Timeline as TimelineIcon,
  Insights as InsightsIcon,
  Psychology as PsychologyIcon,
  Speed as SpeedIcon,
  GpsFixed as TargetIcon,
  MonetizationOn as MoneyIcon,
  School as SchoolIcon,
  Group as GroupIcon,
  Assessment as AssessmentIcon,
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  Visibility as VisibilityIcon,
  Warning as WarningIcon,
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
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Treemap,
  FunnelChart,
  Funnel,
  LabelList
} from 'recharts';

interface BusinessMetrics {
  revenue: {
    total: number;
    growth: number;
    forecast: number[];
    breakdown: any[];
  };
  users: {
    total: number;
    active: number;
    retention: number;
    acquisition: any[];
  };
  performance: {
    examCompletion: number;
    averageScore: number;
    satisfaction: number;
    trends: any[];
  };
  predictions: {
    revenueNext30Days: number;
    userGrowthNext30Days: number;
    riskFactors: any[];
    opportunities: any[];
  };
}

interface AIInsight {
  id: string;
  type: 'opportunity' | 'risk' | 'trend' | 'anomaly';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  confidence: number;
  actionable: boolean;
  recommendations: string[];
}

const AdvancedBusinessIntelligence: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');
  const [metrics, setMetrics] = useState<BusinessMetrics | null>(null);
  const [aiInsights, setAiInsights] = useState<AIInsight[]>([]);
  const [predictiveModel, setPredictiveModel] = useState('revenue');
  const [alertThreshold, setAlertThreshold] = useState(80);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadBusinessIntelligence();
    if (autoRefresh) {
      const interval = setInterval(loadBusinessIntelligence, 300000); // 5 minutes
      return () => clearInterval(interval);
    }
  }, [timeRange, autoRefresh]);

  const loadBusinessIntelligence = async () => {
    try {
      setLoading(true);
      
      // Load comprehensive business metrics
      const metricsResponse = await fetch(`/api/v1/admin/business-intelligence?range=${timeRange}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const metricsData = await metricsResponse.json();
      setMetrics(metricsData);

      // Load AI-powered insights
      const insightsResponse = await fetch('/api/v1/admin/ai-insights', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const insightsData = await insightsResponse.json();
      setAiInsights(insightsData);

    } catch (error) {
      console.error('Error loading business intelligence:', error);
    } finally {
      setLoading(false);
    }
  };

  const KPICard: React.FC<{ 
    title: string; 
    value: string | number; 
    change: number;
    icon: React.ReactNode; 
    color: string;
    prediction?: number;
  }> = ({ title, value, change, icon, color, prediction }) => (
    <motion.div whileHover={{ scale: 1.02 }}>
      <Card sx={{ height: '100%', position: 'relative', overflow: 'hidden' }}>
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            right: 0,
            width: 100,
            height: 100,
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
              {prediction && (
                <Typography variant="caption" color="textSecondary">
                  Predicted: {prediction}% next month
                </Typography>
              )}
            </Box>
            <Avatar sx={{ bgcolor: color, width: 64, height: 64 }}>
              {icon}
            </Avatar>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  const AIInsightCard: React.FC<{ insight: AIInsight }> = ({ insight }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" alignItems="start" justifyContent="space-between">
            <Box flex={1}>
              <Box display="flex" alignItems="center" mb={1}>
                <PsychologyIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6" fontWeight="bold">
                  {insight.title}
                </Typography>
                <Chip 
                  label={insight.type} 
                  size="small" 
                  color={insight.type === 'opportunity' ? 'success' : insight.type === 'risk' ? 'error' : 'info'}
                  sx={{ ml: 1 }}
                />
              </Box>
              
              <Typography variant="body2" color="textSecondary" paragraph>
                {insight.description}
              </Typography>
              
              <Box display="flex" alignItems="center" mb={2}>
                <Typography variant="body2" sx={{ mr: 2 }}>
                  <strong>Impact:</strong> {insight.impact}
                </Typography>
                <Typography variant="body2" sx={{ mr: 2 }}>
                  <strong>Confidence:</strong> {insight.confidence}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={insight.confidence} 
                  sx={{ width: 100, ml: 1 }}
                />
              </Box>
              
              {insight.actionable && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="body2" fontWeight="bold">
                      Recommended Actions ({insight.recommendations.length})
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    {insight.recommendations.map((rec, index) => (
                      <Box key={index} display="flex" alignItems="center" mb={1}>
                        <CheckCircleIcon color="success" fontSize="small" sx={{ mr: 1 }} />
                        <Typography variant="body2">{rec}</Typography>
                      </Box>
                    ))}
                  </AccordionDetails>
                </Accordion>
              )}
            </Box>
            
            <Box textAlign="center">
              <Avatar 
                sx={{ 
                  bgcolor: insight.impact === 'high' ? 'error.main' : 
                           insight.impact === 'medium' ? 'warning.main' : 'info.main',
                  width: 48,
                  height: 48
                }}
              >
                {insight.impact === 'high' ? <WarningIcon /> : 
                 insight.impact === 'medium' ? <InsightsIcon /> : <CheckCircleIcon />}
              </Avatar>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  const PredictiveChart: React.FC<{ data: any[]; type: string }> = ({ data, type }) => (
    <ResponsiveContainer width="100%" height={300}>
      {type === 'revenue' ? (
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <RechartsTooltip />
          <Legend />
          <Area 
            type="monotone" 
            dataKey="actual" 
            stroke="#1976d2" 
            fill="#1976d220" 
            name="Actual"
          />
          <Area 
            type="monotone" 
            dataKey="predicted" 
            stroke="#ff9800" 
            fill="#ff980220" 
            strokeDasharray="5 5"
            name="Predicted"
          />
        </AreaChart>
      ) : (
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <RechartsTooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="actual" 
            stroke="#2e7d32" 
            strokeWidth={2}
            name="Actual"
          />
          <Line 
            type="monotone" 
            dataKey="predicted" 
            stroke="#ed6c02" 
            strokeWidth={2}
            strokeDasharray="5 5"
            name="Predicted"
          />
        </LineChart>
      )}
    </ResponsiveContainer>
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
            Advanced Business Intelligence
          </Typography>
          <Typography variant="body1" color="textSecondary">
            AI-powered insights and predictive analytics for strategic decision making
          </Typography>
        </Box>
        <Box display="flex" gap={2} alignItems="center">
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
            }
            label="Auto Refresh"
          />
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
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
            onClick={loadBusinessIntelligence}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
          >
            Export Report
          </Button>
        </Box>
      </Box>

      {/* AI Insights Alert */}
      {aiInsights.filter(i => i.impact === 'high').length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>{aiInsights.filter(i => i.impact === 'high').length} high-impact insights</strong> require your attention. 
            Review the AI recommendations below.
          </Typography>
        </Alert>
      )}

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Total Revenue"
            value={`₹${metrics?.revenue.total.toLocaleString() || '0'}`}
            change={metrics?.revenue.growth || 0}
            icon={<MoneyIcon />}
            color="#2e7d32"
            prediction={15}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Active Users"
            value={metrics?.users.active.toLocaleString() || '0'}
            change={12}
            icon={<GroupIcon />}
            color="#1976d2"
            prediction={8}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Exam Completion"
            value={`${metrics?.performance.examCompletion || 0}%`}
            change={5}
            icon={<AssessmentIcon />}
            color="#ed6c02"
            prediction={3}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="User Satisfaction"
            value={`${metrics?.performance.satisfaction || 0}%`}
            change={7}
            icon={<SpeedIcon />}
            color="#9c27b0"
            prediction={2}
          />
        </Grid>
      </Grid>

      {/* Tabs */}
      <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Predictive Analytics" icon={<TimelineIcon />} />
        <Tab label="AI Insights" icon={<PsychologyIcon />} />
        <Tab label="Performance Metrics" icon={<AnalyticsIcon />} />
        <Tab label="Risk Analysis" icon={<WarningIcon />} />
      </Tabs>

      {/* Predictive Analytics Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">Predictive Forecasting</Typography>
                  <FormControl size="small">
                    <Select
                      value={predictiveModel}
                      onChange={(e) => setPredictiveModel(e.target.value)}
                    >
                      <MenuItem value="revenue">Revenue Forecast</MenuItem>
                      <MenuItem value="users">User Growth</MenuItem>
                      <MenuItem value="performance">Performance Trends</MenuItem>
                    </Select>
                  </FormControl>
                </Box>
                <PredictiveChart 
                  data={metrics?.revenue.forecast || []} 
                  type={predictiveModel}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Prediction Confidence</Typography>
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" gutterBottom>
                    Revenue Forecast: 87%
                  </Typography>
                  <LinearProgress variant="determinate" value={87} sx={{ height: 8 }} />
                </Box>
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" gutterBottom>
                    User Growth: 92%
                  </Typography>
                  <LinearProgress variant="determinate" value={92} sx={{ height: 8 }} />
                </Box>
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" gutterBottom>
                    Performance: 78%
                  </Typography>
                  <LinearProgress variant="determinate" value={78} sx={{ height: 8 }} />
                </Box>
                
                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    Predictions based on 12 months of historical data using advanced ML models.
                  </Typography>
                </Alert>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* AI Insights Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Typography variant="h6" gutterBottom>
              AI-Powered Business Insights
            </Typography>
            {aiInsights.map((insight) => (
              <AIInsightCard key={insight.id} insight={insight} />
            ))}
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Insight Summary</Typography>
                <Box display="flex" justifyContent="space-between" mb={2}>
                  <Typography variant="body2">High Impact</Typography>
                  <Chip 
                    label={aiInsights.filter(i => i.impact === 'high').length} 
                    color="error" 
                    size="small" 
                  />
                </Box>
                <Box display="flex" justifyContent="space-between" mb={2}>
                  <Typography variant="body2">Medium Impact</Typography>
                  <Chip 
                    label={aiInsights.filter(i => i.impact === 'medium').length} 
                    color="warning" 
                    size="small" 
                  />
                </Box>
                <Box display="flex" justifyContent="space-between" mb={2}>
                  <Typography variant="body2">Low Impact</Typography>
                  <Chip 
                    label={aiInsights.filter(i => i.impact === 'low').length} 
                    color="info" 
                    size="small" 
                  />
                </Box>
                
                <Typography variant="body2" sx={{ mt: 2 }}>
                  <strong>Actionable Insights:</strong> {aiInsights.filter(i => i.actionable).length}
                </Typography>
                
                <Typography variant="body2" sx={{ mt: 1 }}>
                  <strong>Average Confidence:</strong> {Math.round(aiInsights.reduce((sum, i) => sum + i.confidence, 0) / aiInsights.length || 0)}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default AdvancedBusinessIntelligence;
