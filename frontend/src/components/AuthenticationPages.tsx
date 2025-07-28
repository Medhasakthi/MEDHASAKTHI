import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Divider,
  IconButton,
  InputAdornment,
  Chip,
  Paper,

  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Link,
  Checkbox,
  FormControlLabel
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  School as SchoolIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  AdminPanelSettings as AdminIcon,
  Google as GoogleIcon,
  Facebook as FacebookIcon,
  GitHub as GitHubIcon,
  Email as EmailIcon,
  Lock as LockIcon,
  Phone as PhoneIcon,
  Security as SecurityIcon,
  Sms as SmsIcon,
  QrCode as QrCodeIcon,
  VpnKey as VpnKeyIcon,
  CheckCircle as CheckCircleIcon,
  Send as SendIcon,
  Refresh as RefreshIcon,
  Timer as TimerIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';

// Import splash screen components
import SplashScreen from './SplashScreen';
import { useSplashScreen } from '../hooks/useSplashScreen';

interface AuthProps {
  onLogin: (credentials: any) => void;
  onRegister: (userData: any) => void;
  loading?: boolean;
}

interface TwoFactorData {
  method: '2fa_app' | 'sms' | 'email';
  code: string;
  backupCode?: string;
}

const AuthenticationPages: React.FC<AuthProps> = ({ onLogin, onRegister, loading = false }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [showPassword, setShowPassword] = useState(false);
  const [show2FA, setShow2FA] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [showEmailVerification, setShowEmailVerification] = useState(false);

  // Auth page splash screen
  const splash = useSplashScreen({
    duration: 2500,
    showOnFirstVisit: true,
    showOnRouteChange: false
  });
  const [twoFactorStep, setTwoFactorStep] = useState(0);
  const [countdown, setCountdown] = useState(0);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    phone: '',
    userType: '',
    instituteName: '',
    category: '',
    educationLevel: '',
    enable2FA: false,
    agreeTerms: false
  });
  const [twoFactorData, setTwoFactorData] = useState<TwoFactorData>({
    method: '2fa_app',
    code: ''
  });
  const [errors, setErrors] = useState<any>({});
  const [qrCodeUrl, setQrCodeUrl] = useState('');

  const userTypes = [
    { value: 'student', label: 'Student', icon: <PersonIcon />, color: '#2196F3' },
    { value: 'teacher', label: 'Teacher', icon: <SchoolIcon />, color: '#4CAF50' },
    { value: 'institute_admin', label: 'Institute Admin', icon: <BusinessIcon />, color: '#FF9800' },
    { value: 'independent_learner', label: 'Independent Learner', icon: <PersonIcon />, color: '#9C27B0' },
    { value: 'super_admin', label: 'Super Admin', icon: <AdminIcon />, color: '#F44336' }
  ];

  const learnerCategories = [
    'School Student', 'College Student', 'Working Professional', 
    'Job Seeker', 'Entrepreneur', 'Freelancer', 'Retired', 'Homemaker', 'Other'
  ];

  const educationLevels = [
    'Below 10th', '10th Pass', '12th Pass', 'Diploma', 
    'Bachelor\'s Degree', 'Master\'s Degree', 'Doctorate', 'Professional Certification'
  ];

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData({ ...formData, [field]: value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
  };

  const validateForm = () => {
    const newErrors: any = {};
    
    if (!formData.email) newErrors.email = 'Email is required';
    if (!formData.password) newErrors.password = 'Password is required';
    
    if (activeTab === 1) { // Register
      if (!formData.name) newErrors.name = 'Name is required';
      if (!formData.userType) newErrors.userType = 'User type is required';
      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
      if (formData.userType === 'independent_learner') {
        if (!formData.category) newErrors.category = 'Category is required';
        if (!formData.educationLevel) newErrors.educationLevel = 'Education level is required';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    if (activeTab === 0) {
      // Check if 2FA is enabled for this user
      if (formData.enable2FA) {
        setShow2FA(true);
      } else {
        onLogin({ email: formData.email, password: formData.password });
      }
    } else {
      if (formData.enable2FA) {
        setup2FA();
      } else {
        onRegister(formData);
      }
    }
  };

  const setup2FA = async () => {
    try {
      // Simulate 2FA setup API call
      const response = await fetch('/api/v1/auth/setup-2fa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: formData.email })
      });
      const data = await response.json();
      setQrCodeUrl(data.qrCodeUrl);
      setShow2FA(true);
    } catch (error) {
      console.error('2FA setup failed:', error);
    }
  };

  const verify2FA = async () => {
    try {
      const response = await fetch('/api/v1/auth/verify-2fa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          code: twoFactorData.code,
          method: twoFactorData.method
        })
      });

      if (response.ok) {
        setShow2FA(false);
        if (activeTab === 0) {
          onLogin({ email: formData.email, password: formData.password, twoFactorVerified: true });
        } else {
          onRegister({ ...formData, twoFactorEnabled: true });
        }
      }
    } catch (error) {
      console.error('2FA verification failed:', error);
    }
  };

  const sendPasswordReset = async () => {
    try {
      await fetch('/api/v1/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: formData.email })
      });
      setShowForgotPassword(false);
      // Show success message
    } catch (error) {
      console.error('Password reset failed:', error);
    }
  };

  const sendEmailVerification = async () => {
    try {
      await fetch('/api/v1/auth/send-verification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: formData.email })
      });
      setCountdown(60);
      const timer = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (error) {
      console.error('Email verification failed:', error);
    }
  };

  const UserTypeCard: React.FC<{ type: any; selected: boolean; onClick: () => void }> = 
    ({ type, selected, onClick }) => (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Card 
        sx={{ 
          cursor: 'pointer',
          border: selected ? `2px solid ${type.color}` : '2px solid transparent',
          bgcolor: selected ? `${type.color}10` : 'background.paper',
          transition: 'all 0.3s ease'
        }}
        onClick={onClick}
      >
        <CardContent sx={{ textAlign: 'center', py: 2 }}>
          <Avatar sx={{ bgcolor: type.color, mx: 'auto', mb: 1 }}>
            {type.icon}
          </Avatar>
          <Typography variant="body2" fontWeight={selected ? 'bold' : 'normal'}>
            {type.label}
          </Typography>
        </CardContent>
      </Card>
    </motion.div>
  );

  // Show splash screen on first visit to auth pages
  if (splash.isVisible) {
    return (
      <SplashScreen
        onComplete={splash.hide}
        duration={2500}
        title="MEDHASAKTHI"
        subtitle="Secure Authentication Portal"
        variant="auth"
        showProgress={true}
      />
    );
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card sx={{ maxWidth: 500, width: '100%', borderRadius: 3, overflow: 'hidden' }}>
          {/* Header */}
          <Box sx={{ bgcolor: 'primary.main', color: 'white', p: 3, textAlign: 'center' }}>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              MEDHASAKTHI
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.9 }}>
              World-Class Educational Platform
            </Typography>
          </Box>

          <CardContent sx={{ p: 0 }}>
            {/* Tabs */}
            <Tabs 
              value={activeTab} 
              onChange={(e, newValue) => setActiveTab(newValue)}
              variant="fullWidth"
              sx={{ borderBottom: 1, borderColor: 'divider' }}
            >
              <Tab label="Login" />
              <Tab label="Register" />
            </Tabs>

            <Box sx={{ p: 3 }}>
              <form onSubmit={handleSubmit}>
                {/* Login Form */}
                {activeTab === 0 && (
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <TextField
                      fullWidth
                      label="Email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      error={!!errors.email}
                      helperText={errors.email}
                      margin="normal"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <EmailIcon color="action" />
                          </InputAdornment>
                        )
                      }}
                    />
                    
                    <TextField
                      fullWidth
                      label="Password"
                      type={showPassword ? 'text' : 'password'}
                      value={formData.password}
                      onChange={(e) => handleInputChange('password', e.target.value)}
                      error={!!errors.password}
                      helperText={errors.password}
                      margin="normal"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LockIcon color="action" />
                          </InputAdornment>
                        ),
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowPassword(!showPassword)}
                              edge="end"
                            >
                              {showPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        )
                      }}
                    />

                    <Button
                      type="submit"
                      fullWidth
                      variant="contained"
                      size="large"
                      disabled={loading}
                      sx={{ mt: 3, mb: 2, py: 1.5 }}
                    >
                      {loading ? <CircularProgress size={24} /> : 'Login'}
                    </Button>

                    <Box textAlign="center">
                      <Link
                        component="button"
                        variant="body2"
                        onClick={() => setShowForgotPassword(true)}
                        sx={{ textDecoration: 'none' }}
                      >
                        Forgot Password?
                      </Link>
                    </Box>
                  </motion.div>
                )}

                {/* Register Form */}
                {activeTab === 1 && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <TextField
                      fullWidth
                      label="Full Name"
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      error={!!errors.name}
                      helperText={errors.name}
                      margin="normal"
                    />

                    <TextField
                      fullWidth
                      label="Email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      error={!!errors.email}
                      helperText={errors.email}
                      margin="normal"
                    />

                    <TextField
                      fullWidth
                      label="Phone Number"
                      value={formData.phone}
                      onChange={(e) => handleInputChange('phone', e.target.value)}
                      margin="normal"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <PhoneIcon color="action" />
                          </InputAdornment>
                        )
                      }}
                    />

                    <TextField
                      fullWidth
                      label="Password"
                      type={showPassword ? 'text' : 'password'}
                      value={formData.password}
                      onChange={(e) => handleInputChange('password', e.target.value)}
                      error={!!errors.password}
                      helperText={errors.password}
                      margin="normal"
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowPassword(!showPassword)}
                              edge="end"
                            >
                              {showPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        )
                      }}
                    />

                    <TextField
                      fullWidth
                      label="Confirm Password"
                      type="password"
                      value={formData.confirmPassword}
                      onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                      error={!!errors.confirmPassword}
                      helperText={errors.confirmPassword}
                      margin="normal"
                    />

                    {/* User Type Selection */}
                    <Typography variant="h6" sx={{ mt: 3, mb: 2 }}>
                      Select User Type
                    </Typography>
                    <Box
                      sx={{
                        display: 'grid',
                        gridTemplateColumns: { xs: 'repeat(2, 1fr)', sm: 'repeat(3, 1fr)' },
                        gap: 1
                      }}
                    >
                      {userTypes.map((type) => (
                        <UserTypeCard
                          key={type.value}
                          type={type}
                          selected={formData.userType === type.value}
                          onClick={() => handleInputChange('userType', type.value)}
                        />
                      ))}
                    </Box>
                    {errors.userType && (
                      <Typography color="error" variant="body2" sx={{ mt: 1 }}>
                        {errors.userType}
                      </Typography>
                    )}

                    {/* Independent Learner Additional Fields */}
                    {formData.userType === 'independent_learner' && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        transition={{ duration: 0.3 }}
                      >
                        <FormControl fullWidth margin="normal" error={!!errors.category}>
                          <InputLabel>Category</InputLabel>
                          <Select
                            value={formData.category}
                            onChange={(e) => handleInputChange('category', e.target.value)}
                          >
                            {learnerCategories.map((category) => (
                              <MenuItem key={category} value={category}>
                                {category}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>

                        <FormControl fullWidth margin="normal" error={!!errors.educationLevel}>
                          <InputLabel>Education Level</InputLabel>
                          <Select
                            value={formData.educationLevel}
                            onChange={(e) => handleInputChange('educationLevel', e.target.value)}
                          >
                            {educationLevels.map((level) => (
                              <MenuItem key={level} value={level}>
                                {level}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>

                        <Alert severity="info" sx={{ mt: 2 }}>
                          <Typography variant="body2">
                            🎉 <strong>Special Offer:</strong> Get your referral code and earn ₹100 for each successful referral!
                          </Typography>
                        </Alert>
                      </motion.div>
                    )}

                    {/* Enhanced Security Options */}
                    <Box sx={{ mt: 3 }}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={formData.enable2FA}
                            onChange={(e) => handleInputChange('enable2FA', e.target.checked)}
                          />
                        }
                        label={
                          <Box display="flex" alignItems="center">
                            <SecurityIcon sx={{ mr: 1, fontSize: 20 }} />
                            <Typography variant="body2">
                              Enable Two-Factor Authentication (Recommended)
                            </Typography>
                          </Box>
                        }
                      />

                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={formData.agreeTerms}
                            onChange={(e) => handleInputChange('agreeTerms', e.target.checked)}
                            required
                          />
                        }
                        label={
                          <Typography variant="body2">
                            I agree to the{' '}
                            <Link href="#" underline="hover">Terms of Service</Link>
                            {' '}and{' '}
                            <Link href="#" underline="hover">Privacy Policy</Link>
                          </Typography>
                        }
                      />
                    </Box>

                    <Button
                      type="submit"
                      fullWidth
                      variant="contained"
                      size="large"
                      disabled={loading || !formData.agreeTerms}
                      sx={{ mt: 3, mb: 2, py: 1.5 }}
                    >
                      {loading ? <CircularProgress size={24} /> : 'Create Account'}
                    </Button>

                    <Box textAlign="center">
                      <Button
                        variant="text"
                        startIcon={<EmailIcon />}
                        onClick={() => setShowEmailVerification(true)}
                        size="small"
                      >
                        Verify Email Address
                      </Button>
                    </Box>
                  </motion.div>
                )}
              </form>

              {/* Social Login */}
              <Divider sx={{ my: 2 }}>
                <Chip label="OR" size="small" />
              </Divider>

              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                <IconButton sx={{ bgcolor: '#4285f4', color: 'white', '&:hover': { bgcolor: '#3367d6' } }}>
                  <GoogleIcon />
                </IconButton>
                <IconButton sx={{ bgcolor: '#1877f2', color: 'white', '&:hover': { bgcolor: '#166fe5' } }}>
                  <FacebookIcon />
                </IconButton>
                <IconButton sx={{ bgcolor: '#333', color: 'white', '&:hover': { bgcolor: '#24292e' } }}>
                  <GitHubIcon />
                </IconButton>
              </Box>

              {/* Footer */}
              <Box sx={{ textAlign: 'center', mt: 3 }}>
                <Typography variant="body2" color="textSecondary">
                  By continuing, you agree to our Terms of Service and Privacy Policy
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </motion.div>

      {/* Two-Factor Authentication Dialog */}
      <Dialog open={show2FA} onClose={() => setShow2FA(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center">
            <SecurityIcon sx={{ mr: 2 }} />
            Two-Factor Authentication
          </Box>
        </DialogTitle>
        <DialogContent>
          <Stepper activeStep={twoFactorStep} orientation="vertical">
            <Step>
              <StepLabel>Choose Authentication Method</StepLabel>
              <StepContent>
                <Box>
                  <FormControl fullWidth>
                    <InputLabel>Authentication Method</InputLabel>
                    <Select
                      value={twoFactorData.method}
                      onChange={(e) => setTwoFactorData({
                        ...twoFactorData,
                        method: e.target.value as any
                      })}
                    >
                      <MenuItem value="2fa_app">
                        <Box display="flex" alignItems="center">
                          <QrCodeIcon sx={{ mr: 1 }} />
                          Authenticator App (Recommended)
                        </Box>
                      </MenuItem>
                      <MenuItem value="sms">
                        <Box display="flex" alignItems="center">
                          <SmsIcon sx={{ mr: 1 }} />
                          SMS Text Message
                        </Box>
                      </MenuItem>
                      <MenuItem value="email">
                        <Box display="flex" alignItems="center">
                          <EmailIcon sx={{ mr: 1 }} />
                          Email Verification
                        </Box>
                      </MenuItem>
                    </Select>
                  </FormControl>
                </Box>
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    onClick={() => setTwoFactorStep(1)}
                    sx={{ mr: 1 }}
                  >
                    Continue
                  </Button>
                </Box>
              </StepContent>
            </Step>

            <Step>
              <StepLabel>Setup Authentication</StepLabel>
              <StepContent>
                {twoFactorData.method === '2fa_app' && (
                  <Box textAlign="center">
                    <Typography variant="body2" gutterBottom>
                      Scan this QR code with your authenticator app:
                    </Typography>
                    <Box sx={{ p: 2, border: '1px dashed #ccc', borderRadius: 2, mb: 2 }}>
                      {qrCodeUrl ? (
                        <img src={qrCodeUrl} alt="2FA QR Code" style={{ maxWidth: '200px' }} />
                      ) : (
                        <Box sx={{ width: 200, height: 200, bgcolor: 'grey.100', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <QrCodeIcon sx={{ fontSize: 60, color: 'grey.400' }} />
                        </Box>
                      )}
                    </Box>
                    <Alert severity="info" sx={{ mb: 2 }}>
                      Recommended apps: Google Authenticator, Authy, Microsoft Authenticator
                    </Alert>
                  </Box>
                )}

                {twoFactorData.method === 'sms' && (
                  <Alert severity="info" sx={{ mb: 2 }}>
                    We'll send a verification code to your phone number: {formData.phone}
                  </Alert>
                )}

                {twoFactorData.method === 'email' && (
                  <Alert severity="info" sx={{ mb: 2 }}>
                    We'll send a verification code to your email: {formData.email}
                  </Alert>
                )}

                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    onClick={() => setTwoFactorStep(2)}
                    sx={{ mr: 1 }}
                  >
                    Next
                  </Button>
                  <Button onClick={() => setTwoFactorStep(0)}>
                    Back
                  </Button>
                </Box>
              </StepContent>
            </Step>

            <Step>
              <StepLabel>Verify Code</StepLabel>
              <StepContent>
                <TextField
                  fullWidth
                  label="Enter Verification Code"
                  value={twoFactorData.code}
                  onChange={(e) => setTwoFactorData({
                    ...twoFactorData,
                    code: e.target.value
                  })}
                  inputProps={{ maxLength: 6, style: { textAlign: 'center', fontSize: '1.5rem', letterSpacing: '0.5rem' } }}
                  margin="normal"
                />

                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    onClick={verify2FA}
                    disabled={twoFactorData.code.length !== 6}
                    sx={{ mr: 1 }}
                  >
                    Verify & Complete
                  </Button>
                  <Button onClick={() => setTwoFactorStep(1)}>
                    Back
                  </Button>
                </Box>
              </StepContent>
            </Step>
          </Stepper>
        </DialogContent>
      </Dialog>

      {/* Forgot Password Dialog */}
      <Dialog open={showForgotPassword} onClose={() => setShowForgotPassword(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Reset Password</DialogTitle>
        <DialogContent>
          <Typography variant="body2" gutterBottom>
            Enter your email address and we'll send you a link to reset your password.
          </Typography>
          <TextField
            fullWidth
            label="Email Address"
            type="email"
            value={formData.email}
            onChange={(e) => handleInputChange('email', e.target.value)}
            margin="normal"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <EmailIcon />
                </InputAdornment>
              )
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowForgotPassword(false)}>Cancel</Button>
          <Button onClick={sendPasswordReset} variant="contained" startIcon={<SendIcon />}>
            Send Reset Link
          </Button>
        </DialogActions>
      </Dialog>

      {/* Email Verification Dialog */}
      <Dialog open={showEmailVerification} onClose={() => setShowEmailVerification(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Email Verification</DialogTitle>
        <DialogContent>
          <Typography variant="body2" gutterBottom>
            We'll send a verification code to your email address.
          </Typography>
          <TextField
            fullWidth
            label="Email Address"
            type="email"
            value={formData.email}
            onChange={(e) => handleInputChange('email', e.target.value)}
            margin="normal"
          />

          {countdown > 0 && (
            <Alert severity="success" sx={{ mt: 2 }}>
              <Box display="flex" alignItems="center">
                <TimerIcon sx={{ mr: 1 }} />
                Verification email sent! Resend in {countdown} seconds
              </Box>
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowEmailVerification(false)}>Cancel</Button>
          <Button
            onClick={sendEmailVerification}
            variant="contained"
            startIcon={countdown > 0 ? <RefreshIcon /> : <SendIcon />}
            disabled={countdown > 0}
          >
            {countdown > 0 ? 'Resend' : 'Send Verification'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AuthenticationPages;
