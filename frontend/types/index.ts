/**
 * Tipos TypeScript para la aplicación
 */

export interface FileData {
  name: string
  file: File | null
}

export interface CodedResult {
  respuesta: string
  codigo: string
  decision: string
  justificacion?: string
}

export interface ProcessingState {
  loading: boolean
  progress: number
  message: string
  error: string | null
}

export interface ResultsData {
  results: CodedResult[]
  totalRespuestas: number
  totalPreguntas: number
  costoTotal: number
  archivoResultados: string
  archivoCodigos?: string
  stats?: CodificationStats
}

export interface CodificationStats {
  total_respuestas_codificadas: number
  total_codigos_nuevos: number
  total_codigos_historicos: number
  total_tokens: number
  prompt_tokens: number
  completion_tokens: number
  costo_total: number
}

