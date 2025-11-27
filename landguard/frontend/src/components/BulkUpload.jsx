/**
 * Bulk Upload Component
 */

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Stepper,
  Step,
  StepLabel,
  IconButton,
  Chip,
} from '@mui/material'
import {
  CloudUpload,
  CheckCircle,
  Error as ErrorIcon,
  Close,
  GetApp,
} from '@mui/icons-material'
import { bulkUploadLandRecords } from '../services/landRecords'
import { toast } from 'react-toastify'
import { formatFileSize } from '../utils/formatters'
import { ALLOWED_FILE_TYPES, MAX_FILE_SIZE } from '../utils/constants'

const steps = ['Upload File', 'Preview Data', 'Process']

const BulkUpload = () => {
  const [activeStep, setActiveStep] = useState(0)
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [previewData, setPreviewData] = useState([])
  const [uploadResult, setUploadResult] = useState(null)
  const [errors, setErrors] = useState([])

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0]
      if (rejection.file.size > MAX_FILE_SIZE) {
        toast.error(`File too large. Maximum size is ${formatFileSize(MAX_FILE_SIZE)}`)
      } else {
        toast.error('Invalid file type. Please upload CSV or Excel files.')
      }
      return
    }

    if (acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0]
      setFile(selectedFile)
      setActiveStep(1)
      parseFile(selectedFile)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    maxFiles: 1,
    maxSize: MAX_FILE_SIZE,
  })

  const parseFile = (file) => {
    // Simple preview - in production, use papaparse or xlsx library
    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target.result
      const lines = text.split('\n')
      const headers = lines[0].split(',')
      
      const data = lines.slice(1, 6).map((line) => {
        const values = line.split(',')
        const row = {}
        headers.forEach((header, index) => {
          row[header.trim()] = values[index]?.trim()
        })
        return row
      })

      setPreviewData(data)
    }
    reader.readAsText(file)
  }

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file first')
      return
    }

    try {
      setUploading(true)
      setUploadProgress(0)
      setActiveStep(2)

      const result = await bulkUploadLandRecords(file, (progress) => {
        setUploadProgress(progress)
      })

      setUploadResult(result)
      
      if (result.errors && result.errors.length > 0) {
        setErrors(result.errors)
        toast.warning(`Upload completed with ${result.errors.length} errors`)
      } else {
        toast.success('Bulk upload completed successfully!')
      }
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('Failed to upload file. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const handleReset = () => {
    setActiveStep(0)
    setFile(null)
    setPreviewData([])
    setUploadResult(null)
    setErrors([])
    setUploadProgress(0)
  }

  const downloadTemplate = () => {
    // Create sample CSV template
    const template = 'land_id,location,area_sqft,property_type,current_owner\n' +
                    'LND-SAMPLE-0001,Mumbai Maharashtra,1500,residential,John Doe\n' +
                    'LND-SAMPLE-0002,Delhi NCR,2000,commercial,Jane Smith'
    
    const blob = new Blob([template], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'land_records_template.csv'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Bulk Upload
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Upload CSV or Excel files to import multiple land records
        </Typography>
      </Box>

      {/* Stepper */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Step 0: Upload */}
      {activeStep === 0 && (
        <Paper sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Button
              variant="outlined"
              startIcon={<GetApp />}
              onClick={downloadTemplate}
              sx={{ mb: 3 }}
            >
              Download Template
            </Button>
          </Box>

          <Box
            {...getRootProps()}
            className={`upload-area ${isDragActive ? 'drag-active' : ''}`}
          >
            <input {...getInputProps()} />
            <CloudUpload sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive
                ? 'Drop the file here'
                : 'Drag & drop a file here, or click to select'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Supported formats: CSV, XLS, XLSX (Max: {formatFileSize(MAX_FILE_SIZE)})
            </Typography>
          </Box>

          <Alert severity="info" sx={{ mt: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              CSV Format Requirements:
            </Typography>
            <Typography variant="caption" component="div">
              • Required columns: land_id, location, area_sqft, property_type, current_owner
            </Typography>
            <Typography variant="caption" component="div">
              • Use comma (,) as delimiter
            </Typography>
            <Typography variant="caption" component="div">
              • First row should be headers
            </Typography>
          </Alert>
        </Paper>
      )}

      {/* Step 1: Preview */}
      {activeStep === 1 && (
        <Paper sx={{ p: 3 }}>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              mb: 3,
            }}
          >
            <Box>
              <Typography variant="h6" fontWeight="bold">
                Preview Data
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {file?.name} ({formatFileSize(file?.size)})
              </Typography>
            </Box>
            <IconButton onClick={handleReset}>
              <Close />
            </IconButton>
          </Box>

          <TableContainer sx={{ mb: 3, maxHeight: 400 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  {previewData.length > 0 &&
                    Object.keys(previewData[0]).map((header) => (
                      <TableCell key={header}>
                        <strong>{header}</strong>
                      </TableCell>
                    ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {previewData.map((row, index) => (
                  <TableRow key={index}>
                    {Object.values(row).map((value, i) => (
                      <TableCell key={i}>{value}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <Alert severity="warning" sx={{ mb: 3 }}>
            Showing preview of first 5 rows. Total rows will be processed on upload.
          </Alert>

          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            <Button onClick={handleReset}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleUpload}
              disabled={uploading}
            >
              Upload
            </Button>
          </Box>
        </Paper>
      )}

      {/* Step 2: Processing */}
      {activeStep === 2 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" fontWeight="bold" gutterBottom>
            {uploading ? 'Processing...' : 'Upload Complete'}
          </Typography>

          {uploading && (
            <Box sx={{ my: 3 }}>
              <LinearProgress
                variant="determinate"
                value={uploadProgress}
                sx={{ height: 8, borderRadius: 1 }}
              />
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ mt: 1, display: 'block', textAlign: 'center' }}
              >
                {uploadProgress}% Complete
              </Typography>
            </Box>
          )}

          {uploadResult && (
            <Box sx={{ my: 3 }}>
              <Alert
                severity={errors.length > 0 ? 'warning' : 'success'}
                icon={errors.length > 0 ? <ErrorIcon /> : <CheckCircle />}
              >
                <Typography variant="body2" fontWeight="bold">
                  {uploadResult.success_count} records uploaded successfully
                </Typography>
                {errors.length > 0 && (
                  <Typography variant="body2">
                    {errors.length} records failed
                  </Typography>
                )}
              </Alert>

              {/* Errors Table */}
              {errors.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Errors:
                  </Typography>
                  <TableContainer sx={{ maxHeight: 300 }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Row</TableCell>
                          <TableCell>Field</TableCell>
                          <TableCell>Error</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {errors.map((error, index) => (
                          <TableRow key={index}>
                            <TableCell>{error.row}</TableCell>
                            <TableCell>
                              <Chip label={error.field} size="small" />
                            </TableCell>
                            <TableCell>{error.message}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}
            </Box>
          )}

          {!uploading && (
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button variant="contained" onClick={handleReset}>
                Upload Another File
              </Button>
            </Box>
          )}
        </Paper>
      )}
    </Box>
  )
}

export default BulkUpload