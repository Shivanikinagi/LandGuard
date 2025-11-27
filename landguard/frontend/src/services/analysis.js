/**
 * Analysis Service
 */

import api from './api'

/**
 * Get all analysis results
 */
export const getAnalysisResults = async (params = {}) => {
  try {
    const response = await api.get('/analysis', { params })
    return response
  } catch (error) {
    console.error('Get analysis results error:', error)
    throw error
  }
}

/**
 * Get single analysis result by ID
 */
export const getAnalysisById = async (id) => {
  try {
    const response = await api.get(`/analysis/${id}`)
    return response
  } catch (error) {
    console.error('Get analysis error:', error)
    throw error
  }
}

/**
 * Analyze land record
 */
export const analyzeLandRecord = async (landRecordId) => {
  try {
    const response = await api.post(`/analysis/land/${landRecordId}`)
    return response
  } catch (error) {
    console.error('Analyze land record error:', error)
    throw error
  }
}

/**
 * Re-analyze land record
 */
export const reanalyzeLandRecord = async (landRecordId) => {
  try {
    const response = await api.post(`/analysis/land/${landRecordId}/reanalyze`)
    return response
  } catch (error) {
    console.error('Re-analyze land record error:', error)
    throw error
  }
}

/**
 * Get analysis statistics
 */
export const getAnalysisStats = async () => {
  try {
    const response = await api.get('/analysis/stats')
    return response
  } catch (error) {
    console.error('Get analysis stats error:', error)
    throw error
  }
}

/**
 * Get fraud trends
 */
export const getFraudTrends = async (period = '30d') => {
  try {
    const response = await api.get('/analysis/trends', {
      params: { period },
    })
    return response
  } catch (error) {
    console.error('Get fraud trends error:', error)
    throw error
  }
}

/**
 * Get risk distribution
 */
export const getRiskDistribution = async () => {
  try {
    const response = await api.get('/analysis/risk-distribution')
    return response
  } catch (error) {
    console.error('Get risk distribution error:', error)
    throw error
  }
}

/**
 * Export analysis results
 */
export const exportAnalysisResults = async (format = 'csv', filters = {}) => {
  try {
    const response = await api.get('/analysis/export', {
      params: { format, ...filters },
      responseType: 'blob',
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `analysis_results.${format}`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Export analysis results error:', error)
    throw error
  }
}

/**
 * Batch analyze land records
 */
export const batchAnalyze = async (landRecordIds) => {
  try {
    const response = await api.post('/analysis/batch', {
      land_record_ids: landRecordIds,
    })
    return response
  } catch (error) {
    console.error('Batch analyze error:', error)
    throw error
  }
}