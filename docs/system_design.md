# CodexAI System Design Document

## 1. Implementation Approach

### 1.1 Architecture Philosophy
CodexAI follows a **serverless-first, event-driven architecture** leveraging Azure's managed services to minimize operational overhead while maintaining cost efficiency. The system is designed around three core principles:

1. **Separation of Concerns**: CLI tool (upload) → Ingestion (indexing) → RAG (generation) are decoupled via event triggers
2. **Cost Optimization**: Serverless consumption plans, vector caching, and token limiting strategies
3. **Security by Design**: Zero hardcoded credentials, environment-based configuration, and Azure managed identities

### 1.2 Technology Stack Rationale

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Frontend** | React (Vite) + TypeScript | Fast dev experience, type safety, modern tooling |
| **Backend** | Azure Functions (Python) | Serverless, event-driven, auto-scaling, pay-per-execution |
| **Storage** | Azure Blob Storage | Cost-effective object storage with event triggers |
| **Metadata DB** | Cosmos DB (Serverless) | NoSQL flexibility, auto-scaling, pay-per-request |
| **Vector Search** | Azure Cognitive Search | Native vector support, hybrid search, managed service |
| **Embeddings** | text-embedding-ada-002 | High quality, 1536 dimensions, cost-effective |
| **LLM** | gpt-4o-mini | Optimized for cost, sufficient for documentation tasks |

### 1.3 Critical Technical Challenges

1. **Code Chunking Strategy**
   - **Challenge**: Maintaining semantic coherence while respecting token limits
   - **Solution**: Language-aware parsing using AST (Abstract Syntax Tree) to chunk by function/class boundaries with configurable overlap

2. **Context Window Management**
   - **Challenge**: Balancing context richness vs. token costs
   - **Solution**: Implement tiered retrieval (top-10 vector search → re-rank by relevance → limit to 4000 tokens)

3. **Cold Start Latency**
   - **Challenge**: Azure Functions cold starts can delay first request
   - **Solution**: Keep functions warm with scheduled pings, optimize dependencies

4. **Cost Control**
   - **Challenge**: Unbounded LLM API costs
   - **Solution**: Token counting pre-flight checks, user credit limits, caching of embeddings

### 1.4 Open Source Dependencies

- **Python**: `azure-functions`, `azure-storage-blob`, `azure-cosmos`, `azure-search-documents`, `openai`, `tiktoken`, `tree-sitter` (code parsing)
- **Frontend**: `react`, `vite`, `@azure/storage-blob`, `axios`, `react-markdown`, `prismjs` (syntax highlighting)

---

## 2. User & UI Interaction Patterns

### 2.1 Primary User Flows

#### Flow 1: Upload Codebase (CLI)
1. Developer runs `python cli/upload.py --dir ./my-project --name "MyProject"`
2. CLI filters files using `.gitignore` patterns
3. CLI zips codebase and uploads to Azure Blob Storage
4. CLI displays upload confirmation with project ID
5. Background ingestion starts automatically (user notified via UI)

#### Flow 2: Browse Projects (Web UI)
1. User navigates to CodexAI web interface
2. System displays list of uploaded projects with status (Processing/Indexed/Failed)
3. User clicks on a project to view file tree
4. File tree shows all indexed files with metadata (language, size, doc status)

#### Flow 3: Generate Documentation (Web UI)
1. User selects a file from the tree (e.g., `src/api.py`)
2. User clicks "Generate Documentation" button
3. Modal appears with options:
   - Documentation type: API Reference / Tutorial / Overview
   - Include tests: Yes/No
   - Include dependencies: Yes/No
4. User confirms, system shows loading spinner
5. Generated Markdown documentation appears in right panel
6. User can copy, download, or regenerate with different options

#### Flow 4: View/Edit Documentation
1. User clicks on a file with existing documentation
2. Documentation loads in Markdown viewer with syntax highlighting
3. User can toggle between "View" and "Raw" modes
4. User can download as `.md` file or copy to clipboard

### 2.2 UI Interaction Details

