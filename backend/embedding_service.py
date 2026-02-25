"""
Embedding Service - Generates vector embeddings using Azure OpenAI
"""

import os
import logging
from typing import List, Dict
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


class EmbeddingService:
    """Handles embedding generation using Azure OpenAI"""
    
    def __init__(self):
        """Initialize Azure OpenAI client"""
        api_key = os.getenv('AZURE_OPENAI_KEY')
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        deployment = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-ada-002')
        
        if not api_key or api_key == "REPLACE_WITH_YOUR_AZURE_KEY":
            raise ValueError("Azure OpenAI API key not configured")
        
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        self.deployment = deployment
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.deployment
            )
            return response.data[0].embedding
        except Exception as e:
            logging.error(f"Failed to generate embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, chunks: List[Dict], batch_size: int = 16) -> List[Dict]:
        """
        Generate embeddings for multiple chunks in batches
        
        Args:
            chunks: List of chunk dictionaries
            batch_size: Number of chunks to process at once
            
        Returns:
            List of chunks with embeddings added
        """
        logging.info(f"Generating embeddings for {len(chunks)} chunks")
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [chunk['content'] for chunk in batch]
            
            try:
                # Generate embeddings for batch
                response = self.client.embeddings.create(
                    input=texts,
                    model=self.deployment
                )
                
                # Add embeddings to chunks
                for j, embedding_data in enumerate(response.data):
                    batch[j]['embedding'] = embedding_data.embedding
                
                logging.info(f"Generated embeddings for batch {i // batch_size + 1}")
                
            except Exception as e:
                logging.error(f"Failed to generate embeddings for batch: {e}")
                # Add empty embeddings for failed batch
                for chunk in batch:
                    chunk['embedding'] = [0.0] * 1536  # Default dimension for ada-002
        
        return chunks