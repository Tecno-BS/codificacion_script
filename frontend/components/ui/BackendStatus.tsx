/**
 * Componente para mostrar el estado del backend
 */
'use client'

import type { BackendStatus } from '@/hooks/useBackendStatus'

interface BackendStatusProps {
  status: BackendStatus
}

export function BackendStatusBadge({ status }: BackendStatusProps) {
  const statusConfig = {
    online: {
      bg: 'bg-green-100 dark:bg-green-900/30',
      text: 'text-green-800 dark:text-green-400',
      label: '🟢 Online',
    },
    offline: {
      bg: 'bg-red-100 dark:bg-red-900/30',
      text: 'text-red-800 dark:text-red-400',
      label: '🔴 Offline',
    },
    checking: {
      bg: 'bg-gray-100 dark:bg-gray-900/30',
      text: 'text-gray-800 dark:text-gray-400',
      label: '🟡 Checking...',
    },
  }

  const config = statusConfig[status]

  return (
    <div className={`flex items-center gap-2 px-3 py-1 rounded-lg text-xs font-medium ${config.bg} ${config.text}`}>
      {config.label}
    </div>
  )
}

