import axios from 'axios'
import { Project, FileItem, Documentation } from './types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const fetchProjects = async (): Promise<Project[]> => {
  const response = await api.get('/projects')
  return response.data
}

export const fetchFiles = async (projectId: string): Promise<{ project_id: string; project_name: string; files: FileItem[] }> => {
  const response = await api.get(`/projects/${projectId}/files`)
  return response.data
}

export const generateDocumentation = async (
  projectId: string,
  filePath: string,
  target: string = 'file'
): Promise<Documentation> => {
  const response = await api.post('/generate-documentation', {
    project_id: projectId,
    file_path: filePath,
    target,
  })
  return response.data
}

export const getDocumentation = async (docId: string): Promise<Documentation> => {
  const response = await api.get(`/documentation/${docId}`)
  return response.data
}