- **Responsive Design**: Mobile-first approach, collapsible sidebar on small screens
- **Real-time Updates**: WebSocket connection for ingestion progress (optional MVP+)
- **Error Handling**: Toast notifications for API errors, retry buttons for failed operations
- **Accessibility**: ARIA labels, keyboard navigation, screen reader support

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  ┌──────────────┐                        ┌──────────────┐       │
│  │  CLI Tool    │                        │  Web Browser │       │
│  │  (Python)    │                        │  (React)     │       │
│  └──────┬───────┘                        └──────┬───────┘       │
└─────────┼────────────────────────────────────────┼──────────────┘
          │                                        │
          │ 1. Upload                              │ 2. HTTP Requests
          ▼                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Azure Cloud Layer                           │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Frontend - Azure App Service                 │  │
│  │                 React Web UI (Vite)                       │  │
│  └───────────────────────────┬──────────────────────────────┘  │
│                              │                                   │
│                              │ HTTP                              │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │     Backend - Azure Functions (Consumption Plan)          │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │   Blob     │  │ Ingestion  │  │    RAG     │         │  │
│  │  │  Trigger   │  │  Function  │  │ Inference  │         │  │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘         │  │
│  │        │               │               │                  │  │
│  │        │ 3. Event      │ 4. Embed      │ 6. Search        │  │
│  │        ▼               ▼               ▼                  │  │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Azure Blob   │  │  Cosmos DB   │  │  Cognitive   │         │
│  │   Storage    │  │ (Metadata)   │  │   Search     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Azure OpenAI Service                         │  │
│  │  ┌─────────────────────┐  ┌─────────────────────┐       │  │
│  │  │ text-embedding-ada  │  │    gpt-4o-mini      │       │  │
│  │  └─────────────────────┘  └─────────────────────┘       │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

See `architect.plantuml` for detailed component diagram.

### 3.2 Data Flow

#### Upload → Ingestion Flow
```
CLI → Blob Storage (upload) → Blob Trigger → Ingestion Function
                                                    ↓
                                        ┌───────────┴───────────┐
                                        ▼                       ▼
                                  Azure OpenAI           Cognitive Search
                                  (embeddings)           (vector index)
                                        ↓                       ↓
                                        └───────────┬───────────┘
                                                    ▼
                                              Cosmos DB
                                              (metadata)
```

#### RAG Inference Flow
```
Web UI → API Function → RAG Function
                            ↓
                    ┌───────┴───────┐
                    ▼               ▼
            Cognitive Search    Cosmos DB
            (vector search)     (file content)
                    ↓               ↓
                    └───────┬───────┘
                            ▼
                      Azure OpenAI
                      (gpt-4o-mini)
                            ↓
                      Cosmos DB
                      (save docs)
```

### 3.3 Component Breakdown

#### 3.3.1 CLI Tool (`/cli`)
- **Responsibility**: Local codebase preparation and upload
- **Key Functions**:
  - `zip_codebase()`: Filter files using `.gitignore`, create zip archive
  - `upload_to_blob()`: Upload zip to Azure Blob Storage with metadata
- **Dependencies**: `azure-storage-blob`, `gitignore-parser`
- **Configuration**: `AZURE_STORAGE_CONNECTION_STRING` (env var)

#### 3.3.2 Azure Functions (`/backend`)

**A. Blob Upload Trigger**
- **Trigger**: Blob created event in `codebases` container
- **Responsibility**: Initialize project metadata, trigger ingestion
- **Output**: Project record in Cosmos DB with status "processing"

**B. Ingestion Function**
- **Trigger**: Called by Blob Upload Trigger
- **Responsibility**: 
  1. Extract zip file
  2. Parse code files using language-specific parsers (tree-sitter)
  3. Chunk code by function/class boundaries
  4. Generate embeddings via Azure OpenAI
  5. Index chunks in Cognitive Search
  6. Store metadata in Cosmos DB
- **Configuration**:
  - `CHUNK_SIZE`: 500 tokens (default)
  - `CHUNK_OVERLAP`: 50 tokens
  - `MAX_CONTEXT_TOKENS`: 4000

**C. RAG Inference Function**
- **Trigger**: HTTP request from API Gateway
- **Responsibility**:
  1. Retrieve target file content
  2. Generate query embedding
  3. Perform vector search for relevant context
  4. Build augmented prompt with context
  5. Call gpt-4o-mini for documentation generation
  6. Save documentation to Cosmos DB
