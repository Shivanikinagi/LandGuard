import { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  TrendingUp,
  Warning,
  CheckCircle,
  Assessment,
} from '@mui/icons-material'
import StatsCard from './StatsCard'
import RiskChart from './RiskChart'
import { getDashboardStats } from '../services/dashboard'

const Dashboard = () => {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [dashboardData, setDashboardData] = useState(null)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getDashboardStats()
      setDashboardData(data)
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      setError('Failed to load dashboard data. Please try again.')
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
        <Alert severity="error">{error}</Alert>
      </Box>
    )
  }

  const stats = dashboardData?.statistics || {}
  const recentAnalyses = dashboardData?.recent_analyses || []
  const fraudTrends = dashboardData?.fraud_trends || []
  const riskDistribution = dashboardData?.risk_distribution || []

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={3}>
        Overview of land fraud detection system
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Total Records"
            value={stats.total_records || 0}
            icon={<Assessment />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Flagged Records"
            value={stats.flagged_records || 0}
            icon={<Warning />}
            color="error"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="High Risk"
            value={stats.high_risk || 0}
            icon={<TrendingUp />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Fraud Rate"
            value={`${stats.fraud_percentage || 0}%`}
            icon={<CheckCircle />}
            color="success"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Fraud Trends
              </Typography>
              <RiskChart data={fraudTrends} type="line" />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Distribution
              </Typography>
              <RiskChart data={riskDistribution} type="pie" />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Analyses */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Analyses
          </Typography>
          <Box>
            {recentAnalyses.length === 0 ? (
              <Typography color="text.secondary">No recent analyses found</Typography>
            ) : (
              recentAnalyses.map((analysis) => (
                <Box
                  key={analysis.id}
                  p={2}
                  mb={1}
                  borderRadius={1}
                  bgcolor="grey.50"
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Box>
                    <Typography variant="body1" fontWeight={500}>
                      {analysis.land_record_id}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {analysis.location}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography
                      variant="caption"
                      px={1.5}
                      py={0.5}
                      borderRadius={1}
                      bgcolor={
                        analysis.risk_level === 'HIGH'
                          ? 'error.light'
                          : analysis.risk_level === 'MEDIUM'
                          ? 'warning.light'
                          : 'success.light'
                      }
                      color="white"
                    >
                      {analysis.risk_level}
                    </Typography>
                  </Box>
                </Box>
              ))
            )}
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}

export default Dashboard