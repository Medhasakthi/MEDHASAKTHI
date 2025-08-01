import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
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
  Divider,
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
  Chip,
  Avatar,
  Paper
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Security as SecurityIcon,
  Email as EmailIcon,
  Payment as PaymentIcon,
  Notifications as NotificationsIcon,
  Storage as StorageIcon,
  Backup as BackupIcon,
  Update as UpdateIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';

interface SystemConfig {
  general: {
    siteName: string;
    siteUrl: string;
    adminEmail: string;
    timezone: string;
    language: string;
    maintenanceMode: boolean;
  };
  email: {
    smtpHost: string;
    smtpPort: number;
    smtpUsername: string;
    smtpPassword: string;
    fromEmail: string;
    fromName: string;
    enableTLS: boolean;
  };
  payment: {
    upiEnabled: boolean;
    cardEnabled: boolean;
    walletEnabled: boolean;
    minAmount: number;
    maxAmount: number;
    currency: string;
  };
  security: {
    passwordMinLength: number;
    sessionTimeout: number;
    maxLoginAttempts: number;
    twoFactorAuth: boolean;
    ipWhitelist: string[];
  };
  notifications: {
    emailNotifications: boolean;
    smsNotifications: boolean;
    pushNotifications: boolean;
    welcomeEmails: boolean;
    paymentNotifications: boolean;
  };
}

interface UPIProvider {
  id: string;
  name: string;
  upiId: string;
  isActive: boolean;
  isPrimary: boolean;
  minAmount: number;
  maxAmount: number;
}

