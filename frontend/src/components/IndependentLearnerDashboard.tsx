import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
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
  Paper,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  School as SchoolIcon,
  Certificate as CertificateIcon,
  Payment as PaymentIcon,
  Person as PersonIcon,
  Share as ShareIcon,
  TrendingUp as TrendingUpIcon,
  Star as StarIcon,
  BookmarkBorder as BookmarkIcon,
  PlayArrow as PlayIcon,
  Download as DownloadIcon,
  ContentCopy as CopyIcon,
  WhatsApp as WhatsAppIcon,
  Email as EmailIcon
} from '@mui/icons-material';

// Import splash screen components
import PageSplashScreen from './PageSplashScreen';
import { useRouteSplashScreen } from '../hooks/useSplashScreen';
import { getSplashConfig } from '../config/splashConfig';

interface LearnerProfile {
  id: string;
  name: string;
  email: string;
  phone: string;
  category: string;
  educationLevel: string;
  referralCode: string;
  totalReferrals: number;
  referralEarnings: number;
  joinedDate: string;
}

interface Program {
  id: string;
  title: string;
  description: string;
  category: string;
  duration: string;
  price: number;
  discountedPrice?: number;
  rating: number;
  enrolledStudents: number;
  isEnrolled: boolean;
  progress?: number;
  certificateUrl?: string;
}

interface ReferralStats {
  totalReferrals: number;
  successfulReferrals: number;
  pendingReferrals: number;
  totalEarnings: number;
  thisMonthEarnings: number;
}

const IndependentLearnerDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const [programs, setPrograms] = useState<Program[]>([]);
  const [enrolledPrograms, setEnrolledPrograms] = useState<Program[]>([]);
  const [referralStats, setReferralStats] = useState<ReferralStats | null>(null);

  // Independent learner splash screen
  const splashConfig = getSplashConfig('independent-learner');
  const splash = useRouteSplashScreen('independent-learner', splashConfig.duration);
  const [selectedProgram, setSelectedProgram] = useState<Program | null>(null);
  const [enrollmentDialog, setEnrollmentDialog] = useState(false);
  const [referralDialog, setReferralDialog] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load learner profile
      const profileResponse = await fetch('/api/v1/independent/profile', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const profileData = await profileResponse.json();
      setProfile(profileData);

      // Load available programs
      const programsResponse = await fetch('/api/v1/independent/programs', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const programsData = await programsResponse.json();
      setPrograms(programsData);

      // Load enrolled programs
      const enrolledResponse = await fetch('/api/v1/independent/enrolled-programs', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const enrolledData = await enrolledResponse.json();
      setEnrolledPrograms(enrolledData);

      // Load referral statistics
      const referralResponse = await fetch('/api/v1/independent/referral-stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const referralData = await referralResponse.json();
      setReferralStats(referralData);

    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProgramEnrollment = async (programId: string) => {
    try {
      const response = await fetch(`/api/v1/independent/enroll/${programId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        loadDashboardData();
        setEnrollmentDialog(false);
        setSelectedProgram(null);
      }
    } catch (error) {
      console.error('Error enrolling in program:', error);
    }
  };

  const copyReferralCode = () => {
    if (profile?.referralCode) {
      navigator.clipboard.writeText(profile.referralCode);
      // Show success message
    }
  };

  const shareReferralCode = (platform: 'whatsapp' | 'email') => {
    if (!profile) return;

    const referralLink = `https://medhasakthi.com/register?ref=${profile.referralCode}`;
    const message = `Join MEDHASAKTHI with my referral code ${profile.referralCode} and get special discounts on certification programs! ${referralLink}`;

    if (platform === 'whatsapp') {
      window.open(`https://wa.me/?text=${encodeURIComponent(message)}`);
    } else if (platform === 'email') {
      window.open(`mailto:?subject=Join MEDHASAKTHI&body=${encodeURIComponent(message)}`);
    }
  };

  const StatCard: React.FC<{ title: string; value: string | number; icon: React.ReactNode; color: string }> = 
    ({ title, value, icon, color }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
          </Box>
          <Box sx={{ color, fontSize: 40 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  // Show splash screen on first visit to independent learner dashboard
  if (splash.isVisible) {
    return (
      <PageSplashScreen
        title={splashConfig.title}
        subtitle={splashConfig.subtitle}
        icon={<SchoolIcon className="w-8 h-8" />}
        color={splashConfig.color}
        onComplete={splash.hide}
      />
    );
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Welcome Section */}
      <Box display="flex" alignItems="center" mb={3}>
        <Avatar sx={{ width: 60, height: 60, mr: 2, bgcolor: 'primary.main' }}>
          {profile?.name?.charAt(0)}
        </Avatar>
        <Box>
          <Typography variant="h4" gutterBottom>
            Welcome back, {profile?.name}!
          </Typography>
          <Typography variant="body1" color="textSecondary">
            {profile?.category} • Member since {profile?.joinedDate && new Date(profile.joinedDate).toLocaleDateString()}
          </Typography>
        </Box>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Enrolled Programs"
            value={enrolledPrograms.length}
            icon={<SchoolIcon />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Certificates Earned"
            value={enrolledPrograms.filter(p => p.certificateUrl).length}
            icon={<CertificateIcon />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Referral Earnings"
            value={`₹${referralStats?.totalEarnings || 0}`}
            icon={<TrendingUpIcon />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Referrals"
            value={referralStats?.totalReferrals || 0}
            icon={<ShareIcon />}
            color="#9c27b0"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Enrolled Programs */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                My Learning Journey
              </Typography>
              
              {enrolledPrograms.length === 0 ? (
                <Alert severity="info">
                  You haven't enrolled in any programs yet. Browse available programs below!
                </Alert>
              ) : (
                <List>
                  {enrolledPrograms.map((program) => (
                    <ListItem key={program.id} divider>
                      <ListItemIcon>
                        <SchoolIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={program.title}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              {program.description}
                            </Typography>
                            {program.progress !== undefined && (
                              <Box mt={1}>
                                <Box display="flex" justifyContent="space-between" alignItems="center">
                                  <Typography variant="body2">Progress</Typography>
                                  <Typography variant="body2">{program.progress}%</Typography>
                                </Box>
                                <LinearProgress 
                                  variant="determinate" 
                                  value={program.progress} 
                                  sx={{ mt: 0.5 }}
                                />
                              </Box>
                            )}
                          </Box>
                        }
                      />
                      <Box>
                        {program.certificateUrl ? (
                          <Button
                            startIcon={<DownloadIcon />}
                            variant="outlined"
                            size="small"
                            onClick={() => window.open(program.certificateUrl)}
                          >
                            Certificate
                          </Button>
                        ) : (
                          <Button
                            startIcon={<PlayIcon />}
                            variant="contained"
                            size="small"
                          >
                            Continue
                          </Button>
                        )}
                      </Box>
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>

          {/* Available Programs */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recommended Programs
              </Typography>
              
              <Grid container spacing={2}>
                {programs.slice(0, 6).map((program) => (
                  <Grid item xs={12} sm={6} key={program.id}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box display="flex" justifyContent="space-between" alignItems="start" mb={1}>
                          <Typography variant="h6" component="div">
                            {program.title}
                          </Typography>
                          <Chip label={program.category} size="small" />
                        </Box>
                        
                        <Typography variant="body2" color="textSecondary" mb={2}>
                          {program.description}
                        </Typography>
                        
                        <Box display="flex" alignItems="center" mb={2}>
                          <StarIcon color="warning" fontSize="small" />
                          <Typography variant="body2" sx={{ ml: 0.5, mr: 2 }}>
                            {program.rating}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {program.enrolledStudents} students
                          </Typography>
                        </Box>
                        
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Box>
                            {program.discountedPrice ? (
                              <Box>
                                <Typography variant="h6" color="primary">
                                  ₹{program.discountedPrice}
                                </Typography>
                                <Typography variant="body2" sx={{ textDecoration: 'line-through' }}>
                                  ₹{program.price}
                                </Typography>
                              </Box>
                            ) : (
                              <Typography variant="h6">₹{program.price}</Typography>
                            )}
                          </Box>
                          <Button
                            variant="contained"
                            size="small"
                            onClick={() => {
                              setSelectedProgram(program);
                              setEnrollmentDialog(true);
                            }}
                            disabled={program.isEnrolled}
                          >
                            {program.isEnrolled ? 'Enrolled' : 'Enroll'}
                          </Button>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Referral Section */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Referral Program
              </Typography>
              
              <Alert severity="success" sx={{ mb: 2 }}>
                Earn ₹100 for each successful referral!
              </Alert>
              
              <Box mb={2}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Your Referral Code
                </Typography>
                <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="h6" fontFamily="monospace">
                      {profile?.referralCode}
                    </Typography>
                    <Tooltip title="Copy Code">
                      <IconButton onClick={copyReferralCode} size="small">
                        <CopyIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Paper>
              </Box>
              
              <Box mb={3}>
                <Typography variant="body2" gutterBottom>
                  Share your code:
                </Typography>
                <Box display="flex" gap={1}>
                  <Button
                    startIcon={<WhatsAppIcon />}
                    variant="outlined"
                    size="small"
                    onClick={() => shareReferralCode('whatsapp')}
                  >
                    WhatsApp
                  </Button>
                  <Button
                    startIcon={<EmailIcon />}
                    variant="outlined"
                    size="small"
                    onClick={() => shareReferralCode('email')}
                  >
                    Email
                  </Button>
                </Box>
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Referral Statistics
              </Typography>
              <Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Total Referrals:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {referralStats?.totalReferrals || 0}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Successful:</Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main">
                    {referralStats?.successfulReferrals || 0}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">This Month Earnings:</Typography>
                  <Typography variant="body2" fontWeight="bold" color="primary.main">
                    ₹{referralStats?.thisMonthEarnings || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Enrollment Dialog */}
      <Dialog open={enrollmentDialog} onClose={() => setEnrollmentDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Enroll in Program</DialogTitle>
        <DialogContent>
          {selectedProgram && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedProgram.title}
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                {selectedProgram.description}
              </Typography>
              <Typography variant="h5" color="primary" gutterBottom>
                ₹{selectedProgram.discountedPrice || selectedProgram.price}
                {selectedProgram.discountedPrice && (
                  <Typography component="span" variant="body2" sx={{ textDecoration: 'line-through', ml: 1 }}>
                    ₹{selectedProgram.price}
                  </Typography>
                )}
              </Typography>
              <Typography variant="body2">
                Duration: {selectedProgram.duration}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEnrollmentDialog(false)}>Cancel</Button>
          <Button 
            onClick={() => selectedProgram && handleProgramEnrollment(selectedProgram.id)}
            variant="contained"
          >
            Proceed to Payment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default IndependentLearnerDashboard;
