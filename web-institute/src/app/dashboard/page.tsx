/**
 * Dashboard Page for Institute Portal
 */
'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  Avatar,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  Psychology,
  Quiz,
  School,
  People,
  AutoAwesome,
  Refresh,
  Visibility,
  Add,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';

import DashboardLayout from '../../components/layout/DashboardLayout';
import { withAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';
import { AIGenerationStats } from '../../types/question';

interface DashboardStats {
  totalStudents: number;
  totalTeachers: number;
  totalQuestions: number;
  totalExams: number;
  aiQuestionsGenerated: number;
  recentActivity: Array<{
    id: string;
    type: string;
    description: string;
    timestamp: string;
    user: string;
  }>;
}

function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats>({
    totalStudents: 0,
    totalTeachers: 0,
    totalQuestions: 0,
    totalExams: 0,
    aiQuestionsGenerated: 0,
    recentActivity: [],
  });
  const [aiStats, setAiStats] = useState<AIGenerationStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Load AI generation stats
      const aiStatsData = await apiService.getGenerationStats();
      setAiStats(aiStatsData);
      
      // Mock other stats for now
      setStats({
        totalStudents: 1250,
        totalTeachers: 45,
        totalQuestions: aiStatsData.total_questions_generated + 150,
        totalExams: 28,
        aiQuestionsGenerated: aiStatsData.total_questions_generated,
        recentActivity: [
          {
            id: '1',
            type: 'question_generated',
            description: 'Generated 5 Math questions using AI',
            timestamp: '2 hours ago',
            user: 'John Smith',
          },
          {
            id: '2',
            type: 'exam_created',
            description: 'Created new Physics exam',
            timestamp: '4 hours ago',
            user: 'Sarah Johnson',
          },
          {
            id: '3',
            type: 'student_enrolled',
            description: '15 new students enrolled',
            timestamp: '1 day ago',
            user: 'System',
          },
        ],
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const StatCard = ({ 
    title, 
    value, 
    icon, 
    color, 
    trend, 
    onClick 
  }: {
    title: string;
    value: number | string;
    icon: React.ReactElement;
    color: string;
    trend?: string;
    onClick?: () => void;
  }) => (
    <Card 
      sx={{ 
        cursor: onClick ? 'pointer' : 'default',
        transition: 'transform 0.2s',
        '&:hover': onClick ? { transform: 'translateY(-2px)' } : {},
      }}
      onClick={onClick}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h4" fontWeight="bold" color={color}>
              {typeof value === 'number' ? value.toLocaleString() : value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {title}
            </Typography>
            {trend && (
              <Chip
                label={trend}
                size="small"
                color="success"
                sx={{ mt: 1 }}
              />
            )}
          </Box>
          <Avatar sx={{ bgcolor: color, width: 56, height: 56 }}>
            {icon}
          </Avatar>
        </Box>
      </CardContent>
    </Card>
  );

  const QuickAction = ({ 
    title, 
    description, 
    icon, 
    color, 
    onClick 
  }: {
    title: string;
    description: string;
    icon: React.ReactElement;
    color: string;
    onClick: () => void;
  }) => (
    <Card sx={{ cursor: 'pointer', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }} onClick={onClick}>
      <CardContent sx={{ textAlign: 'center', py: 3 }}>
        <Avatar sx={{ bgcolor: color, width: 64, height: 64, mx: 'auto', mb: 2 }}>
          {icon}
        </Avatar>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {description}
        </Typography>
      </CardContent>
    </Card>
  );

  if (isLoading) {
    return (
      <DashboardLayout>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
          <LinearProgress sx={{ width: 200 }} />
        </Box>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <Box>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center', mb: 4 }}>
          <Box>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Dashboard
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Welcome back! Here's what's happening at your institute.
            </Typography>
          </Box>
          <Tooltip title="Refresh Data">
            <IconButton onClick={loadDashboardData}>
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Students"
              value={stats.totalStudents}
              icon={<School />}
              color="#4caf50"
              trend="+12% this month"
              onClick={() => router.push('/students')}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Teachers"
              value={stats.totalTeachers}
              icon={<People />}
              color="#2196f3"
              trend="+3 new"
              onClick={() => router.push('/teachers')}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Question Bank"
              value={stats.totalQuestions}
              icon={<Quiz />}
              color="#ff9800"
              trend="+45 this week"
              onClick={() => router.push('/questions')}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="AI Generated"
              value={stats.aiQuestionsGenerated}
              icon={<Psychology />}
              color="#9c27b0"
              trend="Latest: 2h ago"
              onClick={() => router.push('/ai/generator')}
            />
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          {/* Quick Actions */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <QuickAction
                    title="Generate Questions"
                    description="Use AI to create new questions"
                    icon={<AutoAwesome />}
                    color="#667eea"
                    onClick={() => router.push('/ai/generator')}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <QuickAction
                    title="Create Exam"
                    description="Set up a new examination"
                    icon={<Add />}
                    color="#4caf50"
                    onClick={() => router.push('/exams/create')}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <QuickAction
                    title="View Reports"
                    description="Check performance analytics"
                    icon={<TrendingUp />}
                    color="#ff9800"
                    onClick={() => router.push('/reports')}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <QuickAction
                    title="Manage Students"
                    description="Add or edit student records"
                    icon={<School />}
                    color="#2196f3"
                    onClick={() => router.push('/students')}
                  />
                </Grid>
              </Grid>
            </Paper>

            {/* AI Generation Stats */}
            {aiStats && (
              <Paper sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    AI Generation Statistics
                  </Typography>
                  <Button
                    variant="outlined"
                    startIcon={<Visibility />}
                    onClick={() => router.push('/ai/analytics')}
                  >
                    View Details
                  </Button>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Typography variant="h5" color="primary" fontWeight="bold">
                      {aiStats.total_generations}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Generations
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="h5" color="success.main" fontWeight="bold">
                      {aiStats.success_rate.toFixed(1)}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Success Rate
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="h5" color="warning.main" fontWeight="bold">
                      {aiStats.average_generation_time.toFixed(1)}s
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Avg. Time
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="h5" color="info.main" fontWeight="bold">
                      ${aiStats.total_cost.toFixed(2)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Cost
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>
            )}
          </Grid>

          {/* Recent Activity */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: 'fit-content' }}>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <Box>
                {stats.recentActivity.map((activity) => (
                  <Box key={activity.id} sx={{ mb: 2, pb: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
                    <Typography variant="body2" fontWeight="medium">
                      {activity.description}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {activity.user} • {activity.timestamp}
                    </Typography>
                  </Box>
                ))}
              </Box>
              <Button
                fullWidth
                variant="outlined"
                sx={{ mt: 2 }}
                onClick={() => router.push('/activity')}
              >
                View All Activity
              </Button>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </DashboardLayout>
  );
}

export default withAuth(DashboardPage);
