"""
Ingestion Pipeline Handler
Processes uploaded codebases: unzip, chunk, embed, and index
"""

import os
import zipfile
import tempfile
import logging
from pathlib import Path
from typing import List, Dict
import uuid
from datetime import datetime

from code_chunker import CodeChunker
from embedding_service import EmbeddingService
from search_service import SearchService
from cosmos_service import CosmosService


def handle_ingestion(project_name: str, blob_content: bytes) -> Dict:
    """
    Main ingestion handler
    
    Args:
        project_name: Name of the project
        blob_content: Zip file content as bytes
        
    Returns:
        Dict with processing results
    """
    logging.info(f"Starting ingestion for project: {project_name}")
    
    # Initialize services
    chunker = CodeChunker()
    embedding_service = EmbeddingService()
    search_service = SearchService()
    cosmos_service = CosmosService()
    
    # Create temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_path = temp_path / "codebase.zip"
        
        # Write blob content to file
        with open(zip_path, 'wb') as f:
            f.write(blob_content)
        
        # Extract zip
        extract_path = temp_path / "extracted"
        extract_path.mkdir()
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        logging.info(f"Extracted codebase to {extract_path}")
        
        # Create project in Cosmos DB
        project_id = str(uuid.uuid4())
        project_doc = {
            'id': project_id,
            'name': project_name,
            'upload_date': datetime.utcnow().isoformat(),
            'status': 'processing',
            'file_count': 0,
            'chunk_count': 0
        }
        cosmos_service.create_project(project_doc)
        
        # Process all code files
        all_chunks = []
        file_count = 0
        
        for file_path in extract_path.rglob('*'):
            if file_path.is_file() and is_code_file(file_path):
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Get relative path
                    rel_path = str(file_path.relative_to(extract_path))
                    
                    # Detect language
                    language = detect_language(file_path)
                    
                    # Chunk the code
                    chunks = chunker.chunk_code(content, language, rel_path)
                    
                    # Create file document in Cosmos DB
                    file_id = str(uuid.uuid4())
                    file_doc = {
                        'id': file_id,
                        'project_id': project_id,
                        'file_path': rel_path,
                        'language': language,
                        'status': 'indexed',
                        'chunk_count': len(chunks),
                        'indexed_date': datetime.utcnow().isoformat()
                    }
                    cosmos_service.create_file(file_doc)
                    
                    # Add file_id and project_id to chunks
                    for chunk in chunks:
                        chunk['file_id'] = file_id
                        chunk['project_id'] = project_id
                    
                    all_chunks.extend(chunks)
                    file_count += 1
                    
                    logging.info(f"Processed {rel_path}: {len(chunks)} chunks")
                    
                except Exception as e:
                    logging.error(f"Failed to process {file_path}: {e}")
        
        # Generate embeddings for all chunks
        logging.info(f"Generating embeddings for {len(all_chunks)} chunks")
        chunks_with_embeddings = embedding_service.generate_embeddings_batch(all_chunks)
        
        # Index in Azure Cognitive Search
        logging.info("Indexing chunks in Azure Cognitive Search")
        search_service.index_chunks(chunks_with_embeddings)
        
        # Update project status
        project_doc['status'] = 'completed'
        project_doc['file_count'] = file_count
        project_doc['chunk_count'] = len(all_chunks)
        project_doc['completed_date'] = datetime.utcnow().isoformat()
        cosmos_service.update_project(project_id, project_doc)
        
        logging.info(f"Ingestion completed: {file_count} files, {len(all_chunks)} chunks")
        
        return {
            'project_id': project_id,
            'project_name': project_name,
            'file_count': file_count,
            'chunk_count': len(all_chunks),
            'status': 'completed'
        }


def is_code_file(file_path: Path) -> bool:
    """Check if file is a code file"""
    code_extensions = {
        '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
        '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.r',
        '.m', '.mm', '.sh', '.bash', '.sql', '.html', '.css', '.scss', '.sass',
        '.vue', '.json', '.yaml', '.yml', '.xml', '.md', '.txt'
    }
    return file_path.suffix.lower() in code_extensions


def detect_language(file_path: Path) -> str:
    """Detect programming language from file extension"""
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.sh': 'bash',
        '.bash': 'bash',
        '.sql': 'sql',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.vue': 'vue',
        '.md': 'markdown',
    }
    return extension_map.get(file_path.suffix.lower(), 'text')