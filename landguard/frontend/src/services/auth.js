/**
 * Authentication Service
 */

import api from './api'

/**
 * Login user
 */
export const login = async (username, password) => {
  try {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    const response = await api.post('/auth/login/form', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    return response
  } catch (error) {
    console.error('Login error:', error)
    throw error
  }
}

/**
 * Logout user
 */
export const logout = async () => {
  try {
    await api.post('/auth/logout')
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  } catch (error) {
    console.error('Logout error:', error)
    // Clear local storage anyway
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
}

/**
 * Get current user profile
 */
export const getCurrentUser = async () => {
  try {
    const response = await api.get('/auth/me')
    return response
  } catch (error) {
    console.error('Get current user error:', error)
    throw error
  }
}

/**
 * Change password
 */
export const changePassword = async (currentPassword, newPassword) => {
  try {
    const response = await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
    return response
  } catch (error) {
    console.error('Change password error:', error)
    throw error
  }
}

/**
 * Verify token is valid
 */
export const verifyToken = async () => {
  try {
    const response = await api.get('/auth/verify')
    return response
  } catch (error) {
    console.error('Verify token error:', error)
    return false
  }
}