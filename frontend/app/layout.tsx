import type React from "react"
import type { Metadata } from "next"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"

export const metadata: Metadata = {
  title: "Codificador de Preguntas Abiertas",
  description: "Codifica automáticamente respuestas abiertas usando inteligencia artificial",
  icons: {
    icon: "/bs-logo-180x180.png",
    apple: "/bs-logo-180x180.png",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es">
      <body className={`font-sans antialiased`}>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
