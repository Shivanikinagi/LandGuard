/**
 * Base API service for HTTP requests
 */

import axios from 'axios'
import { toast } from 'react-toastify'

// Ensure the API base URL has the proper protocol and format
let API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
if (API_BASE_URL) {
  // Remove trailing slash if present
  API_BASE_URL = API_BASE_URL.replace(/\/$/, '')
  
  // Add protocol if missing
  if (!API_BASE_URL.startsWith('http://') && !API_BASE_URL.startsWith('https://')) {
    API_BASE_URL = `http://${API_BASE_URL}`
  }
}

const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 30000

// Storage keys
const STORAGE_KEYS = {
  AUTH_TOKEN: 'token',
  USER_DATA: 'user',
}

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor - Handle errors
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      const { status, data, headers } = error.response
      console.error('API Error Response:', status, data, headers)

      switch (status) {
        case 401:
          // Unauthorized - clear auth and redirect to login
          localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN)
          localStorage.removeItem(STORAGE_KEYS.USER_DATA)
          window.location.href = '/login'
          toast.error('Session expired. Please login again.')
          break
        
        case 403:
          toast.error('You do not have permission to perform this action.')
          break
        
        case 404:
          toast.error('The requested resource was not found.')
          break
        
        case 422:
          // Validation error
          const validationErrors = data.detail || []
          if (Array.isArray(validationErrors)) {
            validationErrors.forEach(err => {
              toast.error(`${err.loc?.join('.')}: ${err.msg}`)
            })
          } else {
            toast.error(data.message || 'Validation error occurred.')
          }
          break
        
        case 500:
          toast.error('Server error. Please try again later.')
          break
        
        default:
          toast.error(data?.detail || data?.message || 'An error occurred.')
      }

      return Promise.reject(error)
    } else if (error.request) {
      // Request made but no response
      console.error('API Network Error:', error.request)
      toast.error('Network error. Please check your connection.')
      return Promise.reject(new Error('Network error'))
    } else {
      // Something else happened
      console.error('API Unexpected Error:', error.message)
      toast.error('An unexpected error occurred.')
      return Promise.reject(error)
    }
  }
)

// Request interceptor - Add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('API Request with token:', config.url, token.substring(0, 20) + '...')
    } else {
      console.log('API Request without token:', config.url)
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * GET request
 */
export const get = async (url, config = {}) => {
  try {
    const response = await api.get(url, config)
    return response
  } catch (error) {
    throw error
  }
}

/**
 * POST request
 */
export const post = async (url, data, config = {}) => {
  try {
    const response = await api.post(url, data, config)
    return response
  } catch (error) {
    throw error
  }
}

/**
 * PUT request
 */
export const put = async (url, data, config = {}) => {
  try {
    const response = await api.put(url, data, config)
    return response
  } catch (error) {
    throw error
  }
}

/**
 * PATCH request
 */
export const patch = async (url, data, config = {}) => {
  try {
    const response = await api.patch(url, data, config)
    return response
  } catch (error) {
    throw error
  }
}

/**
 * DELETE request
 */
export const del = async (url, config = {}) => {
  try {
    const response = await api.delete(url, config)
    return response
  } catch (error) {
    throw error
  }
}

/**
 * Upload file
 */
export const upload = async (url, formData, onProgress) => {
  try {
    const response = await api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          onProgress(percentCompleted)
        }
      },
    })
    return response
  } catch (error) {
    throw error
  }
}

/**
 * Download file
 */
export const download = async (url, filename) => {
  try {
    const response = await api.get(url, {
      responseType: 'blob',
    })
    
    // Create blob link to download
    const urlBlob = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = urlBlob
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.parentNode.removeChild(link)
  } catch (error) {
    throw error
  }
}

// Add default export
export default api
