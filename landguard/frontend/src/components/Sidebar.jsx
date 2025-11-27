/**
 * Sidebar Navigation Component
 */

import { useLocation, useNavigate } from 'react-router-dom'
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  Landscape,
  Analytics,
  CloudUpload,
  Assessment,
  People,
  Settings,
  Description,
} from '@mui/icons-material'
import { useAuth } from '../hooks/useAuth'
import { USER_ROLES } from '../utils/constants'

const DRAWER_WIDTH = 240

const menuItems = [
  {
    text: 'Dashboard',
    icon: <DashboardIcon />,
    path: '/dashboard',
    roles: [USER_ROLES.ADMIN, USER_ROLES.ANALYST, USER_ROLES.VIEWER],
  },
  {
    text: 'Land Records',
    icon: <Landscape />,
    path: '/land-records',
    roles: [USER_ROLES.ADMIN, USER_ROLES.ANALYST, USER_ROLES.VIEWER],
  },
  {
    text: 'Analysis',
    icon: <Analytics />,
    path: '/analysis',
    roles: [USER_ROLES.ADMIN, USER_ROLES.ANALYST],
  },
  {
    text: 'Bulk Upload',
    icon: <CloudUpload />,
    path: '/bulk-upload',
    roles: [USER_ROLES.ADMIN, USER_ROLES.ANALYST],
  },
  {
    text: 'Reports',
    icon: <Assessment />,
    path: '/reports',
    roles: [USER_ROLES.ADMIN, USER_ROLES.ANALYST, USER_ROLES.VIEWER],
  },
  {
    text: 'User Management',
    icon: <People />,
    path: '/users',
    roles: [USER_ROLES.ADMIN],
  },
  {
    text: 'Process Document',
    icon: <Description />,
    path: '/process-document',
    roles: [USER_ROLES.ADMIN, USER_ROLES.ANALYST],
  },
]

const Sidebar = ({ open }) => {
  const location = useLocation()
  const navigate = useNavigate()
  const { user } = useAuth()

  const handleNavigation = (path) => {
    navigate(path)
  }

  const isActive = (path) => {
    return location.pathname === path
  }

  const hasAccess = (roles) => {
    return user && roles.includes(user.role)
  }

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          marginTop: '64px',
          borderRight: '1px solid rgba(0, 0, 0, 0.12)',
        },
      }}
    >
      <Box sx={{ overflow: 'auto' }}>
        <List>
          {menuItems.map((item) => {
            if (!hasAccess(item.roles)) {
              return null
            }

            return (
              <ListItem key={item.text} disablePadding>
                <ListItemButton
                  selected={isActive(item.path)}
                  onClick={() => handleNavigation(item.path)}
                  sx={{
                    '&.Mui-selected': {
                      backgroundColor: 'primary.light',
                      color: 'primary.main',
                      '&:hover': {
                        backgroundColor: 'primary.light',
                      },
                      '& .MuiListItemIcon-root': {
                        color: 'primary.main',
                      },
                    },
                  }}
                >
                  <ListItemIcon
                    sx={{
                      color: isActive(item.path) ? 'primary.main' : 'inherit',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            )
          })}
        </List>

        <Divider />

        {/* Settings Section */}
        <List>
          <ListItem disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <Settings />
              </ListItemIcon>
              <ListItemText primary="Settings" />
            </ListItemButton>
          </ListItem>
        </List>
      </Box>
    </Drawer>
  )
}

export default Sidebar