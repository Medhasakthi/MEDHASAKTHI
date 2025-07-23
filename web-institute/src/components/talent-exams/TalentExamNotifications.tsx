/**
 * Talent Exam Notifications Component for Institutes
 * Displays notifications about talent exams and allows registration
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  Alert,
  Badge,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Divider,
  Avatar,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  School as SchoolIcon,
  Schedule as ScheduleIcon,
  Assignment as AssignmentIcon,
  TrendingUp as TrendingUpIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Visibility as ViewIcon,
  HowToReg as RegisterIcon,
  AccessTime as TimeIcon,
  CalendarToday as CalendarIcon,
  MonetizationOn as FeeIcon
} from '@mui/icons-material';
import { formatDistanceToNow, format } from 'date-fns';
import { toast } from 'react-hot-toast';

// Types
interface TalentExamNotification {
  id: string;
  title: string;
  message: string;
  notificationType: string;
  examId?: string;
  scheduledAt: string;
  sentAt?: string;
  status: string;
  isRead?: boolean;
  exam?: {
    id: string;
    title: string;
    examCode: string;
    classLevel: string;
    examDate: string;
    examTime: string;
    registrationEndDate: string;
    registrationFee: number;
    status: string;
  };
}

interface UpcomingExam {
  id: string;
  title: string;
  examCode: string;
  classLevel: string;
  examDate: string;
  examTime: string;
  registrationStartDate: string;
  registrationEndDate: string;
  registrationFee: number;
  status: string;
  durationMinutes: number;
  totalQuestions: number;
  totalMarks: number;
}

const NOTIFICATION_TYPES = {
  exam_scheduled: { icon: ScheduleIcon, color: 'primary', label: 'Exam Scheduled' },
  registration_open: { icon: RegisterIcon, color: 'success', label: 'Registration Open' },
  registration_reminder: { icon: TimeIcon, color: 'warning', label: 'Registration Reminder' },
  registration_closing: { icon: WarningIcon, color: 'error', label: 'Registration Closing' },
  registration_closed: { icon: ErrorIcon, color: 'default', label: 'Registration Closed' },
  exam_reminder: { icon: CalendarIcon, color: 'info', label: 'Exam Reminder' },
  date_change: { icon: InfoIcon, color: 'warning', label: 'Date Change' },
  results_published: { icon: TrendingUpIcon, color: 'success', label: 'Results Published' }
};

export const TalentExamNotifications: React.FC = () => {
  const [notifications, setNotifications] = useState<TalentExamNotification[]>([]);
  const [upcomingExams, setUpcomingExams] = useState<UpcomingExam[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [selectedNotification, setSelectedNotification] = useState<TalentExamNotification | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    loadNotifications();
    loadUpcomingExams();
    
    // Set up polling for new notifications
    const interval = setInterval(() => {
      loadNotifications();
    }, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const loadNotifications = async () => {
    try {
      // API call to load notifications
      // const response = await api.get('/talent-exams/notifications');
      // setNotifications(response.data);
      
      // Mock data for now
      const mockNotifications: TalentExamNotification[] = [
        {
          id: '1',
          title: '🎓 New Talent Exam Scheduled - Annual Talent Exam Class 10',
          message: 'A new talent exam "Annual Talent Exam Class 10" has been scheduled for December 15, 2024. Registration opens October 1, 2024. Fee: ₹500.',
          notificationType: 'exam_scheduled',
          examId: 'exam1',
          scheduledAt: '2024-09-15T10:00:00Z',
          sentAt: '2024-09-15T10:00:00Z',
          status: 'sent',
          isRead: false,
          exam: {
            id: 'exam1',
            title: 'Annual Talent Exam Class 10',
            examCode: 'ANN1024A1',
            classLevel: 'class_10',
            examDate: '2024-12-15',
            examTime: '10:00',
            registrationEndDate: '2024-11-30T23:59:59Z',
            registrationFee: 500,
            status: 'registration_open'
          }
        },
        {
          id: '2',
          title: '📝 Registration Open - Mathematics Olympiad Class 8',
          message: 'Registration is now open for "Mathematics Olympiad Class 8" scheduled on November 20, 2024. Register your Class 8 students before October 31, 2024.',
          notificationType: 'registration_open',
          examId: 'exam2',
          scheduledAt: '2024-09-01T09:00:00Z',
          sentAt: '2024-09-01T09:00:00Z',
          status: 'sent',
          isRead: true,
          exam: {
            id: 'exam2',
            title: 'Mathematics Olympiad Class 8',
            examCode: 'OLY824B2',
            classLevel: 'class_8',
            examDate: '2024-11-20',
            examTime: '14:00',
            registrationEndDate: '2024-10-31T23:59:59Z',
            registrationFee: 300,
            status: 'registration_open'
          }
        },
        {
          id: '3',
          title: '⏰ Registration Opening Tomorrow - Science Aptitude Test Class 12',
          message: 'Registration for "Science Aptitude Test Class 12" opens tomorrow. Prepare your Class 12 students for this exciting opportunity!',
          notificationType: 'registration_reminder',
          examId: 'exam3',
          scheduledAt: '2024-09-20T18:00:00Z',
          sentAt: '2024-09-20T18:00:00Z',
          status: 'sent',
          isRead: false
        }
      ];
      
      setNotifications(mockNotifications);
      setUnreadCount(mockNotifications.filter(n => !n.isRead).length);
    } catch (error) {
      toast.error('Failed to load notifications');
    }
  };

  const loadUpcomingExams = async () => {
    setLoading(true);
    try {
      // API call to load upcoming exams
      // const response = await api.get('/talent-exams/upcoming');
      // setUpcomingExams(response.data);
      
      // Mock data for now
      const mockExams: UpcomingExam[] = [
        {
          id: 'exam1',
          title: 'Annual Talent Exam Class 10',
          examCode: 'ANN1024A1',
          classLevel: 'class_10',
          examDate: '2024-12-15',
          examTime: '10:00',
          registrationStartDate: '2024-10-01T00:00:00Z',
          registrationEndDate: '2024-11-30T23:59:59Z',
          registrationFee: 500,
          status: 'registration_open',
          durationMinutes: 180,
          totalQuestions: 100,
          totalMarks: 200
        },
        {
          id: 'exam2',
          title: 'Mathematics Olympiad Class 8',
          examCode: 'OLY824B2',
          classLevel: 'class_8',
          examDate: '2024-11-20',
          examTime: '14:00',
          registrationStartDate: '2024-09-01T00:00:00Z',
          registrationEndDate: '2024-10-31T23:59:59Z',
          registrationFee: 300,
          status: 'registration_open',
          durationMinutes: 120,
          totalQuestions: 50,
          totalMarks: 100
        }
      ];
      
      setUpcomingExams(mockExams);
    } catch (error) {
      toast.error('Failed to load upcoming exams');
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId: string) => {
    try {
      // API call to mark as read
      // await api.patch(`/talent-exams/notifications/${notificationId}/read`);
      
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, isRead: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      toast.error('Failed to mark notification as read');
    }
  };

  const viewNotificationDetails = (notification: TalentExamNotification) => {
    setSelectedNotification(notification);
    setDetailsOpen(true);
    
    if (!notification.isRead) {
      markAsRead(notification.id);
    }
  };

  const navigateToRegistration = (examId: string) => {
    // Navigate to exam registration page
    window.location.href = `/talent-exams/${examId}/register`;
  };

  const getNotificationIcon = (type: string) => {
    const typeInfo = NOTIFICATION_TYPES[type as keyof typeof NOTIFICATION_TYPES];
    if (!typeInfo) return NotificationsIcon;
    
    const IconComponent = typeInfo.icon;
    return <IconComponent />;
  };

  const getNotificationColor = (type: string) => {
    const typeInfo = NOTIFICATION_TYPES[type as keyof typeof NOTIFICATION_TYPES];
    return typeInfo?.color || 'default';
  };

  const getStatusChip = (status: string) => {
    const statusColors = {
      registration_open: 'success',
      registration_closed: 'error',
      scheduled: 'default',
      ongoing: 'info',
      completed: 'default'
    };
    
    return (
      <Chip
        label={status.replace('_', ' ').toUpperCase()}
        color={statusColors[status as keyof typeof statusColors] as any || 'default'}
        size="small"
      />
    );
  };

  const isRegistrationOpen = (exam: UpcomingExam) => {
    const now = new Date();
    const regStart = new Date(exam.registrationStartDate);
    const regEnd = new Date(exam.registrationEndDate);
    
    return now >= regStart && now <= regEnd && exam.status === 'registration_open';
  };

  const getDaysUntilDeadline = (deadline: string) => {
    const days = Math.ceil((new Date(deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
    return days;
  };

  const renderNotificationsList = () => (
    <List>
      {notifications.map((notification) => (
        <React.Fragment key={notification.id}>
          <ListItem
            button
            onClick={() => viewNotificationDetails(notification)}
            sx={{
              backgroundColor: notification.isRead ? 'transparent' : 'action.hover',
              '&:hover': { backgroundColor: 'action.selected' }
            }}
          >
            <ListItemIcon>
              <Badge
                color="error"
                variant="dot"
                invisible={notification.isRead}
              >
                <Avatar
                  sx={{
                    bgcolor: `${getNotificationColor(notification.notificationType)}.light`,
                    color: `${getNotificationColor(notification.notificationType)}.main`
                  }}
                >
                  {getNotificationIcon(notification.notificationType)}
                </Avatar>
              </Badge>
            </ListItemIcon>
            
            <ListItemText
              primary={
                <Typography
                  variant="subtitle2"
                  fontWeight={notification.isRead ? 'normal' : 'bold'}
                >
                  {notification.title}
                </Typography>
              }
              secondary={
                <Box>
                  <Typography variant="body2" color="text.secondary" noWrap>
                    {notification.message}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatDistanceToNow(new Date(notification.sentAt || notification.scheduledAt))} ago
                  </Typography>
                </Box>
              }
            />
            
            <ListItemSecondaryAction>
              <IconButton size="small">
                <ViewIcon />
              </IconButton>
            </ListItemSecondaryAction>
          </ListItem>
          <Divider />
        </React.Fragment>
      ))}
    </List>
  );

  const renderUpcomingExams = () => (
    <Grid container spacing={3}>
      {upcomingExams.map((exam) => (
        <Grid item xs={12} md={6} key={exam.id}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                <Typography variant="h6" gutterBottom>
                  {exam.title}
                </Typography>
                {getStatusChip(exam.status)}
              </Box>
              
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Code: {exam.examCode} | Class: {exam.classLevel.replace('_', ' ').toUpperCase()}
              </Typography>
              
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <CalendarIcon sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                    <Typography variant="body2">
                      {format(new Date(exam.examDate), 'MMM dd, yyyy')}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <TimeIcon sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                    <Typography variant="body2">
                      {exam.examTime} ({exam.durationMinutes} min)
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <FeeIcon sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                    <Typography variant="body2">
                      {exam.registrationFee > 0 ? `₹${exam.registrationFee}` : 'Free'}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AssignmentIcon sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                    <Typography variant="body2">
                      {exam.totalQuestions} Q | {exam.totalMarks} M
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
              
              {isRegistrationOpen(exam) && (
                <Alert severity="info" sx={{ mt: 2, mb: 2 }}>
                  Registration closes in {getDaysUntilDeadline(exam.registrationEndDate)} days
                </Alert>
              )}
              
              <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<ViewIcon />}
                  onClick={() => {/* View details */}}
                >
                  View Details
                </Button>
                
                {isRegistrationOpen(exam) && (
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={<RegisterIcon />}
                    onClick={() => navigateToRegistration(exam.id)}
                  >
                    Register Students
                  </Button>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Talent Exam Notifications
        </Typography>
        <Badge badgeContent={unreadCount} color="error">
          <NotificationsIcon />
        </Badge>
      </Box>

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <NotificationsIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4">{notifications.length}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Notifications
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
                <WarningIcon sx={{ fontSize: 40, color: 'warning.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4">{unreadCount}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Unread
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
                <SchoolIcon sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4">{upcomingExams.length}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Upcoming Exams
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
                <RegisterIcon sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4">
                    {upcomingExams.filter(e => isRegistrationOpen(e)).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Open for Registration
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content */}
      <Card>
        <CardContent>
          <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
            <Tab 
              label={
                <Badge badgeContent={unreadCount} color="error">
                  Notifications
                </Badge>
              } 
            />
            <Tab label="Upcoming Exams" />
          </Tabs>

          <Box sx={{ mt: 3 }}>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : activeTab === 0 ? (
              notifications.length === 0 ? (
                <Alert severity="info">No notifications available</Alert>
              ) : (
                renderNotificationsList()
              )
            ) : (
              upcomingExams.length === 0 ? (
                <Alert severity="info">No upcoming exams</Alert>
              ) : (
                renderUpcomingExams()
              )
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Notification Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedNotification?.title}
        </DialogTitle>
        <DialogContent>
          {selectedNotification && (
            <Box>
              <Typography variant="body1" paragraph>
                {selectedNotification.message}
              </Typography>
              
              <Typography variant="caption" color="text.secondary">
                Sent: {selectedNotification.sentAt ? 
                  format(new Date(selectedNotification.sentAt), 'PPpp') : 
                  'Not sent yet'
                }
              </Typography>
              
              {selectedNotification.exam && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Exam Details
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2">
                        <strong>Exam Code:</strong> {selectedNotification.exam.examCode}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">
                        <strong>Class:</strong> {selectedNotification.exam.classLevel.replace('_', ' ')}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">
                        <strong>Date:</strong> {format(new Date(selectedNotification.exam.examDate), 'PPP')}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">
                        <strong>Time:</strong> {selectedNotification.exam.examTime}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">
                        <strong>Fee:</strong> ₹{selectedNotification.exam.registrationFee}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">
                        <strong>Status:</strong> {getStatusChip(selectedNotification.exam.status)}
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Close</Button>
          {selectedNotification?.exam && isRegistrationOpen(selectedNotification.exam as any) && (
            <Button
              variant="contained"
              onClick={() => {
                navigateToRegistration(selectedNotification.exam!.id);
                setDetailsOpen(false);
              }}
            >
              Register Students
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};
