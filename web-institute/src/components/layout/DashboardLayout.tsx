/**
 * Dashboard Layout Component
 */
'use client';

import React, { useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Tooltip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Psychology,
  Quiz,
  School,
  People,
  Analytics,
  Settings,
  Logout,
  AccountCircle,
  Notifications,
  ChevronLeft,
  AutoAwesome,
  LibraryBooks,
  Assessment,
} from '@mui/icons-material';

import { useAuth } from '../../contexts/AuthContext';

const drawerWidth = 280;

interface DashboardLayoutProps {
  children: React.ReactNode;
}

interface NavigationItem {
  text: string;
  icon: React.ReactElement;
  path: string;
  badge?: number;
  divider?: boolean;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const router = useRouter();
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  // Navigation items based on user role
  const getNavigationItems = (): NavigationItem[] => {
    const baseItems: NavigationItem[] = [
      {
        text: 'Dashboard',
        icon: <Dashboard />,
        path: '/dashboard',
      },
      {
        text: 'AI Question Generator',
        icon: <Psychology />,
        path: '/ai/generator',
        badge: 3, // New features
      },
      {
        text: 'Question Bank',
        icon: <LibraryBooks />,
        path: '/questions',
      },
      {
        text: 'Exams',
        icon: <Quiz />,
        path: '/exams',
      },
      {
        text: 'Students',
        icon: <School />,
        path: '/students',
      },
      {
        text: 'Teachers',
        icon: <People />,
        path: '/teachers',
        divider: true,
      },
      {
        text: 'Analytics',
        icon: <Analytics />,
        path: '/analytics',
      },
      {
        text: 'Reports',
        icon: <Assessment />,
        path: '/reports',
      },
      {
        text: 'Settings',
        icon: <Settings />,
        path: '/settings',
        divider: true,
      },
    ];

    // Filter based on user role
    if (user?.role === 'teacher') {
      return baseItems.filter(item => 
        !['Teachers', 'Settings'].includes(item.text)
      );
    }

    return baseItems;
  };

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    handleProfileMenuClose();
    await logout();
    router.push('/login');
  };

  const handleNavigation = (path: string) => {
    router.push(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const drawer = (
    <Box>
      {/* Logo and Title */}
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <AutoAwesome sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
        <Typography variant="h6" fontWeight="bold" color="primary">
          MEDHASAKTHI
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Institute Portal
        </Typography>
      </Box>

      <Divider />

      {/* Navigation Items */}
      <List sx={{ px: 2 }}>
        {getNavigationItems().map((item) => (
          <React.Fragment key={item.text}>
            <ListItem disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={pathname === item.path}
                sx={{
                  borderRadius: 2,
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'white',
                    },
                  },
                }}
              >
                <ListItemIcon>
                  {item.badge ? (
                    <Badge badgeContent={item.badge} color="error">
                      {item.icon}
                    </Badge>
                  ) : (
                    item.icon
                  )}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '0.9rem',
                    fontWeight: pathname === item.path ? 600 : 400,
                  }}
                />
              </ListItemButton>
            </ListItem>
            {item.divider && <Divider sx={{ my: 1 }} />}
          </React.Fragment>
        ))}
      </List>

      {/* User Info at Bottom */}
      <Box sx={{ position: 'absolute', bottom: 0, left: 0, right: 0, p: 2 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            p: 2,
            bgcolor: 'grey.50',
            borderRadius: 2,
          }}
        >
          <Avatar sx={{ width: 32, height: 32, mr: 2 }}>
            {user?.profile?.first_name?.[0] || user?.email?.[0]?.toUpperCase()}
          </Avatar>
          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            <Typography variant="body2" fontWeight="medium" noWrap>
              {user?.profile?.first_name} {user?.profile?.last_name}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              {user?.role?.replace('_', ' ').toUpperCase()}
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          bgcolor: 'white',
          color: 'text.primary',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {getNavigationItems().find(item => item.path === pathname)?.text || 'Dashboard'}
          </Typography>

          {/* Notifications */}
          <Tooltip title="Notifications">
            <IconButton color="inherit" sx={{ mr: 1 }}>
              <Badge badgeContent={4} color="error">
                <Notifications />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* Profile Menu */}
          <Tooltip title="Account">
            <IconButton
              color="inherit"
              onClick={handleProfileMenuOpen}
              sx={{ ml: 1 }}
            >
              <Avatar sx={{ width: 32, height: 32 }}>
                {user?.profile?.first_name?.[0] || user?.email?.[0]?.toUpperCase()}
              </Avatar>
            </IconButton>
          </Tooltip>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
            onClick={handleProfileMenuClose}
            PaperProps={{
              elevation: 0,
              sx: {
                overflow: 'visible',
                filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
                mt: 1.5,
                '& .MuiAvatar-root': {
                  width: 32,
                  height: 32,
                  ml: -0.5,
                  mr: 1,
                },
                '&:before': {
                  content: '""',
                  display: 'block',
                  position: 'absolute',
                  top: 0,
                  right: 14,
                  width: 10,
                  height: 10,
                  bgcolor: 'background.paper',
                  transform: 'translateY(-50%) rotate(45deg)',
                  zIndex: 0,
                },
              },
            }}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <MenuItem onClick={() => handleNavigation('/profile')}>
              <AccountCircle sx={{ mr: 2 }} />
              Profile
            </MenuItem>
            <MenuItem onClick={() => handleNavigation('/settings')}>
              <Settings sx={{ mr: 2 }} />
              Settings
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <Logout sx={{ mr: 2 }} />
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>

        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              borderRight: '1px solid',
              borderColor: 'divider',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          bgcolor: 'grey.50',
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
}
