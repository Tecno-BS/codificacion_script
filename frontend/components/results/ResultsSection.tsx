/**
 * Componente de sección de resultados
 */
'use client'

import { CheckCircle2, RotateCcw, Download } from 'lucide-react'
import { StatsCard } from '../ui/StatsCard'
import { formatCurrency } from '@/utils/helpers'
import type { ResultsData } from '@/types'
import * as api from '@/lib/api'

interface ResultsSectionProps {
  results: ResultsData
  onReset: () => void
  onNotification?: (message: string, type?: 'success' | 'info' | 'warning') => void
}

export function ResultsSection({ results, onReset, onNotification }: ResultsSectionProps) {
  const handleDownloadResults = async () => {
    if (!results.archivoResultados) return

    try {
      const blob = await api.descargarResultados(results.archivoResultados)
      api.downloadBlob(blob, results.archivoResultados)
      if (onNotification) {
        onNotification('📥 Archivo descargado exitosamente', 'success')
      }
    } catch (error) {
      if (onNotification) {
        onNotification(
          `❌ Error al descargar: ${error instanceof Error ? error.message : 'Error'}`,
          'warning'
        )
      }
    }
  }

  const handleDownloadCodigosNuevos = async () => {
    if (!results.archivoCodigos) return

    try {
      const blob = await api.descargarCodigosNuevos(results.archivoCodigos)
      api.downloadBlob(blob, results.archivoCodigos)
      if (onNotification) {
        onNotification('📥 Catálogo descargado exitosamente', 'success')
      }
    } catch (error) {
      if (onNotification) {
        onNotification(
          `❌ Error al descargar: ${error instanceof Error ? error.message : 'Error'}`,
          'warning'
        )
      }
    }
  }

  return (
    <div className="mb-8 animate-fade-in-up">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-bold flex items-center gap-3">
          <CheckCircle2 className="w-8 h-8 text-green-600" />
          Codificación Completada
        </h2>
        <button
          onClick={onReset}
          className="bg-muted hover:bg-muted/80 text-foreground px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-all transform hover:scale-105 active:scale-95"
        >
          <RotateCcw className="w-4 h-4" />
          Nueva Codificación
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <StatsCard
          label="Total Respuestas (archivo)"
          value={results.totalRespuestas}
        />
        <StatsCard
          label="Respuestas Codificadas"
          value={results.stats?.total_respuestas_codificadas ?? results.totalRespuestas}
        />
        <StatsCard
          label="Costo Total (USD)"
          value={formatCurrency(results.stats?.costo_total ?? results.costoTotal)}
        />
      </div>

      {/* Extra stats: códigos y tokens */}
      {results.stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <StatsCard
            label="Códigos Nuevos Generados"
            value={results.stats.total_codigos_nuevos}
          />
          <StatsCard
            label="Códigos Históricos Aplicados"
            value={results.stats.total_codigos_historicos}
          />
          <StatsCard
            label="Tokens Totales"
            value={results.stats.total_tokens}
          />
        </div>
      )}

      {/* Download Buttons */}
      <div className="flex flex-wrap gap-4">
        <button
          onClick={handleDownloadResults}
          className="bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-700 hover:to-orange-600 shadow-lg hover:shadow-xl hover:shadow-orange-500/50 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-all transform hover:scale-105 active:scale-95"
        >
          <Download className="w-5 h-5" />
          Descargar Resultados
        </button>
        {results.archivoCodigos && (
          <button
            onClick={handleDownloadCodigosNuevos}
            className="bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-700 hover:to-orange-600 shadow-lg hover:shadow-xl hover:shadow-orange-500/50 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-all transform hover:scale-105 active:scale-95"
          >
            <Download className="w-5 h-5" />
            Descargar Códigos Nuevos
          </button>
        )}
      </div>

      {/* Success Message */}
      <div className="mt-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-4 flex items-start gap-3">
        <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
        <div>
          <p className="font-semibold text-green-900 dark:text-green-100">
            ¡Proceso completado exitosamente!
          </p>
          <p className="text-sm text-green-700 dark:text-green-300 mt-1">
            Los archivos están listos para descargar. El archivo de resultados contiene todas las respuestas
            codificadas.
          </p>
        </div>
      </div>
    </div>
  )
}

