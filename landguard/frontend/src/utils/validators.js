/**
 * Utility functions for validation
 */

/**
 * Validate email
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validate phone number (Indian)
 */
export const isValidPhone = (phone) => {
  const phoneRegex = /^[6-9]\d{9}$/
  const cleaned = phone.replace(/\D/g, '')
  return phoneRegex.test(cleaned)
}

/**
 * Validate username
 */
export const isValidUsername = (username) => {
  // Must be 3-20 characters, alphanumeric and underscore
  const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/
  return usernameRegex.test(username)
}

/**
 * Validate password
 */
export const isValidPassword = (password) => {
  // Minimum 8 characters, at least one letter and one number
  const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$/
  return passwordRegex.test(password)
}

/**
 * Validate required field
 */
export const isRequired = (value) => {
  if (typeof value === 'string') {
    return value.trim().length > 0
  }
  return value !== null && value !== undefined
}

/**
 * Validate number
 */
export const isValidNumber = (value) => {
  return !isNaN(parseFloat(value)) && isFinite(value)
}

/**
 * Validate positive number
 */
export const isPositiveNumber = (value) => {
  return isValidNumber(value) && parseFloat(value) > 0
}

/**
 * Validate area (square feet)
 */
export const isValidArea = (area) => {
  return isPositiveNumber(area) && parseFloat(area) <= 1000000000 // Max 1 billion sq ft
}

/**
 * Validate land ID format
 */
export const isValidLandId = (landId) => {
  // Format: LND-XXXX-XXXX
  const landIdRegex = /^LND-[A-Z0-9]{4,}-[A-Z0-9]{4,}$/
  return landIdRegex.test(landId)
}

/**
 * Validate file type
 */
export const isValidFileType = (file, allowedTypes) => {
  return allowedTypes.includes(file.type)
}

/**
 * Validate file size
 */
export const isValidFileSize = (file, maxSize) => {
  return file.size <= maxSize
}

/**
 * Validate date
 */
export const isValidDate = (date) => {
  const parsedDate = new Date(date)
  return parsedDate instanceof Date && !isNaN(parsedDate)
}

/**
 * Validate date range
 */
export const isValidDateRange = (startDate, endDate) => {
  const start = new Date(startDate)
  const end = new Date(endDate)
  return isValidDate(startDate) && isValidDate(endDate) && start <= end
}

/**
 * Validate URL
 */
export const isValidUrl = (url) => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * Validate pincode (Indian)
 */
export const isValidPincode = (pincode) => {
  const pincodeRegex = /^[1-9][0-9]{5}$/
  return pincodeRegex.test(pincode)
}

/**
 * Get validation error message
 */
export const getValidationError = (field, value, rules = {}) => {
  if (rules.required && !isRequired(value)) {
    return `${field} is required`
  }

  if (rules.email && value && !isValidEmail(value)) {
    return `${field} must be a valid email`
  }

  if (rules.phone && value && !isValidPhone(value)) {
    return `${field} must be a valid phone number`
  }

  if (rules.username && value && !isValidUsername(value)) {
    return `${field} must be 3-20 characters, alphanumeric and underscore only`
  }

  if (rules.password && value && !isValidPassword(value)) {
    return `${field} must be at least 8 characters with letters and numbers`
  }

  if (rules.number && value && !isValidNumber(value)) {
    return `${field} must be a valid number`
  }

  if (rules.positive && value && !isPositiveNumber(value)) {
    return `${field} must be a positive number`
  }

  if (rules.min && value && parseFloat(value) < rules.min) {
    return `${field} must be at least ${rules.min}`
  }

  if (rules.max && value && parseFloat(value) > rules.max) {
    return `${field} must be at most ${rules.max}`
  }

  if (rules.minLength && value && value.length < rules.minLength) {
    return `${field} must be at least ${rules.minLength} characters`
  }

  if (rules.maxLength && value && value.length > rules.maxLength) {
    return `${field} must be at most ${rules.maxLength} characters`
  }

  return null
}

/**
 * Validate form
 */
export const validateForm = (formData, validationRules) => {
  const errors = {}

  Object.keys(validationRules).forEach((field) => {
    const error = getValidationError(
      field,
      formData[field],
      validationRules[field]
    )
    if (error) {
      errors[field] = error
    }
  })

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  }
}