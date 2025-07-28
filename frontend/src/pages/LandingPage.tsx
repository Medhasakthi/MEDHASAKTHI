import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  Avatar,
  Chip,
  Paper,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  School as SchoolIcon,
  EmojiEvents as TrophyIcon,
  Psychology as AIIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Analytics as AnalyticsIcon,
  Star as StarIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const features = [
    {
      icon: <AIIcon sx={{ fontSize: 40 }} />,
      title: 'AI-Powered Learning',
      description: 'Advanced AI algorithms personalize your learning experience and generate intelligent questions.',
      color: '#667eea',
    },
    {
      icon: <TrophyIcon sx={{ fontSize: 40 }} />,
      title: 'Talent Exams',
      description: 'Comprehensive talent examination system for all educational levels and specializations.',
      color: '#f093fb',
    },
    {
      icon: <SecurityIcon sx={{ fontSize: 40 }} />,
      title: 'Enterprise Security',
      description: 'Military-grade security with advanced authentication and real-time monitoring.',
      color: '#4facfe',
    },
    {
      icon: <SpeedIcon sx={{ fontSize: 40 }} />,
      title: 'Lightning Fast',
      description: 'Sub-100ms response times globally with intelligent caching and optimization.',
      color: '#43e97b',
    },
    {
      icon: <AnalyticsIcon sx={{ fontSize: 40 }} />,
      title: 'Advanced Analytics',
      description: 'Comprehensive analytics and insights to track progress and identify improvement areas.',
      color: '#fa709a',
    },
    {
      icon: <SchoolIcon sx={{ fontSize: 40 }} />,
      title: 'Complete Curriculum',
      description: 'Full coverage of Indian education system from Class 1-12 to professional certifications.',
      color: '#fee140',
    },
  ];

  const testimonials = [
    {
      name: 'Dr. Priya Sharma',
      role: 'Principal, Delhi Public School',
      avatar: '/avatars/principal1.jpg',
      rating: 5,
      comment: 'MEDHASAKTHI has revolutionized how we conduct talent exams. The AI-powered question generation is incredible!',
    },
    {
      name: 'Rahul Kumar',
      role: 'Class 12 Student',
      avatar: '/avatars/student1.jpg',
      rating: 5,
      comment: 'The personalized learning experience helped me improve my scores by 40%. Best platform ever!',
    },
    {
      name: 'Prof. Anjali Gupta',
      role: 'Education Director',
      avatar: '/avatars/teacher1.jpg',
      rating: 5,
      comment: 'The comprehensive analytics and real-time monitoring features are game-changing for educators.',
    },
  ];

  const stats = [
    { value: '10,000+', label: 'Students' },
    { value: '500+', label: 'Institutes' },
    { value: '1M+', label: 'Questions' },
    { value: '99.9%', label: 'Uptime' },
  ];

  return (
    <Box>
      <Navbar />
      
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          py: { xs: 8, md: 12 },
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 4, alignItems: 'center' }}>
            <Box>
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
              >
                <Typography
                  variant="h2"
                  component="h1"
                  gutterBottom
                  sx={{
                    fontWeight: 700,
                    fontSize: { xs: '2.5rem', md: '3.5rem' },
                    lineHeight: 1.2,
                  }}
                >
                  World's Most Advanced
                  <br />
                  <span style={{ color: '#ffd700' }}>AI-Powered</span>
                  <br />
                  Educational Platform
                </Typography>
                <Typography
                  variant="h5"
                  sx={{
                    mb: 4,
                    opacity: 0.9,
                    fontSize: { xs: '1.2rem', md: '1.5rem' },
                  }}
                >
                  Revolutionizing talent exams with cutting-edge AI, personalized learning,
                  and enterprise-grade security for the next generation of learners.
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={() => navigate('/register')}
                    sx={{
                      bgcolor: 'white',
                      color: 'primary.main',
                      px: 4,
                      py: 1.5,
                      fontSize: '1.1rem',
                      '&:hover': {
                        bgcolor: 'grey.100',
                      },
                    }}
                    endIcon={<ArrowForwardIcon />}
                  >
                    Get Started Free
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={() => navigate('/login')}
                    sx={{
                      borderColor: 'white',
                      color: 'white',
                      px: 4,
                      py: 1.5,
                      fontSize: '1.1rem',
                      '&:hover': {
                        borderColor: 'white',
                        bgcolor: 'rgba(255,255,255,0.1)',
                      },
                    }}
                  >
                    Sign In
                  </Button>
                </Box>
              </motion.div>
            </Box>
            <Box>
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8, delay: 0.2 }}
              >
                <Box
                  component="img"
                  src="/images/hero-dashboard.png"
                  alt="MEDHASAKTHI Dashboard"
                  sx={{
                    width: '100%',
                    height: 'auto',
                    borderRadius: 2,
                    boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
                  }}
                />
              </motion.div>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* Stats Section */}
      <Box sx={{ py: 6, bgcolor: 'grey.50' }}>
        <Container maxWidth="lg">
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 4 }}>
            {stats.map((stat, index) => (
              <Box key={index}>
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <Box textAlign="center">
                    <Typography
                      variant="h3"
                      component="div"
                      sx={{
                        fontWeight: 700,
                        color: 'primary.main',
                        mb: 1,
                      }}
                    >
                      {stat.value}
                    </Typography>
                    <Typography variant="h6" color="textSecondary">
                      {stat.label}
                    </Typography>
                  </Box>
                </motion.div>
              </Box>
            ))}
          </Box>
        </Container>
      </Box>

      {/* Features Section */}
      <Box sx={{ py: 8 }}>
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <Typography
              variant="h3"
              component="h2"
              textAlign="center"
              gutterBottom
              sx={{ fontWeight: 700, mb: 2 }}
            >
              Why Choose MEDHASAKTHI?
            </Typography>
            <Typography
              variant="h6"
              textAlign="center"
              color="textSecondary"
              sx={{ mb: 6, maxWidth: 600, mx: 'auto' }}
            >
              Experience the future of education with our world-class features
              designed for excellence and innovation.
            </Typography>
          </motion.div>

          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 4 }}>
            {features.map((feature, index) => (
              <Box key={index}>
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <Card
                    sx={{
                      height: '100%',
                      transition: 'transform 0.3s ease-in-out',
                      '&:hover': {
                        transform: 'translateY(-8px)',
                      },
                    }}
                  >
                    <CardContent sx={{ p: 3 }}>
                      <Box
                        sx={{
                          width: 80,
                          height: 80,
                          borderRadius: 2,
                          background: `linear-gradient(135deg, ${feature.color}, ${feature.color}aa)`,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          mb: 3,
                        }}
                      >
                        {feature.icon}
                      </Box>
                      <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                        {feature.title}
                      </Typography>
                      <Typography variant="body1" color="textSecondary">
                        {feature.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Box>
            ))}
          </Box>
        </Container>
      </Box>

      {/* Testimonials Section */}
      <Box sx={{ py: 8, bgcolor: 'grey.50' }}>
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <Typography
              variant="h3"
              component="h2"
              textAlign="center"
              gutterBottom
              sx={{ fontWeight: 700, mb: 2 }}
            >
              What Our Users Say
            </Typography>
            <Typography
              variant="h6"
              textAlign="center"
              color="textSecondary"
              sx={{ mb: 6 }}
            >
              Join thousands of satisfied educators and students
            </Typography>
          </motion.div>

          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 4 }}>
            {testimonials.map((testimonial, index) => (
              <Box key={index}>
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.2 }}
                  viewport={{ once: true }}
                >
                  <Card sx={{ height: '100%' }}>
                    <CardContent sx={{ p: 3 }}>
                      <Box display="flex" alignItems="center" mb={2}>
                        <Avatar
                          src={testimonial.avatar}
                          sx={{ width: 60, height: 60, mr: 2 }}
                        >
                          {testimonial.name.charAt(0)}
                        </Avatar>
                        <Box>
                          <Typography variant="h6" sx={{ fontWeight: 600 }}>
                            {testimonial.name}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {testimonial.role}
                          </Typography>
                          <Box display="flex" mt={0.5}>
                            {[...Array(testimonial.rating)].map((_, i) => (
                              <StarIcon key={i} sx={{ color: '#ffd700', fontSize: 16 }} />
                            ))}
                          </Box>
                        </Box>
                      </Box>
                      <Typography variant="body1" sx={{ fontStyle: 'italic' }}>
                        "{testimonial.comment}"
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Box>
            ))}
          </Box>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box
        sx={{
          py: 8,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
        }}
      >
        <Container maxWidth="md">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <Box textAlign="center">
              <Typography
                variant="h3"
                component="h2"
                gutterBottom
                sx={{ fontWeight: 700, mb: 2 }}
              >
                Ready to Transform Education?
              </Typography>
              <Typography
                variant="h6"
                sx={{ mb: 4, opacity: 0.9 }}
              >
                Join the revolution and experience the future of learning today.
                Start your free trial and see the difference MEDHASAKTHI makes.
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={() => navigate('/register')}
                  sx={{
                    bgcolor: 'white',
                    color: 'primary.main',
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                    '&:hover': {
                      bgcolor: 'grey.100',
                    },
                  }}
                >
                  Start Free Trial
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  sx={{
                    borderColor: 'white',
                    color: 'white',
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                    '&:hover': {
                      borderColor: 'white',
                      bgcolor: 'rgba(255,255,255,0.1)',
                    },
                  }}
                >
                  Schedule Demo
                </Button>
              </Box>
            </Box>
          </motion.div>
        </Container>
      </Box>

      <Footer />
    </Box>
  );
};

export default LandingPage;
