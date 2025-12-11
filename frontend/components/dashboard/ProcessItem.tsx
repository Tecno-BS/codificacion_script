/**
 * Item individual de proceso en el dashboard
 */
'use client'

import { RefreshCw, Play, Pause, Trash2 } from 'lucide-react'
import { getEstadoColor, getEstadoIcono, getProgresoColor } from '@/utils/processHelpers'
import type { MonitoreoData } from '@/lib/api'

interface ProcessItemProps {
  proceso: MonitoreoData['procesos'][0]
  accionesEnProceso: Set<string>
  onPausar: (procesoId: string) => Promise<void>
  onReanudar: (procesoId: string) => Promise<void>
  onCancelar: (procesoId: string) => Promise<void>
}

export function ProcessItem({
  proceso,
  accionesEnProceso,
  onPausar,
  onReanudar,
  onCancelar,
}: ProcessItemProps) {
  const estaEnProceso = accionesEnProceso.has(proceso.proceso_id)
  const puedeAccionar = proceso.estado !== 'completado' && proceso.estado !== 'cancelado'

  return (
    <div className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4 flex-1">
          {/* Estado */}
          <div className={`w-3 h-3 rounded-full ${getEstadoColor(proceso.estado)}`} />

          {/* Info del proceso */}
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <div className="flex items-center gap-2">{getEstadoIcono(proceso.estado)}</div>
              <span className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                {proceso.estado}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">
                {proceso.proceso_id.substring(0, 8)}...
              </span>
            </div>

            {/* Progreso */}
            <div className="mb-2">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-600 dark:text-gray-400">Progreso</span>
                <span className="font-medium text-gray-900 dark:text-white">{proceso.progreso_pct}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${getProgresoColor(proceso.estado)}`}
                  style={{ width: `${proceso.progreso_pct}%` }}
                />
              </div>
            </div>

            {/* Detalles */}
            <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
              <span>Respuestas: {proceso.respuestas}</span>
              <span>•</span>
              <span>Batches: {proceso.batches}</span>
            </div>

            {/* Mensaje */}
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{proceso.mensaje}</p>
          </div>
        </div>

        {/* Botones de Acción */}
        {puedeAccionar && (
          <div className="flex items-center gap-2">
            {proceso.estado === 'pausado' ? (
              <button
                onClick={() => onReanudar(proceso.proceso_id)}
                disabled={estaEnProceso}
                className="p-2 rounded-lg bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-900/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Reanudar proceso"
              >
                {estaEnProceso ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              </button>
            ) : (
              <button
                onClick={() => onPausar(proceso.proceso_id)}
                disabled={estaEnProceso}
                className="p-2 rounded-lg bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 hover:bg-yellow-200 dark:hover:bg-yellow-900/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Pausar proceso"
              >
                {estaEnProceso ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Pause className="w-4 h-4" />}
              </button>
            )}
            <button
              onClick={() => onCancelar(proceso.proceso_id)}
              disabled={estaEnProceso}
              className="p-2 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Cancelar proceso"
            >
              {estaEnProceso ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

