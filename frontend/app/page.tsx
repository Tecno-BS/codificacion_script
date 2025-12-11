'use client'

import { useState } from 'react'
import { Sparkles, Settings, AlertCircle } from 'lucide-react'
import * as api from '@/lib/api'
import { useDarkMode } from '@/hooks/useDarkMode'
import { useNotifications } from '@/hooks/useNotifications'
import { useBackendStatus } from '@/hooks/useBackendStatus'
import { useModels } from '@/hooks/useModels'
import { useFileUpload } from '@/hooks/useFileUpload'
import { useAuxiliarData } from '@/hooks/useAuxiliarData'
import { useCodification } from '@/hooks/useCodification'
import { Header } from '@/components/layout/Header'
import { Footer } from '@/components/layout/Footer'
import { Notification } from '@/components/ui/Notification'
import { FileUpload } from '@/components/ui/FileUpload'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { HelpModal } from '@/components/modals/HelpModal'
import { AuxiliarConfigModal } from '@/components/modals/AuxiliarConfigModal'
import { ResultsSection } from '@/components/results/ResultsSection'

export default function Page() {
  // Hooks
  const { darkMode, toggleDarkMode } = useDarkMode()
  const { notification, isLeaving, showNotification, showDelayedNotification } = useNotifications(true)
  const { status: backendStatus } = useBackendStatus()
  const { availableModels, selectedModel, setSelectedModel } = useModels()
  const { files, handleFileUpload, resetFiles } = useFileUpload()
  const {
    usarDatoAuxiliar,
    setUsarDatoAuxiliar,
    showConfigAuxiliar,
    setShowConfigAuxiliar,
    datosAuxiliares,
    setDatosAuxiliares,
    categorizacionAuxiliar,
    setCategorizacionAuxiliar,
    hayDatosAuxiliaresPendientes,
    resetAuxiliarData,
  } = useAuxiliarData()
  const {
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
    reset: resetCodification,
  } = useCodification()

  // UI State
  const [showHelp, setShowHelp] = useState(false)
  const [notifications, setNotifications] = useState(true)

  // Manejar carga de archivos
  const handleFileUploadWithExtraction = async (index: number, uploadedFile: File | null) => {
    const file = handleFileUpload(index, uploadedFile)

    if (file && index === 0) {
      // Si es el archivo de respuestas, extraer datos auxiliares
      try {
        const resultado = await api.extraerDatosAuxiliares(file)
        console.log('📊 Resultado de extraer datos auxiliares:', resultado)

        // Verificar que el resultado tenga la estructura correcta
        if (resultado && resultado.datos_auxiliares && Array.isArray(resultado.datos_auxiliares)) {
          setDatosAuxiliares(resultado.datos_auxiliares)

          // Inicializar categorización vacía
          setCategorizacionAuxiliar({
            negativas: [],
            neutrales: [],
            positivas: [],
          })

          showNotification(
            `✅ ${files[index].name} cargado. ${resultado.total || resultado.datos_auxiliares.length} datos auxiliares encontrados`,
            'success'
          )
        } else {
          console.error('❌ Formato de respuesta incorrecto:', resultado)
          showNotification(`✅ ${files[index].name} cargado`, 'success')
        }
      } catch (error) {
        console.error('Error al extraer datos auxiliares:', error)
        showNotification(`✅ ${files[index].name} cargado`, 'success')
      }
    } else if (file) {
      showNotification(`✅ ${files[index].name} cargado`, 'success')
    }
  }

  // Ejecutar codificación
  const handleExecuteCodification = async () => {
    if (!files[0].file) {
      showNotification('❌ Por favor, carga el archivo de respuestas', 'warning')
      return
    }

    if (backendStatus === 'offline') {
      showNotification('❌ Backend no disponible', 'warning')
      return
    }

    // Validar configuración de dato auxiliar si está activado
    if (usarDatoAuxiliar) {
      const totalCategorizados =
        categorizacionAuxiliar.negativas.length +
        categorizacionAuxiliar.neutrales.length +
        categorizacionAuxiliar.positivas.length

      if (totalCategorizados === 0) {
        showNotification('❌ Por favor, categoriza al menos un dato auxiliar', 'warning')
        return
      }
    }

    try {
      await executeCodification(
        files[0].file!,
        files[1].file,
        selectedModel,
        usarDatoAuxiliar
          ? {
              usar: true,
              categorizacion: categorizacionAuxiliar,
            }
          : undefined,
        (response) => {
          showNotification(`🎉 ${response.mensaje}`, 'success')
        },
        (error) => {
          showNotification(`❌ Error: ${error.message}`, 'warning')
        }
      )
    } catch (error) {
      showNotification(`❌ Error: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'warning')
    }
  }

  // Pausar/Reanudar proceso
  const handleTogglePausa = async () => {
    try {
      await togglePausa()
      showNotification(pausado ? '▶️ Proceso reanudado' : '⏸️ Proceso pausado', 'info')
    } catch (error) {
      showNotification(
        `❌ Error al ${pausado ? 'reanudar' : 'pausar'}: ${error instanceof Error ? error.message : 'Error desconocido'}`,
        'warning'
      )
    }
  }

  // Cancelar proceso
  const handleCancelar = async () => {
    try {
      await cancelar()
      showNotification('🛑 Codificación cancelada', 'warning')
    } catch (error) {
      showNotification(`❌ Error al cancelar: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'warning')
    }
  }

  // Reiniciar
  const handleReset = () => {
    resetFiles()
    resetAuxiliarData()
    resetCodification()
    showNotification('🔄 Listo para una nueva codificación', 'info')
  }

  // Toggle notificaciones
  const handleToggleNotifications = () => {
    const nuevoEstado = !notifications
    setNotifications(nuevoEstado)

    if (nuevoEstado) {
      showDelayedNotification('🔔 Notificaciones activadas', 0)
    } else {
      showDelayedNotification('🔕 Notificaciones desactivadas', 0)
    }
  }

  return (
    <div className={`min-h-screen transition-colors duration-300 ${darkMode ? 'dark' : ''}`}>
      <Header
        darkMode={darkMode}
        onToggleDarkMode={toggleDarkMode}
        notifications={notifications}
        onToggleNotifications={handleToggleNotifications}
        backendStatus={backendStatus}
        availableModels={availableModels}
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
        onNotification={showNotification}
        onShowHelp={() => setShowHelp(true)}
      />

      <Notification notification={notification} isLeaving={isLeaving} />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        {!results ? (
          <>
            {/* Hero Section */}
            <div className="text-center mb-12 animate-fade-in-up">
              <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">
                Codificador <span className="text-orange-600 dark:text-orange-400">de preguntas abiertas</span>
              </h2>
              <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                Sube tus archivos Excel y deja que nuestro modelo de IA analice automáticamente tus respuestas
              </p>
            </div>

            {/* Upload Section */}
            <div className="space-y-6 mb-12">
              {/* Opción de Dato Auxiliar encima de Respuestas (solo cuando hay archivo de respuestas) */}
              {files[0].file && (
                <div className="w-full md:w-1/2">
                  <div className="flex items-center gap-3 rounded-lg py-2">
                    <input
                      type="checkbox"
                      id="usar-dato-auxiliar"
                      checked={usarDatoAuxiliar}
                      onChange={(e) => {
                        setUsarDatoAuxiliar(e.target.checked)
                        if (e.target.checked && datosAuxiliares.length > 0) {
                          // Si se activa y hay datos, abrir configuración
                          setShowConfigAuxiliar(true)
                        }
                      }}
                      className="w-5 h-5 text-orange-600 rounded focus:ring-orange-500"
                    />
                    <label htmlFor="usar-dato-auxiliar" className="text-sm font-medium cursor-pointer">
                      Dato auxiliar
                    </label>
                    {usarDatoAuxiliar && (
                      <button
                        onClick={() => setShowConfigAuxiliar(true)}
                        className="ml-1 px-2 py-1.5 bg-orange-500 hover:bg-orange-600 text-white text-sm rounded-lg flex items-center gap-2 transition-all"
                      >
                        <Settings className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              )}

              <div className="grid md:grid-cols-2 gap-8">
                {files.map((file, index) => (
                  <FileUpload
                    key={index}
                    file={file}
                    index={index}
                    onFileUpload={handleFileUploadWithExtraction}
                    animationDelay={index * 100}
                  />
                ))}
              </div>
            </div>

            {/* Error Display */}
            {processing.error && (
              <div className="mb-8 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 flex items-start gap-3 animate-fade-in-up">
                <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-red-900 dark:text-red-100 mb-1">Error en la codificación</p>
                  <p className="text-sm text-red-700 dark:text-red-300">{processing.error}</p>
                </div>
              </div>
            )}

            {/* Progress Bar */}
            <ProgressBar
              processing={processing}
              pausado={pausado}
              batchActual={batchActual}
              totalBatches={totalBatches}
              respuestasProcesadas={respuestasProcesadas}
              totalRespuestasProceso={totalRespuestasProceso}
              procesoId={procesoId}
              onTogglePausa={handleTogglePausa}
              onCancelar={handleCancelar}
            />

            {/* Action Buttons */}
            <div className="flex gap-4 justify-center animate-fade-in-up" style={{ animationDelay: '200ms' }}>
              <button
                onClick={handleExecuteCodification}
                disabled={
                  !files[0].file ||
                  processing.loading ||
                  backendStatus === 'offline' ||
                  hayDatosAuxiliaresPendientes
                }
                className="relative overflow-hidden bg-gradient-to-r from-orange-600 via-orange-500 to-orange-600 hover:from-orange-700 hover:via-orange-600 hover:to-orange-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-8 py-4 rounded-xl font-semibold flex items-center gap-2 transition-all transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl hover:shadow-orange-500/50"
              >
                <Sparkles className="w-5 h-5" />
                Codificar con IA
              </button>
            </div>
          </>
        ) : (
          <ResultsSection results={results} onReset={handleReset} onNotification={showNotification} />
        )}
      </main>

      <Footer />

      {/* Modals */}
      <HelpModal isOpen={showHelp} onClose={() => setShowHelp(false)} />

      <AuxiliarConfigModal
        isOpen={showConfigAuxiliar}
        onClose={() => setShowConfigAuxiliar(false)}
        datosAuxiliares={datosAuxiliares}
        categorizacionAuxiliar={categorizacionAuxiliar}
        onCategorizacionChange={setCategorizacionAuxiliar}
        onClearAll={() =>
          setCategorizacionAuxiliar({
            negativas: [],
            neutrales: [],
            positivas: [],
          })
        }
      />
    </div>
  )
}
