/**
 * Talent Exam Management Component for Super Admin
 * Allows super admin to schedule, manage, and monitor talent exams
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
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
  Switch,
  FormControlLabel,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Tooltip,
  Menu,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Schedule as ScheduleIcon,
  Notifications as NotificationsIcon,
  Analytics as AnalyticsIcon,
  MoreVert as MoreVertIcon,
  School as SchoolIcon,
  Assignment as AssignmentIcon,
  People as PeopleIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';
import { DatePicker, TimePicker } from '@mui/x-date-pickers';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { toast } from 'react-hot-toast';

// Types
interface TalentExam {
  id: string;
  examCode: string;
  title: string;
  description?: string;
  examType: string;
  classLevel: string;
  academicYear: string;
  examDate: string;
  examTime: string;
  durationMinutes: number;
  registrationStartDate: string;
  registrationEndDate: string;
  totalQuestions: number;
  totalMarks: number;
  registrationFee: number;
  status: string;
  isActive: boolean;
  maxRegistrations?: number;
  registrationCount?: number;
  createdAt: string;
}

interface ExamFormData {
  title: string;
  description: string;
  examType: string;
  classLevel: string;
  academicYear: string;
  examDate: Date | null;
  examTime: Date | null;
  durationMinutes: number;
  registrationStartDate: Date | null;
  registrationEndDate: Date | null;
  totalQuestions: number;
  totalMarks: number;
  passingMarks: number;
  registrationFee: number;
  negativeMarking: boolean;
  negativeMarksPerQuestion: number;
  isProctored: boolean;
  allowCalculator: boolean;
  maxRegistrations: number;
}

const EXAM_TYPES = [
  { value: 'annual_talent', label: 'Annual Talent Exam' },
  { value: 'olympiad', label: 'Olympiad' },
  { value: 'scholarship', label: 'Scholarship Test' },
  { value: 'aptitude', label: 'Aptitude Test' },
  { value: 'subject_mastery', label: 'Subject Mastery' },
  { value: 'competitive', label: 'Competitive Exam' }
];

const CLASS_LEVELS = [
  { value: 'class_1', label: 'Class 1' },
  { value: 'class_2', label: 'Class 2' },
  { value: 'class_3', label: 'Class 3' },
  { value: 'class_4', label: 'Class 4' },
  { value: 'class_5', label: 'Class 5' },
  { value: 'class_6', label: 'Class 6' },
  { value: 'class_7', label: 'Class 7' },
  { value: 'class_8', label: 'Class 8' },
  { value: 'class_9', label: 'Class 9' },
  { value: 'class_10', label: 'Class 10' },
  { value: 'class_11', label: 'Class 11' },
  { value: 'class_12', label: 'Class 12' }
];

const EXAM_STATUSES = [
  { value: 'scheduled', label: 'Scheduled', color: 'default' },
  { value: 'registration_open', label: 'Registration Open', color: 'primary' },
  { value: 'registration_closed', label: 'Registration Closed', color: 'warning' },
  { value: 'ongoing', label: 'Ongoing', color: 'info' },
  { value: 'completed', label: 'Completed', color: 'success' },
  { value: 'results_published', label: 'Results Published', color: 'success' },
  { value: 'cancelled', label: 'Cancelled', color: 'error' }
];

export const TalentExamManagement: React.FC = () => {
  const [exams, setExams] = useState<TalentExam[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedExam, setSelectedExam] = useState<TalentExam | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuExam, setMenuExam] = useState<TalentExam | null>(null);
  
  const [formData, setFormData] = useState<ExamFormData>({
    title: '',
    description: '',
    examType: 'annual_talent',
    classLevel: 'class_1',
    academicYear: '2024-25',
    examDate: null,
    examTime: null,
    durationMinutes: 120,
    registrationStartDate: null,
    registrationEndDate: null,
    totalQuestions: 50,
    totalMarks: 100,
    passingMarks: 40,
    registrationFee: 0,
    negativeMarking: false,
    negativeMarksPerQuestion: 0.25,
    isProctored: true,
    allowCalculator: false,
    maxRegistrations: 1000
  });

  useEffect(() => {
    loadExams();
  }, []);

  const loadExams = async () => {
    setLoading(true);
    try {
      // API call to load talent exams
      // const response = await api.get('/talent-exams');
      // setExams(response.data.exams);
      
      // Mock data for now
      const mockExams: TalentExam[] = [
        {
          id: '1',
          examCode: 'ANN1024A1',
          title: 'Annual Talent Exam - Class 10',
          description: 'Annual talent examination for Class 10 students',
          examType: 'annual_talent',
          classLevel: 'class_10',
          academicYear: '2024-25',
          examDate: '2024-12-15',
          examTime: '10:00',
          durationMinutes: 180,
          registrationStartDate: '2024-10-01T00:00:00Z',
          registrationEndDate: '2024-11-30T23:59:59Z',
          totalQuestions: 100,
          totalMarks: 200,
          registrationFee: 500,
          status: 'registration_open',
          isActive: true,
          maxRegistrations: 5000,
          registrationCount: 1250,
          createdAt: '2024-09-15T10:00:00Z'
        },
        {
          id: '2',
          examCode: 'OLY824B2',
          title: 'Mathematics Olympiad - Class 8',
          description: 'Mathematics olympiad for Class 8 students',
          examType: 'olympiad',
          classLevel: 'class_8',
          academicYear: '2024-25',
          examDate: '2024-11-20',
          examTime: '14:00',
          durationMinutes: 120,
          registrationStartDate: '2024-09-01T00:00:00Z',
          registrationEndDate: '2024-10-31T23:59:59Z',
          totalQuestions: 50,
          totalMarks: 100,
          registrationFee: 300,
          status: 'scheduled',
          isActive: true,
          maxRegistrations: 2000,
          registrationCount: 0,
          createdAt: '2024-08-20T15:30:00Z'
        }
      ];
      
      setExams(mockExams);
    } catch (error) {
      toast.error('Failed to load talent exams');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateExam = async () => {
    try {
      // Validate form data
      if (!formData.title || !formData.examDate || !formData.examTime) {
        toast.error('Please fill in all required fields');
        return;
      }

      // API call to create exam
      // const response = await api.post('/talent-exams', formData);
      
      toast.success('Talent exam created successfully!');
      setCreateDialogOpen(false);
      resetForm();
      loadExams();
    } catch (error) {
      toast.error('Failed to create talent exam');
    }
  };

  const handleUpdateExam = async () => {
    if (!selectedExam) return;

    try {
      // API call to update exam
      // const response = await api.put(`/talent-exams/${selectedExam.id}`, formData);
      
      toast.success('Talent exam updated successfully!');
      setEditDialogOpen(false);
      setSelectedExam(null);
      resetForm();
      loadExams();
    } catch (error) {
      toast.error('Failed to update talent exam');
    }
  };

  const handleStatusChange = async (examId: string, newStatus: string) => {
    try {
      // API call to change status
      // await api.patch(`/talent-exams/${examId}/status`, { status: newStatus });
      
      toast.success(`Exam status changed to ${newStatus}`);
      loadExams();
    } catch (error) {
      toast.error('Failed to change exam status');
    }
  };

  const handleOpenRegistration = async (exam: TalentExam) => {
    try {
      // API call to open registration
      // await api.post(`/talent-exams/${exam.id}/open-registration`);
      
      toast.success('Registration opened successfully!');
      loadExams();
    } catch (error) {
      toast.error('Failed to open registration');
    }
  };

  const handleCloseRegistration = async (exam: TalentExam) => {
    try {
      // API call to close registration
      // await api.post(`/talent-exams/${exam.id}/close-registration`);
      
      toast.success('Registration closed successfully!');
      loadExams();
    } catch (error) {
      toast.error('Failed to close registration');
    }
  };

  const handleSendNotification = async (exam: TalentExam) => {
    try {
      // API call to send notification
      // await api.post(`/talent-exams/${exam.id}/send-notification`);
      
      toast.success('Notification sent to all institutes!');
    } catch (error) {
      toast.error('Failed to send notification');
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      examType: 'annual_talent',
      classLevel: 'class_1',
      academicYear: '2024-25',
      examDate: null,
      examTime: null,
      durationMinutes: 120,
      registrationStartDate: null,
      registrationEndDate: null,
      totalQuestions: 50,
      totalMarks: 100,
      passingMarks: 40,
      registrationFee: 0,
      negativeMarking: false,
      negativeMarksPerQuestion: 0.25,
      isProctored: true,
      allowCalculator: false,
      maxRegistrations: 1000
    });
  };

  const openEditDialog = (exam: TalentExam) => {
    setSelectedExam(exam);
    setFormData({
      title: exam.title,
      description: exam.description || '',
      examType: exam.examType,
      classLevel: exam.classLevel,
      academicYear: exam.academicYear,
      examDate: new Date(exam.examDate),
      examTime: new Date(`2024-01-01T${exam.examTime}`),
      durationMinutes: exam.durationMinutes,
      registrationStartDate: new Date(exam.registrationStartDate),
      registrationEndDate: new Date(exam.registrationEndDate),
      totalQuestions: exam.totalQuestions,
      totalMarks: exam.totalMarks,
      passingMarks: Math.floor(exam.totalMarks * 0.4),
      registrationFee: exam.registrationFee,
      negativeMarking: false,
      negativeMarksPerQuestion: 0.25,
      isProctored: true,
      allowCalculator: false,
      maxRegistrations: exam.maxRegistrations || 1000
    });
    setEditDialogOpen(true);
  };

  const getStatusChip = (status: string) => {
    const statusInfo = EXAM_STATUSES.find(s => s.value === status);
    return (
      <Chip
        label={statusInfo?.label || status}
        color={statusInfo?.color as any || 'default'}
        size="small"
      />
    );
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, exam: TalentExam) => {
    setAnchorEl(event.currentTarget);
    setMenuExam(exam);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setMenuExam(null);
  };

  const renderExamForm = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Exam Title *"
          value={formData.title}
          onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Exam Type *</InputLabel>
          <Select
            value={formData.examType}
            onChange={(e) => setFormData(prev => ({ ...prev, examType: e.target.value }))}
          >
            {EXAM_TYPES.map(type => (
              <MenuItem key={type.value} value={type.value}>
                {type.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Class Level *</InputLabel>
          <Select
            value={formData.classLevel}
            onChange={(e) => setFormData(prev => ({ ...prev, classLevel: e.target.value }))}
          >
            {CLASS_LEVELS.map(level => (
              <MenuItem key={level.value} value={level.value}>
                {level.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Academic Year *"
          value={formData.academicYear}
          onChange={(e) => setFormData(prev => ({ ...prev, academicYear: e.target.value }))}
          placeholder="e.g., 2024-25"
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <DatePicker
          label="Exam Date *"
          value={formData.examDate}
          onChange={(date) => setFormData(prev => ({ ...prev, examDate: date }))}
          renderInput={(params) => <TextField {...params} fullWidth />}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TimePicker
          label="Exam Time *"
          value={formData.examTime}
          onChange={(time) => setFormData(prev => ({ ...prev, examTime: time }))}
          renderInput={(params) => <TextField {...params} fullWidth />}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Duration (minutes) *"
          type="number"
          value={formData.durationMinutes}
          onChange={(e) => setFormData(prev => ({ ...prev, durationMinutes: parseInt(e.target.value) }))}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <DatePicker
          label="Registration Start Date *"
          value={formData.registrationStartDate}
          onChange={(date) => setFormData(prev => ({ ...prev, registrationStartDate: date }))}
          renderInput={(params) => <TextField {...params} fullWidth />}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <DatePicker
          label="Registration End Date *"
          value={formData.registrationEndDate}
          onChange={(date) => setFormData(prev => ({ ...prev, registrationEndDate: date }))}
          renderInput={(params) => <TextField {...params} fullWidth />}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Total Questions *"
          type="number"
          value={formData.totalQuestions}
          onChange={(e) => setFormData(prev => ({ ...prev, totalQuestions: parseInt(e.target.value) }))}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Total Marks *"
          type="number"
          value={formData.totalMarks}
          onChange={(e) => setFormData(prev => ({ ...prev, totalMarks: parseInt(e.target.value) }))}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Registration Fee (₹)"
          type="number"
          value={formData.registrationFee}
          onChange={(e) => setFormData(prev => ({ ...prev, registrationFee: parseFloat(e.target.value) }))}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Max Registrations"
          type="number"
          value={formData.maxRegistrations}
          onChange={(e) => setFormData(prev => ({ ...prev, maxRegistrations: parseInt(e.target.value) }))}
        />
      </Grid>

      <Grid item xs={12}>
        <TextField
          fullWidth
          label="Description"
          multiline
          rows={3}
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={formData.negativeMarking}
              onChange={(e) => setFormData(prev => ({ ...prev, negativeMarking: e.target.checked }))}
            />
          }
          label="Negative Marking"
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={formData.isProctored}
              onChange={(e) => setFormData(prev => ({ ...prev, isProctored: e.target.checked }))}
            />
          }
          label="Proctored Exam"
        />
      </Grid>
    </Grid>
  );

  const renderExamsTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Exam Code</TableCell>
            <TableCell>Title</TableCell>
            <TableCell>Class</TableCell>
            <TableCell>Exam Date</TableCell>
            <TableCell>Registration</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Registrations</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {exams.map((exam) => (
            <TableRow key={exam.id}>
              <TableCell>
                <Typography variant="body2" fontFamily="monospace">
                  {exam.examCode}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="body2" fontWeight="medium">
                  {exam.title}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {exam.examType.replace('_', ' ')}
                </Typography>
              </TableCell>
              <TableCell>
                <Chip
                  label={exam.classLevel.replace('_', ' ')}
                  size="small"
                  variant="outlined"
                />
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {new Date(exam.examDate).toLocaleDateString()}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {exam.examTime}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {new Date(exam.registrationStartDate).toLocaleDateString()} -
                </Typography>
                <Typography variant="body2">
                  {new Date(exam.registrationEndDate).toLocaleDateString()}
                </Typography>
              </TableCell>
              <TableCell>
                {getStatusChip(exam.status)}
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {exam.registrationCount || 0} / {exam.maxRegistrations || 'Unlimited'}
                </Typography>
              </TableCell>
              <TableCell>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Tooltip title="View Details">
                    <IconButton size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="Edit Exam">
                    <IconButton size="small" onClick={() => openEditDialog(exam)}>
                      <EditIcon />
                    </IconButton>
                  </Tooltip>

                  <IconButton
                    size="small"
                    onClick={(e) => handleMenuOpen(e, exam)}
                  >
                    <MoreVertIcon />
                  </IconButton>
                </Box>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">
            Talent Exam Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Schedule New Exam
          </Button>
        </Box>

        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <SchoolIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                  <Box>
                    <Typography variant="h4">{exams.length}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Exams
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
                  <AssignmentIcon sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                  <Box>
                    <Typography variant="h4">
                      {exams.filter(e => e.status === 'registration_open').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Registration Open
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
                  <PeopleIcon sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
                  <Box>
                    <Typography variant="h4">
                      {exams.reduce((sum, exam) => sum + (exam.registrationCount || 0), 0)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Registrations
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
                  <TrendingUpIcon sx={{ fontSize: 40, color: 'warning.main', mr: 2 }} />
                  <Box>
                    <Typography variant="h4">
                      {exams.filter(e => e.status === 'completed').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Completed Exams
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
              <Tab label="All Exams" />
              <Tab label="Scheduled" />
              <Tab label="Active" />
              <Tab label="Completed" />
            </Tabs>

            <Box sx={{ mt: 3 }}>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : (
                renderExamsTable()
              )}
            </Box>
          </CardContent>
        </Card>

        {/* Create Exam Dialog */}
        <Dialog
          open={createDialogOpen}
          onClose={() => setCreateDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>Schedule New Talent Exam</DialogTitle>
          <DialogContent>
            {renderExamForm()}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
            <Button variant="contained" onClick={handleCreateExam}>
              Schedule Exam
            </Button>
          </DialogActions>
        </Dialog>

        {/* Edit Exam Dialog */}
        <Dialog
          open={editDialogOpen}
          onClose={() => setEditDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>Edit Talent Exam</DialogTitle>
          <DialogContent>
            {renderExamForm()}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
            <Button variant="contained" onClick={handleUpdateExam}>
              Update Exam
            </Button>
          </DialogActions>
        </Dialog>

        {/* Action Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          {menuExam?.status === 'scheduled' && (
            <MenuItem onClick={() => {
              if (menuExam) handleOpenRegistration(menuExam);
              handleMenuClose();
            }}>
              <ListItemIcon>
                <ScheduleIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Open Registration</ListItemText>
            </MenuItem>
          )}
          
          {menuExam?.status === 'registration_open' && (
            <MenuItem onClick={() => {
              if (menuExam) handleCloseRegistration(menuExam);
              handleMenuClose();
            }}>
              <ListItemIcon>
                <ScheduleIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Close Registration</ListItemText>
            </MenuItem>
          )}

          <MenuItem onClick={() => {
            if (menuExam) handleSendNotification(menuExam);
            handleMenuClose();
          }}>
            <ListItemIcon>
              <NotificationsIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Send Notification</ListItemText>
          </MenuItem>

          <MenuItem onClick={() => {
            // Navigate to analytics
            handleMenuClose();
          }}>
            <ListItemIcon>
              <AnalyticsIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>View Analytics</ListItemText>
          </MenuItem>
        </Menu>
      </Box>
    </LocalizationProvider>
  );
};
