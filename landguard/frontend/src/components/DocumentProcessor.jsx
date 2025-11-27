/**
 * Document Processor Component
 * Handles the complete document processing workflow
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
  Stepper,
  Step,
  StepLabel,
  TextField,
  IconButton,
  Chip,
  Card,
  CardContent,
  Divider,
  CircularProgress,
} from '@mui/material'
import {
  CloudUpload,
  CheckCircle,
  Error as ErrorIcon,
  Close,
  Lock,
  Storage,
  Verified,
  Timeline,
} from '@mui/icons-material'
import { toast } from 'react-toastify'
import { formatFileSize } from '../utils/formatters'
import { ALLOWED_FILE_TYPES, MAX_FILE_SIZE } from '../utils/constants'
import { processDocument, verifyDocument } from '../services/processing'

const steps = [
  'Upload Document',
  'Set Password',
  'Process Document',
  'Verification'
]

const DocumentProcessor = () => {
  const [activeStep, setActiveStep] = useState(0)
  const [file, setFile] = useState(null)
  const [password, setPassword] = useState('')
  const [processing, setProcessing] = useState(false)
  const [verifying, setVerifying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState('')
  const [processingResult, setProcessingResult] = useState(null)
  const [verificationResult, setVerificationResult] = useState(null)

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0]
      if (rejection.file.size > MAX_FILE_SIZE) {
        toast.error(`File too large. Maximum size is ${formatFileSize(MAX_FILE_SIZE)}`)
      } else {
        toast.error('Invalid file type. Please upload a valid document.')
      }
      return
    }

    if (acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0]
      setFile(selectedFile)
      setActiveStep(1)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpg', '.jpeg', '.png'],
      'text/plain': ['.txt'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    maxSize: MAX_FILE_SIZE,
  })

  const handleProcess = async () => {
    if (!file) {
      toast.error('Please select a file first')
      return
    }

    if (!password) {
      toast.error('Please enter a password for encryption')
      return
    }

    try {
      setProcessing(true)
      setProgress(0)
      setCurrentStep('Starting processing...')
      setActiveStep(2)

      const result = await processDocument(file, password, (progress, step) => {
        setProgress(progress)
        setCurrentStep(step)
      })

      setProcessingResult(result)
      toast.success('Document processed successfully!')
    } catch (error) {
      console.error('Processing error:', error)
      toast.error('Failed to process document. Please try again.')
    } finally {
      setProcessing(false)
    }
  }

  const handleVerify = async () => {
    if (!processingResult) {
      toast.error('No document to verify')
      return
    }

    try {
      setVerifying(true)
      
      const result = await verifyDocument(processingResult.record_id)
      setVerificationResult(result)
      setActiveStep(3)
      
      if (result.verified) {
        toast.success('Document verified successfully!')
      } else {
        toast.warning('Document verification failed')
      }
    } catch (error) {
      console.error('Verification error:', error)
      toast.error('Failed to verify document. Please try again.')
    } finally {
      setVerifying(false)
    }
  }

  const handleReset = () => {
    setActiveStep(0)
    setFile(null)
    setPassword('')
    setProcessing(false)
    setVerifying(false)
    setProgress(0)
    setCurrentStep('')
    setProcessingResult(null)
    setVerificationResult(null)
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Document Processor
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Process land documents through the complete security workflow
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
          <Box
            {...getRootProps()}
            className={`upload-area ${isDragActive ? 'drag-active' : ''}`}
            sx={{
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'grey.300',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: isDragActive ? 'primary.light' : 'background.default',
              transition: 'all 0.2s ease-in-out'
            }}
          >
            <input {...getInputProps()} />
            <CloudUpload sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive
                ? 'Drop the file here'
                : 'Drag & drop a document here, or click to select'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Supported formats: PDF, DOC, DOCX, TXT, JPG, PNG (Max: {formatFileSize(MAX_FILE_SIZE)})
            </Typography>
          </Box>

          <Alert severity="info" sx={{ mt: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Document Processing Workflow:
            </Typography>
            <Typography variant="caption" component="div">
              1. Upload land/property documents
            </Typography>
            <Typography variant="caption" component="div">
              2. Check for anomalies and suspicious activity
            </Typography>
            <Typography variant="caption" component="div">
              3. Compress the file to reduce storage space
            </Typography>
            <Typography variant="caption" component="div">
              4. Encrypt the file with military-grade security
            </Typography>
            <Typography variant="caption" component="div">
              5. Create .ppc files with metadata
            </Typography>
            <Typography variant="caption" component="div">
              6. Upload to IPFS for decentralized storage
            </Typography>
            <Typography variant="caption" component="div">
              7. Store CID on blockchain for immutable proof
            </Typography>
          </Alert>
        </Paper>
      )}

      {/* Step 1: Set Password */}
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
                Set Encryption Password
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {file?.name} ({formatFileSize(file?.size)})
              </Typography>
            </Box>
            <IconButton onClick={handleReset}>
              <Close />
            </IconButton>
          </Box>

          <TextField
            fullWidth
            type="password"
            label="Encryption Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            helperText="Enter a strong password to encrypt your document"
            sx={{ mb: 3 }}
          />

          <Alert severity="warning" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>Important:</strong> This password will be used to encrypt your document. 
              Make sure to store it securely as it cannot be recovered.
            </Typography>
          </Alert>

          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            <Button onClick={() => setActiveStep(0)}>Back</Button>
            <Button
              variant="contained"
              onClick={handleProcess}
              disabled={!password}
              startIcon={<Lock />}
            >
              Process Document
            </Button>
          </Box>
        </Paper>
      )}

      {/* Step 2: Processing */}
      {activeStep === 2 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" fontWeight="bold" gutterBottom>
            {processing ? 'Processing Document...' : 'Processing Complete'}
          </Typography>

          {processing && (
            <Box sx={{ my: 3 }}>
              <LinearProgress
                variant="determinate"
                value={progress}
                sx={{ height: 8, borderRadius: 1, mb: 2 }}
              />
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ display: 'block', textAlign: 'center' }}
              >
                {currentStep}
              </Typography>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ mt: 1, display: 'block', textAlign: 'center' }}
              >
                {progress}% Complete
              </Typography>
            </Box>
          )}

          {processingResult && !processing && (
            <Box sx={{ my: 3 }}>
              <Alert
                severity="success"
                icon={<CheckCircle />}
                sx={{ mb: 3 }}
              >
                <Typography variant="body2" fontWeight="bold">
                  Document processed successfully!
                </Typography>
              </Alert>

              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Processing Results
                  </Typography>
                  
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
                    <Chip 
                      icon={<Storage />} 
                      label={`Compression: ${processingResult.compression_ratio?.toFixed(2) || 'N/A'}x`} 
                      color="primary" 
                      variant="outlined" 
                    />
                    <Chip 
                      icon={<Verified />} 
                      label={processingResult.blockchain_verified ? "Blockchain Verified" : "Not Verified"} 
                      color={processingResult.blockchain_verified ? "success" : "warning"} 
                      variant="outlined" 
                    />
                  </Box>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Typography variant="subtitle2" gutterBottom>
                    Document Details
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Record ID:</strong> {processingResult.record_id}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Record Number:</strong> {processingResult.record_number}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Original Filename:</strong> {processingResult.original_filename}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>File Size:</strong> {formatFileSize(processingResult.file_size)}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>IPFS CID:</strong> {processingResult.cid}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Transaction Hash:</strong> {processingResult.transaction_hash ? processingResult.transaction_hash.substring(0, 20) + '...' : 'N/A'}
                  </Typography>
                </CardContent>
              </Card>

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button onClick={handleReset}>Process Another</Button>
                <Button
                  variant="contained"
                  onClick={handleVerify}
                  disabled={verifying}
                  startIcon={verifying ? <CircularProgress size={20} /> : <Timeline />}
                >
                  {verifying ? 'Verifying...' : 'Verify Document'}
                </Button>
              </Box>
            </Box>
          )}
        </Paper>
      )}

      {/* Step 3: Verification */}
      {activeStep === 3 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" fontWeight="bold" gutterBottom>
            Document Verification
          </Typography>

          {verificationResult && (
            <Box sx={{ my: 3 }}>
              <Alert
                severity={verificationResult.verified ? "success" : "error"}
                icon={verificationResult.verified ? <CheckCircle /> : <ErrorIcon />}
                sx={{ mb: 3 }}
              >
                <Typography variant="body2" fontWeight="bold">
                  {verificationResult.verified 
                    ? "Document verified successfully!" 
                    : "Document verification failed!"}
                </Typography>
              </Alert>

              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Verification Results
                  </Typography>
                  
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
                    <Chip 
                      label={`IPFS: ${verificationResult.ipfs_verification?.verified ? "Verified" : "Failed"}`} 
                      color={verificationResult.ipfs_verification?.verified ? "success" : "error"} 
                      variant="outlined" 
                    />
                    <Chip 
                      label={`Blockchain: ${verificationResult.blockchain_verification?.verified ? "Verified" : "Failed"}`} 
                      color={verificationResult.blockchain_verification?.verified ? "success" : "error"} 
                      variant="outlined" 
                    />
                  </Box>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Typography variant="subtitle2" gutterBottom>
                    Verification Details
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Record ID:</strong> {verificationResult.record_id}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Record Number:</strong> {verificationResult.record_number}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>IPFS CID:</strong> {verificationResult.ipfs_verification.cid}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Transaction Hash:</strong> {verificationResult.blockchain_verification?.tx_hash ? verificationResult.blockchain_verification.tx_hash.substring(0, 20) + '...' : 'N/A'}
                  </Typography>
                </CardContent>
              </Card>

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button onClick={handleReset}>Process Another</Button>
              </Box>
            </Box>
          )}
        </Paper>
      )}
    </Box>
  )
}

export default DocumentProcessor