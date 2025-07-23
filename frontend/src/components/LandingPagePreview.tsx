import React from 'react';
import {
  Box,
  Typography,
  Button,
  Container,
  Grid,
  Card,
  CardContent,
  Chip,
  Stack,
  Avatar
} from '@mui/material';
import {
  PersonOutline as StudentIcon,
  Business as BusinessIcon,
  Launch as LaunchIcon,
  CheckCircle as CheckIcon,
  Star as StarIcon
} from '@mui/icons-material';

/**
 * Landing Page Preview Component
 * This shows a simplified preview of the new MEDHASAKTHI landing page
 * with category selection for single domain setup
 */
const LandingPagePreview: React.FC = () => {
  const handlePortalSelect = (portalType: string) => {
    alert(`Redirecting to ${portalType} portal...`);
  };

  return (
    <Box>
      {/* Hero Section Preview */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          py: 8,
          minHeight: '80vh',
          display: 'flex',
          alignItems: 'center'
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
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
              <Typography variant="h2" component="h1" gutterBottom fontWeight="bold">
                MEDHASAKTHI
                <Typography component="span" variant="h3" sx={{ color: '#FFD700', display: 'block' }}>
                  AI-Powered Education Platform
                </Typography>
              </Typography>
              <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
                🤖 AI Question Generation • 💳 Zero-Fee Payments • 📊 Real-Time Analytics • 🔒 Enterprise Security
              </Typography>
              
              {/* Category Selection Buttons */}
              <Box sx={{ mb: 4 }}>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                  Choose Your Portal:
                </Typography>
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                  <Button
                    variant="contained"
                    size="large"
                    sx={{ 
                      bgcolor: '#FFD700', 
                      color: 'black',
                      '&:hover': { bgcolor: '#FFC107' },
                      px: 4,
                      py: 2,
                      borderRadius: 3,
                      fontWeight: 'bold'
                    }}
                    startIcon={<StudentIcon />}
                    onClick={() => handlePortalSelect('Student')}
                  >
                    Student Portal
                  </Button>
                  <Button
                    variant="contained"
                    size="large"
                    sx={{ 
                      bgcolor: '#4CAF50', 
                      color: 'white',
                      '&:hover': { bgcolor: '#45a049' },
                      px: 4,
                      py: 2,
                      borderRadius: 3,
                      fontWeight: 'bold'
                    }}
                    startIcon={<BusinessIcon />}
                    onClick={() => handlePortalSelect('Institute')}
                  >
                    Institute Portal
                  </Button>
                </Stack>
              </Box>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card 
                elevation={20} 
                sx={{ 
                  p: 4, 
                  borderRadius: 4,
                  background: 'rgba(255,255,255,0.95)',
                  color: 'text.primary'
                }}
              >
                <Typography variant="h5" gutterBottom color="primary" textAlign="center" fontWeight="bold">
                  🎯 Platform Highlights
                </Typography>
                <Grid container spacing={3}>
                  {[
                    { value: '100+', label: 'AI-Generated Questions', color: '#FF6B6B' },
                    { value: '₹0', label: 'Transaction Fees', color: '#4CAF50' },
                    { value: '99.9%', label: 'System Uptime', color: '#2196F3' },
                    { value: '24/7', label: 'Support Available', color: '#9C27B0' }
                  ].map((stat, index) => (
                    <Grid item xs={6} key={index}>
                      <Box textAlign="center">
                        <Typography variant="h3" fontWeight="bold" sx={{ color: stat.color, mb: 1 }}>
                          {stat.value}
                        </Typography>
                        <Typography variant="body1" fontWeight="medium">{stat.label}</Typography>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
                
                <Box textAlign="center" sx={{ mt: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mb: 1 }}>
                    {[1,2,3,4,5].map((star) => (
                      <StarIcon key={star} sx={{ color: '#FFD700', fontSize: 24 }} />
                    ))}
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    5.0 Rating • 1000+ Happy Users
                  </Typography>
                </Box>
              </Card>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Portal Categories Preview */}
      <Box sx={{ py: 6, bgcolor: 'grey.50' }}>
        <Container maxWidth="lg">
          <Typography variant="h3" component="h2" textAlign="center" gutterBottom fontWeight="bold">
            Choose Your Learning Journey
          </Typography>
          <Typography variant="h6" textAlign="center" color="text.secondary" sx={{ mb: 4 }}>
            Select the portal that best fits your educational needs
          </Typography>

          <Grid container spacing={4}>
            {[
              {
                title: 'Student Portal',
                subtitle: 'Access exams, courses & certificates',
                icon: <StudentIcon sx={{ fontSize: 48 }} />,
                gradient: 'linear-gradient(135deg, #2196F3 0%, #21CBF3 100%)',
                features: ['Take AI-powered exams', 'Track performance', 'Earn certificates', 'Mobile & Web access'],
                platform: 'Web & Mobile'
              },
              {
                title: 'Institute Portal',
                subtitle: 'Manage students, exams & analytics',
                icon: <BusinessIcon sx={{ fontSize: 48 }} />,
                gradient: 'linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%)',
                features: ['Manage students & teachers', 'Create custom exams', 'Advanced analytics', 'Bulk operations'],
                platform: 'Web Portal'
              }
            ].map((category, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card 
                  sx={{ 
                    height: '100%',
                    background: category.gradient,
                    color: 'white',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: '0 20px 40px rgba(0,0,0,0.2)'
                    }
                  }}
                  onClick={() => handlePortalSelect(category.title)}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                      <Box sx={{ color: 'white', mr: 2 }}>
                        {category.icon}
                      </Box>
                      <Box>
                        <Typography variant="h4" fontWeight="bold">
                          {category.title}
                        </Typography>
                        <Typography variant="body1" sx={{ opacity: 0.9 }}>
                          {category.subtitle}
                        </Typography>
                      </Box>
                    </Box>

                    <Box sx={{ mb: 3 }}>
                      {category.features.map((feature, idx) => (
                        <Box key={idx} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <CheckIcon sx={{ color: 'white', fontSize: 20, mr: 1 }} />
                          <Typography variant="body2" color="white">
                            {feature}
                          </Typography>
                        </Box>
                      ))}
                    </Box>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Chip 
                        label={category.platform}
                        sx={{ 
                          bgcolor: 'rgba(255,255,255,0.2)', 
                          color: 'white',
                          fontWeight: 'bold'
                        }}
                      />
                      <Button
                        variant="contained"
                        sx={{ 
                          bgcolor: 'white', 
                          color: '#2196F3',
                          '&:hover': { bgcolor: 'grey.100' },
                          fontWeight: 'bold'
                        }}
                        endIcon={<LaunchIcon />}
                      >
                        Access Portal
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPagePreview;
