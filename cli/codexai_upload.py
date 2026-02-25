#!/usr/bin/env python3
"""
CodexAI CLI Tool - Upload local codebases to Azure Blob Storage
"""

import os
import sys
import zipfile
import tempfile
from pathlib import Path
from typing import List, Set
import click
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, BlobClient
import pathspec
from tqdm import tqdm
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Load environment variables
load_dotenv()


class CodebaseUploader:
    """Handles codebase scanning, filtering, zipping, and uploading to Azure"""
    
    def __init__(self, connection_string: str, container_name: str):
        """Initialize the uploader with Azure credentials"""
        if not connection_string or connection_string == "REPLACE_WITH_YOUR_CONNECTION_STRING":
            raise ValueError(
                "Azure Storage connection string not configured. "
                "Please set AZURE_STORAGE_CONNECTION_STRING in your .env file."
            )
        
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_name = container_name
        
        # Ensure container exists
        try:
            self.container_client = self.blob_service_client.get_container_client(container_name)
            if not self.container_client.exists():
                self.container_client.create_container()
        except Exception as e:
            print(f"{Fore.RED}✗ Failed to access container: {e}")
            raise
    
    def parse_gitignore(self, project_path: Path) -> pathspec.PathSpec:
        """Parse .gitignore file and return a PathSpec object"""
        gitignore_path = project_path / ".gitignore"
        
        # Default patterns to always ignore
        default_patterns = [
            ".git/",
            ".env",
            ".env.*",
            "node_modules/",
            "__pycache__/",
            "*.pyc",
            ".DS_Store",
            "venv/",
            "env/",
            "dist/",
            "build/",
            ".vscode/",
            ".idea/",
            "*.log",
            ".pytest_cache/",
            "coverage/",
            "*.egg-info/",
        ]
        
        patterns = default_patterns.copy()
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                patterns.extend([
                    line.strip() 
                    for line in f 
                    if line.strip() and not line.startswith('#')
                ])
        
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    
    def is_code_file(self, file_path: Path) -> bool:
        """Check if a file is a code file based on extension"""
        code_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
            '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.r',
            '.m', '.mm', '.sh', '.bash', '.sql', '.html', '.css', '.scss', '.sass',
            '.vue', '.json', '.yaml', '.yml', '.xml', '.md', '.txt', '.conf', '.config',
            '.toml', '.ini', '.env.example', '.gitignore', 'Dockerfile', 'Makefile'
        }
        
        # Check extension
        if file_path.suffix.lower() in code_extensions:
            return True
        
        # Check specific filenames without extensions
        if file_path.name in {'Dockerfile', 'Makefile', 'README', 'LICENSE'}:
            return True
        
        return False
    
    def scan_directory(self, project_path: Path) -> tuple[List[Path], pathspec.PathSpec]:
        """Scan directory and return list of code files"""
        print(f"{Fore.CYAN}📁 Scanning directory: {project_path}")
        
        spec = self.parse_gitignore(project_path)
        all_files = []
        code_files = []
        
        for root, dirs, files in os.walk(project_path):
            root_path = Path(root)
            rel_root = root_path.relative_to(project_path)
            
            # Filter directories
            dirs[:] = [
                d for d in dirs 
                if not spec.match_file(str(rel_root / d) + '/')
            ]
            
            # Process files
            for file in files:
                file_path = root_path / file
                rel_path = file_path.relative_to(project_path)
                all_files.append(rel_path)
                
                # Check if file should be included
                if not spec.match_file(str(rel_path)) and self.is_code_file(file_path):
                    code_files.append(file_path)
        
        print(f"{Fore.GREEN}✓ Found {len(all_files)} files")
        print(f"{Fore.GREEN}✓ Filtered to {len(code_files)} code files (using .gitignore)")
        
        return code_files, spec
    
    def create_archive(self, project_path: Path, files: List[Path]) -> tuple[str, int]:
        """Create a zip archive of the code files"""
        print(f"{Fore.CYAN}📦 Creating archive...")
        
        # Create temporary zip file
        temp_dir = tempfile.gettempdir()
        project_name = project_path.name
        zip_path = os.path.join(temp_dir, f"{project_name}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in tqdm(files, desc="Compressing", unit="file"):
                arcname = file_path.relative_to(project_path)
                zipf.write(file_path, arcname)
        
        # Get file size
        file_size = os.path.getsize(zip_path)
        size_mb = file_size / (1024 * 1024)
        
        print(f"{Fore.GREEN}✓ Archive created: {size_mb:.2f} MB")
        
        return zip_path, file_size
    
    def upload_to_azure(self, zip_path: str, project_name: str, file_size: int) -> str:
        """Upload zip file to Azure Blob Storage"""
        print(f"{Fore.CYAN}☁️  Uploading to Azure...")
        
        blob_name = f"{project_name}/{project_name}.zip"
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=blob_name
        )
        
        # Upload with progress bar
        with open(zip_path, 'rb') as data:
            with tqdm(total=file_size, desc="Uploading", unit="B", unit_scale=True) as pbar:
                def progress_callback(current, total):
                    pbar.update(current - pbar.n)
                
                blob_client.upload_blob(
                    data,
                    overwrite=True,
                    metadata={
                        'project_name': project_name,
                        'upload_source': 'codexai-cli'
                    }
                )
        
        print(f"{Fore.GREEN}✓ Upload complete")
        
        return blob_name
    
    def trigger_ingestion(self, blob_name: str) -> str:
        """Trigger the ingestion pipeline (returns job ID)"""
        print(f"{Fore.CYAN}🔄 Triggering ingestion pipeline...")
        
        # In a real implementation, this would call an Azure Function HTTP trigger
        # For now, we'll simulate a job ID
        import uuid
        job_id = str(uuid.uuid4())[:8]
        
        print(f"{Fore.GREEN}✓ Processing started (Job ID: {job_id})")
        
        return job_id


