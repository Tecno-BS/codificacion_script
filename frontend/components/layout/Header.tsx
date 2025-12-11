/**
 * Componente Header de la aplicación
 */
'use client'

import { Activity, HelpCircle, Bell, Moon, Sun } from 'lucide-react'
import Link from 'next/link'
import { BackendStatusBadge } from '../ui/BackendStatus'
import { ModelSelector } from '../ui/ModelSelector'
import type { BackendStatus } from '@/hooks/useBackendStatus'
import type { ModeloGPT } from '@/lib/api'

interface HeaderProps {
  darkMode: boolean
  onToggleDarkMode: () => void
  notifications: boolean
  onToggleNotifications: () => void
  backendStatus: BackendStatus
  availableModels: ModeloGPT[]
  selectedModel: string
  onModelChange: (modelId: string) => void
  onNotification?: (message: string, type?: 'success' | 'info' | 'warning') => void
  onShowHelp: () => void
}

export function Header({
  darkMode,
  onToggleDarkMode,
  notifications,
  onToggleNotifications,
  backendStatus,
  availableModels,
  selectedModel,
  onModelChange,
  onNotification,
  onShowHelp,
}: HeaderProps) {
  return (
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
            <BackendStatusBadge status={backendStatus} />

            <ModelSelector
              models={availableModels}
              selectedModel={selectedModel}
              onModelChange={onModelChange}
              onNotification={onNotification}
            />

            <Link
              href="/dashboard"
              className="p-2 rounded-lg bg-muted border border-border text-muted-foreground hover:bg-orange-500 hover:text-white transition-all shadow-sm flex items-center gap-2"
              title="Ver dashboard de procesos"
            >
              <Activity className="w-4 h-4" />
            </Link>

            <button
              onClick={onShowHelp}
              className="p-2 rounded-lg bg-muted border border-border text-muted-foreground hover:bg-orange-500 hover:text-white transition-all shadow-sm"
              title="Ayuda sobre formato de archivos"
            >
              <HelpCircle className="w-5 h-5" />
            </button>

            <button
              onClick={onToggleNotifications}
              className={`p-2 rounded-lg transition-all border shadow-sm ${
                notifications
                  ? 'bg-primary/10 border-primary text-primary hover:bg-primary/20'
                  : 'bg-muted border-border text-muted-foreground hover:bg-muted/80'
              }`}
            >
              <Bell className="w-5 h-5" />
            </button>

            <button
              onClick={onToggleDarkMode}
              className="p-2 rounded-lg bg-muted border border-border text-muted-foreground hover:bg-muted/80 transition-all shadow-sm"
            >
              {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

