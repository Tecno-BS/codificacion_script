/**
 * Banner de notificaciones del dashboard
 */
'use client'

interface NotificationBannerProps {
  message: string
  type: 'success' | 'error'
}

export function NotificationBanner({ message, type }: NotificationBannerProps) {
  return (
    <div
      className={`mb-6 rounded-lg p-4 border animate-fade-in-up ${
        type === 'success'
          ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
          : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
      }`}
    >
      <p className={type === 'success' ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'}>
        {message}
      </p>
    </div>
  )
}

