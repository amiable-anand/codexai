export interface Project {
  id: string
  name: string
  status: 'processing' | 'indexed' | 'failed'
  upload_date: string
  file_count: number
  chunk_count: number
}

export interface FileItem {
  id: string
  file_path: string
  language: string
  status: string
  chunk_count: number
}

export interface Documentation {
  documentation_id: string
  content: string
  metadata: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
    context_chunks: number
  }
}