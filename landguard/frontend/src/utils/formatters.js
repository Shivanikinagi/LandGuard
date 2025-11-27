/**
 * Utility functions for formatting data
 */

import { format } from 'date-fns'
import { DATE_FORMAT, DATETIME_FORMAT } from './constants'

/**
 * Format date
 */
export const formatDate = (date, formatString = DATE_FORMAT) => {
  if (!date) return 'N/A'
  try {
    return format(new Date(date), formatString)
  } catch (error) {
    return 'Invalid Date'
  }
}

/**
 * Format datetime
 */
export const formatDateTime = (date) => {
  return formatDate(date, DATETIME_FORMAT)
}

/**
 * Format currency (Indian Rupees)
 */
export const formatCurrency = (amount) => {
  if (amount === null || amount === undefined) return '₹0'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

/**
 * Format number with commas
 */
export const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  return new Intl.NumberFormat('en-IN').format(num)
}

/**
 * Format percentage
 */
export const formatPercentage = (value, decimals = 1) => {
  if (value === null || value === undefined) return '0%'
  return `${Number(value).toFixed(decimals)}%`
}

/**
 * Format file size
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

/**
 * Format area (square feet)
 */
export const formatArea = (sqft) => {
  if (sqft === null || sqft === undefined) return '0 sq ft'
  return `${formatNumber(sqft)} sq ft`
}

/**
 * Truncate text
 */
export const truncateText = (text, maxLength = 50) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

/**
 * Format risk score
 */
export const formatRiskScore = (score) => {
  if (score === null || score === undefined) return 'N/A'
  return `${Number(score).toFixed(1)}/100`
}

/**
 * Format confidence
 */
export const formatConfidence = (confidence) => {
  if (confidence === null || confidence === undefined) return 'N/A'
  return formatPercentage(confidence * 100)
}

/**
 * Capitalize first letter
 */
export const capitalize = (str) => {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

/**
 * Format property type
 */
export const formatPropertyType = (type) => {
  if (!type) return 'N/A'
  return type
    .split('_')
    .map(word => capitalize(word))
    .join(' ')
}

/**
 * Format risk level
 */
export const formatRiskLevel = (level) => {
  if (!level) return 'Unknown'
  return capitalize(level)
}

/**
 * Format boolean
 */
export const formatBoolean = (value) => {
  return value ? 'Yes' : 'No'
}

/**
 * Format phone number
 */
export const formatPhoneNumber = (phone) => {
  if (!phone) return 'N/A'
  // Remove all non-numeric characters
  const cleaned = phone.replace(/\D/g, '')
  // Format as +91 XXXXX XXXXX
  if (cleaned.length === 10) {
    return `+91 ${cleaned.slice(0, 5)} ${cleaned.slice(5)}`
  }
  return phone
}

/**
 * Format address
 */
export const formatAddress = (address) => {
  if (!address) return 'N/A'
  const parts = [
    address.street,
    address.city,
    address.state,
    address.pincode,
  ].filter(Boolean)
  return parts.join(', ')
}