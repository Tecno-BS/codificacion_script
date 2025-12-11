/**
 * Componente de notificación flotante
 */
'use client'

import { Sparkles } from 'lucide-react'
import type { NotificationSoundType } from '@/utils/audio'

interface NotificationProps {
  notification: { message: string; type: NotificationSoundType } | null
  isLeaving: boolean
}

export function Notification({ notification, isLeaving }: NotificationProps) {
  if (!notification) return null

  return (
    <div className="fixed top-20 left-0 right-0 z-50 flex justify-center pointer-events-none">
      <div
        className={`
          px-6 py-3 rounded-lg shadow-xl flex items-center gap-2 pointer-events-auto
          bg-gradient-to-r from-orange-600 to-orange-500
          text-white
          ${isLeaving ? 'animate-fade-out-up' : 'animate-fade-in-up'}
        `}
      >
        <Sparkles className="w-4 h-4" />
        {notification.message}
      </div>
    </div>
  )
}

