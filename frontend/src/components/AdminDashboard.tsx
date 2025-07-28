import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Tabs,
  Tab
} from '@mui/material';
import Grid from '@mui/material/Grid2';
import {
  People as PeopleIcon,
  School as SchoolIcon,
  Payment as PaymentIcon,
  Settings as SettingsIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  TrendingUp as TrendingUpIcon,
  MonetizationOn as MoneyIcon,
  Computer as ServerIcon,
  Speed as LoadBalancerIcon
} from '@mui/icons-material';

// Import load balancer components
import LoadBalancerManagement from './LoadBalancerManagement';
import LoadBalancerDashboard from './LoadBalancerDashboard';

// Import splash screen components
import PageSplashScreen from './PageSplashScreen';
import { useRouteSplashScreen } from '../hooks/useSplashScreen';

interface AdminDashboardProps {
  userRole: 'super_admin' | 'institute_admin';
}

interface DashboardStats {
  totalUsers: number;
  totalInstitutes: number;
  totalPayments: number;
  totalRevenue: number;
  pendingVerifications: number;
  activeExams: number;
  monthlyGrowth: number;
  conversionRate: number;
}

interface PaymentVerification {
  id: string;
  paymentId: string;
  userName: string;
  amount: number;
  submittedAt: string;
  status: 'pending' | 'verified' | 'rejected';
  screenshotUrl?: string;
}

