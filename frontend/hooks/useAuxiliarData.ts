/**
 * Hook para manejar datos auxiliares y su categorización
 */
import { useState, useMemo } from 'react'

export interface CategorizacionAuxiliar {
  negativas: string[]
  neutrales: string[]
  positivas: string[]
}

export function useAuxiliarData() {
  const [usarDatoAuxiliar, setUsarDatoAuxiliar] = useState(false)
  const [showConfigAuxiliar, setShowConfigAuxiliar] = useState(false)
  const [datosAuxiliares, setDatosAuxiliares] = useState<string[]>([])
  const [categorizacionAuxiliar, setCategorizacionAuxiliar] = useState<CategorizacionAuxiliar>({
    negativas: [],
    neutrales: [],
    positivas: [],
  })

  // Verificar si hay datos auxiliares sin categorizar
  const hayDatosAuxiliaresPendientes = useMemo(() => {
    if (!usarDatoAuxiliar) return false
    return datosAuxiliares.some(
      (d) =>
        !categorizacionAuxiliar.negativas.includes(d) &&
        !categorizacionAuxiliar.neutrales.includes(d) &&
        !categorizacionAuxiliar.positivas.includes(d)
    )
  }, [usarDatoAuxiliar, datosAuxiliares, categorizacionAuxiliar])

  const resetAuxiliarData = () => {
    setDatosAuxiliares([])
    setCategorizacionAuxiliar({
      negativas: [],
      neutrales: [],
      positivas: [],
    })
    setUsarDatoAuxiliar(false)
  }

  return {
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
  }
}

