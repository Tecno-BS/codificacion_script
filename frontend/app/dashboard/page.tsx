'use client'

import { useState } from 'react'
import { useMonitoring } from '@/hooks/useMonitoring'
import { useProcessActions } from '@/hooks/useProcessActions'
import { DashboardHeader } from '@/components/dashboard/DashboardHeader'
import { LoadingState } from '@/components/dashboard/LoadingState'
import { NotificationBanner } from '@/components/dashboard/NotificationBanner'
import { ErrorDisplay } from '@/components/dashboard/ErrorDisplay'
import { SummaryCards } from '@/components/dashboard/SummaryCards'
import { StatsCards } from '@/components/dashboard/StatsCards'
import { ProcessList } from '@/components/dashboard/ProcessList'

export default function DashboardPage() {
  const { monitoreo, loading, error, autoRefresh, setAutoRefresh, lastUpdate, cargarMonitoreo } = useMonitoring()
  const { accionesEnProceso, pausar, reanudar, cancelar } = useProcessActions(cargarMonitoreo)
  const [notificacion, setNotificacion] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  const mostrarNotificacion = (message: string, type: 'success' | 'error') => {
    setNotificacion({ message, type })
    setTimeout(() => {
      setNotificacion(null)
    }, 3000)
  }

  const handlePausar = async (procesoId: string) => {
    try {
      await pausar(procesoId)
      mostrarNotificacion('⏸️ Proceso pausado', 'success')
    } catch (error) {
      mostrarNotificacion(
        `❌ Error al pausar: ${error instanceof Error ? error.message : 'Error desconocido'}`,
        'error'
      )
    }
  }

  const handleReanudar = async (procesoId: string) => {
    try {
      await reanudar(procesoId)
      mostrarNotificacion('▶️ Proceso reanudado', 'success')
    } catch (error) {
      mostrarNotificacion(
        `❌ Error al reanudar: ${error instanceof Error ? error.message : 'Error desconocido'}`,
        'error'
      )
    }
  }

  const handleCancelar = async (procesoId: string) => {
    try {
      await cancelar(procesoId)
      mostrarNotificacion('🛑 Proceso cancelado', 'success')
    } catch (error) {
      mostrarNotificacion(
        `❌ Error al cancelar: ${error instanceof Error ? error.message : 'Error desconocido'}`,
        'error'
      )
    }
  }

  if (loading && !monitoreo) {
    return <LoadingState />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <DashboardHeader
        autoRefresh={autoRefresh}
        onToggleAutoRefresh={() => setAutoRefresh(!autoRefresh)}
        loading={loading}
        onRefresh={cargarMonitoreo}
        lastUpdate={lastUpdate}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {notificacion && <NotificationBanner message={notificacion.message} type={notificacion.type} />}
        {error && <ErrorDisplay error={error} />}

        {monitoreo && (
          <>
            <SummaryCards resumen={monitoreo.resumen} />
            <StatsCards estadisticas={monitoreo.estadisticas} />
            <ProcessList
              procesos={monitoreo.procesos}
              accionesEnProceso={accionesEnProceso}
              onPausar={handlePausar}
              onReanudar={handleReanudar}
              onCancelar={handleCancelar}
            />
          </>
        )}
      </main>
    </div>
  )
}
