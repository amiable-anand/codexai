import { useState, useEffect } from 'react'
import { FileText, Folder, RefreshCw } from 'lucide-react'
import ProjectList from './components/ProjectList'
import FileExplorer from './components/FileExplorer'
import DocumentationViewer from './components/DocumentationViewer'
import { Project, FileItem } from './types'
import { fetchProjects, fetchFiles } from './api'

function App() {
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [files, setFiles] = useState<FileItem[]>([])
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    setLoading(true)
    try {
      const data = await fetchProjects()
      setProjects(data)
    } catch (error) {
      console.error('Failed to load projects:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleProjectSelect = async (project: Project) => {
    setSelectedProject(project)
    setSelectedFile(null)
    setLoading(true)
    
    try {
      const data = await fetchFiles(project.id)
      setFiles(data.files)
    } catch (error) {
      console.error('Failed to load files:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (file: FileItem) => {
    setSelectedFile(file)
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FileText className="w-8 h-8 text-primary-500" />
            <h1 className="text-2xl font-bold">CodexAI</h1>
          </div>
          <button
            onClick={loadProjects}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-73px)]">
        {/* Sidebar - Projects */}
        <div className="w-64 bg-gray-800 border-r border-gray-700 overflow-y-auto">
          <div className="p-4">
            <h2 className="text-sm font-semibold text-gray-400 uppercase mb-3">Projects</h2>
            <ProjectList
              projects={projects}
              selectedProject={selectedProject}
              onSelectProject={handleProjectSelect}
              loading={loading}
            />
          </div>
        </div>

        {/* Middle Panel - File Explorer */}
        <div className="w-80 bg-gray-850 border-r border-gray-700 overflow-y-auto">
          {selectedProject ? (
            <div className="p-4">
              <div className="flex items-center space-x-2 mb-4">
                <Folder className="w-5 h-5 text-primary-500" />
                <h2 className="text-lg font-semibold">{selectedProject.name}</h2>
              </div>
              <FileExplorer
                files={files}
                selectedFile={selectedFile}
                onSelectFile={handleFileSelect}
                loading={loading}
              />
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
              <p>Select a project to view files</p>
            </div>
          )}
        </div>

        {/* Main Panel - Documentation Viewer */}
        <div className="flex-1 overflow-y-auto">
          {selectedFile && selectedProject ? (
            <DocumentationViewer
              projectId={selectedProject.id}
              file={selectedFile}
            />
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
              <div className="text-center">
                <FileText className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                <p className="text-lg">Select a file to generate documentation</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App