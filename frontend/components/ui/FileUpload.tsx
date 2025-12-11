/**
 * Componente para carga de archivos
 */
'use client'

import { Upload } from 'lucide-react'
import type { FileData } from '@/types'
import { FILE_ACCEPT_TYPES } from '@/utils/constants'

interface FileUploadProps {
  file: FileData
  index: number
  onFileUpload: (index: number, file: File | null) => void
  animationDelay?: number
}

export function FileUpload({ file, index, onFileUpload, animationDelay = 0 }: FileUploadProps) {
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      onFileUpload(index, droppedFile)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files?.[0] || null
    onFileUpload(index, uploadedFile)
  }

  return (
    <div
      className="group relative animate-fade-in-up"
      style={{ animationDelay: `${animationDelay}ms` }}
    >
      <div
        className="border-2 border-dashed border-border rounded-2xl p-8 hover:border-primary hover:bg-primary/5 transition-all cursor-pointer shadow-sm hover:shadow-lg group-hover:shadow-primary/20 duration-300"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id={`file-${index}`}
          className="hidden"
          accept={FILE_ACCEPT_TYPES}
          onChange={handleFileChange}
        />
        <label htmlFor={`file-${index}`} className="flex flex-col items-center gap-4 cursor-pointer">
          <div className="bg-gradient-to-br from-orange-100 to-orange-50 dark:from-orange-900/30 dark:to-orange-800/20 rounded-xl p-4 group-hover:from-orange-200 group-hover:to-orange-100 dark:group-hover:from-orange-900/40 dark:group-hover:to-orange-800/30 transition-all">
            <Upload className="w-8 h-8 text-orange-600 dark:text-orange-400" />
          </div>
          <div className="text-center">
            <p className="font-semibold text-foreground text-lg">{file.name}</p>
            <p className="text-sm text-muted-foreground">Excel (.xlsx, .xls)</p>
          </div>
          {file.file && (
            <div className="text-xs bg-primary/10 text-primary px-4 py-2 rounded-full font-medium flex items-center gap-2 animate-glow">
              ✓ {file.file.name}
            </div>
          )}
        </label>
      </div>
    </div>
  )
}

