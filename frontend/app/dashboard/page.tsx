"use client"

import { useState, useEffect } from "react"
import { Activity, RefreshCw, CheckCircle2, PauseCircle, XCircle, Clock, TrendingUp, FileText, ArrowLeft, Play, Pause, Trash2 } from "lucide-react"
import * as api from "@/lib/api"
import Link from "next/link"

export default function DashboardPage() {
  const [monitoreo, setMonitoreo] = useState<api.MonitoreoData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const [accionesEnProceso, setAccionesEnProceso] = useState<Set<string>>(new Set())
  const [notificacion, setNotificacion] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  // Función para cargar monitoreo
  const cargarMonitoreo = async () => {
    try {
      setError(null)
      const data = await api.obtenerMonitoreo()
      setMonitoreo(data)
      setLastUpdate(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar monitoreo')
      console.error('Error cargando monitoreo:', err)
    } finally {
      setLoading(false)
    }
  }

  // Cargar al montar
  useEffect(() => {
    cargarMonitoreo()
  }, [])

  // Auto-refresh cada 2 segundos si está activado
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      cargarMonitoreo()
    }, 2000)

    return () => clearInterval(interval)
  }, [autoRefresh])

  // Función para obtener color según estado
  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'activo':
        return 'bg-green-500'
      case 'pausado':
        return 'bg-yellow-500'
      case 'cancelado':
        return 'bg-red-500'
      case 'completado':
        return 'bg-blue-500'
      default:
        return 'bg-gray-500'
    }
  }

  // Función para obtener icono según estado
  const getEstadoIcono = (estado: string) => {
    switch (estado) {
      case 'activo':
        return <Activity className="w-4 h-4" />
      case 'pausado':
        return <PauseCircle className="w-4 h-4" />
      case 'cancelado':
        return <XCircle className="w-4 h-4" />
      case 'completado':
        return <CheckCircle2 className="w-4 h-4" />
      default:
        return <Clock className="w-4 h-4" />
    }
  }

  // Función para mostrar notificación
  const mostrarNotificacion = (message: string, type: 'success' | 'error') => {
    setNotificacion({ message, type })
    setTimeout(() => {
      setNotificacion(null)
    }, 3000)
  }

  // Pausar proceso
  const handlePausar = async (procesoId: string) => {
    if (accionesEnProceso.has(procesoId)) return
    
    setAccionesEnProceso(prev => new Set(prev).add(procesoId))
    try {
      await api.pausarProceso(procesoId)
      mostrarNotificacion('⏸️ Proceso pausado', 'success')
      // Recargar monitoreo después de un breve delay
      setTimeout(() => {
        cargarMonitoreo()
      }, 500)
    } catch (error) {
      mostrarNotificacion(`❌ Error al pausar: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error')
    } finally {
      setAccionesEnProceso(prev => {
        const nuevo = new Set(prev)
        nuevo.delete(procesoId)
        return nuevo
      })
    }
  }

  // Reanudar proceso
  const handleReanudar = async (procesoId: string) => {
    if (accionesEnProceso.has(procesoId)) return
    
    setAccionesEnProceso(prev => new Set(prev).add(procesoId))
    try {
      await api.reanudarProceso(procesoId)
      mostrarNotificacion('▶️ Proceso reanudado', 'success')
      // Recargar monitoreo después de un breve delay
      setTimeout(() => {
        cargarMonitoreo()
      }, 500)
    } catch (error) {
      mostrarNotificacion(`❌ Error al reanudar: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error')
    } finally {
      setAccionesEnProceso(prev => {
        const nuevo = new Set(prev)
        nuevo.delete(procesoId)
        return nuevo
      })
    }
  }

  // Cancelar proceso
  const handleCancelar = async (procesoId: string) => {
    if (accionesEnProceso.has(procesoId)) return
    
    if (!confirm('¿Estás seguro de que deseas cancelar este proceso?')) {
      return
    }
    
    setAccionesEnProceso(prev => new Set(prev).add(procesoId))
    try {
      await api.cancelarProceso(procesoId)
      mostrarNotificacion('🛑 Proceso cancelado', 'success')
      // Recargar monitoreo después de un breve delay
      setTimeout(() => {
        cargarMonitoreo()
      }, 500)
    } catch (error) {
      mostrarNotificacion(`❌ Error al cancelar: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error')
    } finally {
      setAccionesEnProceso(prev => {
        const nuevo = new Set(prev)
        nuevo.delete(procesoId)
        return nuevo
      })
    }
  }

  if (loading && !monitoreo) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-orange-500" />
          <p className="text-gray-600 dark:text-gray-400">Cargando monitoreo...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
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
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  autoRefresh
                    ? 'bg-orange-500 text-white hover:bg-orange-600'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                }`}
              >
                {autoRefresh ? 'Auto-actualizar: ON' : 'Auto-actualizar: OFF'}
              </button>
              <button
                onClick={cargarMonitoreo}
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

      {/* Contenido */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Notificación */}
        {notificacion && (
          <div className={`mb-6 rounded-lg p-4 border ${
            notificacion.type === 'success'
              ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
              : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
          } animate-fade-in-up`}>
            <p className={notificacion.type === 'success' ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'}>
              {notificacion.message}
            </p>
          </div>
        )}

        {error && (
          <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        {monitoreo && (
          <>
            {/* Tarjetas de Resumen */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
              {/* Total Procesos */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Procesos</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                      {monitoreo.resumen.total_procesos}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                    <FileText className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  </div>
                </div>
              </div>

              {/* Activos */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Activos</p>
                    <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">
                      {monitoreo.resumen.activos}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                    <Activity className="w-6 h-6 text-green-600 dark:text-green-400" />
                  </div>
                </div>
              </div>

              {/* Pausados */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Pausados</p>
                    <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mt-2">
                      {monitoreo.resumen.pausados}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg flex items-center justify-center">
                    <PauseCircle className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                  </div>
                </div>
              </div>

              {/* Completados */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Completados</p>
                    <p className="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-2">
                      {monitoreo.resumen.completados}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                    <CheckCircle2 className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  </div>
                </div>
              </div>

              {/* Cancelados */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Cancelados</p>
                    <p className="text-3xl font-bold text-red-600 dark:text-red-400 mt-2">
                      {monitoreo.resumen.cancelados}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center">
                    <XCircle className="w-6 h-6 text-red-600 dark:text-red-400" />
                  </div>
                </div>
              </div>
            </div>

            {/* Estadísticas Generales */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Respuestas</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-white">
                      {monitoreo.estadisticas.total_respuestas.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg flex items-center justify-center">
                    <Activity className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Respuestas Procesadas</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-white">
                      {monitoreo.estadisticas.respuestas_procesadas.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-orange-100 dark:bg-orange-900/30 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Progreso Promedio</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-white">
                      {monitoreo.estadisticas.progreso_promedio.toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Lista de Procesos */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Procesos Activos ({monitoreo.procesos.length})
                </h2>
              </div>
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {monitoreo.procesos.length === 0 ? (
                  <div className="px-6 py-12 text-center">
                    <Activity className="w-12 h-12 mx-auto text-gray-400 dark:text-gray-500 mb-4" />
                    <p className="text-gray-500 dark:text-gray-400">No hay procesos activos</p>
                  </div>
                ) : (
                  monitoreo.procesos.map((proceso) => (
                    <div
                      key={proceso.proceso_id}
                      className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                    >
                      <div className="flex items-center justify-between gap-4">
                        <div className="flex items-center gap-4 flex-1">
                          {/* Estado */}
                          <div className={`w-3 h-3 rounded-full ${getEstadoColor(proceso.estado)}`} />
                          
                          {/* Info del proceso */}
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <div className="flex items-center gap-2">
                                {getEstadoIcono(proceso.estado)}
                                <span className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                                  {proceso.estado}
                                </span>
                              </div>
                              <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">
                                {proceso.proceso_id.substring(0, 8)}...
                              </span>
                            </div>
                            
                            {/* Progreso */}
                            <div className="mb-2">
                              <div className="flex items-center justify-between text-sm mb-1">
                                <span className="text-gray-600 dark:text-gray-400">Progreso</span>
                                <span className="font-medium text-gray-900 dark:text-white">
                                  {proceso.progreso_pct}%
                                </span>
                              </div>
                              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                <div
                                  className={`h-2 rounded-full transition-all ${
                                    proceso.estado === 'activo'
                                      ? 'bg-green-500'
                                      : proceso.estado === 'pausado'
                                      ? 'bg-yellow-500'
                                      : proceso.estado === 'completado'
                                      ? 'bg-blue-500'
                                      : 'bg-red-500'
                                  }`}
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
                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                              {proceso.mensaje}
                            </p>
                          </div>
                        </div>

                        {/* 🆕 Botones de Acción */}
                        {proceso.estado !== 'completado' && proceso.estado !== 'cancelado' && (
                          <div className="flex items-center gap-2">
                            {proceso.estado === 'pausado' ? (
                              <button
                                onClick={() => handleReanudar(proceso.proceso_id)}
                                disabled={accionesEnProceso.has(proceso.proceso_id)}
                                className="p-2 rounded-lg bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-900/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                title="Reanudar proceso"
                              >
                                {accionesEnProceso.has(proceso.proceso_id) ? (
                                  <RefreshCw className="w-4 h-4 animate-spin" />
                                ) : (
                                  <Play className="w-4 h-4" />
                                )}
                              </button>
                            ) : (
                              <button
                                onClick={() => handlePausar(proceso.proceso_id)}
                                disabled={accionesEnProceso.has(proceso.proceso_id)}
                                className="p-2 rounded-lg bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 hover:bg-yellow-200 dark:hover:bg-yellow-900/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                title="Pausar proceso"
                              >
                                {accionesEnProceso.has(proceso.proceso_id) ? (
                                  <RefreshCw className="w-4 h-4 animate-spin" />
                                ) : (
                                  <Pause className="w-4 h-4" />
                                )}
                              </button>
                            )}
                            <button
                              onClick={() => handleCancelar(proceso.proceso_id)}
                              disabled={accionesEnProceso.has(proceso.proceso_id)}
                              className="p-2 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                              title="Cancelar proceso"
                            >
                              {accionesEnProceso.has(proceso.proceso_id) ? (
                                <RefreshCw className="w-4 h-4 animate-spin" />
                              ) : (
                                <Trash2 className="w-4 h-4" />
                              )}
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  )
}

