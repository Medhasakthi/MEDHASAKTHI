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
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Avatar,
  Tooltip,
  Fab,
  LinearProgress,
  Badge,
  Divider
} from '@mui/material';
import {
  School as SchoolIcon,
  Person as PersonIcon,
  Group as GroupIcon,
  Analytics as AnalyticsIcon,
  Add as AddIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  Class as ClassIcon,
  Assignment as AssignmentIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';

interface Institute {
  id: string;
  name: string;
  code: string;
  type: string;
  address: string;
  contactEmail: string;
  contactPhone: string;
  totalStudents: number;
  totalTeachers: number;
  totalClasses: number;
  status: 'active' | 'inactive' | 'pending';
  createdDate: string;
}

interface Student {
  id: string;
  name: string;
  email: string;
  rollNumber: string;
  class: string;
  section: string;
  status: 'active' | 'inactive';
  lastLogin?: string;
  performance: number;
}

interface Teacher {
  id: string;
  name: string;
  email: string;
  employeeId: string;
  subjects: string[];
  classes: string[];
  status: 'active' | 'inactive';
  experience: number;
  rating: number;
}

interface BulkImportResult {
  total: number;
  successful: number;
  failed: number;
  errors: string[];
}

const InstituteManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [institutes, setInstitutes] = useState<Institute[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [selectedInstitute, setSelectedInstitute] = useState<Institute | null>(null);
  const [createDialog, setCreateDialog] = useState(false);
  const [bulkImportDialog, setBulkImportDialog] = useState(false);
  const [importType, setImportType] = useState<'students' | 'teachers'>('students');
  const [importResult, setImportResult] = useState<BulkImportResult | null>(null);
  const [newInstitute, setNewInstitute] = useState<Partial<Institute>>({});

  useEffect(() => {
    loadInstituteData();
  }, []);

  const loadInstituteData = async () => {
    try {
      setLoading(true);
      
      // Load institutes
      const institutesResponse = await fetch('/api/v1/institute', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const institutesData = await institutesResponse.json();
      setInstitutes(institutesData);

      // Load students
      const studentsResponse = await fetch('/api/v1/student', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const studentsData = await studentsResponse.json();
      setStudents(studentsData);

      // Load teachers
      const teachersResponse = await fetch('/api/v1/teacher', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const teachersData = await teachersResponse.json();
      setTeachers(teachersData);

    } catch (error) {
      console.error('Error loading institute data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateInstitute = async () => {
    try {
      const response = await fetch('/api/v1/institute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newInstitute)
      });

      if (response.ok) {
        loadInstituteData();
        setCreateDialog(false);
        setNewInstitute({});
      }
    } catch (error) {
      console.error('Error creating institute:', error);
    }
  };

  const handleBulkImport = async (file: File) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', importType);

      const response = await fetch(`/api/v1/institute/bulk-import/${importType}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setImportResult(result);
        loadInstituteData();
      }
    } catch (error) {
      console.error('Error importing data:', error);
    }
  };

  const StatCard: React.FC<{ 
    title: string; 
    value: string | number; 
    icon: React.ReactNode; 
    color: string;
    trend?: number;
    subtitle?: string;
  }> = ({ title, value, icon, color, trend, subtitle }) => (
    <motion.div
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <Card sx={{ height: '100%', position: 'relative', overflow: 'hidden' }}>
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            right: 0,
            width: 80,
            height: 80,
            background: `linear-gradient(135deg, ${color}20, ${color}40)`,
            borderRadius: '0 0 0 100%'
          }}
        />
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box>
              <Typography color="textSecondary" gutterBottom variant="body2">
                {title}
              </Typography>
              <Typography variant="h4" component="div" fontWeight="bold">
                {value}
              </Typography>
              {subtitle && (
                <Typography variant="body2" color="textSecondary">
                  {subtitle}
                </Typography>
              )}
              {trend !== undefined && (
                <Box display="flex" alignItems="center" mt={1}>
                  <TrendingUpIcon 
                    color={trend > 0 ? 'success' : 'error'} 
                    fontSize="small" 
                  />
                  <Typography 
                    variant="body2" 
                    color={trend > 0 ? 'success.main' : 'error.main'}
                    sx={{ ml: 0.5 }}
                  >
                    {trend > 0 ? '+' : ''}{trend}%
                  </Typography>
                </Box>
              )}
            </Box>
            <Avatar sx={{ bgcolor: color, width: 56, height: 56 }}>
              {icon}
            </Avatar>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Institute Management
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Manage institutes, students, and teachers efficiently
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<UploadIcon />}
            onClick={() => setBulkImportDialog(true)}
          >
            Bulk Import
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialog(true)}
          >
            Add Institute
          </Button>
        </Box>
      </Box>

      {/* Statistics Cards */}
      <Box sx={{ mb: 4, display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3 }}>
        <Box>
          <StatCard
            title="Total Institutes"
            value={institutes.length}
            icon={<SchoolIcon />}
            color="#1976d2"
            trend={12}
            subtitle="Active institutes"
          />
        </Box>
        <Box>
          <StatCard
            title="Total Students"
            value={students.length.toLocaleString()}
            icon={<PersonIcon />}
            color="#2e7d32"
            trend={8}
            subtitle="Enrolled students"
          />
        </Box>
        <Box>
          <StatCard
            title="Total Teachers"
            value={teachers.length}
            icon={<GroupIcon />}
            color="#ed6c02"
            trend={5}
            subtitle="Active teachers"
          />
        </Box>
        <Box>
          <StatCard
            title="Active Classes"
            value={institutes.reduce((sum, inst) => sum + inst.totalClasses, 0)}
            icon={<ClassIcon />}
            color="#9c27b0"
            subtitle="Running classes"
          />
        </Box>
      </Box>

      {/* Tabs */}
      <Paper sx={{ width: '100%', mb: 2 }}>
        <Tabs 
          value={activeTab} 
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
        >
          <Tab label="Institutes" icon={<SchoolIcon />} />
          <Tab label="Students" icon={<PersonIcon />} />
          <Tab label="Teachers" icon={<GroupIcon />} />
          <Tab label="Analytics" icon={<AnalyticsIcon />} />
        </Tabs>
      </Paper>

      {/* Institutes Tab */}
      {activeTab === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card>
            <CardContent>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Institute</TableCell>
                      <TableCell>Code</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Students</TableCell>
                      <TableCell>Teachers</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {institutes.map((institute) => (
                      <TableRow key={institute.id} hover>
                        <TableCell>
                          <Box display="flex" alignItems="center">
                            <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                              <SchoolIcon />
                            </Avatar>
                            <Box>
                              <Typography variant="body1" fontWeight="bold">
                                {institute.name}
                              </Typography>
                              <Typography variant="body2" color="textSecondary">
                                {institute.contactEmail}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip label={institute.code} variant="outlined" size="small" />
                        </TableCell>
                        <TableCell>{institute.type}</TableCell>
                        <TableCell>
                          <Badge badgeContent={institute.totalStudents} color="primary">
                            <PersonIcon />
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge badgeContent={institute.totalTeachers} color="secondary">
                            <GroupIcon />
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={institute.status} 
                            color={
                              institute.status === 'active' ? 'success' : 
                              institute.status === 'pending' ? 'warning' : 'error'
                            }
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Tooltip title="View Details">
                            <IconButton size="small">
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit">
                            <IconButton size="small">
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Analytics">
                            <IconButton size="small">
                              <AnalyticsIcon />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Students Tab */}
      {activeTab === 1 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                <Typography variant="h6">Student Management</Typography>
                <Button startIcon={<DownloadIcon />} variant="outlined" size="small">
                  Export Data
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Student</TableCell>
                      <TableCell>Roll Number</TableCell>
                      <TableCell>Class</TableCell>
                      <TableCell>Performance</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {students.slice(0, 10).map((student) => (
                      <TableRow key={student.id} hover>
                        <TableCell>
                          <Box display="flex" alignItems="center">
                            <Avatar sx={{ bgcolor: 'secondary.main', mr: 2 }}>
                              {student.name.charAt(0)}
                            </Avatar>
                            <Box>
                              <Typography variant="body1" fontWeight="bold">
                                {student.name}
                              </Typography>
                              <Typography variant="body2" color="textSecondary">
                                {student.email}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip label={student.rollNumber} variant="outlined" size="small" />
                        </TableCell>
                        <TableCell>{student.class} - {student.section}</TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center">
                            <LinearProgress 
                              variant="determinate" 
                              value={student.performance} 
                              sx={{ width: 60, mr: 1 }}
                            />
                            <Typography variant="body2">{student.performance}%</Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={student.status} 
                            color={student.status === 'active' ? 'success' : 'error'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Tooltip title="View Profile">
                            <IconButton size="small">
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit">
                            <IconButton size="small">
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Teachers Tab */}
      {activeTab === 2 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Teacher Management</Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Teacher</TableCell>
                      <TableCell>Employee ID</TableCell>
                      <TableCell>Subjects</TableCell>
                      <TableCell>Classes</TableCell>
                      <TableCell>Experience</TableCell>
                      <TableCell>Rating</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {teachers.slice(0, 10).map((teacher) => (
                      <TableRow key={teacher.id} hover>
                        <TableCell>
                          <Box display="flex" alignItems="center">
                            <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                              {teacher.name.charAt(0)}
                            </Avatar>
                            <Box>
                              <Typography variant="body1" fontWeight="bold">
                                {teacher.name}
                              </Typography>
                              <Typography variant="body2" color="textSecondary">
                                {teacher.email}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip label={teacher.employeeId} variant="outlined" size="small" />
                        </TableCell>
                        <TableCell>
                          <Box display="flex" gap={0.5} flexWrap="wrap">
                            {teacher.subjects.slice(0, 2).map((subject) => (
                              <Chip key={subject} label={subject} size="small" />
                            ))}
                            {teacher.subjects.length > 2 && (
                              <Chip label={`+${teacher.subjects.length - 2}`} size="small" />
                            )}
                          </Box>
                        </TableCell>
                        <TableCell>{teacher.classes.length} classes</TableCell>
                        <TableCell>{teacher.experience} years</TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center">
                            <Typography variant="body2" sx={{ mr: 1 }}>
                              {teacher.rating}
                            </Typography>
                            <Box sx={{ color: 'warning.main' }}>★</Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Tooltip title="View Profile">
                            <IconButton size="small">
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit">
                            <IconButton size="small">
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Create Institute Dialog */}
      <Dialog open={createDialog} onClose={() => setCreateDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Institute</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 1, display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 2 }}>
            <Box>
              <TextField
                fullWidth
                label="Institute Name"
                value={newInstitute.name || ''}
                onChange={(e) => setNewInstitute({ ...newInstitute, name: e.target.value })}
              />
            </Box>
            <Box>
              <TextField
                fullWidth
                label="Institute Code"
                value={newInstitute.code || ''}
                onChange={(e) => setNewInstitute({ ...newInstitute, code: e.target.value })}
              />
            </Box>
            <Box>
              <FormControl fullWidth>
                <InputLabel>Institute Type</InputLabel>
                <Select
                  value={newInstitute.type || ''}
                  onChange={(e) => setNewInstitute({ ...newInstitute, type: e.target.value })}
                >
                  <MenuItem value="school">School</MenuItem>
                  <MenuItem value="college">College</MenuItem>
                  <MenuItem value="university">University</MenuItem>
                  <MenuItem value="coaching">Coaching Center</MenuItem>
                </Select>
              </FormControl>
            </Box>
            <Box>
              <TextField
                fullWidth
                label="Contact Email"
                type="email"
                value={newInstitute.contactEmail || ''}
                onChange={(e) => setNewInstitute({ ...newInstitute, contactEmail: e.target.value })}
              />
            </Box>
            <Box>
              <TextField
                fullWidth
                label="Address"
                multiline
                rows={3}
                value={newInstitute.address || ''}
                onChange={(e) => setNewInstitute({ ...newInstitute, address: e.target.value })}
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateInstitute} variant="contained">
            Create Institute
          </Button>
        </DialogActions>
      </Dialog>

      {/* Bulk Import Dialog */}
      <Dialog open={bulkImportDialog} onClose={() => setBulkImportDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Bulk Import Data</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2, mb: 2 }}>
            <InputLabel>Import Type</InputLabel>
            <Select
              value={importType}
              onChange={(e) => setImportType(e.target.value as 'students' | 'teachers')}
            >
              <MenuItem value="students">Students</MenuItem>
              <MenuItem value="teachers">Teachers</MenuItem>
            </Select>
          </FormControl>
          
          <Alert severity="info" sx={{ mb: 2 }}>
            Upload a CSV file with the required columns. Download the template for reference.
          </Alert>
          
          <input
            type="file"
            accept=".csv"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleBulkImport(file);
            }}
            style={{ width: '100%', padding: '10px', border: '1px dashed #ccc' }}
          />
          
          {importResult && (
            <Alert severity={importResult.failed > 0 ? 'warning' : 'success'} sx={{ mt: 2 }}>
              <Typography variant="body2">
                <strong>Import Complete:</strong> {importResult.successful} successful, {importResult.failed} failed out of {importResult.total} records.
              </Typography>
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkImportDialog(false)}>Close</Button>
          <Button variant="outlined" startIcon={<DownloadIcon />}>
            Download Template
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InstituteManagement;
