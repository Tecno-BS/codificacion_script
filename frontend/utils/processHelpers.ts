/**
 * Utilidades para procesos del dashboard
 */
import { Activity, PauseCircle, XCircle, CheckCircle2, Clock } from 'lucide-react'
import type { ReactNode } from 'react'

export type EstadoProceso = 'activo' | 'pausado' | 'cancelado' | 'completado'

export function getEstadoColor(estado: string): string {
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

export function getEstadoIcono(estado: string): ReactNode {
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

export function getProgresoColor(estado: string): string {
  switch (estado) {
    case 'activo':
      return 'bg-green-500'
    case 'pausado':
      return 'bg-yellow-500'
    case 'completado':
      return 'bg-blue-500'
    default:
      return 'bg-red-500'
  }
}

