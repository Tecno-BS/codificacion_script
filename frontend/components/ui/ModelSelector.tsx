/**
 * Componente selector de modelo
 */
'use client'

import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import type { ModeloGPT } from '@/lib/api'

interface ModelSelectorProps {
  models: ModeloGPT[]
  selectedModel: string
  onModelChange: (modelId: string) => void
  onNotification?: (message: string, type?: 'success' | 'info' | 'warning') => void
}

export function ModelSelector({
  models,
  selectedModel,
  onModelChange,
  onNotification,
}: ModelSelectorProps) {
  const [showDropdown, setShowDropdown] = useState(false)

  const handleModelSelect = (modelId: string) => {
    const model = models.find((m) => m.id === modelId)
    onModelChange(modelId)
    setShowDropdown(false)
    if (onNotification && model) {
      onNotification(`✅ Modelo cambiado a ${model.nombre}`, 'success')
    }
  }

  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="px-3 py-2 rounded-lg bg-muted hover:bg-muted/80 text-foreground text-sm font-medium flex items-center gap-2 transition-all border border-border shadow-sm"
      >
        <span className="text-xs">Modelo:</span>
        <span className="text-primary font-semibold">{selectedModel}</span>
        <ChevronDown className="w-4 h-4" />
      </button>
      {showDropdown && (
        <div className="absolute top-full right-0 mt-2 bg-card border border-border rounded-lg shadow-xl z-10 min-w-[180px] animate-fade-in-up">
          {models.map((model) => (
            <button
              key={model.id}
              onClick={() => handleModelSelect(model.id)}
              className={`block w-full text-left px-4 py-2 text-sm transition-colors ${
                selectedModel === model.id
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-muted text-foreground'
              }`}
            >
              {model.nombre}
              {model.recomendado && <span className="ml-2 text-xs">⭐</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

