/**
 * Hook para manejar notificaciones
 */
import { useState } from 'react'
import { playNotificationSound, type NotificationSoundType } from '@/utils/audio'
import { NOTIFICATION_DURATION, NOTIFICATION_ANIMATION_DURATION } from '@/utils/constants'

export interface Notification {
  message: string
  type: NotificationSoundType
}

export function useNotifications(enabled: boolean = true) {
  const [notification, setNotification] = useState<Notification | null>(null)
  const [isLeaving, setIsLeaving] = useState(false)

  const showNotification = (
    message: string,
    type: NotificationSoundType = 'info',
    force: boolean = false
  ) => {
    if (!enabled && !force) return

    // Reproducir sonido
    playNotificationSound(type)

    setIsLeaving(false)
    setNotification({ message, type })

    // Después de NOTIFICATION_DURATION, iniciar animación de salida
    setTimeout(() => {
      setIsLeaving(true)
      // Después de la animación, remover notificación
      setTimeout(() => {
        setNotification(null)
        setIsLeaving(false)
      }, NOTIFICATION_ANIMATION_DURATION)
    }, NOTIFICATION_DURATION)
  }

  const showDelayedNotification = (
    message: string,
    delay: number = 0,
    type: NotificationSoundType = 'info'
  ) => {
    setTimeout(() => {
      showNotification(message, type)
    }, delay)
  }

  return {
    notification,
    isLeaving,
    showNotification,
    showDelayedNotification,
  }
}

