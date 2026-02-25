import { useState } from 'react'
import { FileText, Loader, Download, Copy, CheckCircle } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { FileItem, Documentation } from '../types'
import { generateDocumentation } from '../api'

interface DocumentationViewerProps {
  projectId: string
  file: FileItem
}

const DocumentationViewer = ({ projectId, file }: DocumentationViewerProps) => {
  const [documentation, setDocumentation] = useState<Documentation | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const handleGenerate = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const doc = await generateDocumentation(projectId, file.file_path)
      setDocumentation(doc)
    } catch (err) {
      setError('Failed to generate documentation. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    if (documentation) {
      navigator.clipboard.writeText(documentation.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleDownload = () => {
    if (documentation) {
      const blob = new Blob([documentation.content], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${file.file_path.replace(/\//g, '_')}_documentation.md`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FileText className="w-5 h-5 text-primary-500" />
            <div>
              <h2 className="text-lg font-semibold">{file.file_path}</h2>
              <p className="text-sm text-gray-400">{file.language}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {documentation && (
              <>
                <button
                  onClick={handleCopy}
                  className="flex items-center space-x-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                  title="Copy to clipboard"
                >
                  {copied ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
                <button
                  onClick={handleDownload}
                  className="flex items-center space-x-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                  title="Download as Markdown"
                >
                  <Download className="w-4 h-4" />
                </button>
              </>
            )}
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 rounded-lg transition-colors"
            >
              {loading ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <span>{documentation ? 'Regenerate' : 'Generate Documentation'}</span>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {error && (
          <div className="bg-red-900/20 border border-red-700 text-red-400 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <Loader className="w-12 h-12 animate-spin text-primary-500 mx-auto mb-4" />
              <p className="text-gray-400">Generating documentation...</p>
              <p className="text-sm text-gray-500 mt-2">This may take a few seconds</p>
            </div>
          </div>
        )}

        {documentation && !loading && (
          <div>
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown>{documentation.content}</ReactMarkdown>
            </div>
            
            <div className="mt-8 pt-4 border-t border-gray-700 text-sm text-gray-500">
              <div className="flex items-center justify-between">
                <span>Generated at: {new Date().toLocaleString()}</span>
                <span>
                  Tokens: {documentation.metadata.total_tokens} 
                  ({documentation.metadata.prompt_tokens} prompt + {documentation.metadata.completion_tokens} completion)
                </span>
              </div>
            </div>
          </div>
        )}

        {!documentation && !loading && !error && (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-600" />
              <p className="text-lg mb-2">No documentation generated yet</p>
              <p className="text-sm">Click "Generate Documentation" to create AI-powered docs for this file</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentationViewer