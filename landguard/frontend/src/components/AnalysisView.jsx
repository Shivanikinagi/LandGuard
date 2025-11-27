/**
 * Analysis View Component
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  Button,
  IconButton,
  Chip,
  Typography,
  CircularProgress,
  InputAdornment,
  Card,
  CardContent,
  Grid,
} from '@mui/material'
import {
  Search,
  Visibility,
  FilterList,
  Warning,
  CheckCircle,
  Error,
} from '@mui/icons-material'
import { getAnalysisResults } from '../services/analysis'
import { toast } from 'react-toastify'
import {
  formatDate,
  formatRiskScore,
  formatConfidence,
  formatRiskLevel,
} from '../utils/formatters'
import { RISK_COLORS, DEFAULT_PAGE_SIZE } from '../utils/constants'

const AnalysisView = () => {
  const navigate = useNavigate()
  const [analyses, setAnalyses] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(DEFAULT_PAGE_SIZE)
  const [totalAnalyses, setTotalAnalyses] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')
  const [stats, setStats] = useState({
    total: 0,
    fraudDetected: 0,
    lowRisk: 0,
    highRisk: 0,
  })

  useEffect(() => {
    fetchAnalyses()
  }, [page, rowsPerPage])

  const fetchAnalyses = async () => {
    try {
      setLoading(true)
      const response = await getAnalysisResults(page + 1, rowsPerPage, {
        search: searchQuery,
      })
      setAnalyses(response.items || [])
      setTotalAnalyses(response.total || 0)
      
      // Calculate stats
      const fraudCount = response.items?.filter(a => a.fraud_detected).length || 0
      const highRiskCount = response.items?.filter(a => a.risk_level === 'HIGH' || a.risk_level === 'CRITICAL').length || 0
      const lowRiskCount = response.items?.filter(a => a.risk_level === 'LOW').length || 0
      
      setStats({
        total: response.total || 0,
        fraudDetected: fraudCount,
        lowRisk: lowRiskCount,
        highRisk: highRiskCount,
      })
    } catch (error) {
      console.error('Error fetching analyses:', error)
      toast.error('Failed to load analysis results')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    setPage(0)
    fetchAnalyses()
  }

  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const handleViewDetail = (analysis) => {
    navigate(`/land-records/${analysis.land_record_id}`)
  }

  const getRiskChipColor = (riskLevel) => {
    switch (riskLevel) {
      case 'LOW':
        return 'success'
      case 'MEDIUM':
        return 'warning'
      case 'HIGH':
      case 'CRITICAL':
        return 'error'
      default:
        return 'default'
    }
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Analysis Results
        </Typography>
        <Typography variant="body2" color="text.secondary">
          View fraud detection analysis results
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircle color="primary" sx={{ mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  Total Analyses
                </Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold">
                {stats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Warning color="error" sx={{ mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  Fraud Detected
                </Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold" color="error">
                {stats.fraudDetected}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircle color="success" sx={{ mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  Low Risk
                </Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold" color="success.main">
                {stats.lowRisk}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Error color="error" sx={{ mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  High Risk
                </Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold" color="error">
                {stats.highRisk}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            fullWidth
            placeholder="Search by Land ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
          <Button
            variant="contained"
            onClick={handleSearch}
            sx={{ minWidth: 120 }}
          >
            Search
          </Button>
          <IconButton>
            <FilterList />
          </IconButton>
        </Box>
      </Paper>

      {/* Table */}
      <TableContainer component={Paper}>
        {loading ? (
          <Box className="loading-spinner">
            <CircularProgress />
          </Box>
        ) : analyses.length === 0 ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              No analysis results found
            </Typography>
          </Box>
        ) : (
          <>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Land ID</TableCell>
                  <TableCell>Risk Level</TableCell>
                  <TableCell>Risk Score</TableCell>
                  <TableCell>Fraud Detected</TableCell>
                  <TableCell>Confidence</TableCell>
                  <TableCell>Analysis Date</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {analyses.map((analysis) => (
                  <TableRow key={analysis.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {analysis.land_record?.land_id || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={formatRiskLevel(analysis.risk_level)}
                        color={getRiskChipColor(analysis.risk_level)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        fontWeight="bold"
                        sx={{
                          color: RISK_COLORS[analysis.risk_level] || 'text.primary',
                        }}
                      >
                        {formatRiskScore(analysis.risk_score)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={analysis.fraud_detected ? 'Yes' : 'No'}
                        color={analysis.fraud_detected ? 'error' : 'success'}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      {formatConfidence(analysis.confidence)}
                    </TableCell>
                    <TableCell>{formatDate(analysis.created_at)}</TableCell>
                    <TableCell align="right">
                      <IconButton
                        color="primary"
                        onClick={() => handleViewDetail(analysis)}
                      >
                        <Visibility />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <TablePagination
              component="div"
              count={totalAnalyses}
              page={page}
              onPageChange={handleChangePage}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              rowsPerPageOptions={[5, 10, 25, 50]}
            />
          </>
        )}
      </TableContainer>
    </Box>
  )
}

export default AnalysisView