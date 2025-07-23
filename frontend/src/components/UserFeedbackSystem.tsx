import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Rating,
  Chip,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Fab,
  Slide,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  LinearProgress,
  IconButton,
  Tooltip,
  Snackbar
} from '@mui/material';
import {
  Feedback as FeedbackIcon,
  Send as SendIcon,
  Close as CloseIcon,
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  BugReport as BugIcon,
  Lightbulb as IdeaIcon,
  Star as StarIcon,
  Comment as CommentIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface Feedback {
  id: string;
  type: 'bug' | 'feature' | 'improvement' | 'general';
  rating: number;
  title: string;
  description: string;
  category: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'reviewed' | 'in_progress' | 'completed';
  userEmail: string;
  userName: string;
  timestamp: string;
  helpful: number;
  screenshots?: string[];
}

interface FeedbackStats {
  totalFeedback: number;
  averageRating: number;
  typeDistribution: { [key: string]: number };
  recentFeedback: Feedback[];
}

const UserFeedbackSystem: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [feedbackType, setFeedbackType] = useState<'bug' | 'feature' | 'improvement' | 'general'>('general');
  const [rating, setRating] = useState<number>(5);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [feedbackStats, setFeedbackStats] = useState<FeedbackStats | null>(null);
  const [showStats, setShowStats] = useState(false);

  const categories = [
    'User Interface',
    'Performance',
    'Payment System',
    'Exam System',
    'Dashboard',
    'Authentication',
    'Mobile Experience',
    'Documentation',
    'Other'
  ];

  const feedbackTypes = [
    { value: 'bug', label: 'Bug Report', icon: <BugIcon />, color: '#f44336' },
    { value: 'feature', label: 'Feature Request', icon: <IdeaIcon />, color: '#2196f3' },
    { value: 'improvement', label: 'Improvement', icon: <ThumbUpIcon />, color: '#ff9800' },
    { value: 'general', label: 'General Feedback', icon: <CommentIcon />, color: '#4caf50' }
  ];

  useEffect(() => {
    loadFeedbackStats();
  }, []);

  const loadFeedbackStats = async () => {
    try {
      const response = await fetch('/api/v1/feedback/stats', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const stats = await response.json();
      setFeedbackStats(stats);
    } catch (error) {
      console.error('Error loading feedback stats:', error);
    }
  };

  const handleSubmit = async () => {
    if (!title.trim() || !description.trim()) {
      return;
    }

    setSubmitting(true);
    try {
      const feedbackData = {
        type: feedbackType,
        rating,
        title: title.trim(),
        description: description.trim(),
        category,
        priority,
        userEmail: email,
        userName: name
      };

      const response = await fetch('/api/v1/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(feedbackData)
      });

      if (response.ok) {
        setShowSuccess(true);
        resetForm();
        setOpen(false);
        loadFeedbackStats();
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setFeedbackType('general');
    setRating(5);
    setTitle('');
    setDescription('');
    setCategory('');
    setPriority('medium');
  };

  const FeedbackTypeCard: React.FC<{ type: any; selected: boolean; onClick: () => void }> = 
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

  const FeedbackStatsCard: React.FC = () => (
    <Card sx={{ mt: 2 }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <AnalyticsIcon sx={{ mr: 1 }} />
          <Typography variant="h6">Feedback Analytics</Typography>
        </Box>
        
        {feedbackStats && (
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography variant="body2" color="textSecondary">
                Total Feedback
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {feedbackStats.totalFeedback}
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="textSecondary">
                Average Rating
              </Typography>
              <Box display="flex" alignItems="center">
                <Typography variant="h4" fontWeight="bold" sx={{ mr: 1 }}>
                  {feedbackStats.averageRating.toFixed(1)}
                </Typography>
                <Rating value={feedbackStats.averageRating} readOnly size="small" />
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Feedback Distribution
              </Typography>
              {Object.entries(feedbackStats.typeDistribution).map(([type, count]) => (
                <Box key={type} display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                    {type}
                  </Typography>
                  <Box display="flex" alignItems="center">
                    <LinearProgress 
                      variant="determinate" 
                      value={(count / feedbackStats.totalFeedback) * 100}
                      sx={{ width: 60, mr: 1 }}
                    />
                    <Typography variant="body2">{count}</Typography>
                  </Box>
                </Box>
              ))}
            </Grid>
          </Grid>
        )}
      </CardContent>
    </Card>
  );

  return (
    <>
      {/* Floating Feedback Button */}
      <Fab
        color="primary"
        aria-label="feedback"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          zIndex: 1000
        }}
        onClick={() => setOpen(true)}
      >
        <FeedbackIcon />
      </Fab>

      {/* Feedback Dialog */}
      <Dialog 
        open={open} 
        onClose={() => setOpen(false)} 
        maxWidth="md" 
        fullWidth
        TransitionComponent={Slide}
        TransitionProps={{ direction: 'up' }}
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center">
              <FeedbackIcon sx={{ mr: 2 }} />
              <Typography variant="h6">Share Your Feedback</Typography>
            </Box>
            <IconButton onClick={() => setOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {/* Feedback Type Selection */}
          <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
            What type of feedback do you have?
          </Typography>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            {feedbackTypes.map((type) => (
              <Grid item xs={6} sm={3} key={type.value}>
                <FeedbackTypeCard
                  type={type}
                  selected={feedbackType === type.value}
                  onClick={() => setFeedbackType(type.value as any)}
                />
              </Grid>
            ))}
          </Grid>

          {/* Rating */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="body1" gutterBottom>
              How would you rate your overall experience?
            </Typography>
            <Box display="flex" alignItems="center">
              <Rating
                value={rating}
                onChange={(event, newValue) => setRating(newValue || 5)}
                size="large"
              />
              <Typography variant="body2" sx={{ ml: 2 }}>
                {rating === 5 ? 'Excellent' : 
                 rating === 4 ? 'Good' : 
                 rating === 3 ? 'Average' : 
                 rating === 2 ? 'Poor' : 'Very Poor'}
              </Typography>
            </Box>
          </Box>

          {/* Title */}
          <TextField
            fullWidth
            label="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            margin="normal"
            placeholder="Brief summary of your feedback"
            required
          />

          {/* Description */}
          <TextField
            fullWidth
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            margin="normal"
            multiline
            rows={4}
            placeholder="Please provide detailed feedback..."
            required
          />

          {/* Category and Priority */}
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                >
                  {categories.map((cat) => (
                    <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as any)}
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          {/* Contact Information */}
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            Contact Information (Optional)
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Your Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email Address"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                margin="normal"
              />
            </Grid>
          </Grid>

          <Alert severity="info" sx={{ mt: 2 }}>
            Your feedback helps us improve MEDHASAKTHI. We read every submission and use your input to enhance the platform.
          </Alert>

          {/* Show Stats Toggle */}
          <Box textAlign="center" sx={{ mt: 2 }}>
            <Button
              variant="text"
              startIcon={<AnalyticsIcon />}
              onClick={() => setShowStats(!showStats)}
            >
              {showStats ? 'Hide' : 'Show'} Feedback Analytics
            </Button>
          </Box>

          {/* Feedback Stats */}
          <AnimatePresence>
            {showStats && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
              >
                <FeedbackStatsCard />
              </motion.div>
            )}
          </AnimatePresence>
        </DialogContent>

        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={submitting || !title.trim() || !description.trim()}
            startIcon={submitting ? <LinearProgress /> : <SendIcon />}
          >
            {submitting ? 'Submitting...' : 'Submit Feedback'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Snackbar */}
      <Snackbar
        open={showSuccess}
        autoHideDuration={6000}
        onClose={() => setShowSuccess(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      >
        <Alert 
          onClose={() => setShowSuccess(false)} 
          severity="success" 
          sx={{ width: '100%' }}
        >
          Thank you for your feedback! We'll review it and get back to you if needed.
        </Alert>
      </Snackbar>
    </>
  );
};

export default UserFeedbackSystem;
