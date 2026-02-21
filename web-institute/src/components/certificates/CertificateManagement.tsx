/**
 * Certificate Management Component
 * Allows institutes to view, search, and manage generated certificates
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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Pagination,
  InputAdornment,
  Menu,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Search as SearchIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
  MoreVert as MoreVertIcon,
  Email as EmailIcon,
  Verified as VerifiedIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { toast } from 'react-hot-toast';

// Types
interface Certificate {
  id: string;
  certificateNumber: string;
  verificationCode: string;
  title: string;
  recipientName: string;
  recipientEmail: string;
  certificateType: string;
  status: string;
  score?: number;
  grade?: string;
  issuedAt: string;
  validUntil?: string;
  pdfUrl?: string;
  thumbnailUrl?: string;
}

interface SearchFilters {
  query: string;
  certificateType: string;
  status: string;
  dateFrom?: Date;
  dateTo?: Date;
}

const CERTIFICATE_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'course_completion', label: 'Course Completion' },
  { value: 'exam_pass', label: 'Exam Pass' },
  { value: 'achievement', label: 'Achievement' },
  { value: 'participation', label: 'Participation' },
  { value: 'professional', label: 'Professional' },
  { value: 'skill_verification', label: 'Skill Verification' }
];

const CERTIFICATE_STATUSES = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'generated', label: 'Generated' },
  { value: 'issued', label: 'Issued' },
  { value: 'revoked', label: 'Revoked' },
  { value: 'expired', label: 'Expired' }
];

export const CertificateManagement: React.FC = () => {
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchFilters, setSearchFilters] = useState<SearchFilters>({
    query: '',
    certificateType: '',
    status: ''
  });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedCertificate, setSelectedCertificate] = useState<Certificate | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuCertificate, setMenuCertificate] = useState<Certificate | null>(null);

  useEffect(() => {
    loadCertificates();
  }, [page, searchFilters]);

  const loadCertificates = async () => {
    setLoading(true);
    try {
      // API call to load certificates
      // const params = new URLSearchParams({
      //   page: page.toString(),
      //   limit: '20',
      //   ...(searchFilters.query && { query: searchFilters.query }),
      //   ...(searchFilters.certificateType && { certificate_type: searchFilters.certificateType }),
      //   ...(searchFilters.status && { status: searchFilters.status }),
      //   ...(searchFilters.dateFrom && { date_from: searchFilters.dateFrom.toISOString() }),
      //   ...(searchFilters.dateTo && { date_to: searchFilters.dateTo.toISOString() })
      // });
      
      // const response = await api.get(`/certificates?${params}`);
      // setCertificates(response.data.certificates);
      // setTotalPages(response.data.total_pages);
      
      // Mock data for now
      const mockCertificates: Certificate[] = [
        {
          id: '1',
          certificateNumber: 'MEDH-20240722-A1B2',
          verificationCode: 'VER123456789',
          title: 'React Development Certification',
          recipientName: 'John Doe',
          recipientEmail: 'john.doe@example.com',
          certificateType: 'course_completion',
          status: 'issued',
          score: 95,
          grade: 'A+',
          issuedAt: '2024-07-22T10:30:00Z',
          validUntil: '2025-07-22T10:30:00Z'
        },
        {
          id: '2',
          certificateNumber: 'MEDH-20240721-C3D4',
          verificationCode: 'VER987654321',
          title: 'Data Science Professional Certificate',
          recipientName: 'Jane Smith',
          recipientEmail: 'jane.smith@example.com',
          certificateType: 'professional',
          status: 'generated',
          score: 88,
          grade: 'A',
          issuedAt: '2024-07-21T14:15:00Z'
        }
      ];
      
      setCertificates(mockCertificates);
      setTotalPages(1);
      
    } catch (error) {
      toast.error('Failed to load certificates');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    loadCertificates();
  };

  const handleFilterChange = (field: keyof SearchFilters, value: any) => {
    setSearchFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const downloadCertificate = async (certificate: Certificate) => {
    try {
      // API call to download certificate
      // const response = await api.get(`/certificates/${certificate.id}/download`, { responseType: 'blob' });
      // const url = window.URL.createObjectURL(new Blob([response.data]));
      // const link = document.createElement('a');
      // link.href = url;
      // link.setAttribute('download', `${certificate.certificateNumber}.pdf`);
      // document.body.appendChild(link);
      // link.click();
      // link.remove();
      
      toast.success(`Downloading certificate ${certificate.certificateNumber}`);
    } catch (error) {
      toast.error('Failed to download certificate');
    }
  };

  const sendCertificateEmail = async (certificate: Certificate) => {
    try {
      // API call to send certificate via email
      // await api.post(`/certificates/${certificate.id}/send-email`);
      
      toast.success(`Certificate sent to ${certificate.recipientEmail}`);
    } catch (error) {
      toast.error('Failed to send certificate email');
    }
  };

  const verifyCertificate = async (verificationCode: string) => {
    try {
      // API call to verify certificate
      // const response = await api.post('/certificates/verify', { verification_code: verificationCode });
      
      toast.success('Certificate verified successfully');
    } catch (error) {
      toast.error('Certificate verification failed');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'issued': return 'success';
      case 'generated': return 'primary';
      case 'draft': return 'default';
      case 'revoked': return 'error';
      case 'expired': return 'warning';
      default: return 'default';
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, certificate: Certificate) => {
    setAnchorEl(event.currentTarget);
    setMenuCertificate(certificate);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setMenuCertificate(null);
  };

  const viewCertificateDetails = (certificate: Certificate) => {
    setSelectedCertificate(certificate);
    setDetailsOpen(true);
    handleMenuClose();
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Certificate Management
        </Typography>

        {/* Search and Filters */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  placeholder="Search certificates..."
                  value={searchFilters.query}
                  onChange={(e) => handleFilterChange('query', e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon />
                      </InputAdornment>
                    )
                  }}
                />
              </Grid>
              
              <Grid item xs={12} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Type</InputLabel>
                  <Select
                    value={searchFilters.certificateType}
                    onChange={(e) => handleFilterChange('certificateType', e.target.value)}
                  >
                    {CERTIFICATE_TYPES.map(type => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={searchFilters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                  >
                    {CERTIFICATE_STATUSES.map(status => (
                      <MenuItem key={status.value} value={status.value}>
                        {status.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={2}>
                <DatePicker
                  label="From Date"
                  value={searchFilters.dateFrom || null}
                  onChange={(date) => handleFilterChange('dateFrom', date)}
                  slotProps={{
                    textField: {
                      fullWidth: true
                    }
                  }}
                />
              </Grid>

              <Grid item xs={12} md={2}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="contained"
                    onClick={handleSearch}
                    startIcon={<SearchIcon />}
                  >
                    Search
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={loadCertificates}
                    startIcon={<RefreshIcon />}
                  >
                    Refresh
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Certificates Table */}
        <Card>
          <CardContent>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Certificate Number</TableCell>
                    <TableCell>Title</TableCell>
                    <TableCell>Recipient</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Score/Grade</TableCell>
                    <TableCell>Issued Date</TableCell>
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
                      <TableCell>{certificate.title}</TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">{certificate.recipientName}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {certificate.recipientEmail}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={certificate.certificateType.replace('_', ' ')} 
                          size="small" 
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={certificate.status} 
                          size="small" 
                          color={getStatusColor(certificate.status) as any}
                        />
                      </TableCell>
                      <TableCell>
                        {certificate.score && (
                          <Box>
                            <Typography variant="body2">{certificate.score}%</Typography>
                            {certificate.grade && (
                              <Typography variant="caption" color="text.secondary">
                                Grade: {certificate.grade}
                              </Typography>
                            )}
                          </Box>
                        )}
                      </TableCell>
                      <TableCell>
                        {new Date(certificate.issuedAt).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="Download Certificate">
                            <IconButton
                              size="small"
                              onClick={() => downloadCertificate(certificate)}
                            >
                              <DownloadIcon />
                            </IconButton>
                          </Tooltip>
                          
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              onClick={() => viewCertificateDetails(certificate)}
                            >
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>

                          <IconButton
                            size="small"
                            onClick={(e) => handleMenuOpen(e, certificate)}
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

            {/* Pagination */}
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(_, newPage) => setPage(newPage)}
                color="primary"
              />
            </Box>
          </CardContent>
        </Card>

        {/* Action Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={() => {
            if (menuCertificate) sendCertificateEmail(menuCertificate);
            handleMenuClose();
          }}>
            <ListItemIcon>
              <EmailIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Send via Email</ListItemText>
          </MenuItem>
          
          <MenuItem onClick={() => {
            if (menuCertificate) verifyCertificate(menuCertificate.verificationCode);
            handleMenuClose();
          }}>
            <ListItemIcon>
              <VerifiedIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Verify Certificate</ListItemText>
          </MenuItem>
        </Menu>

        {/* Certificate Details Dialog */}
        <Dialog
          open={detailsOpen}
          onClose={() => setDetailsOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>Certificate Details</DialogTitle>
          <DialogContent>
            {selectedCertificate && (
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Certificate Number
                  </Typography>
                  <Typography variant="body1" fontFamily="monospace">
                    {selectedCertificate.certificateNumber}
                  </Typography>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Verification Code
                  </Typography>
                  <Typography variant="body1" fontFamily="monospace">
                    {selectedCertificate.verificationCode}
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Title
                  </Typography>
                  <Typography variant="body1">
                    {selectedCertificate.title}
                  </Typography>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Recipient
                  </Typography>
                  <Typography variant="body1">
                    {selectedCertificate.recipientName}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {selectedCertificate.recipientEmail}
                  </Typography>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip 
                    label={selectedCertificate.status} 
                    color={getStatusColor(selectedCertificate.status) as any}
                  />
                </Grid>

                {selectedCertificate.score && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Score & Grade
                    </Typography>
                    <Typography variant="body1">
                      {selectedCertificate.score}% 
                      {selectedCertificate.grade && ` (${selectedCertificate.grade})`}
                    </Typography>
                  </Grid>
                )}

                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Issued Date
                  </Typography>
                  <Typography variant="body1">
                    {new Date(selectedCertificate.issuedAt).toLocaleString()}
                  </Typography>
                </Grid>

                {selectedCertificate.validUntil && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Valid Until
                    </Typography>
                    <Typography variant="body1">
                      {new Date(selectedCertificate.validUntil).toLocaleString()}
                    </Typography>
                  </Grid>
                )}
              </Grid>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDetailsOpen(false)}>Close</Button>
            {selectedCertificate && (
              <Button
                variant="contained"
                onClick={() => downloadCertificate(selectedCertificate)}
                startIcon={<DownloadIcon />}
              >
                Download
              </Button>
            )}
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  );
};
