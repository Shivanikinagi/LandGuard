/**
 * Report Center Component
 */

import { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
} from '@mui/material'
import {
  PictureAsPdf,
  Description,
  Assessment,
  Download,
  Visibility,
  Add,
} from '@mui/icons-material'
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns'
import { get, post, download } from '../services/api'
import { API_ENDPOINTS } from '../utils/constants'
import { toast } from 'react-toastify'
import { formatDate, formatDateTime } from '../utils/formatters'

const reportTypes = [
  { value: 'summary', label: 'Summary Report', icon: <Description /> },
  { value: 'fraud_analysis', label: 'Fraud Analysis Report', icon: <Assessment /> },
  { value: 'risk_assessment', label: 'Risk Assessment Report', icon: <PictureAsPdf /> },
]

const ReportCenter = () => {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [totalReports, setTotalReports] = useState(0)
  const [openDialog, setOpenDialog] = useState(false)
  const [generating, setGenerating] = useState(false)

  const [formData, setFormData] = useState({
    reportType: 'summary',
    startDate: null,
    endDate: null,
    includeCharts: true,
    format: 'pdf',
  })

  useEffect(() => {
    fetchReports()
  }, [page, rowsPerPage])

  const fetchReports = async () => {
    try {
      setLoading(true)
      const response = await get(
        `${API_ENDPOINTS.REPORTS}?page=${page + 1}&page_size=${rowsPerPage}`
      )
      setReports(response.items || [])
      setTotalReports(response.total || 0)
    } catch (error) {
      console.error('Error fetching reports:', error)
      toast.error('Failed to load reports')
    } finally {
      setLoading(false)
    }
  }

  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const handleOpenDialog = () => {
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setFormData({
      reportType: 'summary',
      startDate: null,
      endDate: null,
      includeCharts: true,
      format: 'pdf',
    })
  }

  const handleFormChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleGenerateReport = async () => {
    try {
      setGenerating(true)
      const response = await post(API_ENDPOINTS.GENERATE_REPORT, {
        report_type: formData.reportType,
        start_date: formData.startDate?.toISOString(),
        end_date: formData.endDate?.toISOString(),
        include_charts: formData.includeCharts,
        format: formData.format,
      })

      toast.success('Report generated successfully!')
      handleCloseDialog()
      fetchReports()
    } catch (error) {
      console.error('Error generating report:', error)
      toast.error('Failed to generate report')
    } finally {
      setGenerating(false)
    }
  }

  const handleDownload = async (report) => {
    try {
      await download(
        API_ENDPOINTS.REPORT_BY_ID(report.id),
        `${report.report_type}_${formatDate(report.created_at)}.${report.format}`
      )
      toast.success('Report downloaded successfully')
    } catch (error) {
      console.error('Error downloading report:', error)
      toast.error('Failed to download report')
    }
  }

  const handleView = (report) => {
    // Open report in new tab
    window.open(`/api/reports/${report.id}/view`, '_blank')
  }

  return (
    <Box>
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 3,
        }}
      >
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Report Center
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Generate and manage reports
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleOpenDialog}
        >
          Generate Report
        </Button>
      </Box>

      {/* Report Type Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {reportTypes.map((type) => (
          <Grid item xs={12} sm={6} md={4} key={type.value}>
            <Card
              className="card-hover"
              sx={{ cursor: 'pointer' }}
              onClick={() => {
                setFormData((prev) => ({ ...prev, reportType: type.value }))
                handleOpenDialog()
              }}
            >
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2,
                  }}
                >
                  <Box
                    sx={{
                      p: 1.5,
                      borderRadius: 2,
                      bgcolor: 'primary.light',
                      color: 'primary.main',
                    }}
                  >
                    {type.icon}
                  </Box>
                  <Typography variant="subtitle1" fontWeight="bold">
                    {type.label}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Reports Table */}
      <TableContainer component={Paper}>
        {loading ? (
          <Box className="loading-spinner">
            <CircularProgress />
          </Box>
        ) : reports.length === 0 ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              No reports available
            </Typography>
          </Box>
        ) : (
          <>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Report Type</TableCell>
                  <TableCell>Generated Date</TableCell>
                  <TableCell>Period</TableCell>
                  <TableCell>Format</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {reports.map((report) => (
                  <TableRow key={report.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {report.report_type
                          .replace(/_/g, ' ')
                          .replace(/\b\w/g, (l) => l.toUpperCase())}
                      </Typography>
                    </TableCell>
                    <TableCell>{formatDateTime(report.created_at)}</TableCell>
                    <TableCell>
                      {report.start_date && report.end_date
                        ? `${formatDate(report.start_date)} - ${formatDate(
                            report.end_date
                          )}`
                        : 'All Time'}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={report.format.toUpperCase()}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={report.status}
                        size="small"
                        color={
                          report.status === 'completed' ? 'success' : 'warning'
                        }
                      />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        color="primary"
                        onClick={() => handleView(report)}
                      >
                        <Visibility />
                      </IconButton>
                      <IconButton
                        color="primary"
                        onClick={() => handleDownload(report)}
                      >
                        <Download />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <TablePagination
              component="div"
              count={totalReports}
              page={page}
              onPageChange={handleChangePage}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              rowsPerPageOptions={[5, 10, 25]}
            />
          </>
        )}
      </TableContainer>

      {/* Generate Report Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Generate New Report</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              select
              fullWidth
              label="Report Type"
              value={formData.reportType}
              onChange={(e) => handleFormChange('reportType', e.target.value)}
            >
              {reportTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </TextField>

            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Start Date"
                value={formData.startDate}
                onChange={(date) => handleFormChange('startDate', date)}
                slotProps={{ textField: { fullWidth: true } }}
              />

              <DatePicker
                label="End Date"
                value={formData.endDate}
                onChange={(date) => handleFormChange('endDate', date)}
                slotProps={{ textField: { fullWidth: true } }}
              />
            </LocalizationProvider>

            <TextField
              select
              fullWidth
              label="Format"
              value={formData.format}
              onChange={(e) => handleFormChange('format', e.target.value)}
            >
              <MenuItem value="pdf">PDF</MenuItem>
              <MenuItem value="xlsx">Excel</MenuItem>
              <MenuItem value="csv">CSV</MenuItem>
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={generating}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleGenerateReport}
            disabled={generating}
          >
            {generating ? <CircularProgress size={24} /> : 'Generate'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default ReportCenter