const SystemSettings: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState<SystemConfig | null>(null);
  const [upiProviders, setUpiProviders] = useState<UPIProvider[]>([]);
  const [upiDialog, setUpiDialog] = useState(false);
  const [newUpiProvider, setNewUpiProvider] = useState<Partial<UPIProvider>>({});
  const [testEmailDialog, setTestEmailDialog] = useState(false);

  useEffect(() => {
    loadSystemConfig();
    loadUpiProviders();
  }, []);

  const loadSystemConfig = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/admin/system-config', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setConfig(data);
    } catch (error) {
      // Handle error silently in production
    } finally {
      setLoading(false);
    }
  };

  const loadUpiProviders = async () => {
    try {
      const response = await fetch('/api/v1/payments/upi/admin/config', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setUpiProviders(data);
    } catch (error) {
      // Handle error silently in production
    }
  };

  const saveConfig = async () => {
    try {
      setSaving(true);
      const response = await fetch('/api/v1/admin/system-config', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(config)
      });

      if (response.ok) {
        // Configuration saved successfully
      }
    } catch (error) {
      // Handle error silently in production
    } finally {
      setSaving(false);
    }
  };

  const addUpiProvider = async () => {
    try {
      const response = await fetch('/api/v1/payments/upi/admin/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newUpiProvider)
      });

      if (response.ok) {
        loadUpiProviders();
        setUpiDialog(false);
        setNewUpiProvider({});
      }
    } catch (error) {
      // Handle error silently in production
    }
  };

  const testEmailConfiguration = async () => {
    try {
      const response = await fetch('/api/v1/admin/test-email', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        setTestEmailDialog(true);
      }
    } catch (error) {
      // Handle error silently in production
    }
  };

  const SettingCard: React.FC<{ title: string; children: React.ReactNode; icon: React.ReactNode }> = 
    ({ title, children, icon }) => (
    <motion.div whileHover={{ scale: 1.01 }}>
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
              {icon}
            </Avatar>
            <Typography variant="h6" fontWeight="bold">
              {title}
            </Typography>
          </Box>
          {children}
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
            System Settings
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Configure system-wide settings and preferences
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadSystemConfig}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={saveConfig}
            disabled={saving}
          >
            {saving ? <CircularProgress size={20} /> : 'Save Changes'}
          </Button>
        </Box>
      </Box>

      {/* Tabs */}
      <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="General" icon={<SettingsIcon />} />
        <Tab label="Email" icon={<EmailIcon />} />
        <Tab label="Payments" icon={<PaymentIcon />} />
        <Tab label="Security" icon={<SecurityIcon />} />
        <Tab label="Notifications" icon={<NotificationsIcon />} />
      </Tabs>

      {/* General Settings */}
      {activeTab === 0 && config && (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3 }}>
          <Box>
            <SettingCard title="Basic Information" icon={<InfoIcon />}>
              <TextField
                fullWidth
                label="Site Name"
                value={config.general.siteName}
                onChange={(e) => setConfig({
                  ...config,
                  general: { ...config.general, siteName: e.target.value }
                })}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Site URL"
                value={config.general.siteUrl}
                onChange={(e) => setConfig({
                  ...config,
                  general: { ...config.general, siteUrl: e.target.value }
                })}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Admin Email"
                type="email"
                value={config.general.adminEmail}
                onChange={(e) => setConfig({
                  ...config,
                  general: { ...config.general, adminEmail: e.target.value }
                })}
                margin="normal"
              />
            </SettingCard>
          </Box>

          <Box>
            <SettingCard title="Regional Settings" icon={<SettingsIcon />}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Timezone</InputLabel>
                <Select
                  value={config.general.timezone}
                  onChange={(e) => setConfig({
                    ...config,
                    general: { ...config.general, timezone: e.target.value }
                  })}
                >
                  <MenuItem value="Asia/Kolkata">Asia/Kolkata (IST)</MenuItem>
                  <MenuItem value="UTC">UTC</MenuItem>
                  <MenuItem value="America/New_York">America/New_York (EST)</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth margin="normal">
                <InputLabel>Language</InputLabel>
                <Select
                  value={config.general.language}
                  onChange={(e) => setConfig({
                    ...config,
                    general: { ...config.general, language: e.target.value }
                  })}
                >
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="hi">Hindi</MenuItem>
                  <MenuItem value="ta">Tamil</MenuItem>
                </Select>
              </FormControl>

              <FormControlLabel
                control={
                  <Switch
                    checked={config.general.maintenanceMode}
                    onChange={(e) => setConfig({
                      ...config,
                      general: { ...config.general, maintenanceMode: e.target.checked }
                    })}
                  />
                }
                label="Maintenance Mode"
              />
            </SettingCard>
          </Box>
        </Box>
      )}

      {/* Email Settings */}
      {activeTab === 1 && config && (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3 }}>
          <Box>
            <SettingCard title="SMTP Configuration" icon={<EmailIcon />}>
              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 2 }}>
                <Box>
                  <TextField
                    fullWidth
                    label="SMTP Host"
                    value={config.email.smtpHost}
                    onChange={(e) => setConfig({
                      ...config,
                      email: { ...config.email, smtpHost: e.target.value }
                    })}
                    margin="normal"
                  />
                </Box>
                <Box>
                  <TextField
                    fullWidth
                    label="SMTP Port"
                    type="number"
                    value={config.email.smtpPort}
                    onChange={(e) => setConfig({
                      ...config,
                      email: { ...config.email, smtpPort: Number(e.target.value) }
                    })}
                    margin="normal"
                  />
                </Box>
                <Box>
                  <TextField
                    fullWidth
                    label="Username"
                    value={config.email.smtpUsername}
                    onChange={(e) => setConfig({
                      ...config,
                      email: { ...config.email, smtpUsername: e.target.value }
                    })}
                    margin="normal"
                  />
                </Box>
                <Box>
                  <TextField
                    fullWidth
                    label="Password"
                    type="password"
                    value={config.email.smtpPassword}
                    onChange={(e) => setConfig({
                      ...config,
                      email: { ...config.email, smtpPassword: e.target.value }
                    })}
                    margin="normal"
                  />
                </Box>
                <Box>
                  <TextField
                    fullWidth
                    label="From Email"
                    type="email"
                    value={config.email.fromEmail}
                    onChange={(e) => setConfig({
                      ...config,
                      email: { ...config.email, fromEmail: e.target.value }
                    })}
                    margin="normal"
                  />
                </Box>
                <Box>
                  <TextField
                    fullWidth
                    label="From Name"
                    value={config.email.fromName}
                    onChange={(e) => setConfig({
                      ...config,
                      email: { ...config.email, fromName: e.target.value }
                    })}
                    margin="normal"
                  />
                </Box>
              </Box>

              <FormControlLabel
                control={
                  <Switch
                    checked={config.email.enableTLS}
                    onChange={(e) => setConfig({
                      ...config,
                      email: { ...config.email, enableTLS: e.target.checked }
                    })}
                  />
                }
                label="Enable TLS/SSL"
                sx={{ mt: 2 }}
              />
            </SettingCard>
          </Box>

          <Box>
            <SettingCard title="Email Testing" icon={<CheckIcon />}>
              <Alert severity="info" sx={{ mb: 2 }}>
                Test your email configuration by sending a test email.
              </Alert>
              <Button
                fullWidth
                variant="contained"
                onClick={testEmailConfiguration}
                startIcon={<EmailIcon />}
              >
                Send Test Email
              </Button>
            </SettingCard>
          </Box>
        </Box>
      )}

      {/* Payment Settings */}
      {activeTab === 2 && config && (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3 }}>
          <Box>
            <SettingCard title="Payment Methods" icon={<PaymentIcon />}>
              <FormControlLabel
                control={
                  <Switch
                    checked={config.payment.upiEnabled}
                    onChange={(e) => setConfig({
                      ...config,
                      payment: { ...config.payment, upiEnabled: e.target.checked }
                    })}
                  />
                }
                label="Enable UPI Payments"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={config.payment.cardEnabled}
                    onChange={(e) => setConfig({
                      ...config,
                      payment: { ...config.payment, cardEnabled: e.target.checked }
                    })}
                  />
                }
                label="Enable Card Payments"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={config.payment.walletEnabled}
                    onChange={(e) => setConfig({
                      ...config,
                      payment: { ...config.payment, walletEnabled: e.target.checked }
                    })}
                  />
                }
                label="Enable Wallet Payments"
              />

              <TextField
                fullWidth
                label="Minimum Amount"
                type="number"
                value={config.payment.minAmount}
                onChange={(e) => setConfig({
                  ...config,
                  payment: { ...config.payment, minAmount: Number(e.target.value) }
                })}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Maximum Amount"
                type="number"
                value={config.payment.maxAmount}
                onChange={(e) => setConfig({
                  ...config,
                  payment: { ...config.payment, maxAmount: Number(e.target.value) }
                })}
                margin="normal"
              />
            </SettingCard>
          </Box>

          <Box>
            <SettingCard title="UPI Providers" icon={<PaymentIcon />}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Configured Providers</Typography>
                <Button
                  startIcon={<AddIcon />}
                  onClick={() => setUpiDialog(true)}
                  size="small"
                >
                  Add Provider
                </Button>
              </Box>
              
              <List dense>
                {upiProviders.map((provider) => (
                  <ListItem key={provider.id}>
                    <ListItemIcon>
                      <PaymentIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={provider.name}
                      secondary={provider.upiId}
                    />
                    <ListItemSecondaryAction>
                      <Chip 
                        label={provider.isActive ? 'Active' : 'Inactive'} 
                        color={provider.isActive ? 'success' : 'default'}
                        size="small"
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </SettingCard>
          </Box>
        </Box>
      )}

      {/* Security Settings */}
      {activeTab === 3 && config && (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3 }}>
          <Box>
            <SettingCard title="Password Policy" icon={<SecurityIcon />}>
              <TextField
                fullWidth
                label="Minimum Password Length"
                type="number"
                value={config.security.passwordMinLength}
                onChange={(e) => setConfig({
                  ...config,
                  security: { ...config.security, passwordMinLength: Number(e.target.value) }
                })}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Session Timeout (minutes)"
                type="number"
                value={config.security.sessionTimeout}
                onChange={(e) => setConfig({
                  ...config,
                  security: { ...config.security, sessionTimeout: Number(e.target.value) }
                })}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Max Login Attempts"
                type="number"
                value={config.security.maxLoginAttempts}
                onChange={(e) => setConfig({
                  ...config,
                  security: { ...config.security, maxLoginAttempts: Number(e.target.value) }
                })}
                margin="normal"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={config.security.twoFactorAuth}
                    onChange={(e) => setConfig({
                      ...config,
                      security: { ...config.security, twoFactorAuth: e.target.checked }
                    })}
                  />
                }
                label="Enable Two-Factor Authentication"
              />
            </SettingCard>
          </Box>

          <Box>
            <SettingCard title="Access Control" icon={<SecurityIcon />}>
              <Alert severity="warning" sx={{ mb: 2 }}>
                IP whitelist is currently disabled. Enable for enhanced security.
              </Alert>
              <TextField
                fullWidth
                label="Allowed IP Addresses"
                multiline
                rows={4}
                value={config.security.ipWhitelist.join('\n')}
                onChange={(e) => setConfig({
                  ...config,
                  security: { 
                    ...config.security, 
                    ipWhitelist: e.target.value.split('\n').filter(ip => ip.trim()) 
                  }
                })}
                margin="normal"
                placeholder="192.168.1.1&#10;10.0.0.1"
              />
            </SettingCard>
          </Box>
        </Box>
      )}

      {/* UPI Provider Dialog */}
      <Dialog open={upiDialog} onClose={() => setUpiDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add UPI Provider</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Provider Name"
            value={newUpiProvider.name || ''}
            onChange={(e) => setNewUpiProvider({ ...newUpiProvider, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="UPI ID"
            value={newUpiProvider.upiId || ''}
            onChange={(e) => setNewUpiProvider({ ...newUpiProvider, upiId: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Minimum Amount"
            type="number"
            value={newUpiProvider.minAmount || ''}
            onChange={(e) => setNewUpiProvider({ ...newUpiProvider, minAmount: Number(e.target.value) })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Maximum Amount"
            type="number"
            value={newUpiProvider.maxAmount || ''}
            onChange={(e) => setNewUpiProvider({ ...newUpiProvider, maxAmount: Number(e.target.value) })}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUpiDialog(false)}>Cancel</Button>
          <Button onClick={addUpiProvider} variant="contained">Add Provider</Button>
        </DialogActions>
      </Dialog>

      {/* Test Email Dialog */}
      <Dialog open={testEmailDialog} onClose={() => setTestEmailDialog(false)}>
        <DialogTitle>Test Email Sent</DialogTitle>
        <DialogContent>
          <Alert severity="success">
            Test email has been sent successfully! Check your inbox.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTestEmailDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SystemSettings;
