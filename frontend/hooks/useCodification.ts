/**
 * Hook principal para manejar el proceso de codificación
 */
import { useState, useEffect, useCallback } from 'react'
import * as api from '@/lib/api'
import type { ProcessingState, ResultsData } from '@/types'

export function useCodification() {
  // Estado de procesamiento
  const [processing, setProcessing] = useState<ProcessingState>({
    loading: false,
    progress: 0,
    message: '',
    error: null,
  })

  // Estado de progreso real
  const [procesoId, setProcesoId] = useState<string | null>(null)
  const [pausado, setPausado] = useState(false)
  const [batchActual, setBatchActual] = useState(0)
  const [totalBatches, setTotalBatches] = useState(0)
  const [respuestasProcesadas, setRespuestasProcesadas] = useState(0)
  const [totalRespuestasProceso, setTotalRespuestasProceso] = useState(0)

  // Estado de resultados
  const [results, setResults] = useState<ResultsData | null>(null)

  // Reconectar a un proceso existente
  const reconectarProceso = useCallback(async (procesoId: string) => {
    try {
      const estado = await api.obtenerEstadoProceso(procesoId)

      // Si el proceso está completado o cancelado, limpiar localStorage
      if (estado.completado || estado.cancelado || estado.progreso_pct >= 100) {
        localStorage.removeItem('proceso_activo_id')
        return
      }

      // Reconectar al proceso
      setProcesoId(procesoId)
      setPausado(estado.pausado)
      setBatchActual(estado.batch_actual)
      setTotalBatches(estado.total_batches)
      setRespuestasProcesadas(estado.respuestas_procesadas)
      setTotalRespuestasProceso(estado.total_respuestas)

      setProcessing({
        loading: true,
        progress: estado.progreso_pct,
        message: estado.mensaje,
        error: null,
      })

      // Reconectar al stream de progreso
      const eventSource = api.conectarProgreso(
        procesoId,
        (data) => {
          setProcessing((prev) => ({
            ...prev,
            progress: data.progreso_pct,
            message: data.mensaje,
          }))

          setBatchActual(data.batch_actual)
          setTotalBatches(data.total_batches)
          setRespuestasProcesadas(data.respuestas_procesadas)
          setTotalRespuestasProceso(data.total_respuestas)
          setPausado(data.pausado)

          // Si hay un error, manejarlo
          if (data.error || data.mensaje_error) {
            const mensajeError = data.mensaje_error || data.mensaje || 'Error desconocido'
            setProcessing((prev) => ({
              ...prev,
              loading: false,
              progress: data.progreso_pct,
              message: mensajeError,
              error: mensajeError,
            }))
            if (onError) {
              onError(new Error(mensajeError))
            }
            setProcesoId(null)
            localStorage.removeItem('proceso_activo_id')
            return
          }

          // Si completó
          if (data.completado) {
            const statsSSE = data.stats || null
            setProcessing((prev) => ({
              ...prev,
              loading: false,
              progress: 100,
              message: '✅ Codificación completada',
            }))

            if (data.archivo_resultados) {
              setResults({
                results: [],
                totalRespuestas: data.total_respuestas,
                totalPreguntas: 0,
                costoTotal: statsSSE?.costo_total ?? 0,
                archivoResultados: data.archivo_resultados,
                archivoCodigos: data.archivo_codigos_nuevos || undefined,
                stats: statsSSE || undefined,
              })
            }
            localStorage.removeItem('proceso_activo_id')
            setProcesoId(null)
          }

          // Si fue cancelado
          if (data.cancelado) {
            setProcessing((prev) => ({
              ...prev,
              loading: false,
              error: 'Proceso cancelado',
            }))
            localStorage.removeItem('proceso_activo_id')
            setProcesoId(null)
          }
        },
        (error) => {
          console.error('Error reconectando:', error)
          localStorage.removeItem('proceso_activo_id')
          setProcesoId(null)
        }
      )

      return () => {
        eventSource.close()
      }
    } catch (error) {
      localStorage.removeItem('proceso_activo_id')
      console.error('Error reconectando proceso:', error)
    }
  }, [])

  // Reconectar al montar si hay un proceso guardado
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const procesoIdGuardado = localStorage.getItem('proceso_activo_id')
      if (procesoIdGuardado) {
        reconectarProceso(procesoIdGuardado)
      }
    }
  }, [reconectarProceso])

  // Ejecutar codificación
  const executeCodification = useCallback(
    async (
      archivoRespuestas: File,
      archivoCodigos: File | null,
      modelo: string,
      configuracionAuxiliar?: {
        usar: boolean
        categorizacion: {
          negativas: string[]
          neutrales: string[]
          positivas: string[]
        }
      },
      onSuccess?: (response: api.CodificacionResponse) => void,
      onError?: (error: Error) => void
    ) => {
      // Resetear estado
      setProcessing({
        loading: true,
        progress: 0,
        message: '📤 Subiendo archivos...',
        error: null,
      })

      setBatchActual(0)
      setTotalBatches(0)
      setRespuestasProcesadas(0)
      setTotalRespuestasProceso(0)
      setPausado(false)

      try {
        const response = await api.codificarRespuestas(
          archivoRespuestas,
          archivoCodigos,
          modelo,
          undefined,
          configuracionAuxiliar
        )

        // Si el backend devuelve un proceso_id, conectarse al SSE
        if (response.proceso_id) {
          setProcesoId(response.proceso_id)
          localStorage.setItem('proceso_activo_id', response.proceso_id)

          // Conectar al stream de progreso
          const eventSource = api.conectarProgreso(
            response.proceso_id,
            (data) => {
              setProcessing((prev) => ({
                ...prev,
                progress: data.progreso_pct,
                message: data.mensaje,
              }))

              setBatchActual(data.batch_actual)
              setTotalBatches(data.total_batches)
              setRespuestasProcesadas(data.respuestas_procesadas)
              setTotalRespuestasProceso(data.total_respuestas)
              setPausado(data.pausado)

              // Si hay un error, manejarlo
              if (data.error || data.mensaje_error) {
                const mensajeError = data.mensaje_error || data.mensaje || 'Error desconocido'
                setProcessing((prev) => ({
                  ...prev,
                  loading: false,
                  progress: data.progreso_pct,
                  message: mensajeError,
                  error: mensajeError,
                }))
                if (onError) {
                  onError(new Error(mensajeError))
                }
                setProcesoId(null)
                localStorage.removeItem('proceso_activo_id')
                return
              }

              // Si completó
              if (data.completado) {
                const archivoResultadosSSE = data.archivo_resultados || response.ruta_resultados
                const archivoCodigosSSE = data.archivo_codigos_nuevos || response.ruta_codigos_nuevos
                const statsSSE = data.stats || null

                setProcessing((prev) => ({
                  ...prev,
                  loading: false,
                  progress: 100,
                  message: '✅ Codificación completada',
                }))

                setResults({
                  results: [],
                  totalRespuestas: data.total_respuestas || response.total_respuestas,
                  totalPreguntas: response.total_preguntas,
                  costoTotal: (statsSSE?.costo_total ?? response.costo_total) || 0,
                  archivoResultados: archivoResultadosSSE || '',
                  archivoCodigos: archivoCodigosSSE || undefined,
                  stats: statsSSE || undefined,
                })

                if (onSuccess) onSuccess(response)
                setProcesoId(null)
                localStorage.removeItem('proceso_activo_id')
              }

              // Si fue cancelado
              if (data.cancelado) {
                setProcessing((prev) => ({
                  ...prev,
                  loading: false,
                  error: 'Proceso cancelado por el usuario',
                }))
                setProcesoId(null)
                localStorage.removeItem('proceso_activo_id')
              }
            },
            (error) => {
              setProcessing({
                loading: false,
                progress: 0,
                message: '',
                error: error.message,
              })
              if (onError) onError(error)
              setProcesoId(null)
              localStorage.removeItem('proceso_activo_id')
            }
          )

          return () => {
            eventSource.close()
          }
        } else {
          // Modo antiguo sin SSE (fallback)
          setProcessing({
            loading: false,
            progress: 100,
            message: '✅ Codificación completada',
            error: null,
          })

          setResults({
            results: [],
            totalRespuestas: response.total_respuestas,
            totalPreguntas: response.total_preguntas,
            costoTotal: response.costo_total,
            archivoResultados: response.ruta_resultados,
            archivoCodigos: response.ruta_codigos_nuevos,
          })

          if (onSuccess) onSuccess(response)
        }
      } catch (error) {
        setProcessing({
          loading: false,
          progress: 0,
          message: '',
          error: error instanceof Error ? error.message : 'Error desconocido',
        })
        if (onError) onError(error instanceof Error ? error : new Error('Error desconocido'))
      }
    },
    []
  )

  // Pausar/Reanudar proceso
  const togglePausa = useCallback(async () => {
    if (!procesoId) return

    try {
      if (pausado) {
        await api.reanudarProceso(procesoId)
      } else {
        await api.pausarProceso(procesoId)
      }
      setPausado(!pausado)
    } catch (error) {
      throw error
    }
  }, [procesoId, pausado])

  // Cancelar proceso
  const cancelar = useCallback(async () => {
    if (!procesoId) return

    try {
      await api.cancelarProceso(procesoId)
      setProcessing((prev) => ({
        ...prev,
        loading: false,
        error: 'Proceso cancelado',
      }))
      setProcesoId(null)
      localStorage.removeItem('proceso_activo_id')
    } catch (error) {
      throw error
    }
  }, [procesoId])

  // Reiniciar
  const reset = useCallback(() => {
    setResults(null)
    setProcessing({
      loading: false,
      progress: 0,
      message: '',
      error: null,
    })
    setBatchActual(0)
    setTotalBatches(0)
    setRespuestasProcesadas(0)
    setTotalRespuestasProceso(0)
    setPausado(false)
    setProcesoId(null)
    localStorage.removeItem('proceso_activo_id')
  }, [])

  return {
    processing,
    results,
    procesoId,
    pausado,
    batchActual,
    totalBatches,
    respuestasProcesadas,
    totalRespuestasProceso,
    executeCodification,
    togglePausa,
    cancelar,
    reset,
  }
}

