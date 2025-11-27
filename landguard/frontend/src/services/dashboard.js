/**
 * Dashboard Service
 */

import api from './api'

/**
 * Get dashboard statistics
 */
export const getDashboardStats = async () => {
  try {
    // Explicitly check for token before making request
    const token = localStorage.getItem('token')
    console.log('Dashboard stats request token:', token ? token.substring(0, 20) + '...' : 'No token')
    
    const response = await api.get('/statistics/overview')
    return response
  } catch (error) {
    console.error('Get dashboard stats error:', error)
    if (error.response) {
      console.error('Error response:', error.response.status, error.response.data)
    }
    throw error
  }
}

/**
 * Get dashboard trends
 */
export const getDashboardTrends = async () => {
  try {
    // Explicitly check for token before making request
    const token = localStorage.getItem('token')
    console.log('Dashboard trends request token:', token ? token.substring(0, 20) + '...' : 'No token')
    
    const response = await api.get('/statistics/trends')
    return response
  } catch (error) {
    console.error('Get dashboard trends error:', error)
    if (error.response) {
      console.error('Error response:', error.response.status, error.response.data)
    }
    throw error
  }
}