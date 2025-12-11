/**
 * Funciones helper de la aplicación
 */

/**
 * Formatea un número como moneda USD
 */
export function formatCurrency(value: number): string {
  return `$${value.toFixed(4)}`
}

/**
 * Formatea un número con separadores de miles
 */
export function formatNumber(value: number): string {
  return value.toLocaleString()
}

/**
 * Formatea un porcentaje
 */
export function formatPercentage(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`
}

/**
 * Obtiene el nombre del archivo desde una ruta completa
 */
export function getFilenameFromPath(path: string): string {
  return path.split('/').pop() || path
}

/**
 * Verifica si un valor está vacío o es nulo
 */
export function isEmpty(value: any): boolean {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

