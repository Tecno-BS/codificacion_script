/**
 * Componente Footer de la aplicación
 */
'use client'

export function Footer() {
  return (
    <footer className="border-t border-border bg-background/95 backdrop-blur-sm mt-16">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center justify-center gap-2">
          <p className="text-sm text-muted-foreground">
            <span className="font-semibold text-foreground">Brandstrat</span> © 2025. Todos los derechos reservados.
          </p>
        </div>
      </div>
    </footer>
  )
}

