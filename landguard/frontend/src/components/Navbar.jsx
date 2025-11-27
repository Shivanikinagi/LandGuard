/**
 * Navigation Bar Component
 */

import { useState } from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Box,
  Badge,
  Tooltip,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Notifications,
  AccountCircle,
  ExitToApp,
  Settings,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { APP_NAME } from '../utils/constants'

const Navbar = ({ toggleSidebar }) => {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [anchorEl, setAnchorEl] = useState(null)

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  const handleLogout = () => {
    handleMenuClose()
    logout()
    navigate('/login')
  }

  const handleProfile = () => {
    handleMenuClose()
    // Navigate to profile page (to be implemented)
  }

  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      }}
    >
      <Toolbar>
        {/* Menu Icon */}
        <IconButton
          color="inherit"
          edge="start"
          onClick={toggleSidebar}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        {/* App Name */}
        <Typography
          variant="h6"
          component="div"
          sx={{
            flexGrow: 1,
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
          }}
        >
          🏛️ {APP_NAME}
        </Typography>

        {/* Right Side Icons */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Notifications */}
          <Tooltip title="Notifications">
            <IconButton color="inherit">
              <Badge badgeContent={3} color="error">
                <Notifications />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* User Menu */}
          <Tooltip title="Account">
            <IconButton
              color="inherit"
              onClick={handleMenuOpen}
              sx={{ ml: 1 }}
            >
              {user?.avatar ? (
                <Avatar
                  src={user.avatar}
                  alt={user.full_name || user.username}
                  sx={{ width: 32, height: 32 }}
                />
              ) : (
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                  {user?.username?.charAt(0).toUpperCase()}
                </Avatar>
              )}
            </IconButton>
          </Tooltip>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            PaperProps={{
              sx: {
                mt: 1.5,
                minWidth: 200,
              },
            }}
          >
            {/* User Info */}
            <Box sx={{ px: 2, py: 1.5, borderBottom: 1, borderColor: 'divider' }}>
              <Typography variant="subtitle2" fontWeight="bold">
                {user?.full_name || user?.username}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {user?.email}
              </Typography>
              <Typography variant="caption" display="block" color="primary">
                {user?.role}
              </Typography>
            </Box>

            {/* Menu Items */}
            <MenuItem onClick={handleProfile}>
              <AccountCircle sx={{ mr: 1 }} fontSize="small" />
              Profile
            </MenuItem>
            <MenuItem onClick={handleMenuClose}>
              <Settings sx={{ mr: 1 }} fontSize="small" />
              Settings
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <ExitToApp sx={{ mr: 1 }} fontSize="small" />
              Logout
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default Navbar