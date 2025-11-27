/**
 * Land Records Service
 */

import api from './api'

/**
 * Get all land records with filters and pagination
 */
export const getLandRecords = async (params = {}) => {
  try {
    const response = await api.get('/land-records', { params })
    return response
  } catch (error) {
    console.error('Get land records error:', error)
    throw error
  }
}

/**
 * Get single land record by ID
 */
export const getLandRecordById = async (id) => {
  try {
    const response = await api.get(`/land-records/${id}`)
    return response
  } catch (error) {
    console.error('Get land record error:', error)
    throw error
  }
}

/**
 * Create new land record
 */
export const createLandRecord = async (data) => {
  try {
    const response = await api.post('/land-records', data)
    return response
  } catch (error) {
    console.error('Create land record error:', error)
    throw error
  }
}

/**
 * Update existing land record
 */
export const updateLandRecord = async (id, data) => {
  try {
    const response = await api.put(`/land-records/${id}`, data)
    return response
  } catch (error) {
    console.error('Update land record error:', error)
    throw error
  }
}

/**
 * Delete land record
 */
export const deleteLandRecord = async (id) => {
  try {
    const response = await api.delete(`/land-records/${id}`)
    return response
  } catch (error) {
    console.error('Delete land record error:', error)
    throw error
  }
}

/**
 * Search land records
 */
export const searchLandRecords = async (query) => {
  try {
    const response = await api.get('/land-records/search', {
      params: { q: query },
    })
    return response
  } catch (error) {
    console.error('Search land records error:', error)
    throw error
  }
}

/**
 * Get land records statistics
 */
export const getLandRecordsStats = async () => {
  try {
    const response = await api.get('/land-records/stats')
    return response
  } catch (error) {
    console.error('Get land records stats error:', error)
    throw error
  }
}

/**
 * Bulk upload land records
 */
export const bulkUploadLandRecords = async (file) => {
  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/land-records/bulk-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response
  } catch (error) {
    console.error('Bulk upload error:', error)
    throw error
  }
}

/**
 * Download sample CSV template
 */
export const downloadTemplate = async () => {
  try {
    const response = await api.get('/land-records/template', {
      responseType: 'blob',
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'land_records_template.csv')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Download template error:', error)
    throw error
  }
}