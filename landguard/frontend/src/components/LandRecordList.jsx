/**
 * Land Records List Component
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
  Menu,
  MenuItem,
} from '@mui/material'
import {
  Search,
  Add,
  Visibility,
  Edit,
  Delete,
  MoreVert,
  FilterList,
} from '@mui/icons-material'
import { getLandRecords, deleteLandRecord } from '../services/landRecords'
import { toast } from 'react-toastify'
import {
  formatDate,
  formatArea,
  formatPropertyType,
} from '../utils/formatters'
import { DEFAULT_PAGE_SIZE } from '../utils/constants'

const LandRecordList = () => {
  const navigate = useNavigate()
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(DEFAULT_PAGE_SIZE)
  const [totalRecords, setTotalRecords] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')
  const [anchorEl, setAnchorEl] = useState(null)
  const [selectedRecord, setSelectedRecord] = useState(null)

  useEffect(() => {
    fetchRecords()
  }, [page, rowsPerPage])

  const fetchRecords = async () => {
    try {
      setLoading(true)
      const response = await getLandRecords(page + 1, rowsPerPage, {
        search: searchQuery,
      })
      setRecords(response.items || [])
      setTotalRecords(response.total || 0)
    } catch (error) {
      console.error('Error fetching records:', error)
      toast.error('Failed to load land records')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    setPage(0)
    fetchRecords()
  }

  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const handleMenuOpen = (event, record) => {
    setAnchorEl(event.currentTarget)
    setSelectedRecord(record)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
    setSelectedRecord(null)
  }

  const handleView = () => {
    if (selectedRecord) {
      navigate(`/land-records/${selectedRecord.id}`)
    }
    handleMenuClose()
  }

  const handleEdit = () => {
    if (selectedRecord) {
      // Navigate to edit page (to be implemented)
      toast.info('Edit functionality coming soon')
    }
    handleMenuClose()
  }

  const handleDelete = async () => {
    if (selectedRecord) {
      if (window.confirm('Are you sure you want to delete this record?')) {
        try {
          await deleteLandRecord(selectedRecord.id)
          toast.success('Land record deleted successfully')
          fetchRecords()
        } catch (error) {
          console.error('Error deleting record:', error)
          toast.error('Failed to delete land record')
        }
      }
    }
    handleMenuClose()
  }

  const handleAddNew = () => {
    // Navigate to add new page (to be implemented)
    toast.info('Add new functionality coming soon')
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
            Land Records
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage and view all land records
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleAddNew}
        >
          Add New Record
        </Button>
      </Box>

      {/* Search and Filter */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            fullWidth
            placeholder="Search by Land ID, Location, or Owner..."
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
        ) : records.length === 0 ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              No land records found
            </Typography>
          </Box>
        ) : (
          <>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Land ID</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>Area</TableCell>
                  <TableCell>Property Type</TableCell>
                  <TableCell>Current Owner</TableCell>
                  <TableCell>Created Date</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {records.map((record) => (
                  <TableRow
                    key={record.id}
                    hover
                    sx={{ cursor: 'pointer' }}
                    onClick={() => navigate(`/land-records/${record.id}`)}
                  >
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {record.land_id}
                      </Typography>
                    </TableCell>
                    <TableCell>{record.location}</TableCell>
                    <TableCell>{formatArea(record.area_sqft)}</TableCell>
                    <TableCell>
                      <Chip
                        label={formatPropertyType(record.property_type)}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{record.current_owner}</TableCell>
                    <TableCell>{formatDate(record.created_at)}</TableCell>
                    <TableCell align="right">
                      <IconButton
                        onClick={(e) => {
                          e.stopPropagation()
                          handleMenuOpen(e, record)
                        }}
                      >
                        <MoreVert />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <TablePagination
              component="div"
              count={totalRecords}
              page={page}
              onPageChange={handleChangePage}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              rowsPerPageOptions={[5, 10, 25, 50]}
            />
          </>
        )}
      </TableContainer>

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleView}>
          <Visibility fontSize="small" sx={{ mr: 1 }} />
          View Details
        </MenuItem>
        <MenuItem onClick={handleEdit}>
          <Edit fontSize="small" sx={{ mr: 1 }} />
          Edit
        </MenuItem>
        <MenuItem onClick={handleDelete}>
          <Delete fontSize="small" sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>
    </Box>
  )
}

export default LandRecordList