import { FileText, Loader } from 'lucide-react'
import { FileItem } from '../types'

interface FileExplorerProps {
  files: FileItem[]
  selectedFile: FileItem | null
  onSelectFile: (file: FileItem) => void
  loading: boolean
}

const FileExplorer = ({ files, selectedFile, onSelectFile, loading }: FileExplorerProps) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader className="w-6 h-6 animate-spin text-primary-500" />
      </div>
    )
  }

  if (files.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No files found</p>
      </div>
    )
  }

  // Group files by directory
  const fileTree: { [key: string]: FileItem[] } = {}
  files.forEach((file) => {
    const parts = file.file_path.split('/')
    const dir = parts.length > 1 ? parts.slice(0, -1).join('/') : 'root'
    if (!fileTree[dir]) {
      fileTree[dir] = []
    }
    fileTree[dir].push(file)
  })

  const getLanguageColor = (language: string) => {
    const colors: { [key: string]: string } = {
      python: 'text-blue-400',
      javascript: 'text-yellow-400',
      typescript: 'text-blue-500',
      java: 'text-red-400',
      go: 'text-cyan-400',
      rust: 'text-orange-400',
    }
    return colors[language] || 'text-gray-400'
  }

  return (
    <div className="space-y-4">
      {Object.entries(fileTree).map(([dir, dirFiles]) => (
        <div key={dir}>
          <div className="text-xs font-semibold text-gray-500 uppercase mb-2">
            {dir}
          </div>
          <div className="space-y-1">
            {dirFiles.map((file) => (
              <button
                key={file.id}
                onClick={() => onSelectFile(file)}
                className={`w-full text-left p-2 rounded transition-colors ${
                  selectedFile?.id === file.id
                    ? 'bg-primary-600 text-white'
                    : 'hover:bg-gray-700 text-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <FileText className={`w-4 h-4 ${getLanguageColor(file.language)}`} />
                  <span className="text-sm truncate">
                    {file.file_path.split('/').pop()}
                  </span>
                </div>
                <div className="mt-1 text-xs text-gray-500">
                  {file.language} • {file.chunk_count} chunks
                </div>
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

export default FileExplorer