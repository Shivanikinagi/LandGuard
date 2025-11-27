/**
 * Dashboard Service
 */

import { get } from './api'

/**
 * Get dashboard statistics
 */
export const getDashboardStats = async () => {
  try {
    const response = await get('/statistics/dashboard')
    return response
  } catch (error) {
    console.error('Get dashboard stats error:', error)
    throw error
  }
}

/**
 * Get system health status
 */
export const getSystemHealth = async () => {
  try {
    const response = await get('/health')
    return response
  } catch (error) {
    console.error('Get system health error:', error)
    throw error
  }
}

/**
 * Get database health status
 */
export const getDatabaseHealth = async () => {
  try {
    const response = await get('/health/db')
    return response
  } catch (error) {
    console.error('Get database health error:', error)
    throw error
  }
}