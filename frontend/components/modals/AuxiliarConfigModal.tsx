/**
 * Modal de configuración de datos auxiliares
 */
'use client'

import { X, XCircle, HelpCircle, CheckCircle2 } from 'lucide-react'
import type { CategorizacionAuxiliar } from '@/hooks/useAuxiliarData'

interface AuxiliarConfigModalProps {
  isOpen: boolean
  onClose: () => void
  datosAuxiliares: string[]
  categorizacionAuxiliar: CategorizacionAuxiliar
  onCategorizacionChange: (categorizacion: CategorizacionAuxiliar) => void
  onClearAll: () => void
}

export function AuxiliarConfigModal({
  isOpen,
  onClose,
  datosAuxiliares,
  categorizacionAuxiliar,
  onCategorizacionChange,
  onClearAll,
}: AuxiliarConfigModalProps) {
  if (!isOpen) return null

  const handleDrop = (
    categoria: 'negativas' | 'neutrales' | 'positivas',
    e: React.DragEvent<HTMLDivElement>
  ) => {
    e.preventDefault()
    e.currentTarget.classList.remove(
      categoria === 'negativas'
        ? 'bg-red-500/20'
        : categoria === 'neutrales'
        ? 'bg-gray-500/20'
        : 'bg-green-500/20'
    )
    const dato = e.dataTransfer.getData('text/plain')
    if (dato) {
      const newState = { ...categorizacionAuxiliar }
      // Remover de todas las categorías
      newState.negativas = newState.negativas.filter((d) => d !== dato)
      newState.neutrales = newState.neutrales.filter((d) => d !== dato)
      newState.positivas = newState.positivas.filter((d) => d !== dato)
      // Agregar a la categoría correspondiente si no está
      if (!newState[categoria].includes(dato)) {
        newState[categoria].push(dato)
      }
      onCategorizacionChange(newState)
    }
  }

  const handleDragOver = (
    categoria: 'negativas' | 'neutrales' | 'positivas',
    e: React.DragEvent<HTMLDivElement>
  ) => {
    e.preventDefault()
    e.currentTarget.classList.add(
      categoria === 'negativas'
        ? 'bg-red-500/20'
        : categoria === 'neutrales'
        ? 'bg-gray-500/20'
        : 'bg-green-500/20'
    )
  }

  const handleDragLeave = (
    categoria: 'negativas' | 'neutrales' | 'positivas',
    e: React.DragEvent<HTMLDivElement>
  ) => {
    e.currentTarget.classList.remove(
      categoria === 'negativas'
        ? 'bg-red-500/20'
        : categoria === 'neutrales'
        ? 'bg-gray-500/20'
        : 'bg-green-500/20'
    )
  }

  const datosSinCategorizar = datosAuxiliares.filter(
    (d) =>
      !categorizacionAuxiliar.negativas.includes(d) &&
      !categorizacionAuxiliar.neutrales.includes(d) &&
      !categorizacionAuxiliar.positivas.includes(d)
  )

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col border border-border">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h2 className="text-2xl font-bold text-primary">Configurar Datos Auxiliares</h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <p className="text-sm text-muted-foreground mb-6">
            Arrastra los datos auxiliares a su categoría correspondiente. Esto ayudará al modelo a generar códigos más
            precisos.
          </p>

          <div className="grid grid-cols-3 gap-4">
            {/* Negativas */}
            <div className="flex flex-col">
              <div className="bg-red-500/10 border-2 border-red-500 rounded-lg p-4 min-h-[200px]">
                <h3 className="font-semibold text-red-600 dark:text-red-400 mb-3 flex items-center gap-2">
                  <XCircle className="w-5 h-5" />
                  Negativas
                </h3>
                <div
                  onDragOver={(e) => handleDragOver('negativas', e)}
                  onDragLeave={(e) => handleDragLeave('negativas', e)}
                  onDrop={(e) => handleDrop('negativas', e)}
                  className="space-y-2 min-h-[150px]"
                >
                  {categorizacionAuxiliar.negativas.map((dato, idx) => (
                    <div
                      key={idx}
                      draggable
                      onDragStart={(e) => e.dataTransfer.setData('text/plain', dato)}
                      className="bg-red-500/20 border border-red-500 rounded p-2 text-sm cursor-move hover:bg-red-500/30 transition-colors"
                    >
                      {dato}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Neutrales */}
            <div className="flex flex-col">
              <div className="bg-gray-500/10 border-2 border-gray-500 rounded-lg p-4 min-h-[200px]">
                <h3 className="font-semibold text-gray-600 dark:text-gray-400 mb-3 flex items-center gap-2">
                  <HelpCircle className="w-5 h-5" />
                  Neutrales
                </h3>
                <div
                  onDragOver={(e) => handleDragOver('neutrales', e)}
                  onDragLeave={(e) => handleDragLeave('neutrales', e)}
                  onDrop={(e) => handleDrop('neutrales', e)}
                  className="space-y-2 min-h-[150px]"
                >
                  {categorizacionAuxiliar.neutrales.map((dato, idx) => (
                    <div
                      key={idx}
                      draggable
                      onDragStart={(e) => e.dataTransfer.setData('text/plain', dato)}
                      className="bg-gray-500/20 border border-gray-500 rounded p-2 text-sm cursor-move hover:bg-gray-500/30 transition-colors"
                    >
                      {dato}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Positivas */}
            <div className="flex flex-col">
              <div className="bg-green-500/10 border-2 border-green-500 rounded-lg p-4 min-h-[200px]">
                <h3 className="font-semibold text-green-600 dark:text-green-400 mb-3 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5" />
                  Positivas
                </h3>
                <div
                  onDragOver={(e) => handleDragOver('positivas', e)}
                  onDragLeave={(e) => handleDragLeave('positivas', e)}
                  onDrop={(e) => handleDrop('positivas', e)}
                  className="space-y-2 min-h-[150px]"
                >
                  {categorizacionAuxiliar.positivas.map((dato, idx) => (
                    <div
                      key={idx}
                      draggable
                      onDragStart={(e) => e.dataTransfer.setData('text/plain', dato)}
                      className="bg-green-500/20 border border-green-500 rounded p-2 text-sm cursor-move hover:bg-green-500/30 transition-colors"
                    >
                      {dato}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Lista de datos sin categorizar */}
          <div className="mt-6">
            <h3 className="font-semibold mb-3 text-muted-foreground">Datos sin categorizar</h3>
            <div className="flex flex-wrap gap-2 p-4 bg-muted/50 rounded-lg min-h-[100px]">
              {datosSinCategorizar.map((dato, idx) => (
                <div
                  key={idx}
                  draggable
                  onDragStart={(e) => e.dataTransfer.setData('text/plain', dato)}
                  className="bg-background border border-border rounded px-3 py-2 text-sm cursor-move hover:bg-muted transition-colors"
                >
                  {dato}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-4 p-6 border-t border-border">
          <button
            onClick={onClearAll}
            className="px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Limpiar todo
          </button>
          <button
            onClick={onClose}
            className="px-6 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-semibold transition-colors"
          >
            Guardar y Cerrar
          </button>
        </div>
      </div>
    </div>
  )
}

