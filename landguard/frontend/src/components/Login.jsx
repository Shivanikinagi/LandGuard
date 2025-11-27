/**
 * Login Component
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
} from '@mui/material'
import { Visibility, VisibilityOff, AccountCircle } from '@mui/icons-material'
import { useAuth } from '../hooks/useAuth.jsx'
import { login as loginService } from '../services/auth'
import { toast } from 'react-toastify'
import '../styles/App.css'

const Login = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!formData.username || !formData.password) {
      setError('Please enter both username and password')
      return
    }

    try {
      setLoading(true)
      const response = await loginService(formData.username, formData.password)
      
      login(response.user)
      localStorage.setItem('token', response.access_token)
      
      toast.success('Login successful!')
      navigate('/dashboard')
    } catch (err) {
      console.error('Login error:', err)
      
      // Handle different types of error responses
      let errorMessage = 'Invalid credentials. Please try again.'
      
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail
        if (typeof detail === 'string') {
          errorMessage = detail
        } else if (Array.isArray(detail)) {
          // Handle validation errors array
          errorMessage = detail.map(error => 
            `${error.loc?.join('.')}: ${error.msg}`
          ).join(', ') || errorMessage
        } else if (typeof detail === 'object') {
          // Handle object errors
          errorMessage = detail.message || JSON.stringify(detail)
        }
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box className="login-container">
      <Card className="login-card">
        <CardContent>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <AccountCircle sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              LandGuard
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Land Fraud Detection System
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              margin="normal"
              disabled={loading}
              autoFocus
            />

            <TextField
              fullWidth
              label="Password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={handleChange}
              margin="normal"
              disabled={loading}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{ mt: 3, mb: 2 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Login'}
            </Button>
          </form>

          <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
              <strong>Demo Credentials:</strong>
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              Admin: admin / admin123
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              Analyst: analyst / analyst123
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              Viewer: viewer / viewer123
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}

export default Login