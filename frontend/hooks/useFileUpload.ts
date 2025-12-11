/**
 * Hook para manejar la carga de archivos
 */
import { useState } from 'react'
import type { FileData } from '@/types'

const DEFAULT_FILES: FileData[] = [
  { name: 'Respuestas', file: null },
  { name: 'Códigos Anteriores (opcional)', file: null },
]

export function useFileUpload() {
  const [files, setFiles] = useState<FileData[]>(DEFAULT_FILES)

  const handleFileUpload = (index: number, uploadedFile: File | null) => {
    const newFiles = [...files]
    newFiles[index].file = uploadedFile
    setFiles(newFiles)
    return uploadedFile
  }

  const resetFiles = () => {
    setFiles(DEFAULT_FILES)
  }

  return {
    files,
    setFiles,
    handleFileUpload,
    resetFiles,
  }
}

