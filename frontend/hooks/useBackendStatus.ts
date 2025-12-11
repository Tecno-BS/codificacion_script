/**
 * Hook para verificar el estado del backend
 */
import { useState, useEffect } from 'react'
import { BACKEND_URL } from '@/utils/constants'

export type BackendStatus = 'checking' | 'online' | 'offline'

export function useBackendStatus() {
  const [status, setStatus] = useState<BackendStatus>('checking')

  const checkStatus = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/health`)
      if (response.ok) {
        setStatus('online')
      } else {
        setStatus('offline')
      }
    } catch (error) {
      console.error('Error conectando al backend:', error)
      setStatus('offline')
    }
  }

  useEffect(() => {
    if (typeof window !== 'undefined') {
      checkStatus()
    }
  }, [])

  return { status, checkStatus }
}

