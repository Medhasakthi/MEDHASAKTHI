/**
 * Certificate Generator Component
 * Allows institutes to generate certificates for students
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Upload as UploadIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { toast } from 'react-hot-toast';

// Types
interface CertificateData {
  title: string;
  description?: string;
  certificateType: string;
  recipientName: string;
  recipientEmail: string;
  studentId?: string;
  issuedBy?: string;
  subjectName?: string;
  courseName?: string;
  examName?: string;
  score?: number;
  grade?: string;
  completionDate?: Date;
  professionCategory?: string;
}

interface CertificateTemplate {
  id: string;
  name: string;
  code: string;
  certificateType: string;
  professionCategory: string;
  description?: string;
}

interface GeneratedCertificate {
  id: string;
  certificateNumber: string;
  title: string;
  recipientName: string;
  recipientEmail: string;
  status: string;
  issuedAt: string;
  pdfUrl?: string;
}

const CERTIFICATE_TYPES = [
  { value: 'course_completion', label: 'Course Completion' },
  { value: 'exam_pass', label: 'Exam Pass' },
  { value: 'achievement', label: 'Achievement' },
  { value: 'participation', label: 'Participation' },
  { value: 'professional', label: 'Professional' },
  { value: 'skill_verification', label: 'Skill Verification' }
];

const PROFESSION_CATEGORIES = [
  { value: 'information_technology', label: 'Information Technology' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'finance_accounting', label: 'Finance & Accounting' },
  { value: 'engineering', label: 'Engineering' },
  { value: 'management', label: 'Management' },
  { value: 'education', label: 'Education' },
  { value: 'legal', label: 'Legal' },
  { value: 'marketing', label: 'Marketing' },
  { value: 'design_creative', label: 'Design & Creative' },
  { value: 'data_science', label: 'Data Science' },
  { value: 'cybersecurity', label: 'Cybersecurity' },
  { value: 'project_management', label: 'Project Management' },
  { value: 'digital_marketing', label: 'Digital Marketing' },
  { value: 'cloud_computing', label: 'Cloud Computing' },
  { value: 'general', label: 'General' }
];

export const CertificateGenerator: React.FC = () => {
  const [certificateData, setCertificateData] = useState<CertificateData>({
    title: '',
    certificateType: 'course_completion',
    recipientName: '',
    recipientEmail: '',
    professionCategory: 'general'
  });
  
  const [templates, setTemplates] = useState<CertificateTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [generatedCertificates, setGeneratedCertificates] = useState<GeneratedCertificate[]>([]);
  const [loading, setLoading] = useState(false);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [bulkMode, setBulkMode] = useState(false);
  const [bulkData, setBulkData] = useState<CertificateData[]>([]);

  useEffect(() => {
    loadTemplates();
    loadGeneratedCertificates();
  }, []);

  const loadTemplates = async () => {
    try {
      // API call to load templates
      // const response = await api.get('/certificates/templates');
      // setTemplates(response.data);
      
      // Mock data for now
      setTemplates([
        {
          id: '1',
          name: 'IT Professional Certificate',
          code: 'IT_PROF',
          certificateType: 'professional',
          professionCategory: 'information_technology',
          description: 'Professional IT certification template'
        },
        {
          id: '2',
          name: 'Course Completion Certificate',
          code: 'COURSE_COMP',
          certificateType: 'course_completion',
          professionCategory: 'general',
          description: 'General course completion template'
        }
      ]);
    } catch (error) {
      toast.error('Failed to load certificate templates');
    }
  };

  const loadGeneratedCertificates = async () => {
    try {
      // API call to load generated certificates
      // const response = await api.get('/certificates');
      // setGeneratedCertificates(response.data.certificates);
      
      // Mock data for now
      setGeneratedCertificates([]);
    } catch (error) {
      toast.error('Failed to load certificates');
    }
  };

  const handleInputChange = (field: keyof CertificateData, value: any) => {
    setCertificateData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const generateCertificate = async () => {
    if (!certificateData.title || !certificateData.recipientName || !certificateData.recipientEmail) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      // API call to generate certificate
      const requestData = {
        templateId: selectedTemplate || undefined,
        professionCategory: certificateData.professionCategory,
        certificateType: certificateData.certificateType,
        generationType: 'single',
        certificates: [certificateData]
      };

      // const response = await api.post('/certificates/generate', requestData);
      
      // Mock success response
      const mockCertificate: GeneratedCertificate = {
        id: Date.now().toString(),
        certificateNumber: `MEDH-${Date.now()}`,
        title: certificateData.title,
        recipientName: certificateData.recipientName,
        recipientEmail: certificateData.recipientEmail,
        status: 'generated',
        issuedAt: new Date().toISOString()
      };

      setGeneratedCertificates(prev => [mockCertificate, ...prev]);
      toast.success('Certificate generated successfully!');
      
      // Reset form
      setCertificateData({
        title: '',
        certificateType: 'course_completion',
        recipientName: '',
        recipientEmail: '',
        professionCategory: 'general'
      });
      
    } catch (error) {
      toast.error('Failed to generate certificate');
    } finally {
      setLoading(false);
    }
  };

  const downloadCertificate = async (certificateId: string) => {
    try {
      // API call to download certificate
      // const response = await api.get(`/certificates/${certificateId}/download`, { responseType: 'blob' });
      // const url = window.URL.createObjectURL(new Blob([response.data]));
      // const link = document.createElement('a');
      // link.href = url;
      // link.setAttribute('download', `certificate-${certificateId}.pdf`);
      // document.body.appendChild(link);
      // link.click();
      // link.remove();
      
      toast.success('Certificate download started');
    } catch (error) {
      toast.error('Failed to download certificate');
    }
  };

  const addBulkEntry = () => {
    setBulkData(prev => [...prev, {
      title: '',
      certificateType: 'course_completion',
      recipientName: '',
      recipientEmail: '',
      professionCategory: 'general'
    }]);
  };

  const removeBulkEntry = (index: number) => {
    setBulkData(prev => prev.filter((_, i) => i !== index));
  };

  const updateBulkEntry = (index: number, field: keyof CertificateData, value: any) => {
    setBulkData(prev => prev.map((item, i) => 
      i === index ? { ...item, [field]: value } : item
    ));
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Certificate Generator
        </Typography>
        
        <Grid container spacing={3}>
          {/* Certificate Form */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h6">
                    {bulkMode ? 'Bulk Certificate Generation' : 'Single Certificate Generation'}
                  </Typography>
                  <Button
                    variant="outlined"
                    onClick={() => setBulkMode(!bulkMode)}
                  >
                    {bulkMode ? 'Single Mode' : 'Bulk Mode'}
                  </Button>
                </Box>

                {!bulkMode ? (
                  // Single certificate form
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Certificate Title *"
                        value={certificateData.title}
                        onChange={(e) => handleInputChange('title', e.target.value)}
                      />
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>Certificate Type *</InputLabel>
                        <Select
                          value={certificateData.certificateType}
                          onChange={(e) => handleInputChange('certificateType', e.target.value)}
                        >
                          {CERTIFICATE_TYPES.map(type => (
                            <MenuItem key={type.value} value={type.value}>
                              {type.label}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>Profession Category</InputLabel>
                        <Select
                          value={certificateData.professionCategory}
                          onChange={(e) => handleInputChange('professionCategory', e.target.value)}
                        >
                          {PROFESSION_CATEGORIES.map(category => (
                            <MenuItem key={category.value} value={category.value}>
                              {category.label}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>Template</InputLabel>
                        <Select
                          value={selectedTemplate}
                          onChange={(e) => setSelectedTemplate(e.target.value)}
                        >
                          <MenuItem value="">Auto-select based on profession</MenuItem>
                          {templates.map(template => (
                            <MenuItem key={template.id} value={template.id}>
                              {template.name}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Recipient Name *"
                        value={certificateData.recipientName}
                        onChange={(e) => handleInputChange('recipientName', e.target.value)}
                      />
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Recipient Email *"
                        type="email"
                        value={certificateData.recipientEmail}
                        onChange={(e) => handleInputChange('recipientEmail', e.target.value)}
                      />
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Course/Subject Name"
                        value={certificateData.courseName || ''}
                        onChange={(e) => handleInputChange('courseName', e.target.value)}
                      />
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Exam Name"
                        value={certificateData.examName || ''}
                        onChange={(e) => handleInputChange('examName', e.target.value)}
                      />
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Score (%)"
                        type="number"
                        value={certificateData.score || ''}
                        onChange={(e) => handleInputChange('score', parseFloat(e.target.value))}
                        inputProps={{ min: 0, max: 100 }}
                      />
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Grade"
                        value={certificateData.grade || ''}
                        onChange={(e) => handleInputChange('grade', e.target.value)}
                      />
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <DatePicker
                        label="Completion Date"
                        value={certificateData.completionDate || null}
                        onChange={(date) => handleInputChange('completionDate', date)}
                        slotProps={{
                          textField: {
                            fullWidth: true
                          }
                        }}
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Description"
                        multiline
                        rows={3}
                        value={certificateData.description || ''}
                        onChange={(e) => handleInputChange('description', e.target.value)}
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <Box sx={{ display: 'flex', gap: 2 }}>
                        <Button
                          variant="contained"
                          onClick={generateCertificate}
                          disabled={loading}
                          startIcon={loading ? <CircularProgress size={20} /> : <AddIcon />}
                        >
                          {loading ? 'Generating...' : 'Generate Certificate'}
                        </Button>
                        
                        <Button
                          variant="outlined"
                          onClick={() => setPreviewOpen(true)}
                          startIcon={<ViewIcon />}
                        >
                          Preview Template
                        </Button>
                      </Box>
                    </Grid>
                  </Grid>
                ) : (
                  // Bulk certificate form
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="subtitle1">
                        Bulk Certificate Data ({bulkData.length} entries)
                      </Typography>
                      <Box>
                        <Button
                          variant="outlined"
                          onClick={addBulkEntry}
                          startIcon={<AddIcon />}
                          sx={{ mr: 1 }}
                        >
                          Add Entry
                        </Button>
                        <Button
                          variant="outlined"
                          startIcon={<UploadIcon />}
                        >
                          Import CSV
                        </Button>
                      </Box>
                    </Box>

                    {bulkData.length === 0 ? (
                      <Alert severity="info">
                        No bulk entries added yet. Click "Add Entry" to start.
                      </Alert>
                    ) : (
                      <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
                        <Table stickyHeader>
                          <TableHead>
                            <TableRow>
                              <TableCell>Title</TableCell>
                              <TableCell>Recipient Name</TableCell>
                              <TableCell>Email</TableCell>
                              <TableCell>Type</TableCell>
                              <TableCell>Actions</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {bulkData.map((entry, index) => (
                              <TableRow key={index}>
                                <TableCell>
                                  <TextField
                                    size="small"
                                    value={entry.title}
                                    onChange={(e) => updateBulkEntry(index, 'title', e.target.value)}
                                    placeholder="Certificate title"
                                  />
                                </TableCell>
                                <TableCell>
                                  <TextField
                                    size="small"
                                    value={entry.recipientName}
                                    onChange={(e) => updateBulkEntry(index, 'recipientName', e.target.value)}
                                    placeholder="Recipient name"
                                  />
                                </TableCell>
                                <TableCell>
                                  <TextField
                                    size="small"
                                    value={entry.recipientEmail}
                                    onChange={(e) => updateBulkEntry(index, 'recipientEmail', e.target.value)}
                                    placeholder="Email address"
                                  />
                                </TableCell>
                                <TableCell>
                                  <Select
                                    size="small"
                                    value={entry.certificateType}
                                    onChange={(e) => updateBulkEntry(index, 'certificateType', e.target.value)}
                                  >
                                    {CERTIFICATE_TYPES.map(type => (
                                      <MenuItem key={type.value} value={type.value}>
                                        {type.label}
                                      </MenuItem>
                                    ))}
                                  </Select>
                                </TableCell>
                                <TableCell>
                                  <IconButton
                                    size="small"
                                    onClick={() => removeBulkEntry(index)}
                                    color="error"
                                  >
                                    <DeleteIcon />
                                  </IconButton>
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}

                    {bulkData.length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <Button
                          variant="contained"
                          onClick={() => {
                            // Generate bulk certificates
                            toast.success(`Generating ${bulkData.length} certificates...`);
                          }}
                          disabled={loading}
                          startIcon={loading ? <CircularProgress size={20} /> : <AddIcon />}
                        >
                          {loading ? 'Generating...' : `Generate ${bulkData.length} Certificates`}
                        </Button>
                      </Box>
                    )}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Templates and Recent Certificates */}
          <Grid item xs={12} md={4}>
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Available Templates
                </Typography>
                {templates.map(template => (
                  <Chip
                    key={template.id}
                    label={template.name}
                    variant={selectedTemplate === template.id ? "filled" : "outlined"}
                    onClick={() => setSelectedTemplate(template.id)}
                    sx={{ m: 0.5 }}
                  />
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Certificates
                </Typography>
                {generatedCertificates.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No certificates generated yet
                  </Typography>
                ) : (
                  generatedCertificates.slice(0, 5).map(cert => (
                    <Box key={cert.id} sx={{ mb: 2, p: 1, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                      <Typography variant="subtitle2">{cert.title}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {cert.recipientName}
                      </Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                        <Chip label={cert.status} size="small" />
                        <Tooltip title="Download Certificate">
                          <IconButton
                            size="small"
                            onClick={() => downloadCertificate(cert.id)}
                          >
                            <DownloadIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Box>
                  ))
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Template Preview Dialog */}
        <Dialog
          open={previewOpen}
          onClose={() => setPreviewOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>Certificate Template Preview</DialogTitle>
          <DialogContent>
            <Box sx={{ 
              height: 400, 
              border: 1, 
              borderColor: 'divider', 
              borderRadius: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: 'grey.50'
            }}>
              <Typography variant="h6" color="text.secondary">
                Certificate Preview
                <br />
                <Typography variant="body2">
                  Template: {templates.find(t => t.id === selectedTemplate)?.name || 'Auto-selected'}
                </Typography>
              </Typography>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setPreviewOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  );
};
