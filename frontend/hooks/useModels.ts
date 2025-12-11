/**
 * Hook para manejar los modelos disponibles
 */
import { useState, useEffect } from 'react'
import * as api from '@/lib/api'
import { BACKEND_URL, DEFAULT_MODEL } from '@/utils/constants'

export function useModels() {
  const [availableModels, setAvailableModels] = useState<api.ModeloGPT[]>([])
  const [selectedModel, setSelectedModel] = useState(DEFAULT_MODEL)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadModels = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/v1/modelos`)

        if (response.ok) {
          const data = await response.json()
          setAvailableModels(data.modelos)

          // Seleccionar el modelo recomendado por defecto
          const recommended = data.modelos.find((m: api.ModeloGPT) => m.recomendado)
          if (recommended) {
            setSelectedModel(recommended.id)
          }
        } else {
          throw new Error('Error al cargar modelos')
        }
      } catch (error) {
        console.error('Error cargando modelos:', error)
        // Usar modelos por defecto
        setAvailableModels([
          { id: 'gpt-4o-mini', nombre: 'GPT-4o Mini', recomendado: true },
          { id: 'gpt-4o', nombre: 'GPT-4o' },
          { id: 'gpt-5', nombre: 'GPT-5' },
        ])
      } finally {
        setLoading(false)
      }
    }

    if (typeof window !== 'undefined') {
      loadModels()
    }
  }, [])

  return {
    availableModels,
    selectedModel,
    setSelectedModel,
    loading,
  }
}

