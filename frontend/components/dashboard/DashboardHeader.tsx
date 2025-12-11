/**
 * Header del dashboard
 */
'use client'

import { Activity, ArrowLeft, RefreshCw } from 'lucide-react'
import Link from 'next/link'

interface DashboardHeaderProps {
  autoRefresh: boolean
  onToggleAutoRefresh: () => void
  loading: boolean
  onRefresh: () => void
  lastUpdate: Date | null
}

export function DashboardHeader({
  autoRefresh,
  onToggleAutoRefresh,
  loading,
  onRefresh,
  lastUpdate,
}: DashboardHeaderProps) {
  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-orange-500 dark:hover:text-orange-400 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Volver</span>
            </Link>
            <div className="h-6 w-px bg-gray-300 dark:bg-gray-600" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <Activity className="w-6 h-6 text-orange-500" />
              Dashboard de Procesos
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={onToggleAutoRefresh}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                autoRefresh
                  ? 'bg-orange-500 text-white hover:bg-orange-600'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              {autoRefresh ? 'Auto-actualizar: ON' : 'Auto-actualizar: OFF'}
            </button>
            <button
              onClick={onRefresh}
              disabled={loading}
              className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Actualizar
            </button>
          </div>
        </div>
        {lastUpdate && (
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
            Última actualización: {lastUpdate.toLocaleTimeString()}
          </p>
        )}
      </div>
    </header>
  )
}