- **Token Management**: Pre-flight token counting, truncate context if exceeds limit

**D. API Gateway Function**
- **Trigger**: HTTP requests from Web UI
- **Endpoints**:
  - `GET /api/projects`: List user projects
  - `GET /api/projects/{id}/files`: Get project file tree
  - `POST /api/generate-docs`: Trigger documentation generation
  - `GET /api/docs/{project_id}/{file_path}`: Retrieve documentation

#### 3.3.3 React Frontend (`/frontend`)
- **Framework**: Vite + React 18 + TypeScript
- **Key Components**:
  - `ProjectList`: Display uploaded projects with status
  - `FileExplorer`: Tree view of project files
  - `DocumentationViewer`: Markdown renderer with syntax highlighting
  - `GenerateDocModal`: Configuration dialog for doc generation
- **State Management**: React Context API (or Zustand for MVP+)
- **Styling**: Tailwind CSS for utility-first styling

---

## 4. Data Structures & Interfaces

### 4.1 Cosmos DB Schema

#### Collection: `projects`
```json
{
  "id": "proj_abc123",
  "partition_key": "user_001",
  "user_id": "user_001",
  "name": "MyProject",
  "blob_name": "proj_abc123.zip",
  "status": "indexed",
  "upload_timestamp": "2024-01-09T10:00:00Z",
  "file_count": 42,
  "total_size": 1048576,
  "indexed_at": "2024-01-09T10:05:00Z",
  "metadata": {
    "languages": ["python", "javascript"],
    "framework": "FastAPI"
  }
}
```

#### Collection: `file_metadata`
```json
{
  "id": "file_001",
  "partition_key": "proj_abc123",
  "project_id": "proj_abc123",
  "file_path": "src/api.py",
  "language": "python",
  "size": 2048,
  "chunk_count": 5,
  "has_documentation": true,
  "last_updated": "2024-01-09T10:05:00Z",
  "hash": "sha256_hash",
  "imports": ["fastapi", "pydantic"],
  "exports": ["app", "router"]
}
```

#### Collection: `documentation`
```json
{
  "id": "doc_001",
  "partition_key": "proj_abc123",
  "project_id": "proj_abc123",
  "file_path": "src/api.py",
  "content": "# API Reference\n\n## Endpoints...",
  "doc_type": "api_reference",
  "generated_at": "2024-01-09T10:10:00Z",
  "token_count": 2300,
  "cost": 0.0023,
  "prompt_tokens": 1500,
  "completion_tokens": 800,
  "context_files": ["src/models.py", "tests/test_api.py"]
}
```

### 4.2 Azure Cognitive Search Index

#### Index: `code-chunks`
```json
{
  "name": "code-chunks",
  "fields": [
    {"name": "chunk_id", "type": "Edm.String", "key": true},
    {"name": "project_id", "type": "Edm.String", "filterable": true},
    {"name": "file_path", "type": "Edm.String", "searchable": true},
    {"name": "content", "type": "Edm.String", "searchable": true},
    {"name": "embedding", "type": "Collection(Edm.Single)", "dimensions": 1536, "vectorSearchProfile": "default"},
    {"name": "start_line", "type": "Edm.Int32"},
    {"name": "end_line", "type": "Edm.Int32"},
    {"name": "chunk_type", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "language", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "function_name", "type": "Edm.String", "searchable": true},
    {"name": "class_name", "type": "Edm.String", "searchable": true}
  ],
  "vectorSearch": {
    "profiles": [
      {
        "name": "default",
        "algorithm": "hnsw",
        "vectorizer": null
      }
    ]
  }
}
```

### 4.3 API Contracts

#### POST /api/generate-docs
**Request:**
```json
{
  "project_id": "proj_abc123",
  "file_path": "src/api.py",
  "doc_type": "api_reference",
  "include_tests": true,
  "include_dependencies": true
}
```

**Response:**
```json
{
  "status": "completed",
  "documentation_id": "doc_001",
  "content": "# API Reference\n\n...",
  "token_count": 2300,
  "cost": 0.0023,
  "generated_at": "2024-01-09T10:10:00Z"
}
```

