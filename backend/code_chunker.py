"""
Code Chunker - Intelligently splits code into logical chunks
"""

import re
import uuid
from typing import List, Dict
import tiktoken


class CodeChunker:
    """Chunks code into logical units (functions, classes, modules)"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target size in tokens
            chunk_overlap: Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def chunk_code(self, content: str, language: str, file_path: str) -> List[Dict]:
        """
        Chunk code content into logical units
        
        Args:
            content: Code content
            language: Programming language
            file_path: File path
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        
        # Try language-specific chunking first
        if language == 'python':
            chunks = self._chunk_python(content, file_path)
        elif language in ['javascript', 'typescript']:
            chunks = self._chunk_javascript(content, file_path)
        else:
            # Fall back to simple line-based chunking
            chunks = self._chunk_by_lines(content, file_path, language)
        
        # If no chunks created, create one chunk for entire file
        if not chunks:
            chunks = [{
                'id': str(uuid.uuid4()),
                'file_path': file_path,
                'content': content,
                'chunk_type': 'file',
                'language': language,
                'start_line': 1,
                'end_line': len(content.split('\n')),
                'token_count': len(self.encoding.encode(content))
            }]
        
        return chunks
    
    def _chunk_python(self, content: str, file_path: str) -> List[Dict]:
        """Chunk Python code by functions and classes"""
        chunks = []
        lines = content.split('\n')
        
        # Simple regex-based detection (could be improved with AST)
        current_chunk = []
        current_type = None
        current_name = None
        start_line = 0
        indent_level = 0
        
        for i, line in enumerate(lines, 1):
            # Detect function or class definition
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                # Save previous chunk if exists
                if current_chunk:
                    chunk_content = '\n'.join(current_chunk)
                    token_count = len(self.encoding.encode(chunk_content))
                    
                    chunks.append({
                        'id': str(uuid.uuid4()),
                        'file_path': file_path,
                        'content': chunk_content,
                        'chunk_type': current_type,
                        'chunk_name': current_name,
                        'language': 'python',
                        'start_line': start_line,
                        'end_line': i - 1,
                        'token_count': token_count
                    })
                
                # Start new chunk
                current_chunk = [line]
                start_line = i
                indent_level = len(line) - len(line.lstrip())
                
                if line.strip().startswith('def '):
                    current_type = 'function'
                    match = re.match(r'\s*def\s+(\w+)', line)
                    current_name = match.group(1) if match else 'unknown'
                else:
                    current_type = 'class'
                    match = re.match(r'\s*class\s+(\w+)', line)
                    current_name = match.group(1) if match else 'unknown'
            
            elif current_chunk:
                # Check if we're still in the same block
                line_indent = len(line) - len(line.lstrip()) if line.strip() else indent_level + 1
                
                if line.strip() and line_indent <= indent_level:
                    # End of current block
                    chunk_content = '\n'.join(current_chunk)
                    token_count = len(self.encoding.encode(chunk_content))
                    
                    chunks.append({
                        'id': str(uuid.uuid4()),
                        'file_path': file_path,
                        'content': chunk_content,
                        'chunk_type': current_type,
                        'chunk_name': current_name,
                        'language': 'python',
                        'start_line': start_line,
                        'end_line': i - 1,
                        'token_count': token_count
                    })
                    
                    current_chunk = []
                    current_type = None
                    current_name = None
                else:
                    current_chunk.append(line)
        
        # Save last chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            token_count = len(self.encoding.encode(chunk_content))
            
            chunks.append({
                'id': str(uuid.uuid4()),
                'file_path': file_path,
                'content': chunk_content,
                'chunk_type': current_type,
                'chunk_name': current_name,
                'language': 'python',
                'start_line': start_line,
                'end_line': len(lines),
                'token_count': token_count
            })
        
        return chunks
    
    def _chunk_javascript(self, content: str, file_path: str) -> List[Dict]:
        """Chunk JavaScript/TypeScript code by functions"""
        chunks = []
        lines = content.split('\n')
        
        current_chunk = []
        current_name = None
        start_line = 0
        brace_count = 0
        in_function = False
        
        for i, line in enumerate(lines, 1):
            # Detect function definition
            if re.search(r'\bfunction\s+(\w+)|const\s+(\w+)\s*=\s*\(|(\w+)\s*:\s*\(.*\)\s*=>', line):
                if current_chunk and not in_function:
                    # Save previous chunk
                    chunk_content = '\n'.join(current_chunk)
                    token_count = len(self.encoding.encode(chunk_content))
                    
                    chunks.append({
                        'id': str(uuid.uuid4()),
                        'file_path': file_path,
                        'content': chunk_content,
                        'chunk_type': 'function',
                        'chunk_name': current_name,
                        'language': 'javascript',
                        'start_line': start_line,
                        'end_line': i - 1,
                        'token_count': token_count
                    })
                    current_chunk = []
                
                # Extract function name
                match = re.search(r'function\s+(\w+)|const\s+(\w+)\s*=|(\w+)\s*:', line)
                if match:
                    current_name = match.group(1) or match.group(2) or match.group(3)
                
                start_line = i
                in_function = True
            
            if in_function:
                current_chunk.append(line)
                brace_count += line.count('{') - line.count('}')
                
                if brace_count == 0 and '{' in line:
                    # End of function
                    chunk_content = '\n'.join(current_chunk)
                    token_count = len(self.encoding.encode(chunk_content))
                    
                    chunks.append({
                        'id': str(uuid.uuid4()),
                        'file_path': file_path,
                        'content': chunk_content,
                        'chunk_type': 'function',
                        'chunk_name': current_name,
                        'language': 'javascript',
                        'start_line': start_line,
                        'end_line': i,
                        'token_count': token_count
                    })
                    
                    current_chunk = []
                    in_function = False
                    brace_count = 0
        
        return chunks
    
    def _chunk_by_lines(self, content: str, file_path: str, language: str) -> List[Dict]:
        """Chunk by lines with token limit"""
        chunks = []
        lines = content.split('\n')
        
        current_chunk = []
        current_tokens = 0
        start_line = 1
        
        for i, line in enumerate(lines, 1):
            line_tokens = len(self.encoding.encode(line))
            
            if current_tokens + line_tokens > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_content = '\n'.join(current_chunk)
                
                chunks.append({
                    'id': str(uuid.uuid4()),
                    'file_path': file_path,
                    'content': chunk_content,
                    'chunk_type': 'block',
                    'language': language,
                    'start_line': start_line,
                    'end_line': i - 1,
                    'token_count': current_tokens
                })
                
                # Start new chunk with overlap
                overlap_lines = current_chunk[-3:] if len(current_chunk) > 3 else current_chunk
                current_chunk = overlap_lines + [line]
                current_tokens = sum(len(self.encoding.encode(l)) for l in current_chunk)
                start_line = i - len(overlap_lines)
            else:
                current_chunk.append(line)
                current_tokens += line_tokens
        
        # Save last chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            
            chunks.append({
                'id': str(uuid.uuid4()),
                'file_path': file_path,
                'content': chunk_content,
                'chunk_type': 'block',
                'language': language,
                'start_line': start_line,
                'end_line': len(lines),
                'token_count': current_tokens
            })
        
        return chunks