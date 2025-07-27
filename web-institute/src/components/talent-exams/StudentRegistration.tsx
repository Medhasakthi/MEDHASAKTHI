/**
 * Student Registration Component for Talent Exams
 * Allows institutes to register students for talent exams
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stepper,
  Step,
  StepLabel,
  Alert,
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
  Checkbox,
  FormControlLabel,
  Divider,
  CircularProgress,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Payment as PaymentIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { toast } from 'react-hot-toast';
import { useParams } from 'react-router-dom';

// Types
interface TalentExam {
  id: string;
  title: string;
  examCode: string;
  classLevel: string;
  examDate: string;
  examTime: string;
  durationMinutes: number;
  registrationStartDate: string;
  registrationEndDate: string;
  totalQuestions: number;
  totalMarks: number;
  registrationFee: number;
  status: string;
  eligibilityCriteria?: any;
  syllabus?: any;
}

interface StudentRegistration {
  id?: string;
  studentName: string;
  studentEmail: string;
  studentPhone: string;
  dateOfBirth: Date | null;
  currentClass: string;
  schoolName: string;
  parentName: string;
  parentEmail: string;
  parentPhone: string;
  address: {
    street: string;
    city: string;
    state: string;
    pincode: string;
  };
  specialRequirements?: string;
  status?: string;
  registrationNumber?: string;
  paymentStatus?: string;
}

const REGISTRATION_STEPS = [
  'Exam Details',
  'Student Information',
  'Review & Submit',
  'Payment'
];

const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
  'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
  'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
  'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
  'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Puducherry'
];

export const StudentRegistration: React.FC = () => {
  const { examId } = useParams<{ examId: string }>();
  const [exam, setExam] = useState<TalentExam | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [registrations, setRegistrations] = useState<StudentRegistration[]>([]);
  const [currentStudent, setCurrentStudent] = useState<StudentRegistration>({
    studentName: '',
    studentEmail: '',
    studentPhone: '',
    dateOfBirth: null,
    currentClass: '',
    schoolName: '',
    parentName: '',
    parentEmail: '',
    parentPhone: '',
    address: {
      street: '',
      city: '',
      state: '',
      pincode: ''
    },
    specialRequirements: ''
  });
  const [bulkMode, setBulkMode] = useState(false);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [submitDialogOpen, setSubmitDialogOpen] = useState(false);

  useEffect(() => {
    if (examId) {
      loadExamDetails();
      loadExistingRegistrations();
    }
  }, [examId]);

  const loadExamDetails = async () => {
    setLoading(true);
    try {
      // API call to load exam details
      // const response = await api.get(`/talent-exams/${examId}`);
      // setExam(response.data);
      
      // Mock data for now
      const mockExam: TalentExam = {
        id: examId!,
        title: 'Annual Talent Exam Class 10',
        examCode: 'ANN1024A1',
        classLevel: 'class_10',
        examDate: '2024-12-15',
        examTime: '10:00',
        durationMinutes: 180,
        registrationStartDate: '2024-10-01T00:00:00Z',
        registrationEndDate: '2024-11-30T23:59:59Z',
        totalQuestions: 100,
        totalMarks: 200,
        registrationFee: 500,
        status: 'registration_open'
      };
      
      setExam(mockExam);
      setCurrentStudent(prev => ({ ...prev, currentClass: mockExam.classLevel }));
    } catch (error) {
      toast.error('Failed to load exam details');
    } finally {
      setLoading(false);
    }
  };

  const loadExistingRegistrations = async () => {
    try {
      // API call to load existing registrations
      // const response = await api.get(`/talent-exams/${examId}/registrations`);
      // setRegistrations(response.data);
      
      // Mock data for now
      setRegistrations([]);
    } catch (error) {
      toast.error('Failed to load existing registrations');
    }
  };

  const handleStudentChange = (field: string, value: any) => {
    if (field.startsWith('address.')) {
      const addressField = field.split('.')[1];
      setCurrentStudent(prev => ({
        ...prev,
        address: { ...prev.address, [addressField]: value }
      }));
    } else {
      setCurrentStudent(prev => ({ ...prev, [field]: value }));
    }
  };

  const addStudentToList = () => {
    // Validate required fields
    if (!currentStudent.studentName || !currentStudent.parentEmail || !currentStudent.dateOfBirth) {
      toast.error('Please fill in all required fields');
      return;
    }

    // Check if student already exists
    const exists = registrations.some(reg => 
      reg.studentEmail === currentStudent.studentEmail ||
      (reg.studentName === currentStudent.studentName && 
       reg.parentEmail === currentStudent.parentEmail)
    );

    if (exists) {
      toast.error('Student already registered');
      return;
    }

    setRegistrations(prev => [...prev, { ...currentStudent, id: Date.now().toString() }]);
    
    // Reset form
    setCurrentStudent({
      studentName: '',
      studentEmail: '',
      studentPhone: '',
      dateOfBirth: null,
      currentClass: exam?.classLevel || '',
      schoolName: '',
      parentName: '',
      parentEmail: '',
      parentPhone: '',
      address: {
        street: '',
        city: '',
        state: '',
        pincode: ''
      },
      specialRequirements: ''
    });

    toast.success('Student added to registration list');
  };

  const removeStudent = (studentId: string) => {
    setRegistrations(prev => prev.filter(reg => reg.id !== studentId));
    toast.success('Student removed from list');
  };

  const handleBulkUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'text/csv') {
      setCsvFile(file);
      // Process CSV file
      processCsvFile(file);
    } else {
      toast.error('Please select a valid CSV file');
    }
  };

  const processCsvFile = async (file: File) => {
    try {
      const text = await file.text();
      const lines = text.split('\n');
      const headers = lines[0].split(',').map(h => h.trim());
      
      const newRegistrations: StudentRegistration[] = [];
      
      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim());
        if (values.length >= headers.length && values[0]) {
          const registration: StudentRegistration = {
            id: Date.now().toString() + i,
            studentName: values[0] || '',
            studentEmail: values[1] || '',
            studentPhone: values[2] || '',
            dateOfBirth: values[3] ? new Date(values[3]) : null,
            currentClass: exam?.classLevel || '',
            schoolName: values[4] || '',
            parentName: values[5] || '',
            parentEmail: values[6] || '',
            parentPhone: values[7] || '',
            address: {
              street: values[8] || '',
              city: values[9] || '',
              state: values[10] || '',
              pincode: values[11] || ''
            },
            specialRequirements: values[12] || ''
          };
          
          newRegistrations.push(registration);
        }
      }
      
      setRegistrations(prev => [...prev, ...newRegistrations]);
      toast.success(`${newRegistrations.length} students imported successfully`);
    } catch (error) {
      toast.error('Failed to process CSV file');
    }
  };

  const downloadCsvTemplate = () => {
    const headers = [
      'Student Name*',
      'Student Email',
      'Student Phone',
      'Date of Birth (YYYY-MM-DD)*',
      'School Name*',
      'Parent Name*',
      'Parent Email*',
      'Parent Phone*',
      'Address Street',
      'City',
      'State',
      'Pincode',
      'Special Requirements'
    ];
    
    const csvContent = headers.join(',') + '\n';
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'student_registration_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const submitRegistrations = async () => {
    if (registrations.length === 0) {
      toast.error('Please add at least one student');
      return;
    }

    setLoading(true);
    try {
      // API call to submit registrations
      // const response = await api.post(`/talent-exams/${examId}/register-bulk`, {
      //   registrations: registrations
      // });
      
      toast.success(`${registrations.length} students registered successfully!`);
      setActiveStep(3); // Move to payment step
      setSubmitDialogOpen(false);
    } catch (error) {
      toast.error('Failed to submit registrations');
    } finally {
      setLoading(false);
    }
  };

  const calculateTotalFee = () => {
    return registrations.length * (exam?.registrationFee || 0);
  };

  const isRegistrationOpen = () => {
    if (!exam) return false;
    const now = new Date();
    const regStart = new Date(exam.registrationStartDate);
    const regEnd = new Date(exam.registrationEndDate);
    return now >= regStart && now <= regEnd && exam.status === 'registration_open';
  };

  const renderExamDetails = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Exam Information
        </Typography>
        
        {exam && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Exam Title
              </Typography>
              <Typography variant="body1" gutterBottom>
                {exam.title}
              </Typography>
              
              <Typography variant="subtitle2" color="text.secondary">
                Exam Code
              </Typography>
              <Typography variant="body1" gutterBottom fontFamily="monospace">
                {exam.examCode}
              </Typography>
              
              <Typography variant="subtitle2" color="text.secondary">
                Class Level
              </Typography>
              <Typography variant="body1" gutterBottom>
                {exam.classLevel.replace('_', ' ').toUpperCase()}
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Exam Date & Time
              </Typography>
              <Typography variant="body1" gutterBottom>
                {new Date(exam.examDate).toLocaleDateString()} at {exam.examTime}
              </Typography>
              
              <Typography variant="subtitle2" color="text.secondary">
                Duration
              </Typography>
              <Typography variant="body1" gutterBottom>
                {exam.durationMinutes} minutes
              </Typography>
              
              <Typography variant="subtitle2" color="text.secondary">
                Registration Fee
              </Typography>
              <Typography variant="body1" gutterBottom>
                {exam.registrationFee > 0 ? `₹${exam.registrationFee}` : 'Free'}
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary">
                Registration Period
              </Typography>
              <Typography variant="body1">
                {new Date(exam.registrationStartDate).toLocaleDateString()} to{' '}
                {new Date(exam.registrationEndDate).toLocaleDateString()}
              </Typography>
              
              {!isRegistrationOpen() && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  Registration is not currently open for this exam
                </Alert>
              )}
            </Grid>
          </Grid>
        )}
      </CardContent>
    </Card>
  );

  const renderStudentForm = () => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">
            Student Registration
          </Typography>
          <Box>
            <FormControlLabel
              control={
                <Checkbox
                  checked={bulkMode}
                  onChange={(e) => setBulkMode(e.target.checked)}
                />
              }
              label="Bulk Upload"
            />
          </Box>
        </Box>

        {bulkMode ? (
          <Box>
            <Alert severity="info" sx={{ mb: 2 }}>
              Upload a CSV file with student details. Download the template below for the correct format.
            </Alert>
            
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={downloadCsvTemplate}
              >
                Download Template
              </Button>
              
              <Button
                variant="contained"
                component="label"
                startIcon={<UploadIcon />}
              >
                Upload CSV
                <input
                  type="file"
                  accept=".csv"
                  hidden
                  onChange={handleBulkUpload}
                />
              </Button>
            </Box>
          </Box>
        ) : (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Student Name *"
                value={currentStudent.studentName}
                onChange={(e) => handleStudentChange('studentName', e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Student Email"
                type="email"
                value={currentStudent.studentEmail}
                onChange={(e) => handleStudentChange('studentEmail', e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Student Phone"
                value={currentStudent.studentPhone}
                onChange={(e) => handleStudentChange('studentPhone', e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <DatePicker
                label="Date of Birth *"
                value={currentStudent.dateOfBirth}
                onChange={(date) => handleStudentChange('dateOfBirth', date)}
                slotProps={{
                  textField: {
                    fullWidth: true
                  }
                }}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="School Name *"
                value={currentStudent.schoolName}
                onChange={(e) => handleStudentChange('schoolName', e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Current Class"
                value={currentStudent.currentClass.replace('_', ' ').toUpperCase()}
                disabled
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Parent/Guardian Name *"
                value={currentStudent.parentName}
                onChange={(e) => handleStudentChange('parentName', e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Parent Email *"
                type="email"
                value={currentStudent.parentEmail}
                onChange={(e) => handleStudentChange('parentEmail', e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Parent Phone *"
                value={currentStudent.parentPhone}
                onChange={(e) => handleStudentChange('parentPhone', e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Address Street"
                value={currentStudent.address.street}
                onChange={(e) => handleStudentChange('address.street', e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="City"
                value={currentStudent.address.city}
                onChange={(e) => handleStudentChange('address.city', e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>State</InputLabel>
                <Select
                  value={currentStudent.address.state}
                  onChange={(e) => handleStudentChange('address.state', e.target.value)}
                >
                  {INDIAN_STATES.map(state => (
                    <MenuItem key={state} value={state}>
                      {state}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Pincode"
                value={currentStudent.address.pincode}
                onChange={(e) => handleStudentChange('address.pincode', e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Special Requirements"
                multiline
                rows={3}
                value={currentStudent.specialRequirements}
                onChange={(e) => handleStudentChange('specialRequirements', e.target.value)}
                placeholder="Any special accommodations needed (disability support, dietary requirements, etc.)"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={addStudentToList}
                disabled={!isRegistrationOpen()}
              >
                Add Student to List
              </Button>
            </Grid>
          </Grid>
        )}

        {/* Registered Students List */}
        {registrations.length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Students to Register ({registrations.length})
            </Typography>
            
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Student Name</TableCell>
                    <TableCell>Parent Email</TableCell>
                    <TableCell>Date of Birth</TableCell>
                    <TableCell>City</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {registrations.map((student) => (
                    <TableRow key={student.id}>
                      <TableCell>{student.studentName}</TableCell>
                      <TableCell>{student.parentEmail}</TableCell>
                      <TableCell>
                        {student.dateOfBirth ? 
                          new Date(student.dateOfBirth).toLocaleDateString() : 
                          'Not provided'
                        }
                      </TableCell>
                      <TableCell>{student.address.city}</TableCell>
                      <TableCell>
                        <Tooltip title="Remove Student">
                          <IconButton
                            size="small"
                            onClick={() => removeStudent(student.id!)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">
                Total Registration Fee: ₹{calculateTotalFee()}
              </Typography>
              <Button
                variant="contained"
                size="large"
                onClick={() => setSubmitDialogOpen(true)}
                disabled={!isRegistrationOpen()}
              >
                Proceed to Submit
              </Button>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );

  if (loading && !exam) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!exam) {
    return (
      <Alert severity="error">
        Exam not found or you don't have permission to access it.
      </Alert>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Student Registration - {exam.title}
        </Typography>
        
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {REGISTRATION_STEPS.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {activeStep === 0 && renderExamDetails()}
        {activeStep === 1 && renderStudentForm()}
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Button
            disabled={activeStep === 0}
            onClick={() => setActiveStep(prev => prev - 1)}
          >
            Back
          </Button>
          
          {activeStep < 2 && (
            <Button
              variant="contained"
              onClick={() => setActiveStep(prev => prev + 1)}
              disabled={activeStep === 1 && registrations.length === 0}
            >
              Next
            </Button>
          )}
        </Box>

        {/* Submit Confirmation Dialog */}
        <Dialog
          open={submitDialogOpen}
          onClose={() => setSubmitDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Confirm Registration Submission</DialogTitle>
          <DialogContent>
            <Typography variant="body1" paragraph>
              You are about to register {registrations.length} student(s) for {exam.title}.
            </Typography>
            <Typography variant="body1" paragraph>
              Total registration fee: ₹{calculateTotalFee()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Once submitted, you will be redirected to the payment page to complete the registration process.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSubmitDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={submitRegistrations}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <CheckCircleIcon />}
            >
              {loading ? 'Submitting...' : 'Submit Registrations'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  );
};
