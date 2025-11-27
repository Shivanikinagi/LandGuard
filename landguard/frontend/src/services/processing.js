/**
 * Document Processing Service
 * Handles communication with the document processing API endpoints
 */

import api from './api'

/**
 * Process a document through the complete workflow
 * @param {File} file - The document file to process
 * @param {string} password - Encryption password
 * @param {Function} onProgress - Progress callback function
 * @returns {Promise<Object>} Processing result
 */
export const processDocument = async (file, password, onProgress) => {
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('password', password)

    // Create a custom request to track progress
    const response = await api.post('/processing/process-document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress, 'Uploading document')
        }
      }
    })

    return response
  } catch (error) {
    console.error('Process document error:', error)
    throw error
  }
}

/**
 * Verify a processed document
 * @param {number} recordId - The record ID to verify
 * @returns {Promise<Object>} Verification result
 */
export const verifyDocument = async (recordId) => {
  try {
    const response = await api.post(`/processing/verify-document/${recordId}`)
    return response
  } catch (error) {
    console.error('Verify document error:', error)
    throw error
  }
}

/**
 * Get processing status for a record
 * @param {number} recordId - The record ID to check
 * @returns {Promise<Object>} Processing status
 */
export const getProcessingStatus = async (recordId) => {
  try {
    const response = await api.get(`/processing/status/${recordId}`)
    return response
  } catch (error) {
    console.error('Get processing status error:', error)
    throw error
  }
}