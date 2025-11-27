/**
 * Application constants and configuration
 */

// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
export const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 30000

// Application Info
export const APP_NAME = import.meta.env.VITE_APP_NAME || 'LandGuard'
export const APP_VERSION = import.meta.env.VITE_APP_VERSION || '1.0.0'

// User Roles
export const USER_ROLES = {
  ADMIN: 'ADMIN',
  ANALYST: 'ANALYST',
  VIEWER: 'VIEWER',
}

// Risk Levels
export const RISK_LEVELS = {
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
  CRITICAL: 'CRITICAL',
}

// Risk Level Colors
export const RISK_COLORS = {
  LOW: '#4caf50',
  MEDIUM: '#ff9800',
  HIGH: '#ff5722',
  CRITICAL: '#d32f2f',
}

// Property Types
export const PROPERTY_TYPES = {
  RESIDENTIAL: 'residential',
  COMMERCIAL: 'commercial',
  AGRICULTURAL: 'agricultural',
  INDUSTRIAL: 'industrial',
  MIXED: 'mixed',
}

// Analysis Status
export const ANALYSIS_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
}

// Pagination
export const DEFAULT_PAGE_SIZE = 10
export const PAGE_SIZE_OPTIONS = [5, 10, 25, 50, 100]

// File Upload
export const MAX_FILE_SIZE = parseInt(import.meta.env.VITE_MAX_UPLOAD_SIZE) || 10485760 // 10MB
export const ALLOWED_FILE_TYPES = [
  'text/csv',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
]

// Date Formats
export const DATE_FORMAT = 'MMM dd, yyyy'
export const DATETIME_FORMAT = 'MMM dd, yyyy HH:mm'

// Chart Colors
export const CHART_COLORS = [
  '#1976d2',
  '#dc004e',
  '#2e7d32',
  '#ed6c02',
  '#9c27b0',
  '#00bcd4',
]

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'landguard_auth_token',
  USER_DATA: 'landguard_user_data',
  THEME_MODE: 'landguard_theme_mode',
}

// API Endpoints
export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',
  REFRESH: '/auth/refresh',
  
  // Users
  USERS: '/users',
  USER_BY_ID: (id) => `/users/${id}`,
  
  // Land Records
  LAND_RECORDS: '/land-records',
  LAND_RECORD_BY_ID: (id) => `/land-records/${id}`,
  LAND_RECORDS_SEARCH: '/land-records/search',
  LAND_RECORDS_BULK: '/land-records/bulk',
  
  // Analysis
  ANALYSIS: '/analysis',
  ANALYSIS_BY_ID: (id) => `/analysis/${id}`,
  ANALYZE_LAND: (id) => `/analysis/land/${id}`,
  
  // Reports
  REPORTS: '/reports',
  REPORT_BY_ID: (id) => `/reports/${id}`,
  GENERATE_REPORT: '/reports/generate',
  
  // Statistics
  STATS: '/statistics',
  DASHBOARD_STATS: '/statistics/dashboard',
}