import { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material'
import {
  TrendingUp,
  Warning,
  CheckCircle,
  Assessment,
  People,
  Refresh,
} from '@mui/icons-material'
import StatsCard from './StatsCard'
import RiskChart from './RiskChart'
import { getDashboardStats, getDashboardTrends } from '../services/dashboard'
import { useNavigate } from 'react-router-dom'

const Dashboard = () => {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [dashboardData, setDashboardData] = useState(null)
  const [trendsData, setTrendsData] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Fetch both overview and trends data
      const [statsResponse, trendsResponse] = await Promise.all([
        getDashboardStats(),
        getDashboardTrends()
      ])
      
      setDashboardData(statsResponse.data)
      setTrendsData(trendsResponse.data)
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      setError(err)
      
      // Handle 403 Forbidden specifically
      if (err.response?.status === 403) {
        setError(new Error('Authentication failed. Please log in again.'))
        // Optionally redirect to login
        setTimeout(() => {
          localStorage.removeItem('token')
          navigate('/login')
        }, 3000)
      } else if (err.response?.status === 401) {
        setError(new Error('Session expired. Please log in again.'))
        localStorage.removeItem('token')
        navigate('/login')
      } else {
        setError(new Error('Failed to load dashboard data. Please try again.'))
      }
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert 
          severity="error" 
          action={
            <Button 
              color="inherit" 
              size="small" 
              startIcon={<Refresh />}
              onClick={fetchDashboardData}
            >
              Retry
            </Button>
          }
        >
          {error.message}
        </Alert>
      </Box>
    )
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        🏛️ LandGuard Dashboard
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Overview of land fraud detection system
      </Typography>

      <Grid container spacing={3} mt={2}>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Total Records"
            value={dashboardData?.total_records || 0}
            icon={<Assessment />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Total Users"
            value={dashboardData?.total_users || 0}
            icon={<People />}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Fraud Detected"
            value={dashboardData?.fraud_detected || 0}
            icon={<Warning />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Fraud Rate"
            value={`${dashboardData?.fraud_rate || 0}%`}
            icon={<TrendingUp />}
            color="error"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3} mt={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Fraud Trends
              </Typography>
              <RiskChart data={trendsData?.fraud_trends || []} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Distribution
              </Typography>
              <RiskChart data={trendsData?.risk_distribution || []} />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box mt={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Analyses
            </Typography>
            <Typography color="textSecondary">
              {trendsData?.recent_analyses?.length > 0 
                ? "Recent analysis data will be displayed here" 
                : "No recent analyses available"}
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Box>
  )
}

export default Dashboard