/**
 * Tarjetas de estadísticas del dashboard
 */
'use client'

import { TrendingUp, Activity } from 'lucide-react'
import type { MonitoreoData } from '@/lib/api'
import { formatNumber, formatPercentage } from '@/utils/helpers'

interface StatsCardsProps {
  estadisticas: MonitoreoData['estadisticas']
}

export function StatsCards({ estadisticas }: StatsCardsProps) {
  const stats = [
    {
      label: 'Total Respuestas',
      value: formatNumber(estadisticas.total_respuestas),
      icon: TrendingUp,
      iconBg: 'bg-purple-100 dark:bg-purple-900/30',
      iconColor: 'text-purple-600 dark:text-purple-400',
    },
    {
      label: 'Respuestas Procesadas',
      value: formatNumber(estadisticas.respuestas_procesadas),
      icon: Activity,
      iconBg: 'bg-indigo-100 dark:bg-indigo-900/30',
      iconColor: 'text-indigo-600 dark:text-indigo-400',
    },
    {
      label: 'Progreso Promedio',
      value: formatPercentage(estadisticas.progreso_promedio),
      icon: TrendingUp,
      iconBg: 'bg-orange-100 dark:bg-orange-900/30',
      iconColor: 'text-orange-600 dark:text-orange-400',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      {stats.map((stat) => {
        const Icon = stat.icon
        return (
          <div
            key={stat.label}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 ${stat.iconBg} rounded-lg flex items-center justify-center`}>
                <Icon className={`w-5 h-5 ${stat.iconColor}`} />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{stat.label}</p>
                <p className="text-xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

