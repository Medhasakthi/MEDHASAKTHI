import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
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
  Divider
} from '@mui/material';
import {
  Certificate as CertificateIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Verified as VerifiedIcon,
  School as SchoolIcon,
  Person as PersonIcon,
  CalendarToday as CalendarIcon,
  QrCode as QrCodeIcon,
  Print as PrintIcon,
  Email as EmailIcon
} from '@mui/icons-material';

interface Certificate {
  id: string;
  certificateNumber: string;
  recipientName: string;
  recipientEmail: string;
  programTitle: string;
  issueDate: string;
  expiryDate?: string;
  status: 'active' | 'expired' | 'revoked';
  verificationUrl: string;
  downloadUrl: string;
  templateId: string;
  templateName: string;
  grade?: string;
  score?: number;
}

interface CertificateTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  isActive: boolean;
  createdDate: string;
  usageCount: number;
}

interface CertificateStats {
  totalIssued: number;
  activeCount: number;
  expiredCount: number;
  revokedCount: number;
  thisMonthIssued: number;
  verificationRequests: number;
}

const CertificateManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [templates, setTemplates] = useState<CertificateTemplate[]>([]);
  const [stats, setStats] = useState<CertificateStats | null>(null);
  const [selectedCertificate, setSelectedCertificate] = useState<Certificate | null>(null);
  const [viewDialog, setViewDialog] = useState(false);
  const [createDialog, setCreateDialog] = useState(false);
  const [newCertificate, setNewCertificate] = useState<Partial<Certificate>>({});

  useEffect(() => {
    loadCertificateData();
  }, []);

  const loadCertificateData = async () => {
    try {
      setLoading(true);
      
      // Load certificates
      const certificatesResponse = await fetch('/api/v1/certificates', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const certificatesData = await certificatesResponse.json();
      setCertificates(certificatesData);

      // Load templates
      const templatesResponse = await fetch('/api/v1/certificates/templates', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const templatesData = await templatesResponse.json();
      setTemplates(templatesData);

      // Load statistics
      const statsResponse = await fetch('/api/v1/certificates/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const statsData = await statsResponse.json();
      setStats(statsData);

    } catch (error) {
      console.error('Error loading certificate data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCertificateGeneration = async () => {
    try {
      const response = await fetch('/api/v1/certificates/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newCertificate)
      });

      if (response.ok) {
        loadCertificateData();
        setCreateDialog(false);
        setNewCertificate({});
      }
    } catch (error) {
      console.error('Error generating certificate:', error);
    }
  };

  const handleCertificateDownload = async (certificateId: string) => {
    try {
      const response = await fetch(`/api/v1/certificates/${certificateId}/download`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `certificate-${certificateId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error downloading certificate:', error);
    }
  };

  const handleCertificateShare = (certificate: Certificate) => {
    const shareData = {
      title: `Certificate - ${certificate.programTitle}`,
      text: `Check out my certificate for ${certificate.programTitle}`,
      url: certificate.verificationUrl
    };

    if (navigator.share) {
      navigator.share(shareData);
    } else {
      // Fallback to copying URL
      navigator.clipboard.writeText(certificate.verificationUrl);
      // Show success message
    }
  };

  const StatCard: React.FC<{ title: string; value: string | number; icon: React.ReactNode; color: string }> = 
    ({ title, value, icon, color }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
          </Box>
          <Box sx={{ color, fontSize: 40 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom>
          Certificate Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialog(true)}
        >
          Generate Certificate
        </Button>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Issued"
            value={stats?.totalIssued || 0}
            icon={<CertificateIcon />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Certificates"
            value={stats?.activeCount || 0}
            icon={<VerifiedIcon />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="This Month"
            value={stats?.thisMonthIssued || 0}
            icon={<CalendarIcon />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Verifications"
            value={stats?.verificationRequests || 0}
            icon={<QrCodeIcon />}
            color="#9c27b0"
          />
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ width: '100%', mb: 2 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="All Certificates" />
          <Tab label="Templates" />
          <Tab label="Verification" />
        </Tabs>
      </Paper>

      {/* Certificates Tab */}
      {activeTab === 0 && (
        <Card>
          <CardContent>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Certificate #</TableCell>
                    <TableCell>Recipient</TableCell>
                    <TableCell>Program</TableCell>
                    <TableCell>Issue Date</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {certificates.map((certificate) => (
                    <TableRow key={certificate.id}>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {certificate.certificateNumber}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <Avatar sx={{ width: 32, height: 32, mr: 1, bgcolor: 'primary.main' }}>
                            {certificate.recipientName.charAt(0)}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {certificate.recipientName}
                            </Typography>
                            <Typography variant="caption" color="textSecondary">
                              {certificate.recipientEmail}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          {certificate.programTitle}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {certificate.templateName}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {new Date(certificate.issueDate).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={certificate.status} 
                          color={
                            certificate.status === 'active' ? 'success' : 
                            certificate.status === 'expired' ? 'warning' : 'error'
                          }
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Tooltip title="View Certificate">
                          <IconButton 
                            onClick={() => {
                              setSelectedCertificate(certificate);
                              setViewDialog(true);
                            }}
                            size="small"
                          >
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Download">
                          <IconButton 
                            onClick={() => handleCertificateDownload(certificate.id)}
                            size="small"
                          >
                            <DownloadIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Share">
                          <IconButton 
                            onClick={() => handleCertificateShare(certificate)}
                            size="small"
                          >
                            <ShareIcon />
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
      )}

      {/* Templates Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          {templates.map((template) => (
            <Grid item xs={12} sm={6} md={4} key={template.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="between" alignItems="start" mb={2}>
                    <Typography variant="h6" gutterBottom>
                      {template.name}
                    </Typography>
                    <Chip 
                      label={template.isActive ? 'Active' : 'Inactive'} 
                      color={template.isActive ? 'success' : 'default'}
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" color="textSecondary" mb={2}>
                    {template.description}
                  </Typography>
                  <Typography variant="body2" mb={1}>
                    <strong>Category:</strong> {template.category}
                  </Typography>
                  <Typography variant="body2" mb={2}>
                    <strong>Used:</strong> {template.usageCount} times
                  </Typography>
                  <Box display="flex" gap={1}>
                    <Button size="small" startIcon={<EditIcon />}>
                      Edit
                    </Button>
                    <Button size="small" startIcon={<ViewIcon />}>
                      Preview
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Certificate View Dialog */}
      <Dialog open={viewDialog} onClose={() => setViewDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Certificate Details</DialogTitle>
        <DialogContent>
          {selectedCertificate && (
            <Box>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="h6" gutterBottom>Certificate Information</Typography>
                  <Typography><strong>Number:</strong> {selectedCertificate.certificateNumber}</Typography>
                  <Typography><strong>Recipient:</strong> {selectedCertificate.recipientName}</Typography>
                  <Typography><strong>Program:</strong> {selectedCertificate.programTitle}</Typography>
                  <Typography><strong>Issue Date:</strong> {new Date(selectedCertificate.issueDate).toLocaleDateString()}</Typography>
                  {selectedCertificate.score && (
                    <Typography><strong>Score:</strong> {selectedCertificate.score}%</Typography>
                  )}
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="h6" gutterBottom>Verification</Typography>
                  <Typography variant="body2" gutterBottom>
                    Verification URL:
                  </Typography>
                  <Paper sx={{ p: 1, bgcolor: 'grey.100', mb: 2 }}>
                    <Typography variant="body2" fontFamily="monospace" sx={{ wordBreak: 'break-all' }}>
                      {selectedCertificate.verificationUrl}
                    </Typography>
                  </Paper>
                  <Box display="flex" gap={1}>
                    <Button size="small" startIcon={<QrCodeIcon />}>
                      QR Code
                    </Button>
                    <Button size="small" startIcon={<EmailIcon />}>
                      Email
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialog(false)}>Close</Button>
          <Button 
            variant="contained" 
            startIcon={<DownloadIcon />}
            onClick={() => selectedCertificate && handleCertificateDownload(selectedCertificate.id)}
          >
            Download
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Certificate Dialog */}
      <Dialog open={createDialog} onClose={() => setCreateDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Generate New Certificate</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Recipient Name"
              value={newCertificate.recipientName || ''}
              onChange={(e) => setNewCertificate({ ...newCertificate, recipientName: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Recipient Email"
              type="email"
              value={newCertificate.recipientEmail || ''}
              onChange={(e) => setNewCertificate({ ...newCertificate, recipientEmail: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Program Title"
              value={newCertificate.programTitle || ''}
              onChange={(e) => setNewCertificate({ ...newCertificate, programTitle: e.target.value })}
              margin="normal"
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Template</InputLabel>
              <Select
                value={newCertificate.templateId || ''}
                onChange={(e) => setNewCertificate({ ...newCertificate, templateId: e.target.value })}
              >
                {templates.filter(t => t.isActive).map((template) => (
                  <MenuItem key={template.id} value={template.id}>
                    {template.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Score (%)"
              type="number"
              value={newCertificate.score || ''}
              onChange={(e) => setNewCertificate({ ...newCertificate, score: Number(e.target.value) })}
              margin="normal"
              inputProps={{ min: 0, max: 100 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialog(false)}>Cancel</Button>
          <Button onClick={handleCertificateGeneration} variant="contained">
            Generate Certificate
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CertificateManagement;
