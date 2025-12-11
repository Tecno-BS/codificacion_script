/**
 * Tarjetas de resumen del dashboard
 */
'use client'

import { FileText, Activity, PauseCircle, CheckCircle2, XCircle } from 'lucide-react'
import type { MonitoreoData } from '@/lib/api'

interface SummaryCardsProps {
  resumen: MonitoreoData['resumen']
}

export function SummaryCards({ resumen }: SummaryCardsProps) {
  const cards = [
    {
      label: 'Total Procesos',
      value: resumen.total_procesos,
      icon: FileText,
      iconBg: 'bg-blue-100 dark:bg-blue-900/30',
      iconColor: 'text-blue-600 dark:text-blue-400',
      valueColor: 'text-gray-900 dark:text-white',
    },
    {
      label: 'Activos',
      value: resumen.activos,
      icon: Activity,
      iconBg: 'bg-green-100 dark:bg-green-900/30',
      iconColor: 'text-green-600 dark:text-green-400',
      valueColor: 'text-green-600 dark:text-green-400',
    },
    {
      label: 'Pausados',
      value: resumen.pausados,
      icon: PauseCircle,
      iconBg: 'bg-yellow-100 dark:bg-yellow-900/30',
      iconColor: 'text-yellow-600 dark:text-yellow-400',
      valueColor: 'text-yellow-600 dark:text-yellow-400',
    },
    {
      label: 'Completados',
      value: resumen.completados,
      icon: CheckCircle2,
      iconBg: 'bg-blue-100 dark:bg-blue-900/30',
      iconColor: 'text-blue-600 dark:text-blue-400',
      valueColor: 'text-blue-600 dark:text-blue-400',
    },
    {
      label: 'Cancelados',
      value: resumen.cancelados,
      icon: XCircle,
      iconBg: 'bg-red-100 dark:bg-red-900/30',
      iconColor: 'text-red-600 dark:text-red-400',
      valueColor: 'text-red-600 dark:text-red-400',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
      {cards.map((card) => {
        const Icon = card.icon
        return (
          <div
            key={card.label}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{card.label}</p>
                <p className={`text-3xl font-bold mt-2 ${card.valueColor}`}>{card.value}</p>
              </div>
              <div className={`w-12 h-12 ${card.iconBg} rounded-lg flex items-center justify-center`}>
                <Icon className={`w-6 h-6 ${card.iconColor}`} />
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

