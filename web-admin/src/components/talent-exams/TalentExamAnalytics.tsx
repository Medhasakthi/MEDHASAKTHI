/**
 * Talent Exam Analytics Dashboard
 * Comprehensive analytics for talent exam performance, rankings, and insights
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
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
  LinearProgress,
  Avatar,
  IconButton,
  Tooltip,
  Button
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  School as SchoolIcon,
  EmojiEvents as TrophyIcon,
  Assessment as AssessmentIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
  LocationOn as LocationIcon,
  People as PeopleIcon
} from '@mui/icons-material';
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
  ResponsiveContainer
} from 'recharts';

// Types
interface ExamAnalytics {
  examId: string;
  examTitle: string;
  examCode: string;
  classLevel: string;
  totalRegistrations: number;
  totalAppeared: number;
  averageScore: number;
  highestScore: number;
  lowestScore: number;
  passPercentage: number;
  subjectWisePerformance: SubjectPerformance[];
  stateWisePerformance: StatePerformance[];
  instituteWisePerformance: InstitutePerformance[];
  topPerformers: TopPerformer[];
  difficultyAnalysis: DifficultyAnalysis[];
  timeAnalysis: TimeAnalysis;
}

interface SubjectPerformance {
  subject: string;
  averageScore: number;
  maxScore: number;
  totalQuestions: number;
  accuracy: number;
}

interface StatePerformance {
  state: string;
  registrations: number;
  appeared: number;
  averageScore: number;
  topScore: number;
  rank: number;
}

interface InstitutePerformance {
  instituteId: string;
  instituteName: string;
  city: string;
  state: string;
  registrations: number;
  appeared: number;
  averageScore: number;
  topScore: number;
  rank: number;
}

interface TopPerformer {
  rank: number;
  studentName: string;
  instituteName: string;
  city: string;
  state: string;
  score: number;
  percentage: number;
  subjectWiseScores: { [subject: string]: number };
}

interface DifficultyAnalysis {
  difficulty: 'easy' | 'medium' | 'hard';
  totalQuestions: number;
  averageScore: number;
  accuracy: number;
}

interface TimeAnalysis {
  averageTimePerQuestion: number;
  fastestCompletion: number;
  slowestCompletion: number;
  timeDistribution: { timeRange: string; count: number }[];
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export const TalentExamAnalytics: React.FC = () => {
  const [selectedExam, setSelectedExam] = useState<string>('');
  const [analytics, setAnalytics] = useState<ExamAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [availableExams, setAvailableExams] = useState<any[]>([]);

  useEffect(() => {
    loadAvailableExams();
  }, []);

  useEffect(() => {
    if (selectedExam) {
      loadAnalytics();
    }
  }, [selectedExam]);

  const loadAvailableExams = async () => {
    try {
      // API call to load completed exams
      // const response = await api.get('/talent-exams?status=completed');
      
      // Mock data
      const mockExams = [
        { id: 'exam1', title: 'Annual Talent Exam Class 10', examCode: 'ANN1024A1', classLevel: 'class_10' },
        { id: 'exam2', title: 'Mathematics Olympiad Class 8', examCode: 'OLY824B2', classLevel: 'class_8' }
      ];
      
      setAvailableExams(mockExams);
      if (mockExams.length > 0) {
        setSelectedExam(mockExams[0].id);
      }
    } catch (error) {
      console.error('Failed to load exams');
    }
  };

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      // API call to load analytics
      // const response = await api.get(`/talent-exams/${selectedExam}/analytics`);
      
      // Mock analytics data
      const mockAnalytics: ExamAnalytics = {
        examId: selectedExam,
        examTitle: 'Annual Talent Exam Class 10',
        examCode: 'ANN1024A1',
        classLevel: 'class_10',
        totalRegistrations: 5000,
        totalAppeared: 4750,
        averageScore: 142.5,
        highestScore: 195,
        lowestScore: 45,
        passPercentage: 78.5,
        subjectWisePerformance: [
          { subject: 'Mathematics', averageScore: 48.5, maxScore: 60, totalQuestions: 30, accuracy: 80.8 },
          { subject: 'Science', averageScore: 52.3, maxScore: 70, totalQuestions: 35, accuracy: 74.7 },
          { subject: 'English', averageScore: 41.7, maxScore: 50, totalQuestions: 25, accuracy: 83.4 },
          { subject: 'Reasoning', averageScore: 38.2, maxScore: 50, totalQuestions: 25, accuracy: 76.4 }
        ],
        stateWisePerformance: [
          { state: 'Maharashtra', registrations: 850, appeared: 820, averageScore: 156.2, topScore: 195, rank: 1 },
          { state: 'Karnataka', registrations: 720, appeared: 695, averageScore: 151.8, topScore: 189, rank: 2 },
          { state: 'Tamil Nadu', registrations: 680, appeared: 650, averageScore: 148.9, topScore: 187, rank: 3 },
          { state: 'Gujarat', registrations: 590, appeared: 570, averageScore: 145.3, topScore: 185, rank: 4 },
          { state: 'Rajasthan', registrations: 520, appeared: 495, averageScore: 142.1, topScore: 182, rank: 5 }
        ],
        instituteWisePerformance: [
          { instituteId: '1', instituteName: 'Delhi Public School', city: 'Mumbai', state: 'Maharashtra', registrations: 45, appeared: 44, averageScore: 168.5, topScore: 195, rank: 1 },
          { instituteId: '2', instituteName: 'Kendriya Vidyalaya', city: 'Bangalore', state: 'Karnataka', registrations: 38, appeared: 37, averageScore: 165.2, topScore: 189, rank: 2 },
          { instituteId: '3', instituteName: 'DAV Public School', city: 'Chennai', state: 'Tamil Nadu', registrations: 42, appeared: 40, averageScore: 162.8, topScore: 187, rank: 3 }
        ],
        topPerformers: [
          { rank: 1, studentName: 'Arjun Sharma', instituteName: 'Delhi Public School', city: 'Mumbai', state: 'Maharashtra', score: 195, percentage: 97.5, subjectWiseScores: { Mathematics: 58, Science: 68, English: 47, Reasoning: 22 } },
          { rank: 2, studentName: 'Priya Patel', instituteName: 'Kendriya Vidyalaya', city: 'Bangalore', state: 'Karnataka', score: 189, percentage: 94.5, subjectWiseScores: { Mathematics: 56, Science: 65, English: 45, Reasoning: 23 } },
          { rank: 3, studentName: 'Rahul Kumar', instituteName: 'DAV Public School', city: 'Chennai', state: 'Tamil Nadu', score: 187, percentage: 93.5, subjectWiseScores: { Mathematics: 55, Science: 64, English: 46, Reasoning: 22 } }
        ],
        difficultyAnalysis: [
          { difficulty: 'easy', totalQuestions: 40, averageScore: 32.5, accuracy: 81.25 },
          { difficulty: 'medium', totalQuestions: 45, averageScore: 28.8, accuracy: 64.0 },
          { difficulty: 'hard', totalQuestions: 25, averageScore: 12.2, accuracy: 48.8 }
        ],
        timeAnalysis: {
          averageTimePerQuestion: 2.8,
          fastestCompletion: 95,
          slowestCompletion: 180,
          timeDistribution: [
            { timeRange: '90-120 min', count: 850 },
            { timeRange: '120-150 min', count: 1650 },
            { timeRange: '150-180 min', count: 2250 }
          ]
        }
      };
      
      setAnalytics(mockAnalytics);
    } catch (error) {
      console.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const renderOverviewCards = () => (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <PeopleIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
              <Box>
                <Typography variant="h4">{analytics?.totalAppeared.toLocaleString()}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Students Appeared
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  out of {analytics?.totalRegistrations.toLocaleString()} registered
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <AssessmentIcon sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
              <Box>
                <Typography variant="h4">{analytics?.averageScore}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Average Score
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  out of 200 marks
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <TrophyIcon sx={{ fontSize: 40, color: 'warning.main', mr: 2 }} />
              <Box>
                <Typography variant="h4">{analytics?.highestScore}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Highest Score
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {analytics?.topPerformers[0]?.studentName}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <TrendingUpIcon sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
              <Box>
                <Typography variant="h4">{analytics?.passPercentage}%</Typography>
                <Typography variant="body2" color="text.secondary">
                  Pass Percentage
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  above 40% marks
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderSubjectAnalysis = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Subject-wise Performance
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics?.subjectWisePerformance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="subject" />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Bar dataKey="averageScore" fill="#8884d8" name="Average Score" />
                <Bar dataKey="maxScore" fill="#82ca9d" name="Max Score" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Difficulty Analysis
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analytics?.difficultyAnalysis}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ difficulty, accuracy }) => `${difficulty}: ${accuracy.toFixed(1)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="accuracy"
                >
                  {analytics?.difficultyAnalysis.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Subject Performance Details
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Subject</TableCell>
                    <TableCell align="right">Questions</TableCell>
                    <TableCell align="right">Max Score</TableCell>
                    <TableCell align="right">Average Score</TableCell>
                    <TableCell align="right">Accuracy</TableCell>
                    <TableCell align="right">Performance</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {analytics?.subjectWisePerformance.map((subject) => (
                    <TableRow key={subject.subject}>
                      <TableCell>{subject.subject}</TableCell>
                      <TableCell align="right">{subject.totalQuestions}</TableCell>
                      <TableCell align="right">{subject.maxScore}</TableCell>
                      <TableCell align="right">{subject.averageScore}</TableCell>
                      <TableCell align="right">{subject.accuracy.toFixed(1)}%</TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <LinearProgress
                            variant="determinate"
                            value={subject.accuracy}
                            sx={{ width: 60, mr: 1 }}
                          />
                          <Typography variant="caption">
                            {subject.accuracy.toFixed(0)}%
                          </Typography>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderRankings = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Top Performers
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Rank</TableCell>
                    <TableCell>Student</TableCell>
                    <TableCell>Institute</TableCell>
                    <TableCell align="right">Score</TableCell>
                    <TableCell align="right">%</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {analytics?.topPerformers.slice(0, 10).map((performer) => (
                    <TableRow key={performer.rank}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {performer.rank <= 3 && (
                            <TrophyIcon
                              sx={{
                                fontSize: 20,
                                color: performer.rank === 1 ? '#FFD700' : performer.rank === 2 ? '#C0C0C0' : '#CD7F32',
                                mr: 1
                              }}
                            />
                          )}
                          #{performer.rank}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {performer.studentName}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {performer.city}, {performer.state}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {performer.instituteName}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="medium">
                          {performer.score}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Chip
                          label={`${performer.percentage}%`}
                          color={performer.percentage >= 90 ? 'success' : performer.percentage >= 75 ? 'primary' : 'default'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              State-wise Performance
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Rank</TableCell>
                    <TableCell>State</TableCell>
                    <TableCell align="right">Appeared</TableCell>
                    <TableCell align="right">Avg Score</TableCell>
                    <TableCell align="right">Top Score</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {analytics?.stateWisePerformance.map((state) => (
                    <TableRow key={state.state}>
                      <TableCell>#{state.rank}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <LocationIcon sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                          {state.state}
                        </Box>
                      </TableCell>
                      <TableCell align="right">{state.appeared}</TableCell>
                      <TableCell align="right">{state.averageScore}</TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="medium">
                          {state.topScore}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Institute Rankings
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Rank</TableCell>
                    <TableCell>Institute</TableCell>
                    <TableCell>Location</TableCell>
                    <TableCell align="right">Students</TableCell>
                    <TableCell align="right">Average Score</TableCell>
                    <TableCell align="right">Top Score</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {analytics?.instituteWisePerformance.map((institute) => (
                    <TableRow key={institute.instituteId}>
                      <TableCell>#{institute.rank}</TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {institute.instituteName}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {institute.city}, {institute.state}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">{institute.appeared}</TableCell>
                      <TableCell align="right">{institute.averageScore}</TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="medium">
                          {institute.topScore}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View Details">
                          <IconButton size="small">
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderInsights = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Time Analysis
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Average time per question: {analytics?.timeAnalysis.averageTimePerQuestion} minutes
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Fastest completion: {analytics?.timeAnalysis.fastestCompletion} minutes
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Slowest completion: {analytics?.timeAnalysis.slowestCompletion} minutes
              </Typography>
            </Box>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={analytics?.timeAnalysis.timeDistribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timeRange" />
                <YAxis />
                <RechartsTooltip />
                <Bar dataKey="count" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Key Insights
            </Typography>
            <Box sx={{ space: 2 }}>
              <Typography variant="body2" paragraph>
                • Mathematics showed the highest accuracy at 80.8%, indicating strong preparation in this subject.
              </Typography>
              <Typography variant="body2" paragraph>
                • Hard difficulty questions had only 48.8% accuracy, suggesting need for advanced problem-solving practice.
              </Typography>
              <Typography variant="body2" paragraph>
                • Maharashtra leads with highest average score of 156.2, followed by Karnataka at 151.8.
              </Typography>
              <Typography variant="body2" paragraph>
                • 78.5% students passed the exam, which is above the expected benchmark of 75%.
              </Typography>
              <Typography variant="body2" paragraph>
                • Most students (47%) completed the exam in 150-180 minutes, indicating appropriate time allocation.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  if (!analytics) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Talent Exam Analytics
        </Typography>
        <FormControl sx={{ minWidth: 300, mb: 3 }}>
          <InputLabel>Select Exam</InputLabel>
          <Select
            value={selectedExam}
            onChange={(e) => setSelectedExam(e.target.value)}
          >
            {availableExams.map(exam => (
              <MenuItem key={exam.id} value={exam.id}>
                {exam.title} ({exam.examCode})
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Talent Exam Analytics
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl sx={{ minWidth: 300 }}>
            <InputLabel>Select Exam</InputLabel>
            <Select
              value={selectedExam}
              onChange={(e) => setSelectedExam(e.target.value)}
            >
              {availableExams.map(exam => (
                <MenuItem key={exam.id} value={exam.id}>
                  {exam.title} ({exam.examCode})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={() => {/* Download report */}}
          >
            Export Report
          </Button>
        </Box>
      </Box>

      <Typography variant="h6" color="text.secondary" gutterBottom>
        {analytics.examTitle} - {analytics.examCode}
      </Typography>

      {renderOverviewCards()}

      <Card>
        <CardContent>
          <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
            <Tab label="Subject Analysis" />
            <Tab label="Rankings" />
            <Tab label="Insights" />
          </Tabs>

          <Box sx={{ mt: 3 }}>
            {activeTab === 0 && renderSubjectAnalysis()}
            {activeTab === 1 && renderRankings()}
            {activeTab === 2 && renderInsights()}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};
