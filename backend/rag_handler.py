"""
RAG (Retrieval-Augmented Generation) Handler
Generates documentation using context from vector search
"""

import os
import logging
from typing import Dict, List
import uuid
from datetime import datetime
import tiktoken

from embedding_service import EmbeddingService
from search_service import SearchService
from cosmos_service import CosmosService
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


class RAGHandler:
    """Handles RAG-based documentation generation"""
    
    def __init__(self):
        """Initialize services"""
        self.embedding_service = EmbeddingService()
        self.search_service = SearchService()
        self.cosmos_service = CosmosService()
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # Initialize Azure OpenAI for chat
        api_key = os.getenv('AZURE_OPENAI_KEY')
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        self.chat_deployment = os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT', 'gpt-4o-mini')
        
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        
        self.max_context_tokens = int(os.getenv('MAX_CONTEXT_TOKENS', '4000'))
    
    def generate_documentation(self, project_id: str, file_path: str, target: str = 'file') -> Dict:
        """
        Generate documentation for a file or specific function
        
        Args:
            project_id: Project ID
            file_path: Path to the file
            target: 'file' or specific function name
            
        Returns:
            Dict with documentation content and metadata
        """
        logging.info(f"Generating documentation for {file_path} in project {project_id}")
        
        # Get file metadata
        files = self.cosmos_service.list_files(project_id)
        target_file = next((f for f in files if f['file_path'] == file_path), None)
        
        if not target_file:
            raise ValueError(f"File not found: {file_path}")
        
        # Build query for vector search
        if target == 'file':
            query = f"Documentation for {file_path}: purpose, functions, classes, and usage"
        else:
            query = f"Documentation for function {target} in {file_path}: purpose, parameters, return value, and usage"
        
        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)
        
        # Perform hybrid search
        search_results = self.search_service.hybrid_search(
            query_text=query,
            query_embedding=query_embedding,
            project_id=project_id,
            top_k=10
        )
        
        logging.info(f"Found {len(search_results)} relevant chunks")
        
        # Build context from search results
        context = self._build_context(search_results, file_path)
        
        # Generate documentation using LLM
        documentation = self._generate_with_llm(file_path, target, context)
        
        # Save documentation to Cosmos DB
        doc_id = str(uuid.uuid4())
        doc_record = {
            'id': doc_id,
            'project_id': project_id,
            'file_path': file_path,
            'target': target,
            'content': documentation['content'],
            'generated_at': datetime.utcnow().isoformat(),
            'prompt_tokens': documentation['prompt_tokens'],
            'completion_tokens': documentation['completion_tokens'],
            'total_tokens': documentation['total_tokens'],
            'context_chunks': len(search_results)
        }
        
        self.cosmos_service.create_documentation(doc_record)
        
        return {
            'documentation_id': doc_id,
            'content': documentation['content'],
            'metadata': {
                'prompt_tokens': documentation['prompt_tokens'],
                'completion_tokens': documentation['completion_tokens'],
                'total_tokens': documentation['total_tokens'],
                'context_chunks': len(search_results)
            }
        }
    
    def _build_context(self, search_results: List[Dict], target_file: str) -> str:
        """Build context string from search results"""
        context_parts = []
        current_tokens = 0
        
        # Reserve tokens for system prompt and response
        available_tokens = self.max_context_tokens - 1000
        
        for result in search_results:
            chunk_text = f"\n## {result['file_path']}"
            if result.get('chunk_name'):
                chunk_text += f" - {result['chunk_type']}: {result['chunk_name']}"
            chunk_text += f"\n```\n{result['content']}\n```\n"
            
            chunk_tokens = len(self.encoding.encode(chunk_text))
            
            if current_tokens + chunk_tokens > available_tokens:
                break
            
            context_parts.append(chunk_text)
            current_tokens += chunk_tokens
        
        return "\n".join(context_parts)
    
    def _generate_with_llm(self, file_path: str, target: str, context: str) -> Dict:
        """Generate documentation using Azure OpenAI"""
        
        system_prompt = """You are an expert technical writer specializing in code documentation.
Your task is to generate comprehensive, clear, and well-structured documentation in Markdown format.

Guidelines:
1. Start with a clear overview/purpose section
2. Document all functions, classes, and methods with:
   - Purpose and description
   - Parameters (name, type, description)
   - Return values (type, description)
   - Usage examples where appropriate
3. Include information about dependencies and related files
4. Use proper Markdown formatting with headers, code blocks, and lists
5. Be concise but thorough
6. Focus on what the code does, not how it's implemented (unless relevant)
"""

        if target == 'file':
            user_prompt = f"""Generate comprehensive documentation for the file: {file_path}

Use the following context from the codebase to understand relationships and dependencies:

{context}

Generate a complete Markdown documentation that includes:
1. File Overview
2. Purpose and Responsibilities
3. Key Functions/Classes
4. Dependencies
5. Usage Examples
6. Related Files

Documentation:"""
        else:
            user_prompt = f"""Generate detailed documentation for the function '{target}' in file: {file_path}

Use the following context from the codebase:

{context}

Generate Markdown documentation that includes:
1. Function Purpose
2. Parameters (with types and descriptions)
3. Return Value (with type and description)
4. Usage Examples
5. Related Functions/Dependencies
6. Notes or Warnings (if applicable)

Documentation:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.chat_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            return {
                'content': content,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            
        except Exception as e:
            logging.error(f"LLM generation failed: {e}")
            raise


def handle_generate_documentation(project_id: str, file_path: str, target: str = 'file') -> Dict:
    """Handler function for documentation generation"""
    handler = RAGHandler()
    return handler.generate_documentation(project_id, file_path, target)