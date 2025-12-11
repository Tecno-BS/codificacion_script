/**
 * Estado de carga del dashboard
 */
'use client'

import { RefreshCw } from 'lucide-react'

export function LoadingState() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
      <div className="text-center">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-orange-500" />
        <p className="text-gray-600 dark:text-gray-400">Cargando monitoreo...</p>
      </div>
    </div>
  )
}

