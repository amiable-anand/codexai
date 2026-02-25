"""
API Handler - Handles HTTP API requests
"""

import logging
from typing import List, Dict, Optional

from cosmos_service import CosmosService


def handle_list_projects() -> List[Dict]:
    """List all projects"""
    cosmos_service = CosmosService()
    projects = cosmos_service.list_projects()
    
    # Format response
    return [
        {
            'id': p['id'],
            'name': p['name'],
            'status': p['status'],
            'upload_date': p['upload_date'],
            'file_count': p.get('file_count', 0),
            'chunk_count': p.get('chunk_count', 0)
        }
        for p in projects
    ]


def handle_list_files(project_id: str) -> Dict:
    """List all files in a project"""
    cosmos_service = CosmosService()
    
    # Get project
    project = cosmos_service.get_project(project_id)
    if not project:
        raise ValueError(f"Project not found: {project_id}")
    
    # Get files
    files = cosmos_service.list_files(project_id)
    
    # Format response
    return {
        'project_id': project_id,
        'project_name': project['name'],
        'files': [
            {
                'id': f['id'],
                'file_path': f['file_path'],
                'language': f['language'],
                'status': f['status'],
                'chunk_count': f.get('chunk_count', 0)
            }
            for f in files
        ]
    }


def handle_get_documentation(doc_id: str) -> Optional[Dict]:
    """Get documentation by ID"""
    cosmos_service = CosmosService()
    
    # Note: We need project_id to query, but it's not in the URL
    # This is a simplified version - in production, you'd need to query across partitions
    # or store doc_id in a separate index
    
    # For now, return None - this would need to be improved
    logging.warning("get_documentation needs project_id for efficient querying")
    return None