/**
 * Hook para manejar acciones de procesos (pausar, reanudar, cancelar)
 */
import { useState, useCallback } from 'react'
import * as api from '@/lib/api'

export function useProcessActions(onSuccess?: () => void) {
  const [accionesEnProceso, setAccionesEnProceso] = useState<Set<string>>(new Set())

  const ejecutarAccion = useCallback(
    async (procesoId: string, accion: () => Promise<void>) => {
      if (accionesEnProceso.has(procesoId)) return

      setAccionesEnProceso((prev) => new Set(prev).add(procesoId))
      try {
        await accion()
        if (onSuccess) {
          setTimeout(() => {
            onSuccess()
          }, 500)
        }
      } finally {
        setAccionesEnProceso((prev) => {
          const nuevo = new Set(prev)
          nuevo.delete(procesoId)
          return nuevo
        })
      }
    },
    [accionesEnProceso, onSuccess]
  )

  const pausar = useCallback(
    async (procesoId: string) => {
      await ejecutarAccion(procesoId, () => api.pausarProceso(procesoId))
    },
    [ejecutarAccion]
  )

  const reanudar = useCallback(
    async (procesoId: string) => {
      await ejecutarAccion(procesoId, () => api.reanudarProceso(procesoId))
    },
    [ejecutarAccion]
  )

  const cancelar = useCallback(
    async (procesoId: string) => {
      if (!confirm('¿Estás seguro de que deseas cancelar este proceso?')) {
        return
      }
      await ejecutarAccion(procesoId, () => api.cancelarProceso(procesoId))
    },
    [ejecutarAccion]
  )

  return {
    accionesEnProceso,
    pausar,
    reanudar,
    cancelar,
  }
}

