"""
Search Service - Manages Azure Cognitive Search indexing and querying
"""

import os
import logging
from typing import List, Dict
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()


class SearchService:
    """Handles Azure Cognitive Search operations"""
    
    def __init__(self):
        """Initialize Azure Cognitive Search client"""
        endpoint = os.getenv('AZURE_COGNITIVE_SEARCH_ENDPOINT')
        api_key = os.getenv('AZURE_COGNITIVE_SEARCH_KEY')
        index_name = os.getenv('AZURE_COGNITIVE_SEARCH_INDEX_NAME', 'codex-index')
        
        if not api_key or api_key == "REPLACE_WITH_YOUR_KEY":
            raise ValueError("Azure Cognitive Search API key not configured")
        
        credential = AzureKeyCredential(api_key)
        
        self.index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
        self.search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
        self.index_name = index_name
        
        # Ensure index exists
        self._ensure_index()
    
    def _ensure_index(self):
        """Create index if it doesn't exist"""
        try:
            # Check if index exists
            self.index_client.get_index(self.index_name)
            logging.info(f"Index {self.index_name} already exists")
        except Exception:
            # Create index
            logging.info(f"Creating index {self.index_name}")
            
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SimpleField(name="project_id", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="file_id", type=SearchFieldDataType.String, filterable=True),
                SearchableField(name="file_path", type=SearchFieldDataType.String),
                SearchableField(name="content", type=SearchFieldDataType.String),
                SimpleField(name="chunk_type", type=SearchFieldDataType.String, filterable=True),
                SearchableField(name="chunk_name", type=SearchFieldDataType.String),
                SimpleField(name="language", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="start_line", type=SearchFieldDataType.Int32),
                SimpleField(name="end_line", type=SearchFieldDataType.Int32),
                SimpleField(name="token_count", type=SearchFieldDataType.Int32),
                SearchField(
                    name="embedding",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="vector-profile"
                ),
            ]
            
            vector_search = VectorSearch(
                profiles=[
                    VectorSearchProfile(
                        name="vector-profile",
                        algorithm_configuration_name="hnsw-config"
                    )
                ],
                algorithms=[
                    HnswAlgorithmConfiguration(name="hnsw-config")
                ]
            )
            
            index = SearchIndex(
                name=self.index_name,
                fields=fields,
                vector_search=vector_search
            )
            
            self.index_client.create_index(index)
            logging.info(f"Index {self.index_name} created successfully")
    
    def index_chunks(self, chunks: List[Dict]):
        """
        Index chunks in Azure Cognitive Search
        
        Args:
            chunks: List of chunk dictionaries with embeddings
        """
        try:
            # Prepare documents for indexing
            documents = []
            for chunk in chunks:
                doc = {
                    'id': chunk['id'],
                    'project_id': chunk['project_id'],
                    'file_id': chunk['file_id'],
                    'file_path': chunk['file_path'],
                    'content': chunk['content'],
                    'chunk_type': chunk.get('chunk_type', 'block'),
                    'chunk_name': chunk.get('chunk_name'),
                    'language': chunk['language'],
                    'start_line': chunk['start_line'],
                    'end_line': chunk['end_line'],
                    'token_count': chunk['token_count'],
                    'embedding': chunk.get('embedding', [])
                }
                documents.append(doc)
            
            # Upload documents in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                result = self.search_client.upload_documents(documents=batch)
                logging.info(f"Indexed batch {i // batch_size + 1}: {len(batch)} documents")
            
            logging.info(f"Successfully indexed {len(documents)} chunks")
            
        except Exception as e:
            logging.error(f"Failed to index chunks: {e}")
            raise
    
    def vector_search(self, query_embedding: List[float], project_id: str, top_k: int = 5) -> List[Dict]:
        """
        Perform vector search
        
        Args:
            query_embedding: Query vector
            project_id: Filter by project ID
            top_k: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            results = self.search_client.search(
                search_text=None,
                vector_queries=[{
                    "kind": "vector",
                    "vector": query_embedding,
                    "fields": "embedding",
                    "k": top_k
                }],
                filter=f"project_id eq '{project_id}'",
                select=["id", "file_path", "content", "chunk_type", "chunk_name", "start_line", "end_line"]
            )
            
            return [
                {
                    'id': result['id'],
                    'file_path': result['file_path'],
                    'content': result['content'],
                    'chunk_type': result.get('chunk_type'),
                    'chunk_name': result.get('chunk_name'),
                    'start_line': result.get('start_line'),
                    'end_line': result.get('end_line'),
                    'score': result['@search.score']
                }
                for result in results
            ]
            
        except Exception as e:
            logging.error(f"Vector search failed: {e}")
            raise
    
    def hybrid_search(self, query_text: str, query_embedding: List[float], project_id: str, top_k: int = 5) -> List[Dict]:
        """
        Perform hybrid search (vector + keyword)
        
        Args:
            query_text: Text query
            query_embedding: Query vector
            project_id: Filter by project ID
            top_k: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            results = self.search_client.search(
                search_text=query_text,
                vector_queries=[{
                    "kind": "vector",
                    "vector": query_embedding,
                    "fields": "embedding",
                    "k": top_k
                }],
                filter=f"project_id eq '{project_id}'",
                select=["id", "file_path", "content", "chunk_type", "chunk_name", "start_line", "end_line"],
                top=top_k
            )
            
            return [
                {
                    'id': result['id'],
                    'file_path': result['file_path'],
                    'content': result['content'],
                    'chunk_type': result.get('chunk_type'),
                    'chunk_name': result.get('chunk_name'),
                    'start_line': result.get('start_line'),
                    'end_line': result.get('end_line'),
                    'score': result['@search.score']
                }
                for result in results
            ]
            
        except Exception as e:
            logging.error(f"Hybrid search failed: {e}")
            raise