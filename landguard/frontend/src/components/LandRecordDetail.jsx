/**
 * Land Record Detail Component
 */

import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Button,
  Divider,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
} from '@mui/material'
import {
  ArrowBack,
  Edit,
  Delete,
  Assessment,
  LocationOn,
  Person,
  CalendarToday,
  Home,
  AttachMoney,
} from '@mui/icons-material'
import { getLandRecordById, deleteLandRecord } from '../services/landRecords'
import { analyzeLandRecord } from '../services/analysis'
import { toast } from 'react-toastify'
import {
  formatDate,
  formatArea,
  formatPropertyType,
  formatCurrency,
} from '../utils/formatters'

const LandRecordDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [record, setRecord] = useState(null)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchRecordDetail()
  }, [id])

  const fetchRecordDetail = async () => {
    try {
      setLoading(true)
      const data = await getLandRecordById(id)
      setRecord(data)
      setError(null)
    } catch (err) {
      console.error('Error fetching record detail:', err)
      setError('Failed to load land record details')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    try {
      setAnalyzing(true)
      const result = await analyzeLandRecord(id)
      toast.success('Analysis completed successfully')
      navigate(`/analysis/${result.id}`)
    } catch (err) {
      console.error('Error analyzing record:', err)
      toast.error('Failed to analyze land record')
    } finally {
      setAnalyzing(false)
    }
  }

  const handleEdit = () => {
    toast.info('Edit functionality coming soon')
  }

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this record?')) {
      try {
        await deleteLandRecord(id)
        toast.success('Land record deleted successfully')
        navigate('/land-records')
      } catch (err) {
        console.error('Error deleting record:', err)
        toast.error('Failed to delete land record')
      }
    }
  }

  if (loading) {
    return (
      <Box className="loading-spinner">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    )
  }

  if (!record) {
    return (
      <Alert severity="warning" sx={{ mt: 2 }}>
        Land record not found
      </Alert>
    )
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate('/land-records')}
        >
          Back
        </Button>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h4" fontWeight="bold">
            {record.land_id}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Land Record Details
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<Edit />}
          onClick={handleEdit}
        >
          Edit
        </Button>
        <Button
          variant="outlined"
          color="error"
          startIcon={<Delete />}
          onClick={handleDelete}
        >
          Delete
        </Button>
        <Button
          variant="contained"
          startIcon={<Assessment />}
          onClick={handleAnalyze}
          disabled={analyzing}
        >
          {analyzing ? 'Analyzing...' : 'Analyze'}
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Basic Information */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Basic Information
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <LocationOn sx={{ mr: 1, color: 'text.secondary' }} />
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Location
                    </Typography>
                    <Typography variant="body1">{record.location}</Typography>
                  </Box>
                </Box>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Home sx={{ mr: 1, color: 'text.secondary' }} />
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Area
                    </Typography>
                    <Typography variant="body1">
                      {formatArea(record.area_sqft)}
                    </Typography>
                  </Box>
                </Box>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Person sx={{ mr: 1, color: 'text.secondary' }} />
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Current Owner
                    </Typography>
                    <Typography variant="body1">
                      {record.current_owner}
                    </Typography>
                  </Box>
                </Box>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <CalendarToday sx={{ mr: 1, color: 'text.secondary' }} />
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Created Date
                    </Typography>
                    <Typography variant="body1">
                      {formatDate(record.created_at)}
                    </Typography>
                  </Box>
                </Box>
              </Grid>

              <Grid item xs={12}>
                <Typography variant="caption" color="text.secondary">
                  Property Type
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <Chip
                    label={formatPropertyType(record.property_type)}
                    color="primary"
                  />
                </Box>
              </Grid>
            </Grid>
          </Paper>

          {/* Ownership History */}
          {record.ownership_history && record.ownership_history.length > 0 && (
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Ownership History
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <List>
                {record.ownership_history.map((owner, index) => (
                  <ListItem key={index} divider={index < record.ownership_history.length - 1}>
                    <ListItemText
                      primary={owner.owner_name}
                      secondary={
                        <>
                          <Typography variant="caption" display="block">
                            From: {formatDate(owner.start_date)}
                          </Typography>
                          <Typography variant="caption" display="block">
                            To: {owner.end_date ? formatDate(owner.end_date) : 'Present'}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}

          {/* Transactions */}
          {record.transactions && record.transactions.length > 0 && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Transaction History
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <List>
                {record.transactions.map((transaction, index) => (
                  <ListItem key={index} divider={index < record.transactions.length - 1}>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2">
                            {transaction.transaction_type}
                          </Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {formatCurrency(transaction.amount)}
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <>
                          <Typography variant="caption" display="block">
                            Date: {formatDate(transaction.date)}
                          </Typography>
                          <Typography variant="caption" display="block">
                            Buyer: {transaction.buyer_name}
                          </Typography>
                          <Typography variant="caption" display="block">
                            Seller: {transaction.seller_name}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          {/* Quick Stats */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Quick Stats
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Total Transactions
                </Typography>
                <Typography variant="h5" fontWeight="bold">
                  {record.transactions?.length || 0}
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Ownership Changes
                </Typography>
                <Typography variant="h5" fontWeight="bold">
                  {record.ownership_history?.length || 0}
                </Typography>
              </Box>

              <Box>
                <Typography variant="caption" color="text.secondary">
                  Documents
                </Typography>
                <Typography variant="h5" fontWeight="bold">
                  {record.documents?.length || 0}
                </Typography>
              </Box>
            </CardContent>
          </Card>

          {/* Documents */}
          {record.documents && record.documents.length > 0 && (
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Documents
                </Typography>
                <Divider sx={{ mb: 2 }} />

                <List dense>
                  {record.documents.map((doc, index) => (
                    <ListItem key={index}>
                      <ListItemText
                        primary={doc.name}
                        secondary={doc.type}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  )
}

export default LandRecordDetail