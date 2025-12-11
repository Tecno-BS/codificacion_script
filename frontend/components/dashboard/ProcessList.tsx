/**
 * Lista de procesos del dashboard
 */
'use client'

import { Activity } from 'lucide-react'
import type { MonitoreoData } from '@/lib/api'
import { ProcessItem } from './ProcessItem'

interface ProcessListProps {
  procesos: MonitoreoData['procesos']
  accionesEnProceso: Set<string>
  onPausar: (procesoId: string) => Promise<void>
  onReanudar: (procesoId: string) => Promise<void>
  onCancelar: (procesoId: string) => Promise<void>
}

export function ProcessList({
  procesos,
  accionesEnProceso,
  onPausar,
  onReanudar,
  onCancelar,
}: ProcessListProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Procesos Activos ({procesos.length})
        </h2>
      </div>
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {procesos.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <Activity className="w-12 h-12 mx-auto text-gray-400 dark:text-gray-500 mb-4" />
            <p className="text-gray-500 dark:text-gray-400">No hay procesos activos</p>
          </div>
        ) : (
          procesos.map((proceso) => (
            <ProcessItem
              key={proceso.proceso_id}
              proceso={proceso}
              accionesEnProceso={accionesEnProceso}
              onPausar={onPausar}
              onReanudar={onReanudar}
              onCancelar={onCancelar}
            />
          ))
        )}
      </div>
    </div>
  )
}

