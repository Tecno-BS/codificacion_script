/**
 * Hook para manejar el monitoreo de procesos
 */
import { useState, useEffect, useCallback } from 'react'
import * as api from '@/lib/api'
import { AUTO_REFRESH_INTERVAL } from '@/utils/constants'

export function useMonitoring() {
  const [monitoreo, setMonitoreo] = useState<api.MonitoreoData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  const cargarMonitoreo = useCallback(async () => {
    try {
      setError(null)
      const data = await api.obtenerMonitoreo()
      setMonitoreo(data)
      setLastUpdate(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar monitoreo')
      console.error('Error cargando monitoreo:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  // Cargar al montar
  useEffect(() => {
    cargarMonitoreo()
  }, [cargarMonitoreo])

  // Auto-refresh cada 2 segundos si está activado
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      cargarMonitoreo()
    }, AUTO_REFRESH_INTERVAL)

    return () => clearInterval(interval)
  }, [autoRefresh, cargarMonitoreo])

  return {
    monitoreo,
    loading,
    error,
    autoRefresh,
    setAutoRefresh,
    lastUpdate,
    cargarMonitoreo,
  }
}

