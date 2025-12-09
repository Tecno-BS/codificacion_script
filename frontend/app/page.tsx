"use client"

import { useState, useEffect } from "react"
import { Upload, Sparkles, Download, RotateCcw, Settings, Bell, Moon, Sun, ChevronDown, AlertCircle, CheckCircle2, Play, Pause, XCircle, HelpCircle, X, FileSpreadsheet, ListOrdered, Activity } from "lucide-react"
import Link from "next/link"
import * as api from "@/lib/api"
import type { FileData, ProcessingState, ResultsData } from "@/types"

export default function Page() {
  // Estado de archivos
  const [files, setFiles] = useState<FileData[]>([
    { name: "Respuestas", file: null },
    { name: "Códigos Anteriores (opcional)", file: null },
  ])
  
  // Estado de procesamiento
  const [processing, setProcessing] = useState<ProcessingState>({
    loading: false,
    progress: 0,
    message: "",
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
  
  // UI State
  const [darkMode, setDarkMode] = useState(false)
  const [showOptions, setShowOptions] = useState(false)
  const [notifications, setNotifications] = useState(true)
  const [selectedModel, setSelectedModel] = useState("gpt-5")
  const [showModelDropdown, setShowModelDropdown] = useState(false)
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'info' | 'warning' } | null>(null)
  const [isNotificationLeaving, setIsNotificationLeaving] = useState(false)
  const [showHelp, setShowHelp] = useState(false)
  
  // Modelos disponibles
  const [availableModels, setAvailableModels] = useState<api.ModeloGPT[]>([])
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking")
  
  // 🆕 Estado para dato auxiliar
  const [usarDatoAuxiliar, setUsarDatoAuxiliar] = useState(false)
  const [showConfigAuxiliar, setShowConfigAuxiliar] = useState(false)
  const [datosAuxiliares, setDatosAuxiliares] = useState<string[]>([])
  const [categorizacionAuxiliar, setCategorizacionAuxiliar] = useState<{
    negativas: string[]
    neutrales: string[]
    positivas: string[]
  }>({
    negativas: [],
    neutrales: [],
    positivas: [],
  })

  // 🆕 Helper: verificar si hay datos auxiliares sin categorizar
  const hayDatosAuxiliaresPendientes = usarDatoAuxiliar && datosAuxiliares.some(
    (d) =>
      !categorizacionAuxiliar.negativas.includes(d) &&
      !categorizacionAuxiliar.neutrales.includes(d) &&
      !categorizacionAuxiliar.positivas.includes(d)
  )

  // Cargar modelos y verificar backend al montar (solo en el cliente)
  useEffect(() => {
    // Asegurar que solo se ejecute en el cliente
    if (typeof window !== 'undefined') {
      checkBackendStatus()
      loadModels()
      
      // 🆕 MEJORA: Reconexión automática si hay un proceso en curso
      const procesoIdGuardado = localStorage.getItem('proceso_activo_id')
      if (procesoIdGuardado) {
        reconectarProceso(procesoIdGuardado)
      }
    }
  }, [])

  // Dark mode
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }, [darkMode])

  // Verificar estado del backend
  const checkBackendStatus = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/health`)
      if (response.ok) {
      setBackendStatus("online")
      } else {
        setBackendStatus("offline")
      }
    } catch (error) {
      console.error("Error conectando al backend:", error)
      setBackendStatus("offline")
    }
  }

  // Cargar modelos disponibles
  const loadModels = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/v1/modelos`)
      
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
      console.error("Error cargando modelos:", error)
      // Usar modelos por defecto
      setAvailableModels([
        { id: "gpt-5", nombre: "GPT-5", recomendado: true },
        { id: "gpt-4o", nombre: "GPT-4o" },
        { id: "gpt-4o-mini", nombre: "GPT-4o Mini" },
      ])
    }
  }

  // Reproducir sonido de notificación
  const playNotificationSound = (type: 'success' | 'info' | 'warning') => {
    try {
      // Solo reproducir si las notificaciones están activadas
      if (!notifications) return

      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      const oscillator = audioContext.createOscillator()
      const gainNode = audioContext.createGain()

      oscillator.connect(gainNode)
      gainNode.connect(audioContext.destination)

      // Configurar sonidos diferentes según el tipo
      if (type === 'success') {
        // Sonido ascendente alegre para éxito (Do - Mi - Sol)
        oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime) // C5
        oscillator.frequency.setValueAtTime(659.25, audioContext.currentTime + 0.1) // E5
        oscillator.frequency.setValueAtTime(783.99, audioContext.currentTime + 0.2) // G5
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3)
      } else if (type === 'warning') {
        // Sonido descendente para advertencia
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime)
        oscillator.frequency.setValueAtTime(400, audioContext.currentTime + 0.15)
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.25)
      } else {
        // Sonido simple para info (un solo tono)
        oscillator.frequency.setValueAtTime(600, audioContext.currentTime)
        gainNode.gain.setValueAtTime(0.2, audioContext.currentTime)
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2)
      }

      oscillator.type = 'sine'
      oscillator.start(audioContext.currentTime)
      oscillator.stop(audioContext.currentTime + 0.3)
    } catch (error) {
      console.error('Error al reproducir sonido:', error)
    }
  }

  // Mostrar notificación
  const showNotificationMessage = (message: string, force: boolean = false, type: 'success' | 'info' | 'warning' = 'info') => {
    if (notifications || force) {
      // Reproducir sonido
      playNotificationSound(type)
      
      setIsNotificationLeaving(false)
      setNotification({ message, type })
      
      // Después de 2.6s, iniciar animación de salida
      setTimeout(() => {
        setIsNotificationLeaving(true)
        // Después de 0.4s (duración de animación), remover notificación
        setTimeout(() => {
          setNotification(null)
          setIsNotificationLeaving(false)
        }, 400)
      }, 2600)
    }
  }

  // Mostrar notificación con delay
  const showDelayedNotification = (message: string, delay: number = 0) => {
    setTimeout(() => {
      // Reproducir sonido
      playNotificationSound('info')
      
      setIsNotificationLeaving(false)
      setNotification({ message, type: 'info' })
      
      // Después de 2.6s, iniciar animación de salida
      setTimeout(() => {
        setIsNotificationLeaving(true)
        // Después de 0.4s (duración de animación), remover notificación
        setTimeout(() => {
          setNotification(null)
          setIsNotificationLeaving(false)
        }, 400)
      }, 2600)
    }, delay)
  }

  // Manejar carga de archivos
  const handleFileUpload = async (index: number, uploadedFile: File | null) => {
    const newFiles = [...files]
    newFiles[index].file = uploadedFile
    setFiles(newFiles)
    
      if (uploadedFile && index === 0) {
      // Si es el archivo de respuestas, extraer datos auxiliares
      try {
        const resultado = await api.extraerDatosAuxiliares(uploadedFile)
        console.log("📊 Resultado de extraer datos auxiliares:", resultado)
        
        // Verificar que el resultado tenga la estructura correcta
        if (resultado && resultado.datos_auxiliares && Array.isArray(resultado.datos_auxiliares)) {
          setDatosAuxiliares(resultado.datos_auxiliares)
          
          // Inicializar categorización vacía
          setCategorizacionAuxiliar({
            negativas: [],
            neutrales: [],
            positivas: [],
          })
          
          showNotificationMessage(`✅ ${files[index].name} cargado. ${resultado.total || resultado.datos_auxiliares.length} datos auxiliares encontrados`, false, 'success')
        } else {
          console.error("❌ Formato de respuesta incorrecto:", resultado)
          showNotificationMessage(`✅ ${files[index].name} cargado`, false, 'success')
        }
      } catch (error) {
        console.error("Error al extraer datos auxiliares:", error)
        showNotificationMessage(`✅ ${files[index].name} cargado`, false, 'success')
      }
    } else if (uploadedFile) {
      showNotificationMessage(`✅ ${files[index].name} cargado`, false, 'success')
    }
  }

  // Ejecutar codificación
  const executeCodification = async () => {
    if (!files[0].file) {
      showNotificationMessage("❌ Por favor, carga el archivo de respuestas", false, 'warning')
      return
    }

    if (backendStatus === "offline") {
      showNotificationMessage("❌ Backend no disponible", false, 'warning')
      return
    }

    // Resetear estado
    setProcessing({
      loading: true,
      progress: 0,
      message: "📤 Subiendo archivos...",
      error: null,
    })

    setBatchActual(0)
    setTotalBatches(0)
    setRespuestasProcesadas(0)
    setTotalRespuestasProceso(0)
    setPausado(false)

    try {
      // Validar configuración de dato auxiliar si está activado
      if (usarDatoAuxiliar) {
        const totalCategorizados = 
          categorizacionAuxiliar.negativas.length +
          categorizacionAuxiliar.neutrales.length +
          categorizacionAuxiliar.positivas.length
        
        if (totalCategorizados === 0) {
          showNotificationMessage("❌ Por favor, categoriza al menos un dato auxiliar", false, 'warning')
          return
        }
      }

      // Llamar al backend para iniciar codificación
      const response = await api.codificarRespuestas(
        files[0].file,
        files[1].file,
        selectedModel,
        undefined, // onProgress se maneja con SSE
        usarDatoAuxiliar ? {
          usar: true,
          categorizacion: categorizacionAuxiliar
        } : undefined
      )

      // Si el backend devuelve un proceso_id, conectarse al SSE
      if (response.proceso_id) {
        setProcesoId(response.proceso_id)
        // 🆕 MEJORA: Guardar proceso_id en localStorage para reconexión
        localStorage.setItem('proceso_activo_id', response.proceso_id)
        
        // Conectar al stream de progreso
        const eventSource = api.conectarProgreso(
          response.proceso_id,
          (data) => {
            // Actualizar progreso en tiempo real
            setProcessing(prev => ({
              ...prev,
              progress: data.progreso_pct,
              message: data.mensaje,
            }))
            
            setBatchActual(data.batch_actual)
            setTotalBatches(data.total_batches)
            setRespuestasProcesadas(data.respuestas_procesadas)
            setTotalRespuestasProceso(data.total_respuestas)
            setPausado(data.pausado)
            
            // Si completó
            if (data.completado) {
              const archivoResultadosSSE = data.archivo_resultados || response.ruta_resultados
              const archivoCodigosSSE = data.archivo_codigos_nuevos || response.ruta_codigos_nuevos
              const statsSSE = data.stats || null

              setProcessing(prev => ({
                ...prev,
                loading: false,
                progress: 100,
                message: "✅ Codificación completada",
              }))

              // Guardar resultados
              setResults({
                results: [],
                totalRespuestas: data.total_respuestas || response.total_respuestas,
                totalPreguntas: response.total_preguntas,
                costoTotal: (statsSSE?.costo_total ?? response.costo_total) || 0,
                archivoResultados: archivoResultadosSSE || "",
                archivoCodigos: archivoCodigosSSE || undefined,
                stats: statsSSE || undefined,
              })
              
              showNotificationMessage(`🎉 ${response.mensaje}`, false, 'success')
              setProcesoId(null)
              // 🆕 Limpiar localStorage cuando se completa
              localStorage.removeItem('proceso_activo_id')
            }
            
            // Si fue cancelado
            if (data.cancelado) {
              setProcessing(prev => ({
                ...prev,
                loading: false,
                error: "Proceso cancelado por el usuario",
              }))
              showNotificationMessage("⚠️ Codificación cancelada", false, 'warning')
              setProcesoId(null)
              // 🆕 Limpiar localStorage cuando se cancela
              localStorage.removeItem('proceso_activo_id')
            }
          },
          (error) => {
            setProcessing({
              loading: false,
              progress: 0,
              message: "",
              error: error.message,
            })
            showNotificationMessage(`❌ Error: ${error.message}`, false, 'warning')
            setProcesoId(null)
            // 🆕 Limpiar localStorage en caso de error
            localStorage.removeItem('proceso_activo_id')
          }
        )
        
        // Guardar EventSource para cerrarlo si es necesario
        return () => {
          eventSource.close()
        }
      } else {
        // Modo antiguo sin SSE (fallback)
      setProcessing({
        loading: false,
        progress: 100,
        message: "✅ Codificación completada",
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

        showNotificationMessage(`🎉 ${response.mensaje}`, false, 'success')
      }

    } catch (error) {
      setProcessing({
        loading: false,
        progress: 0,
        message: "",
        error: error instanceof Error ? error.message : "Error desconocido",
      })
      
      showNotificationMessage(`❌ Error: ${error instanceof Error ? error.message : "Error desconocido"}`, false, 'warning')
    }
  }

  // Pausar/Reanudar proceso
  const handleTogglePausa = async () => {
    if (!procesoId) return
    
    try {
      if (pausado) {
        await api.reanudarProceso(procesoId)
        showNotificationMessage("▶️ Proceso reanudado", false, 'info')
      } else {
        await api.pausarProceso(procesoId)
        showNotificationMessage("⏸️ Proceso pausado", false, 'info')
      }
      setPausado(!pausado)
    } catch (error) {
      showNotificationMessage(`❌ Error al ${pausado ? 'reanudar' : 'pausar'}: ${error instanceof Error ? error.message : 'Error desconocido'}`, false, 'warning')
    }
  }
  
  // Cancelar proceso
  const handleCancelar = async () => {
    if (!procesoId) return
    
    try {
      await api.cancelarProceso(procesoId)
      setProcessing(prev => ({
        ...prev,
        loading: false,
        error: "Proceso cancelado",
      }))
      setProcesoId(null)
      // 🆕 Limpiar localStorage al cancelar
      localStorage.removeItem('proceso_activo_id')
      showNotificationMessage("🛑 Codificación cancelada", false, 'warning')
    } catch (error) {
      showNotificationMessage(`❌ Error al cancelar: ${error instanceof Error ? error.message : 'Error desconocido'}`, false, 'warning')
    }
  }

  // 🆕 MEJORA: Reconectar a un proceso existente
  const reconectarProceso = async (procesoId: string) => {
    try {
      // Verificar que el proceso aún existe
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
          setProcessing(prev => ({
            ...prev,
            progress: data.progreso_pct,
            message: data.mensaje,
          }))
          
          setBatchActual(data.batch_actual)
          setTotalBatches(data.total_batches)
          setRespuestasProcesadas(data.respuestas_procesadas)
          setTotalRespuestasProceso(data.total_respuestas)
          setPausado(data.pausado)
          
          // Si completó
          if (data.completado) {
            const statsSSE = data.stats || null
            setProcessing(prev => ({
              ...prev,
              loading: false,
              progress: 100,
              message: "✅ Codificación completada",
            }))

            // Guardar resultados mínimos para permitir descargas si hay rutas
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
            setProcessing(prev => ({
              ...prev,
              loading: false,
              error: "Proceso cancelado",
            }))
            localStorage.removeItem('proceso_activo_id')
            setProcesoId(null)
          }
        },
        (error) => {
          console.error('Error reconectando:', error)
          // Si no se puede reconectar, limpiar
          localStorage.removeItem('proceso_activo_id')
          setProcesoId(null)
        }
      )
      
      showNotificationMessage("🔄 Reconectado a proceso en curso", false, 'info')
    } catch (error) {
      // Si el proceso no existe, limpiar localStorage
      localStorage.removeItem('proceso_activo_id')
      console.error('Error reconectando proceso:', error)
    }
  }

  // Reiniciar
  const handleReset = () => {
    setFiles([
      { name: "Respuestas", file: null },
      { name: "Códigos Anteriores (opcional)", file: null },
    ])
    setResults(null)
    setProcessing({
      loading: false,
      progress: 0,
      message: "",
      error: null,
    })
    setBatchActual(0)
    setTotalBatches(0)
    setRespuestasProcesadas(0)
    setTotalRespuestasProceso(0)
    setPausado(false)
    setProcesoId(null)
    // 🆕 Limpiar localStorage al reiniciar
    localStorage.removeItem('proceso_activo_id')
    showNotificationMessage("🔄 Listo para una nueva codificación", false, 'info')
  }

  // Descargar resultados
  const downloadResults = async () => {
    if (!results?.archivoResultados) return

    try {
      const blob = await api.descargarResultados(results.archivoResultados)
      api.downloadBlob(blob, results.archivoResultados)
      showNotificationMessage("📥 Archivo descargado exitosamente", false, 'success')
    } catch (error) {
      showNotificationMessage(`❌ Error al descargar: ${error instanceof Error ? error.message : "Error"}`, false, 'warning')
    }
  }

  // Descargar códigos nuevos
  const downloadCodigosNuevos = async () => {
    if (!results?.archivoCodigos) return

    try {
      const blob = await api.descargarCodigosNuevos(results.archivoCodigos)
      api.downloadBlob(blob, results.archivoCodigos)
      showNotificationMessage("📥 Catálogo descargado exitosamente", false, 'success')
    } catch (error) {
      showNotificationMessage(`❌ Error al descargar: ${error instanceof Error ? error.message : "Error"}`, false, 'warning')
    }
  }

  return (
    <div className={`min-h-screen transition-colors duration-300 ${darkMode ? "dark" : ""}`}>
      <header className="sticky top-0 z-50 backdrop-blur-md border-b border-border bg-background/95 shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between gap-4">
            {/* Logo */}
            <div className="flex items-center gap-3 animate-slide-in-left">
              <div className="w-12 h-12 rounded-lg bg-white dark:bg-gray-200 flex items-center justify-center shadow-lg border-2 border-orange-500 transform hover:scale-105 transition-transform overflow-hidden p-1.5">
                <img 
                  src="/bs-logo-180x180.png" 
                  alt="brandstrat_logo" 
                  className="w-full h-full object-contain"
                />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-orange-600 to-orange-500 bg-clip-text text-transparent">
                  Codificación Automatizada
                </h1>
                <p className="text-xs text-muted-foreground">Codificador de preguntas abiertas con IA</p>
              </div>
            </div>

            {/* Controles Derechos */}
            <div className="flex items-center gap-2">
              {/* Estado del backend */}
              <div className={`flex items-center gap-2 px-3 py-1 rounded-lg text-xs font-medium ${
                backendStatus === "online" 
                  ? "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400"
                  : backendStatus === "offline"
                  ? "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400"
                  : "bg-gray-100 dark:bg-gray-900/30 text-gray-800 dark:text-gray-400"
              }`}>
                {backendStatus === "online" ? "🟢 Online" : backendStatus === "offline" ? "🔴 Offline" : "🟡 Checking..."}
              </div>

              {/* Selector de modelo */}
              <div className="relative">
                <button
                  onClick={() => setShowModelDropdown(!showModelDropdown)}
                  className="px-3 py-2 rounded-lg bg-muted hover:bg-muted/80 text-foreground text-sm font-medium flex items-center gap-2 transition-all border border-border shadow-sm"
                >
                  <span className="text-xs">Modelo:</span>
                  <span className="text-primary font-semibold">{selectedModel}</span>
                  <ChevronDown className="w-4 h-4" />
                </button>
                {showModelDropdown && (
                  <div className="absolute top-full right-0 mt-2 bg-card border border-border rounded-lg shadow-xl z-10 min-w-[180px] animate-fade-in-up">
                    {availableModels.map((model) => (
                      <button
                        key={model.id}
                        onClick={() => {
                          setSelectedModel(model.id)
                          setShowModelDropdown(false)
                          showNotificationMessage(`✅ Modelo cambiado a ${model.nombre}`, false, 'success')
                        }}
                        className={`block w-full text-left px-4 py-2 text-sm transition-colors ${
                          selectedModel === model.id
                            ? "bg-primary text-primary-foreground"
                            : "hover:bg-muted text-foreground"
                        }`}
                      >
                        {model.nombre}
                        {model.recomendado && <span className="ml-2 text-xs">⭐</span>}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Dashboard */}
              <Link
                href="/dashboard"
                className="p-2 rounded-lg bg-muted border border-border text-muted-foreground hover:bg-orange-500 hover:text-white transition-all shadow-sm flex items-center gap-2"
                title="Ver dashboard de procesos"
              >
                <Activity className="w-4 h-4" />
              </Link>

              {/* Ayuda */}
              <button
                onClick={() => setShowHelp(true)}
                className="p-2 rounded-lg bg-muted border border-border text-muted-foreground hover:bg-orange-500 hover:text-white transition-all shadow-sm"
                title="Ayuda sobre formato de archivos"
              >
                <HelpCircle className="w-5 h-5" />
              </button>

              {/* Notificaciones */}
              <button
                onClick={() => {
                  const nuevoEstado = !notifications
                  setNotifications(nuevoEstado)
                  
                  if (nuevoEstado) {
                    // Activando: mostrar notificación
                    showDelayedNotification("🔔 Notificaciones activadas", 0)
                  } else {
                    // Desactivando: mostrar notificación
                    showDelayedNotification("🔕 Notificaciones desactivadas", 0)
                  }
                }}
                className={`p-2 rounded-lg transition-all border shadow-sm ${
                  notifications
                    ? "bg-primary/10 border-primary text-primary hover:bg-primary/20"
                    : "bg-muted border-border text-muted-foreground hover:bg-muted/80"
                }`}
              >
                <Bell className="w-5 h-5" />
              </button>

              {/* Dark mode */}
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 rounded-lg bg-muted border border-border text-muted-foreground hover:bg-muted/80 transition-all shadow-sm"
              >
                {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Notificación flotante */}
      {notification && (
        <div className="fixed top-20 left-0 right-0 z-50 flex justify-center pointer-events-none">
          <div className={`
            px-6 py-3 rounded-lg shadow-xl flex items-center gap-2 pointer-events-auto
            bg-gradient-to-r from-orange-600 to-orange-500
            text-white
            ${isNotificationLeaving ? 'animate-fade-out-up' : 'animate-fade-in-up'}
          `}>
          <Sparkles className="w-4 h-4" />
            {notification.message}
          </div>
        </div>
      )}

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
              {/* 🆕 Opción de Dato Auxiliar encima de Respuestas (solo cuando hay archivo de respuestas) */}
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
                  <div
                    key={index}
                    className="group relative animate-fade-in-up"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div
                      className="border-2 border-dashed border-border rounded-2xl p-8 hover:border-primary hover:bg-primary/5 transition-all cursor-pointer shadow-sm hover:shadow-lg group-hover:shadow-primary/20 duration-300"
                      onDragOver={(e) => e.preventDefault()}
                      onDrop={(e) => {
                        e.preventDefault()
                        const droppedFile = e.dataTransfer.files[0]
                        if (droppedFile) {
                          handleFileUpload(index, droppedFile)
                        }
                      }}
                    >
                      <input
                        type="file"
                        id={`file-${index}`}
                        className="hidden"
                        accept=".csv,.xlsx,.xls"
                        onChange={(e) => {
                          const uploadedFile = e.target.files?.[0] || null
                          handleFileUpload(index, uploadedFile)
                        }}
                      />
                      <label htmlFor={`file-${index}`} className="flex flex-col items-center gap-4 cursor-pointer">
                        <div className="bg-gradient-to-br from-orange-100 to-orange-50 dark:from-orange-900/30 dark:to-orange-800/20 rounded-xl p-4 group-hover:from-orange-200 group-hover:to-orange-100 dark:group-hover:from-orange-900/40 dark:group-hover:to-orange-800/30 transition-all">
                          <Upload className="w-8 h-8 text-orange-600 dark:text-orange-400" />
                        </div>
                        <div className="text-center">
                          <p className="font-semibold text-foreground text-lg">{file.name}</p>
                          <p className="text-sm text-muted-foreground">Excel (.xlsx, .xls)</p>
                        </div>
                        {file.file && (
                          <div className="text-xs bg-primary/10 text-primary px-4 py-2 rounded-full font-medium flex items-center gap-2 animate-glow">
                            ✓ {file.file.name}
                          </div>
                        )}
                      </label>
                    </div>
                  </div>
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
            {processing.loading && (
              <div className="mb-8 bg-gradient-to-r from-orange-50 to-orange-100/50 dark:from-orange-900/20 dark:to-orange-800/10 border border-orange-200 dark:border-orange-800 rounded-xl p-6 animate-fade-in-up shadow-lg">
                {/* Mensaje de estado */}
                <div className="flex items-center justify-between mb-4">
                  <p className="text-sm text-foreground font-medium">
                  {processing.message}
                </p>
                  {pausado && (
                    <span className="text-xs bg-yellow-500/20 text-yellow-700 dark:text-yellow-400 px-3 py-1 rounded-full font-semibold">
                      PAUSADO
                    </span>
                  )}
                </div>
                
                {/* Barra de progreso */}
                <div className="w-full bg-orange-200 dark:bg-orange-900/30 rounded-full h-4 overflow-hidden mb-3 shadow-inner">
                  <div
                    className="bg-gradient-to-r from-orange-600 via-orange-500 to-orange-600 h-4 rounded-full transition-all duration-500 shadow-lg flex items-center justify-center"
                    style={{ width: `${processing.progress}%` }}
                  >
                    {processing.progress > 10 && (
                      <span className="text-xs font-bold text-white">
                        {Math.round(processing.progress)}%
                      </span>
                    )}
                  </div>
                </div>
                
                {/* Información detallada */}
                {totalRespuestasProceso > 0 && (
                  <div className="grid grid-cols-2 gap-4 mb-4 text-xs">
                    <div className="bg-white/50 dark:bg-gray-800/50 rounded-lg p-3">
                      <p className="text-muted-foreground mb-1">Respuestas procesadas</p>
                      <p className="text-lg font-bold text-orange-600 dark:text-orange-400">
                        {respuestasProcesadas} / {totalRespuestasProceso}
                      </p>
                    </div>
                    <div className="bg-white/50 dark:bg-gray-800/50 rounded-lg p-3">
                      <p className="text-muted-foreground mb-1">Batches completados</p>
                      <p className="text-lg font-bold text-orange-600 dark:text-orange-400">
                        {batchActual} / {totalBatches}
                      </p>
                    </div>
                  </div>
                )}
                
                {/* Botones de control */}
                {procesoId && (
                  <div className="flex gap-3 justify-center pt-2">
                    <button
                      onClick={handleTogglePausa}
                      className="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-all transform hover:scale-105 active:scale-95 shadow-md"
                    >
                      {pausado ? (
                        <>
                          <Play className="w-4 h-4" />
                          Reanudar
                        </>
                      ) : (
                        <>
                          <Pause className="w-4 h-4" />
                          Pausar
                        </>
                      )}
                    </button>
                    <button
                      onClick={handleCancelar}
                      className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-all transform hover:scale-105 active:scale-95 shadow-md"
                    >
                      <XCircle className="w-4 h-4" />
                      Cancelar
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-4 justify-center animate-fade-in-up" style={{ animationDelay: "200ms" }}>
              <button
                onClick={executeCodification}
                disabled={
                  !files[0].file ||
                  processing.loading ||
                  backendStatus === "offline" ||
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
          <>
            {/* Results Section */}
            <div className="mb-8 animate-fade-in-up">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-3xl font-bold flex items-center gap-3">
                  <CheckCircle2 className="w-8 h-8 text-green-600" />
                  Codificación Completada
                </h2>
                <button
                  onClick={handleReset}
                  className="bg-muted hover:bg-muted/80 text-foreground px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-all transform hover:scale-105 active:scale-95"
                >
                  <RotateCcw className="w-4 h-4" />
                  Nueva Codificación
                </button>
              </div>

              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gradient-to-br from-card to-card/50 rounded-xl p-6 border border-border shadow-md">
                  <p className="text-muted-foreground text-sm font-medium mb-2">Total Respuestas (archivo)</p>
                  <p className="text-3xl font-bold text-primary">{results.totalRespuestas}</p>
                </div>
                <div className="bg-gradient-to-br from-card to-card/50 rounded-xl p-6 border border-border shadow-md">
                  <p className="text-muted-foreground text-sm font-medium mb-2">Respuestas Codificadas</p>
                  <p className="text-3xl font-bold text-primary">
                    {results.stats?.total_respuestas_codificadas ?? results.totalRespuestas}
                  </p>
                </div>
                <div className="bg-gradient-to-br from-card to-card/50 rounded-xl p-6 border border-border shadow-md">
                  <p className="text-muted-foreground text-sm font-medium mb-2">Costo Total (USD)</p>
                  <p className="text-3xl font-bold text-primary">
                    ${(results.stats?.costo_total ?? results.costoTotal).toFixed(4)}
                  </p>
                </div>
              </div>

              {/* Extra stats: códigos y tokens */}
              {results.stats && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                  <div className="bg-gradient-to-br from-card to-card/50 rounded-xl p-6 border border-border shadow-md">
                    <p className="text-muted-foreground text-sm font-medium mb-1">Códigos Nuevos Generados</p>
                    <p className="text-2xl font-semibold text-primary">{results.stats.total_codigos_nuevos}</p>
                  </div>
                  <div className="bg-gradient-to-br from-card to-card/50 rounded-xl p-6 border border-border shadow-md">
                    <p className="text-muted-foreground text-sm font-medium mb-1">Códigos Históricos Aplicados</p>
                    <p className="text-2xl font-semibold text-primary">{results.stats.total_codigos_historicos}</p>
                  </div>
                  <div className="bg-gradient-to-br from-card to-card/50 rounded-xl p-6 border border-border shadow-md">
                    <p className="text-muted-foreground text-sm font-medium mb-1">Tokens Totales</p>
                    <p className="text-2xl font-semibold text-primary">
                      {results.stats.total_tokens}
                    </p>
                  </div>
                </div>
              )}

              {/* Download Buttons */}
              <div className="flex flex-wrap gap-4">
                <button
                  onClick={downloadResults}
                  className="bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-700 hover:to-orange-600 shadow-lg hover:shadow-xl hover:shadow-orange-500/50 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-all transform hover:scale-105 active:scale-95"
                >
                  <Download className="w-5 h-5" />
                  Descargar Resultados
                </button>

              </div>

              {/* Success Message */}
              <div className="mt-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-4 flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-green-900 dark:text-green-100">¡Proceso completado exitosamente!</p>
                  <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                    Los archivos están listos para descargar. El archivo de resultados contiene todas las respuestas codificadas.
                  </p>
                </div>
              </div>
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-background/95 backdrop-blur-sm mt-16">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-center gap-2">
            <p className="text-sm text-muted-foreground">
              <span className="font-semibold text-foreground">Brandstrat</span> © 2025. Todos los derechos reservados.
            </p>
          </div>
        </div>
      </footer>

      {/* Modal de Ayuda */}
      {showHelp && (
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
                  onClick={() => setShowHelp(false)}
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
                    <p className="text-sm font-semibold text-orange-600 dark:text-orange-400 mb-2">📋 Estructura requerida:</p>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li className="flex items-start gap-2">
                        <span className="text-orange-500 font-bold">•</span>
                        <span><strong className="text-foreground">Columna 1 (ID):</strong> Identificador único de cada respuesta</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-orange-500 font-bold">•</span>
                        <span><strong className="text-foreground">Columna 2 en adelante:</strong> Las preguntas con sus respuestas</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-orange-500 font-bold">•</span>
                        <span><strong className="text-foreground">Encabezados:</strong> Los nombres de las columnas serán usados como nombres de preguntas</span>
                      </li>
                    </ul>
                  </div>

                  <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
                    <p className="text-sm font-semibold text-green-700 dark:text-green-400 mb-2">✅ Ejemplo correcto:</p>
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs border-collapse">
                        <thead>
                          <tr className="bg-green-100 dark:bg-green-900/40">
                            <th className="border border-green-300 dark:border-green-700 px-2 py-1">ID</th>
                            <th className="border border-green-300 dark:border-green-700 px-2 py-1">2. ¿Por qué seleccionó esta imagen?</th>
                            <th className="border border-green-300 dark:border-green-700 px-2 py-1">5. ¿Qué le transmite?</th>
                          </tr>
                        </thead>
                        <tbody className="text-muted-foreground">
                          <tr>
                            <td className="border border-green-300 dark:border-green-700 px-2 py-1">1</td>
                            <td className="border border-green-300 dark:border-green-700 px-2 py-1">Me gusta el color</td>
                            <td className="border border-green-300 dark:border-green-700 px-2 py-1">Alegría y felicidad</td>
                          </tr>
                          <tr>
                            <td className="border border-green-300 dark:border-green-700 px-2 py-1">2</td>
                            <td className="border border-green-300 dark:border-green-700 px-2 py-1">Es la más llamativa</td>
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
                    <p className="text-sm font-semibold text-blue-600 dark:text-blue-400 mb-2">📚 Estructura requerida:</p>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li className="flex items-start gap-2">
                        <span className="text-blue-500 font-bold">•</span>
                        <span><strong className="text-foreground">Hojas múltiples:</strong> Una hoja por cada pregunta</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-blue-500 font-bold">•</span>
                        <span><strong className="text-foreground">Nombre de hoja:</strong> Debe coincidir con el nombre de la columna en el archivo de respuestas</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-blue-500 font-bold">•</span>
                        <span><strong className="text-foreground">Columnas requeridas:</strong></span>
                      </li>
                      <ul className="ml-6 space-y-1 mt-1">
                        <li className="text-xs">- <strong className="text-foreground">COD:</strong> Código del catálogo</li>
                        <li className="text-xs">- <strong className="text-foreground">TEXTO:</strong> Descripción del código</li>
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
                      <strong>⚠️ Nota:</strong> Si no proporcionas códigos anteriores, el sistema generará códigos nuevos automáticamente.
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
                    <span>Los archivos deben estar en formato <strong className="text-foreground">.xlsx</strong> o <strong className="text-foreground">.xls</strong></span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-500 font-bold text-lg">•</span>
                    <span>Asegúrate de que las respuestas no tengan celdas vacías en la columna ID</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-500 font-bold text-lg">•</span>
                    <span>Los nombres de las hojas en el archivo de códigos deben coincidir <strong className="text-foreground">exactamente</strong> con los nombres de las columnas</span>
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
                onClick={() => setShowHelp(false)}
                className="w-full bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-700 hover:to-orange-600 text-white px-6 py-3 rounded-xl font-semibold transition-all transform hover:scale-105 active:scale-95 shadow-lg"
              >
                Entendido
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 🆕 Modal de Configuración de Dato Auxiliar */}
      {showConfigAuxiliar && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col border border-border">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-border">
              <h2 className="text-2xl font-bold text-primary">Configurar Datos Auxiliares</h2>
              <button
                onClick={() => setShowConfigAuxiliar(false)}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              <p className="text-sm text-muted-foreground mb-6">
                Arrastra los datos auxiliares a su categoría correspondiente. Esto ayudará al modelo a generar códigos más precisos.
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
                      id="negativas"
                      onDragOver={(e) => {
                        e.preventDefault()
                        e.currentTarget.classList.add('bg-red-500/20')
                      }}
                      onDragLeave={(e) => {
                        e.currentTarget.classList.remove('bg-red-500/20')
                      }}
                      onDrop={(e) => {
                        e.preventDefault()
                        e.currentTarget.classList.remove('bg-red-500/20')
                        const dato = e.dataTransfer.getData('text/plain')
                        if (dato) {
                          setCategorizacionAuxiliar(prev => {
                            const newState = { ...prev }
                            // Remover de otras categorías
                            newState.negativas = newState.negativas.filter(d => d !== dato)
                            newState.neutrales = newState.neutrales.filter(d => d !== dato)
                            newState.positivas = newState.positivas.filter(d => d !== dato)
                            // Agregar a negativas si no está
                            if (!newState.negativas.includes(dato)) {
                              newState.negativas.push(dato)
                            }
                            return newState
                          })
                        }
                      }}
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
                      id="neutrales"
                      onDragOver={(e) => {
                        e.preventDefault()
                        e.currentTarget.classList.add('bg-gray-500/20')
                      }}
                      onDragLeave={(e) => {
                        e.currentTarget.classList.remove('bg-gray-500/20')
                      }}
                      onDrop={(e) => {
                        e.preventDefault()
                        e.currentTarget.classList.remove('bg-gray-500/20')
                        const dato = e.dataTransfer.getData('text/plain')
                        if (dato) {
                          setCategorizacionAuxiliar(prev => {
                            const newState = { ...prev }
                            newState.negativas = newState.negativas.filter(d => d !== dato)
                            newState.neutrales = newState.neutrales.filter(d => d !== dato)
                            newState.positivas = newState.positivas.filter(d => d !== dato)
                            if (!newState.neutrales.includes(dato)) {
                              newState.neutrales.push(dato)
                            }
                            return newState
                          })
                        }
                      }}
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
                      id="positivas"
                      onDragOver={(e) => {
                        e.preventDefault()
                        e.currentTarget.classList.add('bg-green-500/20')
                      }}
                      onDragLeave={(e) => {
                        e.currentTarget.classList.remove('bg-green-500/20')
                      }}
                      onDrop={(e) => {
                        e.preventDefault()
                        e.currentTarget.classList.remove('bg-green-500/20')
                        const dato = e.dataTransfer.getData('text/plain')
                        if (dato) {
                          setCategorizacionAuxiliar(prev => {
                            const newState = { ...prev }
                            newState.negativas = newState.negativas.filter(d => d !== dato)
                            newState.neutrales = newState.neutrales.filter(d => d !== dato)
                            newState.positivas = newState.positivas.filter(d => d !== dato)
                            if (!newState.positivas.includes(dato)) {
                              newState.positivas.push(dato)
                            }
                            return newState
                          })
                        }
                      }}
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
                  {datosAuxiliares
                    .filter(d => 
                      !categorizacionAuxiliar.negativas.includes(d) &&
                      !categorizacionAuxiliar.neutrales.includes(d) &&
                      !categorizacionAuxiliar.positivas.includes(d)
                    )
                    .map((dato, idx) => (
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
                onClick={() => {
                  setCategorizacionAuxiliar({ negativas: [], neutrales: [], positivas: [] })
                }}
                className="px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Limpiar todo
              </button>
              <button
                onClick={() => setShowConfigAuxiliar(false)}
                className="px-6 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-semibold transition-colors"
              >
                Guardar y Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
