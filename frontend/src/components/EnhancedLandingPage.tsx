import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Container,
  Card,
  CardContent,
  Chip,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Avatar,
  Rating,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Fade,
  Slide,
  Zoom,
  Divider,
  Stack,
  Badge
} from '@mui/material';
import {
  Payment as PaymentIcon,
  School as SchoolIcon,
  Security as SecurityIcon,
  Analytics as AnalyticsIcon,
  CheckCircle as CheckIcon,
  Star as StarIcon,
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayIcon,
  TrendingUp as TrendingUpIcon,
  MonetizationOn as MoneyIcon,
  People as PeopleIcon,
  AutoAwesome as AIIcon,
  Psychology as BrainIcon,
  Speed as SpeedIcon,
  CloudDone as CloudIcon,
  ArrowForward as ArrowForwardIcon,
  Business as BusinessIcon,
  PersonOutline as StudentIcon,
  AdminPanelSettings as AdminIcon,
  Smartphone as MobileIcon,
  Web as WebIcon,
  Launch as LaunchIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

// Import splash screen components
import SplashScreen from './SplashScreen';
import { useSplashScreen } from '../hooks/useSplashScreen';
import { getSplashConfig } from '../config/splashConfig';

const EnhancedLandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [demoDialog, setDemoDialog] = useState(false);
  const [userType, setUserType] = useState('');
  const [loginDialog, setLoginDialog] = useState(false);
  const [selectedUserCategory, setSelectedUserCategory] = useState('');
  const [showAnimations, setShowAnimations] = useState(false);

  // Landing page splash screen
  const splashConfig = getSplashConfig('app');
  const splash = useSplashScreen({
    duration: splashConfig.duration,
    showOnFirstVisit: true,
    showOnRouteChange: false
  });

  // Trigger animations on component mount
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowAnimations(true);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  // User categories for login selection
  const userCategories = [
    {
      id: 'student',
      title: 'Student',
      subtitle: 'Institutional students',
      icon: <StudentIcon sx={{ fontSize: 40 }} />,
      color: '#2196F3',
      gradient: 'linear-gradient(135deg, #2196F3 0%, #21CBF3 100%)',
      description: 'Students enrolled in educational institutions',
      redirectUrl: process.env.REACT_APP_STUDENT_URL || 'https://student.medhasakthi.com'
    },
    {
      id: 'teacher',
      title: 'Teacher',
      subtitle: 'Educational instructors',
      icon: <SchoolIcon sx={{ fontSize: 40 }} />,
      color: '#4CAF50',
      gradient: 'linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%)',
      description: 'Teachers and educational staff',
      redirectUrl: process.env.REACT_APP_TEACHER_URL || 'https://teacher.medhasakthi.com'
    },
    {
      id: 'institute_admin',
      title: 'Institute Admin',
      subtitle: 'Institution management',
      icon: <BusinessIcon sx={{ fontSize: 40 }} />,
      color: '#FF9800',
      gradient: 'linear-gradient(135deg, #FF9800 0%, #FFB74D 100%)',
      description: 'Institute administrators and staff',
      redirectUrl: process.env.REACT_APP_ADMIN_URL || 'https://admin.medhasakthi.com'
    },
    {
      id: 'independent_learner',
      title: 'Independent Learner',
      subtitle: 'Individual learners',
      icon: <StudentIcon sx={{ fontSize: 40 }} />,
      color: '#9C27B0',
      gradient: 'linear-gradient(135deg, #9C27B0 0%, #BA68C8 100%)',
      description: 'Self-paced learners and professionals',
      redirectUrl: process.env.REACT_APP_LEARN_URL || 'https://learn.medhasakthi.com'
    }
  ];

  const worldClassFeatures = [
    {
      icon: <AIIcon sx={{ fontSize: 50, color: '#FF6B6B' }} />,
      title: 'AI-Powered Question Generation',
      description: 'Advanced AI creates unlimited, contextual questions tailored to each subject and difficulty level.',
      highlight: 'Smart AI Engine',
      stats: 'Unlimited Questions'
    },
    {
      icon: <PaymentIcon sx={{ fontSize: 50, color: '#4CAF50' }} />,
      title: 'Zero-Fee UPI Payments',
      description: 'Complete payment ecosystem with QR codes, 6 UPI providers, and absolutely zero transaction fees.',
      highlight: '0% Transaction Fees',
      stats: '6 Payment Providers'
    },
    {
      icon: <SpeedIcon sx={{ fontSize: 50, color: '#2196F3' }} />,
      title: 'Real-Time Performance Analytics',
      description: 'Instant insights with advanced analytics, performance tracking, and predictive learning paths.',
      highlight: 'Live Analytics',
      stats: 'Real-Time Insights'
    },
    {
      icon: <SecurityIcon sx={{ fontSize: 50, color: '#FF9800' }} />,
      title: 'Enterprise-Grade Security',
      description: 'Bank-level security with JWT authentication, encrypted data, and role-based access controls.',
      highlight: 'Military-Grade Security',
      stats: 'ISO 27001 Compliant'
    },
    {
      icon: <CloudIcon sx={{ fontSize: 50, color: '#9C27B0' }} />,
      title: 'Cloud-Native Architecture',
      description: 'Scalable microservices architecture with auto-scaling, load balancing, and 99.9% uptime.',
      highlight: '99.9% Uptime',
      stats: 'Auto-Scaling'
    },
    {
      icon: <BrainIcon sx={{ fontSize: 50, color: '#00BCD4' }} />,
      title: 'Adaptive Learning System',
      description: 'Personalized learning paths that adapt to student performance and learning patterns.',
      highlight: 'Personalized Learning',
      stats: 'AI-Driven Adaptation'
    },
    {
      icon: <TrendingUpIcon sx={{ fontSize: 50, color: '#4CAF50' }} />,
      title: 'Performance Growth Tracking',
      description: 'Track student progress with detailed analytics and growth metrics over time.',
      highlight: 'Growth Analytics',
      stats: '360° Performance View'
    },
    {
      icon: <MoneyIcon sx={{ fontSize: 50, color: '#FF9800' }} />,
      title: 'Revenue Management',
      description: 'Complete financial dashboard with revenue tracking, payment analytics, and profit insights.',
      highlight: 'Financial Insights',
      stats: 'Revenue Optimization'
    },
    {
      icon: <PeopleIcon sx={{ fontSize: 50, color: '#9C27B0' }} />,
      title: 'Community Learning',
      description: 'Connect with peers, join study groups, and collaborate on learning objectives.',
      highlight: 'Social Learning',
      stats: 'Collaborative Platform'
    },
    {
      icon: <AnalyticsIcon sx={{ fontSize: 50, color: '#2196F3' }} />,
      title: 'Advanced Analytics Dashboard',
      description: 'Comprehensive analytics with predictive insights and performance forecasting.',
      highlight: 'Predictive Analytics',
      stats: 'AI-Powered Insights'
    }
  ];

  const implementationStats = [
    { value: '100+', label: 'AI-Generated Questions', color: '#FF6B6B' },
    { value: '₹0', label: 'Transaction Fees', color: '#4CAF50' },
    { value: '99.9%', label: 'System Uptime', color: '#2196F3' },
    { value: '24/7', label: 'Support Available', color: '#9C27B0' }
  ];

  const handleLoginClick = () => {
    setLoginDialog(true);
  };

  const handleUserCategorySelect = (category: { id: string; redirectUrl: string }) => {
    setSelectedUserCategory(category.id);
    setLoginDialog(false);

    // Redirect to appropriate portal based on user category
    window.location.href = category.redirectUrl;
  };

  const testimonials = [
    {
      name: 'Dr. Priya Sharma',
      role: 'Principal, Delhi Public School',
      avatar: 'P',
      rating: 5,
      comment: 'The UPI payment system is revolutionary! No more transaction fees and instant verification.'
    },
    {
      name: 'Rajesh Kumar',
      role: 'Independent Learner',
      avatar: 'R',
      rating: 5,
      comment: 'Earned ₹500 through referrals already! The platform is incredibly user-friendly.'
    },
    {
      name: 'Prof. Anita Desai',
      role: 'Computer Science Teacher',
      avatar: 'A',
      rating: 5,
      comment: 'The analytics dashboard provides insights I never had before. Game-changing!'
    }
  ];

  const pricingPlans = [
    {
      title: 'Student',
      price: '₹200',
      period: '/month',
      originalPrice: '₹300',
      discount: '33% OFF',
      features: [
        'Access to all courses',
        'Practice exams',
        'Performance analytics',
        'Digital certificates',
        'Email support'
      ],
      popular: false,
      color: '#2196F3'
    },
    {
      title: 'Independent Learner',
      price: '₹500',
      period: '/program',
      originalPrice: '₹800',
      discount: '37% OFF',
      features: [
        'Professional certifications',
        'Referral rewards (₹100 each)',
        'Dynamic pricing discounts',
        'Priority support',
        'Lifetime certificate access'
      ],
      popular: true,
      color: '#4CAF50'
    },
    {
      title: 'Institution',
      price: 'Custom',
      period: '/year',
      originalPrice: null,
      discount: 'Best Value',
      features: [
        'Unlimited students',
        'Bulk import tools',
        'Advanced analytics',
        'Custom branding',
        'Dedicated support'
      ],
      popular: false,
      color: '#FF9800'
    }
  ];

  const faqs = [
    {
      question: 'How does the 0% UPI fee system work?',
      answer: 'Our UPI system directly integrates with payment providers, eliminating middleman fees. You pay exactly what you see - no hidden charges!'
    },
    {
      question: 'What makes the referral program special?',
      answer: 'Earn ₹100 for each successful referral! Our system tracks referrals automatically and credits your account instantly upon successful enrollment.'
    },
    {
      question: 'Is the platform really production-ready?',
      answer: 'Yes! With 85+ implemented features, 35+ unit tests, and enterprise-grade monitoring, we\'re ready for immediate deployment.'
    },
    {
      question: 'How secure is my data?',
      answer: 'We use bank-level security with JWT authentication, encrypted data storage, and role-based access controls. Your data is completely safe.'
    }
  ];

  // Show splash screen on first visit to landing page
  if (splash.isVisible) {
    return (
      <SplashScreen
        onComplete={splash.hide}
        duration={splashConfig.duration}
        title={splashConfig.title}
        subtitle={splashConfig.subtitle}
        variant={splashConfig.variant}
        showProgress={splashConfig.showProgress}
      />
    );
  }

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          py: 10,
          position: 'relative',
          overflow: 'hidden',
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center'
        }}
      >
        {/* Animated background elements */}
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            opacity: 0.1,
            background: 'url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.1"%3E%3Ccircle cx="30" cy="30" r="4"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")'
          }}
        />

        <Container maxWidth="lg">
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 6, alignItems: 'center' }}>
            <Box>
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
              >
                <Fade in={showAnimations} timeout={1000}>
                  <Chip
                    label="🚀 Next-Generation AI Exam Platform"
                    sx={{
                      bgcolor: 'rgba(255,255,255,0.2)',
                      color: 'white',
                      mb: 3,
                      fontSize: '1rem',
                      py: 2
                    }}
                  />
                </Fade>
                <Slide direction="right" in={showAnimations} timeout={1200}>
                  <Typography variant="h1" component="h1" gutterBottom fontWeight="bold" sx={{ fontSize: { xs: '2.5rem', md: '3.5rem' } }}>
                    MEDHASAKTHI
                    <Typography component="span" variant="h2" sx={{ color: '#FFD700', display: 'block', fontSize: { xs: '1.8rem', md: '2.5rem' } }}>
                      AI-Powered Education Platform
                    </Typography>
                  </Typography>
                </Slide>
                <Typography variant="h6" sx={{ mb: 4, opacity: 0.9, lineHeight: 1.6 }}>
                  🤖 AI Question Generation • 💳 Zero-Fee Payments • 📊 Real-Time Analytics • 🔒 Enterprise Security
                </Typography>

                <Typography variant="body1" sx={{ mb: 4, opacity: 0.8, fontSize: '1.1rem' }}>
                  Join thousands of students, teachers, and institutions already using our platform to revolutionize education with AI-powered assessments.
                </Typography>

                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Zoom in={showAnimations} timeout={1500}>
                    <Button
                      variant="contained"
                      size="large"
                      sx={{
                        bgcolor: '#FFD700',
                        color: 'black',
                        '&:hover': { bgcolor: '#FFC107', transform: 'translateY(-2px)' },
                        px: 4,
                        py: 2,
                      borderRadius: 3,
                      fontWeight: 'bold',
                      fontSize: '1.1rem',
                      transition: 'all 0.3s ease'
                    }}
                    onClick={handleLoginClick}
                  >
                    Login / Sign Up
                  </Button>
                  </Zoom>
                  <Zoom in={showAnimations} timeout={1700}>
                    <Button
                    variant="outlined"
                    size="large"
                    sx={{
                      borderColor: 'white',
                      color: 'white',
                      '&:hover': { bgcolor: 'rgba(255,255,255,0.1)', transform: 'translateY(-2px)' },
                      px: 4,
                      py: 2,
                      borderRadius: 3,
                      fontWeight: 'bold',
                      transition: 'all 0.3s ease'
                    }}
                    startIcon={<PlayIcon />}
                    onClick={() => setDemoDialog(true)}
                  >
                    Watch Demo
                  </Button>
                  </Zoom>
                </Box>
              </motion.div>
            </Box>
            <Box>
              <motion.div
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.3 }}
              >
                <Paper
                  elevation={20}
                  sx={{
                    p: 4,
                    borderRadius: 4,
                    background: 'rgba(255,255,255,0.95)',
                    color: 'text.primary',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255,255,255,0.2)'
                  }}
                >
                  <Typography variant="h5" gutterBottom color="primary" textAlign="center" fontWeight="bold">
                    🎯 Platform Highlights
                  </Typography>
                  <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3 }}>
                    {implementationStats.map((stat, index) => (
                      <Box key={index}>
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                        >
                          <Box textAlign="center">
                            <Typography variant="h3" fontWeight="bold" sx={{ color: stat.color, mb: 1 }}>
                              {stat.value}
                            </Typography>
                            <Typography variant="body1" fontWeight="medium">{stat.label}</Typography>
                          </Box>
                        </motion.div>
                      </Box>
                    ))}
                  </Box>

                  <Divider sx={{ my: 3 }} />

                  <Box textAlign="center">
                    <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                      Trusted by educational institutions worldwide
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1 }}>
                      {[1,2,3,4,5].map((star) => (
                        <StarIcon key={star} sx={{ color: '#FFD700', fontSize: 24 }} />
                      ))}
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      5.0 Rating • 1000+ Happy Users
                    </Typography>
                  </Box>
                </Paper>
              </motion.div>
            </Box>
          </Box>
        </Container>
      </Box>



      {/* World-Class Features */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <Box textAlign="center" mb={6}>
            <Typography variant="h3" component="h2" gutterBottom fontWeight="bold">
              World-Class Features
            </Typography>
            <Typography variant="h6" color="textSecondary">
              Advanced AI-powered features that revolutionize education
            </Typography>
          </Box>
        </motion.div>
        
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 4 }}>
          {worldClassFeatures.map((feature, index) => (
            <Box key={index}>
              <Card 
                sx={{ 
                  height: '100%', 
                  transition: 'transform 0.3s, box-shadow 0.3s',
                  '&:hover': { 
                    transform: 'translateY(-8px)',
                    boxShadow: '0 12px 24px rgba(0,0,0,0.15)'
                  }
                }}
                elevation={4}
              >
                <CardContent sx={{ p: 4 }}>
                  <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                    {feature.icon}
                    <Box textAlign="right">
                      <Chip 
                        label={feature.highlight} 
                        color="primary" 
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="body2" color="textSecondary">
                        {feature.stats}
                      </Typography>
                    </Box>
                  </Box>
                  <Typography variant="h5" component="h3" gutterBottom fontWeight="bold">
                    {feature.title}
                  </Typography>
                  <Typography variant="body1" color="textSecondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          ))}
        </Box>
      </Container>

      {/* Pricing Section */}
      <Box sx={{ bgcolor: 'grey.50', py: 8 }}>
        <Container maxWidth="lg">
          <Box textAlign="center" mb={6}>
            <Typography variant="h3" component="h2" gutterBottom fontWeight="bold">
              Simple, Transparent Pricing
            </Typography>
            <Typography variant="h6" color="textSecondary">
              No hidden fees, no surprises. Pay only for what you use.
            </Typography>
          </Box>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 4, justifyContent: 'center' }}>
            {pricingPlans.map((plan, index) => (
              <Box key={index}>
                <Card 
                  sx={{ 
                    height: '100%',
                    position: 'relative',
                    border: plan.popular ? `3px solid ${plan.color}` : 'none',
                    transform: plan.popular ? 'scale(1.05)' : 'none',
                    transition: 'transform 0.3s'
                  }}
                  elevation={plan.popular ? 8 : 2}
                >
                  {plan.popular && (
                    <Chip 
                      label="Most Popular" 
                      color="primary" 
                      sx={{ 
                        position: 'absolute', 
                        top: -12, 
                        left: '50%', 
                        transform: 'translateX(-50%)',
                        bgcolor: plan.color
                      }}
                    />
                  )}
                  <CardContent sx={{ p: 4, textAlign: 'center' }}>
                    <Stack spacing={2} alignItems="center">
                      <Badge badgeContent="NEW" color="error" invisible={!plan.popular}>
                        <Typography variant="h5" gutterBottom fontWeight="bold">
                          {plan.title}
                        </Typography>
                      </Badge>
                      <Box mb={2}>
                        <Typography variant="h3" component="div" fontWeight="bold" sx={{ color: plan.color }}>
                          {plan.price}
                          <Typography component="span" variant="h6" color="textSecondary">
                            {plan.period}
                          </Typography>
                        </Typography>
                        {plan.originalPrice && (
                          <Typography variant="body2" sx={{ textDecoration: 'line-through' }}>
                            {plan.originalPrice}
                          </Typography>
                        )}
                        <Chip label={plan.discount} color="success" size="small" sx={{ mt: 1 }} />
                      </Box>
                    </Stack>
                    <List dense>
                      {plan.features.map((feature, idx) => (
                        <ListItem key={idx} sx={{ px: 0 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <CheckIcon color="success" fontSize="small" />
                          </ListItemIcon>
                          <ListItemText primary={feature} />
                        </ListItem>
                      ))}
                    </List>
                    <Button
                      variant={plan.popular ? "contained" : "outlined"}
                      fullWidth
                      size="large"
                      sx={{ 
                        mt: 3,
                        bgcolor: plan.popular ? plan.color : 'transparent',
                        borderColor: plan.color,
                        color: plan.popular ? 'white' : plan.color,
                        '&:hover': {
                          bgcolor: plan.popular ? plan.color : `${plan.color}20`
                        }
                      }}
                      onClick={() => navigate('/register')}
                    >
                      Get Started
                    </Button>
                  </CardContent>
                </Card>
              </Box>
            ))}
          </Box>
        </Container>
      </Box>

      {/* Testimonials */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Box textAlign="center" mb={6}>
          <Typography variant="h3" component="h2" gutterBottom fontWeight="bold">
            What Our Users Say
          </Typography>
          <Typography variant="h6" color="textSecondary">
            Real feedback from real users
          </Typography>
        </Box>
        
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 4 }}>
          {testimonials.map((testimonial, index) => (
            <Box key={index}>
              <Card sx={{ height: '100%' }} elevation={3}>
                <CardContent sx={{ p: 4 }}>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                      {testimonial.avatar}
                    </Avatar>
                    <Box>
                      <Typography variant="h6" fontWeight="bold">
                        {testimonial.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {testimonial.role}
                      </Typography>
                    </Box>
                  </Box>
                  <Rating value={testimonial.rating} readOnly sx={{ mb: 2 }} />
                  <Typography variant="body1" style={{ fontStyle: 'italic' }}>
                    "{testimonial.comment}"
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          ))}
        </Box>
      </Container>

      {/* FAQ Section */}
      <Box sx={{ bgcolor: 'grey.50', py: 8 }}>
        <Container maxWidth="md">
          <Box textAlign="center" mb={6}>
            <Typography variant="h3" component="h2" gutterBottom fontWeight="bold">
              Frequently Asked Questions
            </Typography>
          </Box>
          
          {faqs.map((faq, index) => (
            <Accordion key={index} sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6" fontWeight="bold">
                  {faq.question}
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body1">
                  {faq.answer}
                </Typography>
              </AccordionDetails>
            </Accordion>
          ))}
        </Container>
      </Box>

      {/* CTA Section */}
      <Box sx={{ bgcolor: 'primary.main', color: 'white', py: 8 }}>
        <Container maxWidth="md" sx={{ textAlign: 'center' }}>
          <Typography variant="h3" component="h2" gutterBottom fontWeight="bold">
            Ready to Go Live?
          </Typography>
          <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
            Join the world-class educational platform that's ready for production deployment today!
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              sx={{ 
                bgcolor: 'white', 
                color: 'primary.main',
                '&:hover': { bgcolor: 'grey.100' },
                px: 4,
                py: 1.5
              }}
              onClick={() => navigate('/register')}
            >
              Start Free Trial
            </Button>
            <Button
              variant="outlined"
              size="large"
              sx={{ 
                borderColor: 'white', 
                color: 'white',
                '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' },
                px: 4,
                py: 1.5
              }}
              onClick={() => navigate('/contact')}
            >
              Contact Sales
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Demo Dialog */}
      <Dialog open={demoDialog} onClose={() => setDemoDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Choose Your Demo Experience</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>I am a...</InputLabel>
            <Select
              value={userType}
              onChange={(e) => setUserType(e.target.value)}
            >
              <MenuItem value="student">Student</MenuItem>
              <MenuItem value="teacher">Teacher</MenuItem>
              <MenuItem value="admin">Administrator</MenuItem>
              <MenuItem value="learner">Independent Learner</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDemoDialog(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={() => {
              setDemoDialog(false);
              navigate(`/demo/${userType}`);
            }}
            disabled={!userType}
          >
            Start Demo
          </Button>
        </DialogActions>
      </Dialog>

      {/* Login Category Selection Dialog */}
      <Dialog
        open={loginDialog}
        onClose={() => setLoginDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 4,
            background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
          }
        }}
      >
        <DialogTitle sx={{ textAlign: 'center', pb: 1 }}>
          <IconButton
            onClick={() => setLoginDialog(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <CloseIcon />
          </IconButton>
          <Typography variant="h4" fontWeight="bold" color="primary">
            Login to MEDHASAKTHI
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Select your user type to continue
          </Typography>
        </DialogTitle>
        <DialogContent sx={{ px: 4, pb: 4 }}>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3 }}>
            {userCategories.map((category) => (
              <Box key={category.id}>
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Card
                    sx={{
                      cursor: 'pointer',
                      background: category.gradient,
                      color: 'white',
                      height: '100%',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 12px 24px rgba(0,0,0,0.15)'
                      }
                    }}
                    onClick={() => handleUserCategorySelect(category)}
                  >
                    <CardContent sx={{ p: 3, textAlign: 'center' }}>
                      <Box sx={{ mb: 2 }}>
                        {category.icon}
                      </Box>
                      <Typography variant="h5" fontWeight="bold" gutterBottom>
                        {category.title}
                      </Typography>
                      <Typography variant="body1" sx={{ opacity: 0.9, mb: 1 }}>
                        {category.subtitle}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.8, fontSize: '0.9rem' }}>
                        {category.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Box>
            ))}
          </Box>

          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Don't have an account? Registration is available after selecting your user type.
            </Typography>
          </Box>
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default EnhancedLandingPage;