#### GET /api/projects/{project_id}/files
**Response:**
```json
{
  "project_id": "proj_abc123",
  "files": [
    {
      "file_path": "src/api.py",
      "language": "python",
      "size": 2048,
      "has_documentation": true,
      "chunk_count": 5
    }
  ]
}
```

See `class_diagram.plantuml` for complete interface definitions.

---

## 5. Program Call Flow

### 5.1 Ingestion Pipeline Sequence
1. **CLI Upload** → Blob Storage (zip file)
2. **Blob Trigger** → Create project record in Cosmos DB
3. **Ingestion Function**:
   - Download zip from Blob Storage
   - Extract and parse files
   - For each file:
     - Chunk code using AST parser
     - Generate embeddings (batch API call)
     - Index chunks in Cognitive Search
     - Store file metadata in Cosmos DB
   - Update project status to "indexed"

### 5.2 RAG Inference Sequence
1. **Web UI** → POST /api/generate-docs
2. **API Gateway** → Validate request, call RAG Function
3. **RAG Function**:
   - Fetch target file from Cosmos DB
   - Generate query embedding
   - Vector search in Cognitive Search (top-10)
   - Fetch related file contents
   - Build prompt with context (limit 4000 tokens)
   - Call gpt-4o-mini
   - Parse and save documentation
4. **API Gateway** → Return documentation to UI

See `sequence_diagram.plantuml` for detailed interactions with exact input/output parameters.

---

## 6. Code Chunking & Embedding Strategy

### 6.1 Chunking Algorithm

**Language-Aware Parsing:**
- Use `tree-sitter` library for AST-based parsing
- Supported languages: Python, JavaScript, TypeScript, Java, Go

**Chunking Rules:**
1. **Primary Boundary**: Function/method definitions
2. **Secondary Boundary**: Class definitions (if no functions, chunk entire class)
3. **Fallback**: Line-based chunking (500 tokens) with 50-token overlap
4. **Metadata Extraction**:
   - Function name, class name
   - Docstrings
   - Import statements
   - Decorators/annotations

**Example (Python):**
```python
# Original file: api.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.post("/process")
def process_data(data: dict):
    """Process incoming data"""
    return {"result": "processed"}
```

**Chunks Generated:**
```json
[
  {
    "chunk_id": "chunk_001",
    "content": "from fastapi import FastAPI\n\napp = FastAPI()",
    "chunk_type": "import",
    "start_line": 1,
    "end_line": 3
  },
  {
    "chunk_id": "chunk_002",
    "content": "@app.get(\"/health\")\ndef health_check():\n    \"\"\"Health check endpoint\"\"\"\n    return {\"status\": \"ok\"}",
    "chunk_type": "function",
    "function_name": "health_check",
    "start_line": 5,
    "end_line": 8
  },
  {
    "chunk_id": "chunk_003",
    "content": "@app.post(\"/process\")\ndef process_data(data: dict):\n    \"\"\"Process incoming data\"\"\"\n    return {\"result\": \"processed\"}",
    "chunk_type": "function",
    "function_name": "process_data",
    "start_line": 10,
    "end_line": 13
  }
]
```

### 6.2 Embedding Strategy

**Model**: `text-embedding-ada-002` (1536 dimensions)

**Batch Processing**:
- Group chunks into batches of 100
- Single API call per batch to minimize latency
- Retry logic for failed batches

**Caching**:
- Store embeddings in Cognitive Search (persistent)
- No re-embedding on re-indexing unless file hash changes

**Cost Calculation**:
- $0.0001 per 1K tokens
- Average file (2KB) → ~500 tokens → $0.00005 per file

---

## 7. Security Architecture

### 7.1 Credential Management

**Environment Variables (Required):**
```bash
# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini

# Azure Cognitive Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_KEY=your-admin-key
AZURE_SEARCH_INDEX_NAME=code-chunks

# Cosmos DB
COSMOS_ENDPOINT=https://your-cosmos.documents.azure.com:443/
COSMOS_KEY=your-primary-key
COSMOS_DATABASE_NAME=codexai
```

**Best Practices:**
1. **Never commit `.env` files** to version control
2. Use **Azure Key Vault** for production deployments
3. Rotate keys every 90 days
4. Use **Managed Identities** for Azure Functions (production)

### 7.2 Authentication & Authorization

