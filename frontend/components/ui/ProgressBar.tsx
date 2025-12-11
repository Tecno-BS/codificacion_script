/**
 * Componente de barra de progreso
 */
'use client'

import { Play, Pause, XCircle } from 'lucide-react'
import type { ProcessingState } from '@/types'

interface ProgressBarProps {
  processing: ProcessingState
  pausado: boolean
  batchActual: number
  totalBatches: number
  respuestasProcesadas: number
  totalRespuestasProceso: number
  procesoId: string | null
  onTogglePausa: () => Promise<void>
  onCancelar: () => Promise<void>
}

export function ProgressBar({
  processing,
  pausado,
  batchActual,
  totalBatches,
  respuestasProcesadas,
  totalRespuestasProceso,
  procesoId,
  onTogglePausa,
  onCancelar,
}: ProgressBarProps) {
  if (!processing.loading) return null

  return (
    <div className="mb-8 bg-gradient-to-r from-orange-50 to-orange-100/50 dark:from-orange-900/20 dark:to-orange-800/10 border border-orange-200 dark:border-orange-800 rounded-xl p-6 animate-fade-in-up shadow-lg">
      {/* Mensaje de estado */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-foreground font-medium">{processing.message}</p>
        {pausado && (
          <span className="text-xs bg-yellow-500/20 text-yellow-700 dark:text-yellow-400 px-3 py-1 rounded-full font-semibold">
            PAUSADO
          </span>
        )}
      </div>

      {/* Barra de progreso */}
      <div className="w-full bg-orange-200 dark:bg-orange-900/30 rounded-full h-4 overflow-hidden mb-3 shadow-inner">
        <div
          className="bg-gradient-to-r from-orange-600 via-orange-500 to-orange-600 h-4 rounded-full transition-all duration-500 shadow-lg flex items-center justify-center"
          style={{ width: `${processing.progress}%` }}
        >
          {processing.progress > 10 && (
            <span className="text-xs font-bold text-white">{Math.round(processing.progress)}%</span>
          )}
        </div>
      </div>

      {/* Información detallada */}
      {totalRespuestasProceso > 0 && (
        <div className="grid grid-cols-2 gap-4 mb-4 text-xs">
          <div className="bg-white/50 dark:bg-gray-800/50 rounded-lg p-3">
            <p className="text-muted-foreground mb-1">Respuestas procesadas</p>
            <p className="text-lg font-bold text-orange-600 dark:text-orange-400">
              {respuestasProcesadas} / {totalRespuestasProceso}
            </p>
          </div>
          <div className="bg-white/50 dark:bg-gray-800/50 rounded-lg p-3">
            <p className="text-muted-foreground mb-1">Batches completados</p>
            <p className="text-lg font-bold text-orange-600 dark:text-orange-400">
              {batchActual} / {totalBatches}
            </p>
          </div>
        </div>
      )}

      {/* Botones de control */}
      {procesoId && (
        <div className="flex gap-3 justify-center pt-2">
          <button
            onClick={onTogglePausa}
            className="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-all transform hover:scale-105 active:scale-95 shadow-md"
          >
            {pausado ? (
              <>
                <Play className="w-4 h-4" />
                Reanudar
              </>
            ) : (
              <>
                <Pause className="w-4 h-4" />
                Pausar
              </>
            )}
          </button>
          <button
            onClick={onCancelar}
            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-all transform hover:scale-105 active:scale-95 shadow-md"
          >
            <XCircle className="w-4 h-4" />
            Cancelar
          </button>
        </div>
      )}
    </div>
  )
}

