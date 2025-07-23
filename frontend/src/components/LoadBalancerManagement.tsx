import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
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
  Chip,
  IconButton,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Snackbar,
  Tooltip,
  LinearProgress,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  HealthAndSafety as HealthIcon,
  Computer as ServerIcon,
  Speed as SpeedIcon,
  Settings as SettingsIcon,
  CloudQueue as CloudIcon,
  Storage as StorageIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface Server {
  id: number;
  hostname: string;
  ip_address: string;
  port: number;
  server_type: string;
  weight: number;
  max_fails: number;
  fail_timeout: number;
  status: string;
  health_status: string;
  response_time_ms?: number;
  region?: string;
  cpu_cores?: number;
  memory_gb?: number;
  added_at: string;
  endpoint: string;
}

interface LoadBalancerStatus {
  total_servers: number;
  healthy_servers: number;
  servers: Server[];
}

const LoadBalancerManagement: React.FC = () => {
  const [servers, setServers] = useState<Server[]>([]);
  const [loading, setLoading] = useState(false);
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [selectedServer, setSelectedServer] = useState<Server | null>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Form state for adding/editing servers
  const [formData, setFormData] = useState({
    hostname: '',
    ip_address: '',
    port: 8000,
    server_type: 'backend',
    weight: 1,
    max_fails: 3,
    fail_timeout: 30,
    region: '',
    cpu_cores: 2,
    memory_gb: 4,
    notes: '',
    tags: ''
  });

  useEffect(() => {
    loadServers();
    
    // Auto-refresh every 30 seconds if enabled
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(loadServers, 30000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const loadServers = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/load-balancer/status', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (response.ok) {
        const data: LoadBalancerStatus = await response.json();
        setServers(data.servers);
      }
    } catch (error) {
      console.error('Error loading servers:', error);
      showSnackbar('Error loading servers', 'error');
    } finally {
      setLoading(false);
    }
  };

  const addServer = async () => {
    try {
      const response = await fetch('/api/v1/load-balancer/servers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        showSnackbar('Server added successfully', 'success');
        setOpenAddDialog(false);
        resetForm();
        loadServers();
      } else {
        const error = await response.json();
        showSnackbar(error.detail || 'Error adding server', 'error');
      }
    } catch (error) {
      console.error('Error adding server:', error);
      showSnackbar('Error adding server', 'error');
    }
  };

  const removeServer = async (serverId: number) => {
    if (!confirm('Are you sure you want to remove this server?')) return;

    try {
      const response = await fetch(`/api/v1/load-balancer/servers/${serverId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });

      if (response.ok) {
        showSnackbar('Server removed successfully', 'success');
        loadServers();
      } else {
        const error = await response.json();
        showSnackbar(error.detail || 'Error removing server', 'error');
      }
    } catch (error) {
      console.error('Error removing server:', error);
      showSnackbar('Error removing server', 'error');
    }
  };

  const updateServerWeight = async (serverId: number, newWeight: number) => {
    try {
      const response = await fetch(`/api/v1/load-balancer/servers/${serverId}/weight`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ weight: newWeight })
      });

      if (response.ok) {
        showSnackbar('Server weight updated', 'success');
        loadServers();
      } else {
        const error = await response.json();
        showSnackbar(error.detail || 'Error updating weight', 'error');
      }
    } catch (error) {
      console.error('Error updating weight:', error);
      showSnackbar('Error updating weight', 'error');
    }
  };

  const triggerHealthCheck = async (serverId?: number) => {
    try {
      const url = serverId 
        ? `/api/v1/load-balancer/health-check?server_id=${serverId}`
        : '/api/v1/load-balancer/health-check';
        
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });

      if (response.ok) {
        showSnackbar('Health check completed', 'success');
        loadServers();
      } else {
        const error = await response.json();
        showSnackbar(error.detail || 'Health check failed', 'error');
      }
    } catch (error) {
      console.error('Error during health check:', error);
      showSnackbar('Health check failed', 'error');
    }
  };

  const reloadNginxConfig = async () => {
    try {
      const response = await fetch('/api/v1/load-balancer/reload-config', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });

      if (response.ok) {
        showSnackbar('Nginx configuration reloaded', 'success');
      } else {
        const error = await response.json();
        showSnackbar(error.detail || 'Error reloading config', 'error');
      }
    } catch (error) {
      console.error('Error reloading config:', error);
      showSnackbar('Error reloading config', 'error');
    }
  };

  const showSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbar({ open: true, message, severity });
  };

  const resetForm = () => {
    setFormData({
      hostname: '',
      ip_address: '',
      port: 8000,
      server_type: 'backend',
      weight: 1,
      max_fails: 3,
      fail_timeout: 30,
      region: '',
      cpu_cores: 2,
      memory_gb: 4,
      notes: '',
      tags: ''
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'error';
      case 'maintenance': return 'warning';
      default: return 'default';
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'success';
      case 'unhealthy': return 'error';
      default: return 'warning';
    }
  };

  const healthyServers = servers.filter(s => s.health_status === 'healthy').length;
  const totalServers = servers.length;

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Load Balancer Management
        </Typography>
        <Box display="flex" gap={2}>
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
            }
            label="Auto Refresh"
          />
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadServers}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<SettingsIcon />}
            onClick={reloadNginxConfig}
          >
            Reload Config
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenAddDialog(true)}
          >
            Add Server
          </Button>
        </Box>
      </Box>

      {/* Status Overview */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <ServerIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {totalServers}
                  </Typography>
                  <Typography color="textSecondary">
                    Total Servers
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <HealthIcon sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4" fontWeight="bold" color="success.main">
                    {healthyServers}
                  </Typography>
                  <Typography color="textSecondary">
                    Healthy Servers
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <SpeedIcon sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {totalServers > 0 ? Math.round((healthyServers / totalServers) * 100) : 0}%
                  </Typography>
                  <Typography color="textSecondary">
                    Health Rate
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <CloudIcon sx={{ fontSize: 40, color: 'warning.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {servers.filter(s => s.server_type === 'backend').length}
                  </Typography>
                  <Typography color="textSecondary">
                    Backend Servers
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Servers Table */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Server Pool</Typography>
            <Button
              variant="outlined"
              startIcon={<HealthIcon />}
              onClick={() => triggerHealthCheck()}
              size="small"
            >
              Check All Health
            </Button>
          </Box>
          
          {loading && <LinearProgress sx={{ mb: 2 }} />}
          
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Server</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Health</TableCell>
                  <TableCell>Weight</TableCell>
                  <TableCell>Response Time</TableCell>
                  <TableCell>Specs</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <AnimatePresence>
                  {servers.map((server) => (
                    <motion.tr
                      key={server.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      component={TableRow}
                    >
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {server.hostname}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {server.ip_address}:{server.port}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={server.server_type}
                          size="small"
                          color={server.server_type === 'backend' ? 'primary' : 'secondary'}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={server.status}
                          size="small"
                          color={getStatusColor(server.status) as any}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={server.health_status}
                          size="small"
                          color={getHealthColor(server.health_status) as any}
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          type="number"
                          value={server.weight}
                          onChange={(e) => updateServerWeight(server.id, parseInt(e.target.value))}
                          size="small"
                          sx={{ width: 80 }}
                          inputProps={{ min: 1, max: 100 }}
                        />
                      </TableCell>
                      <TableCell>
                        {server.response_time_ms ? `${server.response_time_ms}ms` : 'N/A'}
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption">
                          {server.cpu_cores}C / {server.memory_gb}GB
                          {server.region && ` / ${server.region}`}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box display="flex" gap={1}>
                          <Tooltip title="Health Check">
                            <IconButton
                              size="small"
                              onClick={() => triggerHealthCheck(server.id)}
                            >
                              <HealthIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedServer(server);
                                setOpenEditDialog(true);
                              }}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Remove">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => removeServer(server.id)}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </motion.tr>
                  ))}
                </AnimatePresence>
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Add Server Dialog */}
      <Dialog open={openAddDialog} onClose={() => setOpenAddDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add New Server</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Hostname"
                value={formData.hostname}
                onChange={(e) => setFormData({ ...formData, hostname: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="IP Address"
                value={formData.ip_address}
                onChange={(e) => setFormData({ ...formData, ip_address: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Port"
                type="number"
                value={formData.port}
                onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
                required
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Server Type</InputLabel>
                <Select
                  value={formData.server_type}
                  onChange={(e) => setFormData({ ...formData, server_type: e.target.value })}
                >
                  <MenuItem value="backend">Backend</MenuItem>
                  <MenuItem value="frontend">Frontend</MenuItem>
                  <MenuItem value="database">Database</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Weight"
                type="number"
                value={formData.weight}
                onChange={(e) => setFormData({ ...formData, weight: parseInt(e.target.value) })}
                inputProps={{ min: 1, max: 100 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Region"
                value={formData.region}
                onChange={(e) => setFormData({ ...formData, region: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="CPU Cores"
                type="number"
                value={formData.cpu_cores}
                onChange={(e) => setFormData({ ...formData, cpu_cores: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Memory (GB)"
                type="number"
                value={formData.memory_gb}
                onChange={(e) => setFormData({ ...formData, memory_gb: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={2}
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={addServer}>Add Server</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default LoadBalancerManagement;
