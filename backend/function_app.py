"""
Azure Functions for CodexAI
Handles ingestion, RAG inference, and API endpoints
"""

import azure.functions as func
import logging
import json

app = func.FunctionApp()

# Import handlers
from ingestion_handler import handle_ingestion
from rag_handler import handle_generate_documentation
from api_handler import handle_list_projects, handle_list_files, handle_get_documentation


@app.blob_trigger(
    arg_name="myblob",
    path="codebases/{project_name}/{filename}",
    connection="AZURE_STORAGE_CONNECTION_STRING"
)
def ingestion_trigger(myblob: func.InputStream):
    """
    Triggered when a new codebase is uploaded to Blob Storage.
    Processes the code, generates embeddings, and indexes in Cognitive Search.
    """
    logging.info(f"Ingestion triggered for: {myblob.name}, Size: {myblob.length} bytes")
    
    try:
        # Extract project name from blob path
        path_parts = myblob.name.split('/')
        project_name = path_parts[1] if len(path_parts) > 1 else "unknown"
        
        # Read blob content
        blob_content = myblob.read()
        
        # Process the codebase
        result = handle_ingestion(project_name, blob_content)
        
        logging.info(f"Ingestion completed for {project_name}: {result}")
        
    except Exception as e:
        logging.error(f"Ingestion failed: {str(e)}")
        raise


@app.route(route="generate-documentation", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def generate_documentation(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP endpoint to generate documentation for a specific file or function.
    Uses RAG to retrieve relevant context and generate comprehensive docs.
    """
    logging.info("Generate documentation request received")
    
    try:
        # Parse request body
        req_body = req.get_json()
        project_id = req_body.get('project_id')
        file_path = req_body.get('file_path')
        target = req_body.get('target')  # 'file' or specific function name
        
        if not project_id or not file_path:
            return func.HttpResponse(
                json.dumps({"error": "project_id and file_path are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Generate documentation
        result = handle_generate_documentation(project_id, file_path, target)
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Documentation generation failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="projects", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def list_projects(req: func.HttpRequest) -> func.HttpResponse:
    """List all uploaded projects"""
    logging.info("List projects request received")
    
    try:
        projects = handle_list_projects()
        
        return func.HttpResponse(
            json.dumps(projects),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"List projects failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="projects/{project_id}/files", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def list_files(req: func.HttpRequest) -> func.HttpResponse:
    """List all files in a project"""
    project_id = req.route_params.get('project_id')
    logging.info(f"List files request for project: {project_id}")
    
    try:
        files = handle_list_files(project_id)
        
        return func.HttpResponse(
            json.dumps(files),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"List files failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="documentation/{doc_id}", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def get_documentation(req: func.HttpRequest) -> func.HttpResponse:
    """Get generated documentation by ID"""
    doc_id = req.route_params.get('doc_id')
    logging.info(f"Get documentation request: {doc_id}")
    
    try:
        documentation = handle_get_documentation(doc_id)
        
        if not documentation:
            return func.HttpResponse(
                json.dumps({"error": "Documentation not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        return func.HttpResponse(
            json.dumps(documentation),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Get documentation failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )