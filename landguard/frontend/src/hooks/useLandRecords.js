/**
 * Custom Hook for Land Records Management
 */

import { useState, useEffect, useCallback } from 'react'
import { getLandRecords, getLandRecordById } from '../services/landRecords'
import { toast } from 'react-toastify'

export const useLandRecords = (initialFilters = {}) => {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 0,
  })
  const [filters, setFilters] = useState(initialFilters)

  const fetchRecords = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await getLandRecords({
        ...filters,
        page: pagination.page,
        limit: pagination.limit,
      })
      
      setRecords(response.data || [])
      setPagination({
        page: response.page || 1,
        limit: response.limit || 10,
        total: response.total || 0,
        totalPages: response.totalPages || 0,
      })
    } catch (err) {
      console.error('Error fetching land records:', err)
      setError(err.message || 'Failed to fetch land records')
      toast.error('Failed to load land records')
    } finally {
      setLoading(false)
    }
  }, [filters, pagination.page, pagination.limit])

  useEffect(() => {
    fetchRecords()
  }, [fetchRecords])

  const updateFilters = useCallback((newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }))
    setPagination((prev) => ({ ...prev, page: 1 }))
  }, [])

  const changePage = useCallback((newPage) => {
    setPagination((prev) => ({ ...prev, page: newPage }))
  }, [])

  const refresh = useCallback(() => {
    fetchRecords()
  }, [fetchRecords])

  return {
    records,
    loading,
    error,
    pagination,
    filters,
    updateFilters,
    changePage,
    refresh,
  }
}

export const useLandRecord = (recordId) => {
  const [record, setRecord] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchRecord = useCallback(async () => {
    if (!recordId) return

    try {
      setLoading(true)
      setError(null)
      
      const response = await getLandRecordById(recordId)
      setRecord(response)
    } catch (err) {
      console.error('Error fetching land record:', err)
      setError(err.message || 'Failed to fetch land record')
      toast.error('Failed to load land record details')
    } finally {
      setLoading(false)
    }
  }, [recordId])

  useEffect(() => {
    fetchRecord()
  }, [fetchRecord])

  const refresh = useCallback(() => {
    fetchRecord()
  }, [fetchRecord])

  return {
    record,
    loading,
    error,
    refresh,
  }
}