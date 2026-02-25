import { Folder, Clock, CheckCircle, XCircle, Loader } from 'lucide-react'
import { Project } from '../types'

interface ProjectListProps {
  projects: Project[]
  selectedProject: Project | null
  onSelectProject: (project: Project) => void
  loading: boolean
}

const ProjectList = ({ projects, selectedProject, onSelectProject, loading }: ProjectListProps) => {
  if (loading && projects.length === 0) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader className="w-6 h-6 animate-spin text-primary-500" />
      </div>
    )
  }

  if (projects.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No projects yet</p>
        <p className="text-sm mt-2">Upload a codebase using the CLI tool</p>
      </div>
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'indexed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'processing':
        return <Clock className="w-4 h-4 text-yellow-500 animate-pulse" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />
      default:
        return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  return (
    <div className="space-y-2">
      {projects.map((project) => (
        <button
          key={project.id}
          onClick={() => onSelectProject(project)}
          className={`w-full text-left p-3 rounded-lg transition-colors ${
            selectedProject?.id === project.id
              ? 'bg-primary-600 text-white'
              : 'bg-gray-700 hover:bg-gray-600 text-gray-200'
          }`}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-2 flex-1 min-w-0">
              <Folder className="w-4 h-4 flex-shrink-0" />
              <span className="font-medium truncate">{project.name}</span>
            </div>
            {getStatusIcon(project.status)}
          </div>
          <div className="mt-2 text-xs text-gray-400 space-y-1">
            <div>{project.file_count} files</div>
            <div>{new Date(project.upload_date).toLocaleDateString()}</div>
          </div>
        </button>
      ))}
    </div>
  )
}

export default ProjectList