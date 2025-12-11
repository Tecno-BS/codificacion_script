/**
 * Modal de ayuda sobre formato de archivos
 */
'use client'

import { X, HelpCircle, FileSpreadsheet, ListOrdered } from 'lucide-react'

interface HelpModalProps {
  isOpen: boolean
  onClose: () => void
}

export function HelpModal({ isOpen, onClose }: HelpModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in-up p-4">
      <div className="bg-background border-2 border-orange-500 rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto animate-fade-in-up">
        {/* Header del Modal */}
        <div className="sticky top-0 bg-gradient-to-r from-orange-600 to-orange-500 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <HelpCircle className="w-7 h-7 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">Ayuda - Formato de Archivos</h2>
                <p className="text-orange-100 text-sm">Guía para preparar tus archivos Excel</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <X className="w-6 h-6 text-white" />
            </button>
          </div>
        </div>

        {/* Contenido del Modal */}
        <div className="p-6 space-y-6">
          {/* Archivo de Respuestas */}
          <div className="border border-border rounded-xl p-5 bg-gradient-to-br from-orange-50 to-white dark:from-orange-900/10 dark:to-background">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center">
                <FileSpreadsheet className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-foreground">1. Archivo de Respuestas (Obligatorio)</h3>
            </div>

            <div className="space-y-3 ml-13">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-border">
                <p className="text-sm font-semibold text-orange-600 dark:text-orange-400 mb-2">
                  📋 Estructura requerida:
                </p>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="text-orange-500 font-bold">•</span>
                    <span>
                      <strong className="text-foreground">Columna 1 (ID):</strong> Identificador único de cada
                      respuesta
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-orange-500 font-bold">•</span>
                    <span>
                      <strong className="text-foreground">Columna 2 en adelante:</strong> Las preguntas con sus
                      respuestas
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-orange-500 font-bold">•</span>
                    <span>
                      <strong className="text-foreground">Encabezados:</strong> Los nombres de las columnas serán
                      usados como nombres de preguntas
                    </span>
                  </li>
                </ul>
              </div>

              <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
                <p className="text-sm font-semibold text-green-700 dark:text-green-400 mb-2">
                  ✅ Ejemplo correcto:
                </p>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs border-collapse">
                    <thead>
                      <tr className="bg-green-100 dark:bg-green-900/40">
                        <th className="border border-green-300 dark:border-green-700 px-2 py-1">ID</th>
                        <th className="border border-green-300 dark:border-green-700 px-2 py-1">
                          2. ¿Por qué seleccionó esta imagen?
                        </th>
                        <th className="border border-green-300 dark:border-green-700 px-2 py-1">
                          5. ¿Qué le transmite?
                        </th>
                      </tr>
                    </thead>
                    <tbody className="text-muted-foreground">
                      <tr>
                        <td className="border border-green-300 dark:border-green-700 px-2 py-1">1</td>
                        <td className="border border-green-300 dark:border-green-700 px-2 py-1">Me gusta el color</td>
                        <td className="border border-green-300 dark:border-green-700 px-2 py-1">
                          Alegría y felicidad
                        </td>
                      </tr>
                      <tr>
                        <td className="border border-green-300 dark:border-green-700 px-2 py-1">2</td>
                        <td className="border border-green-300 dark:border-green-700 px-2 py-1">
                          Es la más llamativa
                        </td>
                        <td className="border border-green-300 dark:border-green-700 px-2 py-1">Energía positiva</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          {/* Archivo de Códigos Anteriores */}
          <div className="border border-border rounded-xl p-5 bg-gradient-to-br from-blue-50 to-white dark:from-blue-900/10 dark:to-background">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                <ListOrdered className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-foreground">2. Archivo de Códigos Anteriores (Opcional)</h3>
            </div>

            <div className="space-y-3 ml-13">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-border">
                <p className="text-sm font-semibold text-blue-600 dark:text-blue-400 mb-2">
                  📚 Estructura requerida:
                </p>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="text-blue-500 font-bold">•</span>
                    <span>
                      <strong className="text-foreground">Hojas múltiples:</strong> Una hoja por cada pregunta
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-500 font-bold">•</span>
                    <span>
                      <strong className="text-foreground">Nombre de hoja:</strong> Debe coincidir con el nombre de la
                      columna en el archivo de respuestas
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-500 font-bold">•</span>
                    <span>
                      <strong className="text-foreground">Columnas requeridas:</strong>
                    </span>
                  </li>
                  <ul className="ml-6 space-y-1 mt-1">
                    <li className="text-xs">
                      - <strong className="text-foreground">COD:</strong> Código del catálogo
                    </li>
                    <li className="text-xs">
                      - <strong className="text-foreground">TEXTO:</strong> Descripción del código
                    </li>
                  </ul>
                </ul>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
                <p className="text-sm font-semibold text-blue-700 dark:text-blue-400 mb-2">💡 Ejemplo de hoja:</p>
                <p className="text-xs text-muted-foreground mb-2">Hoja: "2. ¿Por qué seleccionó esta imagen?"</p>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs border-collapse">
                    <thead>
                      <tr className="bg-blue-100 dark:bg-blue-900/40">
                        <th className="border border-blue-300 dark:border-blue-700 px-2 py-1">COD</th>
                        <th className="border border-blue-300 dark:border-blue-700 px-2 py-1">TEXTO</th>
                      </tr>
                    </thead>
                    <tbody className="text-muted-foreground">
                      <tr>
                        <td className="border border-blue-300 dark:border-blue-700 px-2 py-1">1</td>
                        <td className="border border-blue-300 dark:border-blue-700 px-2 py-1">Color atractivo</td>
                      </tr>
                      <tr>
                        <td className="border border-blue-300 dark:border-blue-700 px-2 py-1">2</td>
                        <td className="border border-blue-300 dark:border-blue-700 px-2 py-1">Diseño llamativo</td>
                      </tr>
                      <tr>
                        <td className="border border-blue-300 dark:border-blue-700 px-2 py-1">3</td>
                        <td className="border border-blue-300 dark:border-blue-700 px-2 py-1">Mensaje claro</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3 border border-yellow-200 dark:border-yellow-800">
                <p className="text-xs text-yellow-800 dark:text-yellow-400">
                  <strong>⚠️ Nota:</strong> Si no proporcionas códigos anteriores, el sistema generará códigos nuevos
                  automáticamente.
                </p>
              </div>
            </div>
          </div>

          {/* Tips adicionales */}
          <div className="border border-border rounded-xl p-5 bg-gradient-to-br from-purple-50 to-white dark:from-purple-900/10 dark:to-background">
            <h3 className="text-lg font-bold text-foreground mb-3">💡 Tips Adicionales</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="flex items-start gap-2">
                <span className="text-purple-500 font-bold text-lg">•</span>
                <span>
                  Los archivos deben estar en formato <strong className="text-foreground">.xlsx</strong> o{' '}
                  <strong className="text-foreground">.xls</strong>
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-500 font-bold text-lg">•</span>
                <span>Asegúrate de que las respuestas no tengan celdas vacías en la columna ID</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-500 font-bold text-lg">•</span>
                <span>
                  Los nombres de las hojas en el archivo de códigos deben coincidir{' '}
                  <strong className="text-foreground">exactamente</strong> con los nombres de las columnas
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-500 font-bold text-lg">•</span>
                <span>Si una pregunta no tiene catálogo, el sistema generará códigos nuevos automáticamente</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Footer del Modal */}
        <div className="border-t border-border p-4 bg-muted/30">
          <button
            onClick={onClose}
            className="w-full bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-700 hover:to-orange-600 text-white px-6 py-3 rounded-xl font-semibold transition-all transform hover:scale-105 active:scale-95 shadow-lg"
          >
            Entendido
          </button>
        </div>
      </div>
    </div>
  )
}