interface UPIConfiguration {
  id: string;
  upiId: string;
  upiName: string;
  provider: string;
  isActive: boolean;
  isPrimary: boolean;
  minAmount: number;
  maxAmount: number;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ userRole }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [pendingPayments, setPendingPayments] = useState<PaymentVerification[]>([]);
  const [upiConfigs, setUpiConfigs] = useState<UPIConfiguration[]>([]);

  // Page splash screen for admin dashboard
  const splash = useRouteSplashScreen('admin-dashboard', 2500);
  const [selectedPayment, setSelectedPayment] = useState<PaymentVerification | null>(null);
  const [verificationDialog, setVerificationDialog] = useState(false);
  const [configDialog, setConfigDialog] = useState(false);
  const [newConfig, setNewConfig] = useState<Partial<UPIConfiguration>>({});

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load dashboard statistics
      const statsResponse = await fetch('/api/v1/admin/analytics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const statsData = await statsResponse.json();
      setStats(statsData);

      // Load pending payment verifications
      const paymentsResponse = await fetch('/api/v1/payments/upi/admin/pending-verifications', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const paymentsData = await paymentsResponse.json();
      setPendingPayments(paymentsData);

      // Load UPI configurations
      const configResponse = await fetch('/api/v1/payments/upi/admin/config', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const configData = await configResponse.json();
      setUpiConfigs(configData);

    } catch (error) {
      // Handle error loading dashboard data
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentVerification = async (paymentId: string, action: 'verify' | 'reject') => {
    try {
      const response = await fetch(`/api/v1/payments/upi/admin/verify/${paymentId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ action })
      });

      if (response.ok) {
        // Refresh pending payments
        loadDashboardData();
        setVerificationDialog(false);
        setSelectedPayment(null);
      }
    } catch (error) {
      // Handle error verifying payment
    }
  };

  const handleUPIConfigSave = async () => {
    try {
      const response = await fetch('/api/v1/payments/upi/admin/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newConfig)
      });

      if (response.ok) {
        loadDashboardData();
        setConfigDialog(false);
        setNewConfig({});
      }
    } catch (error) {
      // Handle error saving UPI config
    }
  };

  const StatCard: React.FC<{ title: string; value: string | number; icon: React.ReactNode; color: string; trend?: number }> = 
    ({ title, value, icon, color, trend }) => (
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
            {trend !== undefined && (
              <Box display="flex" alignItems="center" mt={1}>
                <TrendingUpIcon color={trend > 0 ? 'success' : 'error'} fontSize="small" />
                <Typography variant="body2" color={trend > 0 ? 'success.main' : 'error.main'}>
                  {trend > 0 ? '+' : ''}{trend}%
                </Typography>
              </Box>
            )}
          </Box>
          <Box sx={{ color, fontSize: 40 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  // Show splash screen on first visit to admin dashboard
  if (splash.isVisible) {
    return (
      <PageSplashScreen
        title="Admin Dashboard"
        subtitle={`Welcome, ${userRole === 'super_admin' ? 'Super Admin' : 'Administrator'}`}
        icon={<SettingsIcon sx={{ fontSize: 32 }} />}
        color="#1565c0"
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
      <Typography variant="h4" gutterBottom>
        {userRole === 'super_admin' ? 'Super Admin Dashboard' : 'Institute Admin Dashboard'}
      </Typography>

      {/* Dashboard Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid xs={12} sm={6} md={3}>
          <StatCard
            title="Total Users"
            value={stats?.totalUsers || 0}
            icon={<PeopleIcon />}
            color="#1976d2"
            trend={stats?.monthlyGrowth}
          />
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <StatCard
            title="Total Revenue"
            value={`₹${(stats?.totalRevenue || 0).toLocaleString()}`}
            icon={<MoneyIcon />}
            color="#2e7d32"
          />
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Verifications"
            value={stats?.pendingVerifications || 0}
            icon={<PaymentIcon />}
            color="#ed6c02"
          />
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <StatCard
            title="Active Exams"
            value={stats?.activeExams || 0}
            icon={<SchoolIcon />}
            color="#9c27b0"
          />
        </Grid>
      </Grid>

      {/* Tabs for different sections */}
      <Paper sx={{ width: '100%', mb: 2 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Payment Verifications" />
          <Tab label="UPI Configuration" />
          <Tab label="Analytics" />
          {userRole === 'super_admin' && <Tab label="System Settings" />}
          {userRole === 'super_admin' && <Tab label="Load Balancer" icon={<LoadBalancerIcon />} />}
          {userRole === 'super_admin' && <Tab label="Server Monitoring" icon={<ServerIcon />} />}
        </Tabs>
      </Paper>

      {/* Payment Verifications Tab */}
      {activeTab === 0 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Pending Payment Verifications</Typography>
              <Button variant="outlined" onClick={loadDashboardData}>
                Refresh
              </Button>
            </Box>
            
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Payment ID</TableCell>
                    <TableCell>User</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Submitted</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {pendingPayments.map((payment) => (
                    <TableRow key={payment.id}>
                      <TableCell>{payment.paymentId}</TableCell>
                      <TableCell>{payment.userName}</TableCell>
                      <TableCell>₹{payment.amount}</TableCell>
                      <TableCell>{new Date(payment.submittedAt).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <Chip 
                          label={payment.status} 
                          color={payment.status === 'pending' ? 'warning' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton 
                          onClick={() => {
                            setSelectedPayment(payment);
                            setVerificationDialog(true);
                          }}
                          size="small"
                        >
                          <ViewIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* UPI Configuration Tab */}
      {activeTab === 1 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">UPI Configuration</Typography>
              <Button 
                variant="contained" 
                startIcon={<AddIcon />}
                onClick={() => setConfigDialog(true)}
              >
                Add UPI ID
              </Button>
            </Box>
            
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>UPI ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Provider</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Primary</TableCell>
                    <TableCell>Limits</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {upiConfigs.map((config) => (
                    <TableRow key={config.id}>
                      <TableCell>{config.upiId}</TableCell>
                      <TableCell>{config.upiName}</TableCell>
                      <TableCell>{config.provider}</TableCell>
                      <TableCell>
                        <Chip 
                          label={config.isActive ? 'Active' : 'Inactive'} 
                          color={config.isActive ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {config.isPrimary && <CheckCircleIcon color="primary" />}
                      </TableCell>
                      <TableCell>₹{config.minAmount} - ₹{config.maxAmount}</TableCell>
                      <TableCell>
                        <IconButton size="small">
                          <EditIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Analytics Tab */}
      {activeTab === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>System Analytics</Typography>
            <Typography color="textSecondary">
              Analytics dashboard coming soon...
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* System Settings Tab */}
      {userRole === 'super_admin' && activeTab === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>System Settings</Typography>
            <Typography color="textSecondary">
              System configuration settings coming soon...
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Load Balancer Management Tab */}
      {userRole === 'super_admin' && activeTab === 4 && (
        <LoadBalancerManagement />
      )}

      {/* Server Monitoring Tab */}
      {userRole === 'super_admin' && activeTab === 5 && (
        <LoadBalancerDashboard />
      )}

      {/* Payment Verification Dialog */}
      <Dialog open={verificationDialog} onClose={() => setVerificationDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Payment Verification</DialogTitle>
        <DialogContent>
          {selectedPayment && (
            <Box>
              <Typography variant="h6" gutterBottom>Payment Details</Typography>
              <Typography><strong>Payment ID:</strong> {selectedPayment.paymentId}</Typography>
              <Typography><strong>User:</strong> {selectedPayment.userName}</Typography>
              <Typography><strong>Amount:</strong> ₹{selectedPayment.amount}</Typography>
              <Typography><strong>Submitted:</strong> {new Date(selectedPayment.submittedAt).toLocaleString()}</Typography>
              
              {selectedPayment.screenshotUrl && (
                <Box mt={2}>
                  <Typography variant="h6" gutterBottom>Payment Screenshot</Typography>
                  <img 
                    src={selectedPayment.screenshotUrl} 
                    alt="Payment Screenshot" 
                    style={{ maxWidth: '100%', height: 'auto' }}
                  />
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVerificationDialog(false)}>Cancel</Button>
          <Button 
            onClick={() => selectedPayment && handlePaymentVerification(selectedPayment.paymentId, 'reject')}
            color="error"
            startIcon={<CancelIcon />}
          >
            Reject
          </Button>
          <Button 
            onClick={() => selectedPayment && handlePaymentVerification(selectedPayment.paymentId, 'verify')}
            color="success"
            startIcon={<CheckCircleIcon />}
          >
            Verify
          </Button>
        </DialogActions>
      </Dialog>

      {/* UPI Configuration Dialog */}
      <Dialog open={configDialog} onClose={() => setConfigDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add UPI Configuration</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="UPI ID"
              value={newConfig.upiId || ''}
              onChange={(e) => setNewConfig({ ...newConfig, upiId: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label="UPI Name"
              value={newConfig.upiName || ''}
              onChange={(e) => setNewConfig({ ...newConfig, upiName: e.target.value })}
              margin="normal"
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Provider</InputLabel>
              <Select
                value={newConfig.provider || ''}
                onChange={(e) => setNewConfig({ ...newConfig, provider: e.target.value })}
              >
                <MenuItem value="PhonePe">PhonePe</MenuItem>
                <MenuItem value="Google Pay">Google Pay</MenuItem>
                <MenuItem value="Paytm">Paytm</MenuItem>
                <MenuItem value="BHIM">BHIM</MenuItem>
                <MenuItem value="Amazon Pay">Amazon Pay</MenuItem>
                <MenuItem value="WhatsApp Pay">WhatsApp Pay</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Minimum Amount"
              type="number"
              value={newConfig.minAmount || ''}
              onChange={(e) => setNewConfig({ ...newConfig, minAmount: Number(e.target.value) })}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Maximum Amount"
              type="number"
              value={newConfig.maxAmount || ''}
              onChange={(e) => setNewConfig({ ...newConfig, maxAmount: Number(e.target.value) })}
              margin="normal"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialog(false)}>Cancel</Button>
          <Button onClick={handleUPIConfigSave} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminDashboard;
