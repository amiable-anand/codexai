"""
Cosmos DB Service - Manages metadata storage
"""

import os
import logging
from typing import Dict, List, Optional
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from dotenv import load_dotenv

load_dotenv()


class CosmosService:
    """Handles Cosmos DB operations for metadata storage"""
    
    def __init__(self):
        """Initialize Cosmos DB client"""
        endpoint = os.getenv('AZURE_COSMOS_ENDPOINT')
        key = os.getenv('AZURE_COSMOS_KEY')
        database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'codexai')
        
        if not key or key == "REPLACE_WITH_YOUR_KEY":
            raise ValueError("Azure Cosmos DB key not configured")
        
        self.client = CosmosClient(endpoint, key)
        self.database_name = database_name
        
        # Ensure database and containers exist
        self._ensure_database()
        self._ensure_containers()
        
        # Get container clients
        self.projects_container = self.database.get_container_client('projects')
        self.files_container = self.database.get_container_client('files')
        self.docs_container = self.database.get_container_client('documentation_requests')
    
    def _ensure_database(self):
        """Create database if it doesn't exist"""
        try:
            self.database = self.client.create_database_if_not_exists(id=self.database_name)
            logging.info(f"Database {self.database_name} ready")
        except Exception as e:
            logging.error(f"Failed to create database: {e}")
            raise
    
    def _ensure_containers(self):
        """Create containers if they don't exist"""
        containers = [
            ('projects', '/id'),
            ('files', '/project_id'),
            ('documentation_requests', '/project_id')
        ]
        
        for container_name, partition_key in containers:
            try:
                self.database.create_container_if_not_exists(
                    id=container_name,
                    partition_key=PartitionKey(path=partition_key)
                )
                logging.info(f"Container {container_name} ready")
            except Exception as e:
                logging.error(f"Failed to create container {container_name}: {e}")
                raise
    
    def create_project(self, project_doc: Dict) -> Dict:
        """Create a new project document"""
        try:
            return self.projects_container.create_item(body=project_doc)
        except Exception as e:
            logging.error(f"Failed to create project: {e}")
            raise
    
    def update_project(self, project_id: str, project_doc: Dict) -> Dict:
        """Update an existing project document"""
        try:
            return self.projects_container.upsert_item(body=project_doc)
        except Exception as e:
            logging.error(f"Failed to update project: {e}")
            raise
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get a project by ID"""
        try:
            return self.projects_container.read_item(item=project_id, partition_key=project_id)
        except exceptions.CosmosResourceNotFoundError:
            return None
        except Exception as e:
            logging.error(f"Failed to get project: {e}")
            raise
    
    def list_projects(self) -> List[Dict]:
        """List all projects"""
        try:
            query = "SELECT * FROM c ORDER BY c.upload_date DESC"
            items = list(self.projects_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            return items
        except Exception as e:
            logging.error(f"Failed to list projects: {e}")
            raise
    
    def create_file(self, file_doc: Dict) -> Dict:
        """Create a new file document"""
        try:
            return self.files_container.create_item(body=file_doc)
        except Exception as e:
            logging.error(f"Failed to create file: {e}")
            raise
    
    def list_files(self, project_id: str) -> List[Dict]:
        """List all files in a project"""
        try:
            query = f"SELECT * FROM c WHERE c.project_id = '{project_id}'"
            items = list(self.files_container.query_items(
                query=query,
                partition_key=project_id
            ))
            return items
        except Exception as e:
            logging.error(f"Failed to list files: {e}")
            raise
    
    def get_file(self, file_id: str, project_id: str) -> Optional[Dict]:
        """Get a file by ID"""
        try:
            return self.files_container.read_item(item=file_id, partition_key=project_id)
        except exceptions.CosmosResourceNotFoundError:
            return None
        except Exception as e:
            logging.error(f"Failed to get file: {e}")
            raise
    
    def create_documentation(self, doc: Dict) -> Dict:
        """Create a documentation request record"""
        try:
            return self.docs_container.create_item(body=doc)
        except Exception as e:
            logging.error(f"Failed to create documentation: {e}")
            raise
    
    def get_documentation(self, doc_id: str, project_id: str) -> Optional[Dict]:
        """Get documentation by ID"""
        try:
            return self.docs_container.read_item(item=doc_id, partition_key=project_id)
        except exceptions.CosmosResourceNotFoundError:
            return None
        except Exception as e:
            logging.error(f"Failed to get documentation: {e}")
            raise