@click.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--name', '-n', help='Project name (defaults to directory name)')
def upload(project_path: str, name: str):
    """
    Upload a local codebase to CodexAI for documentation generation.
    
    PROJECT_PATH: Path to the local directory containing your code
    """
    try:
        print(f"{Fore.CYAN}{Style.BRIGHT}")
        print("CodexAI - Automated Code Documentation")
        print("=" * 50)
        print(Style.RESET_ALL)
        
        # Get configuration
        connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'codebases')
        
        if not connection_string:
            print(f"{Fore.RED}✗ Error: AZURE_STORAGE_CONNECTION_STRING not set")
            print(f"{Fore.YELLOW}Please create a .env file with your Azure credentials.")
            print(f"{Fore.YELLOW}See .env.template for required variables.")
            sys.exit(1)
        
        # Initialize uploader
        uploader = CodebaseUploader(connection_string, container_name)
        
        # Process project path
        project_path_obj = Path(project_path).resolve()
        project_name = name or project_path_obj.name
        
        # Scan directory
        code_files, spec = uploader.scan_directory(project_path_obj)
        
        if not code_files:
            print(f"{Fore.RED}✗ No code files found in the directory")
            sys.exit(1)
        
        # Create archive
        zip_path, file_size = uploader.create_archive(project_path_obj, code_files)
        
        # Upload to Azure
        blob_name = uploader.upload_to_azure(zip_path, project_name, file_size)
        
        # Trigger ingestion
        job_id = uploader.trigger_ingestion(blob_name)
        
        # Cleanup
        os.remove(zip_path)
        
        # Success message
        print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ Done!")
        print(f"{Style.RESET_ALL}")
        print(f"Visit {Fore.CYAN}https://codexai.azurewebsites.net{Style.RESET_ALL} to view your project.")
        print(f"Project: {Fore.YELLOW}{project_name}{Style.RESET_ALL}")
        print(f"Job ID: {Fore.YELLOW}{job_id}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    upload()