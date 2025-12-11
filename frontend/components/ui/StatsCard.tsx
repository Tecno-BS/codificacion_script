/**
 * Componente de tarjeta de estadísticas
 */
'use client'

interface StatsCardProps {
  label: string
  value: string | number
  className?: string
}

export function StatsCard({ label, value, className = '' }: StatsCardProps) {
  return (
    <div className={`bg-gradient-to-br from-card to-card/50 rounded-xl p-6 border border-border shadow-md ${className}`}>
      <p className="text-muted-foreground text-sm font-medium mb-2">{label}</p>
      <p className="text-3xl font-bold text-primary">{value}</p>
    </div>
  )
}

