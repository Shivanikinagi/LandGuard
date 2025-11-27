/**
 * Reports Service
 */

import api from './api'

/**
 * Get all reports
 */
export const getReports = async (params = {}) => {
  try {
    const response = await api.get('/reports', { params })
    return response
  } catch (error) {
    console.error('Get reports error:', error)
    throw error
  }
}

/**
 * Get single report by ID
 */
export const getReportById = async (id) => {
  try {
    const response = await api.get(`/reports/${id}`)
    return response
  } catch (error) {
    console.error('Get report error:', error)
    throw error
  }
}

/**
 * Generate new report
 */
export const generateReport = async (data) => {
  try {
    const response = await api.post('/reports/generate', data)
    return response
  } catch (error) {
    console.error('Generate report error:', error)
    throw error
  }
}

/**
 * Download report
 */
export const downloadReport = async (id, format = 'pdf') => {
  try {
    const response = await api.get(`/reports/${id}/download`, {
      params: { format },
      responseType: 'blob',
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `report_${id}.${format}`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Download report error:', error)
    throw error
  }
}

/**
 * Delete report
 */
export const deleteReport = async (id) => {
  try {
    const response = await api.delete(`/reports/${id}`)
    return response
  } catch (error) {
    console.error('Delete report error:', error)
    throw error
  }
}

/**
 * Get report types
 */
export const getReportTypes = async () => {
  try {
    const response = await api.get('/reports/types')
    return response
  } catch (error) {
    console.error('Get report types error:', error)
    throw error
  }
}

/**
 * Schedule report
 */
export const scheduleReport = async (data) => {
  try {
    const response = await api.post('/reports/schedule', data)
    return response
  } catch (error) {
    console.error('Schedule report error:', error)
    throw error
  }
}

/**
 * Get scheduled reports
 */
export const getScheduledReports = async () => {
  try {
    const response = await api.get('/reports/scheduled')
    return response
  } catch (error) {
    console.error('Get scheduled reports error:', error)
    throw error
  }
}

/**
 * Cancel scheduled report
 */
export const cancelScheduledReport = async (id) => {
  try {
    const response = await api.delete(`/reports/scheduled/${id}`)
    return response
  } catch (error) {
    console.error('Cancel scheduled report error:', error)
    throw error
  }
}

/**
 * Share report
 */
export const shareReport = async (id, emails) => {
  try {
    const response = await api.post(`/reports/${id}/share`, {
      emails,
    })
    return response
  } catch (error) {
    console.error('Share report error:', error)
    throw error
  }
}