**MVP Scope:**
- No user authentication (single-user mode)
- API Gateway validates requests via shared secret

**Production Roadmap:**
- Azure AD B2C for user authentication
- Role-based access control (RBAC)
- Project-level permissions

### 7.3 Data Privacy

- **Code Storage**: Encrypted at rest (Azure Blob Storage default)
- **Data Retention**: User-controlled deletion of projects
- **Compliance**: GDPR-ready (data export/deletion APIs)

---

## 8. Deployment Architecture

### 8.1 Azure Resources

| Resource | SKU/Tier | Purpose | Estimated Cost |
|----------|----------|---------|----------------|
| App Service | B1 (Basic) | Host React frontend | $13/month |
| Function App | Consumption | Serverless backend | $0.20/million executions |
| Blob Storage | Standard LRS | Code archives | $0.02/GB |
| Cosmos DB | Serverless | Metadata storage | $0.25/million RUs |
| Cognitive Search | Basic | Vector search | $75/month |
| OpenAI | Pay-as-you-go | Embeddings + LLM | Variable |

**Total Estimated Cost (MVP)**: ~$100-150/month for moderate usage

### 8.2 CI/CD Pipeline

**GitHub Actions Workflow:**
1. **Frontend**: Build React app → Deploy to App Service
2. **Backend**: Package Azure Functions → Deploy to Function App
3. **Infrastructure**: Terraform/Bicep for resource provisioning (optional)

**Deployment Steps:**
```yaml
# .github/workflows/deploy.yml
- name: Build Frontend
  run: cd frontend && npm run build
  
- name: Deploy to App Service
  uses: azure/webapps-deploy@v2
  with:
    app-name: codexai-frontend
    
- name: Deploy Functions
  run: func azure functionapp publish codexai-backend
```

### 8.3 Environment Configuration

**Development:**
- Local Azure Functions runtime
- Azurite for Blob Storage emulation
- Cosmos DB emulator

**Production:**
- Azure-hosted resources
- Application Insights for monitoring
- Azure Monitor for alerts

---

## 9. Database ER Diagram Overview

The system uses **Cosmos DB** for metadata and **Cognitive Search** for vector embeddings.

**Key Relationships:**
- `projects` (1) → (N) `file_metadata`
- `projects` (1) → (N) `documentation`
- `file_metadata` (1) → (1) `documentation`

**Partitioning Strategy:**
- `projects`: Partitioned by `user_id`
- `file_metadata`: Partitioned by `project_id`
- `documentation`: Partitioned by `project_id`

See `er_diagram.plantuml` for complete schema.

---

## 10. Unclear Aspects & Assumptions

### 10.1 Clarifications Needed

1. **User Authentication**: Should MVP include multi-user support, or is single-user sufficient?
   - **Assumption**: Single-user mode for MVP, add auth in v2

2. **Supported Languages**: Which programming languages should be prioritized?
   - **Assumption**: Python, JavaScript, TypeScript (expand based on demand)

3. **Documentation Types**: What formats beyond API reference are needed?
   - **Assumption**: API Reference, Tutorial, Overview (configurable)

4. **Cost Limits**: Should there be per-user credit limits?
   - **Assumption**: No limits for MVP, add in production

### 10.2 Technical Assumptions

1. **Code Size**: Average project size < 100MB (zip file)
2. **Concurrency**: < 10 concurrent documentation generations
3. **Latency**: Acceptable doc generation time < 30 seconds
4. **Accuracy**: LLM-generated docs require human review (no guarantees)

### 10.3 Future Enhancements

- **Real-time Collaboration**: Multiple users editing documentation
- **Version Control**: Track documentation changes over time
- **Custom Templates**: User-defined documentation formats
- **IDE Integration**: VS Code extension for in-editor doc generation

---

## 11. Success Metrics

1. **Functional**:
   - 95% successful ingestion rate
   - < 30s average documentation generation time
   - 90% user satisfaction with doc quality

2. **Performance**:
   - < 5s API response time (p95)
   - < 10s cold start time for Azure Functions

3. **Cost**:
   - < $0.10 per documentation generation
   - < $200/month total Azure costs (MVP)

---

## Appendix: File Structure

See `file_tree.md` for complete project structure.