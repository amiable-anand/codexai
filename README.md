# CodexAI - Automated Code Documentation System

CodexAI is a RAG-powered automated code documentation system that ingests local codebases, indexes them using vector embeddings, and allows users to generate high-context Markdown documentation via a web UI.

## 🚀 Features

- **CLI Upload Tool**: Easily upload local codebases with automatic .gitignore filtering
- **Intelligent Code Chunking**: Language-aware parsing that chunks code by functions and classes
- **Vector Search**: Powered by Azure Cognitive Search for accurate context retrieval
- **RAG-based Documentation**: Generates comprehensive documentation using Azure OpenAI (gpt-4o-mini)
- **Modern Web UI**: Clean React interface for browsing projects and generating docs
- **Cost Efficient**: Token limiting and serverless architecture to minimize costs

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher**
- **Node.js 18 or higher**
- **Azure CLI** (for deployment)
- **Git**

You will also need an active **Azure subscription** with access to:
- Azure Storage Account
- Azure Cosmos DB
- Azure Cognitive Search
- Azure OpenAI Service (requires application approval)
- Azure Functions
- Azure App Service

## 🔧 Setup Guide

### 1. Clone the Repository

```bash
git clone <repository-url>
cd codexai
```

### 2. Azure Configuration

#### **CRITICAL SECURITY NOTE** ⚠️

**NEVER commit your `.env` file to version control!** 

The `.env` file contains sensitive API keys and connection strings. Always keep it in `.gitignore` and use `.env.template` as a reference.

#### Required Environment Variables

Create a `.env` file in the project root by copying `.env.template`:

```bash
cp .env.template .env
```

Then fill in your Azure credentials:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_KEY=<your-azure-openai-api-key>
AZURE_OPENAI_ENDPOINT=https://<your-resource-name>.openai.azure.com/
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure Cognitive Search Configuration
AZURE_COGNITIVE_SEARCH_ENDPOINT=https://<your-search-service>.search.windows.net
AZURE_COGNITIVE_SEARCH_KEY=<your-admin-key>
AZURE_COGNITIVE_SEARCH_INDEX_NAME=codex-index

# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=<account>;AccountKey=<key>;EndpointSuffix=core.windows.net

# Azure Cosmos DB Configuration
AZURE_COSMOS_ENDPOINT=https://<your-cosmos-account>.documents.azure.com:443/
AZURE_COSMOS_KEY=<your-primary-key>
AZURE_COSMOS_DATABASE_NAME=codexai
AZURE_COSMOS_PROJECTS_CONTAINER=projects
AZURE_COSMOS_FILES_CONTAINER=files
AZURE_COSMOS_DOCS_CONTAINER=documentation_requests

# Application Configuration
MAX_CONTEXT_TOKENS=4000
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

#### How to Get Azure Credentials

1. **Azure OpenAI**:
   - Apply for Azure OpenAI access at https://aka.ms/oai/access
   - Create an Azure OpenAI resource in Azure Portal
   - Deploy `text-embedding-ada-002` and `gpt-4o-mini` models
   - Copy the endpoint and API key from "Keys and Endpoint" section

2. **Azure Cognitive Search**:
   - Create a Cognitive Search service (Basic tier recommended)
   - Copy the URL and admin key from "Keys" section

3. **Azure Blob Storage**:
   - Create a Storage Account
   - Go to "Access keys" and copy the connection string

4. **Azure Cosmos DB**:
   - Create a Cosmos DB account (Serverless mode)
   - Copy the URI and Primary Key from "Keys" section

### 3. Install Dependencies

#### CLI Tool

```bash
cd cli
pip install -r requirements.txt
cd ..
```

#### Backend (Azure Functions)

```bash
cd backend
pip install -r requirements.txt
cd ..
```

#### Frontend (React)

```bash
cd frontend
npm install
cd ..
```

### 4. Azure Resource Setup

You need to create the following Azure resources:

1. **Resource Group**: `codexai-rg`
2. **Storage Account**: Create a container named `codebases`
3. **Cosmos DB**: Database will be created automatically on first run
4. **Cognitive Search**: Index will be created automatically on first run
5. **Function App**: For hosting Azure Functions
6. **App Service**: For hosting React frontend

**Optional**: Use the provided Terraform/Bicep scripts (if available) or create resources manually through Azure Portal.

## 📖 Usage Flow

### Step 1: Upload a Codebase (CLI)

Navigate to your project directory and run:

```bash
python cli/codexai_upload.py /path/to/your/project
```

Or with a custom project name:

```bash
python cli/codexai_upload.py /path/to/your/project --name "MyAwesomeProject"
```

The CLI will:
1. Scan your directory
2. Filter files using `.gitignore` patterns
3. Create a zip archive
4. Upload to Azure Blob Storage
5. Trigger the ingestion pipeline

**Example Output**:
```
CodexAI - Automated Code Documentation
==================================================

📁 Scanning directory: ./my-project
✓ Found 247 files
✓ Filtered to 189 code files (using .gitignore)
📦 Creating archive...
✓ Archive created: 2.3 MB

☁️  Uploading to Azure...
Progress: [████████████████████] 100%
✓ Upload complete

🔄 Triggering ingestion pipeline...
✓ Processing started (Job ID: abc-123)

✅ Done!
Visit https://codexai.azurewebsites.net to view your project.
```

### Step 2: Browse Projects (Web UI)

#### Local Development

```bash
cd frontend
npm run dev
```

Open http://localhost:3000 in your browser.

#### Production

Visit your deployed Azure App Service URL: `https://codexai.azurewebsites.net`

### Step 3: Generate Documentation

1. Select a project from the left sidebar
2. Browse files in the middle panel
3. Click on a file to view details
4. Click "Generate Documentation" button
5. Wait for AI to generate comprehensive docs
6. Copy or download the generated Markdown

## 🏗️ Architecture Overview

```
┌─────────────┐         ┌──────────────┐
│  CLI Tool   │────────▶│ Blob Storage │
└─────────────┘         └──────┬───────┘
                               │ Trigger
                               ▼
                        ┌──────────────┐
                        │   Azure      │
                        │  Functions   │
                        └──────┬───────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐      ┌──────────────┐      ┌──────────────┐
│  Cosmos DB    │      │  Cognitive   │      │ Azure OpenAI │
│  (Metadata)   │      │    Search    │      │ (Embeddings  │
│               │      │  (Vectors)   │      │  + LLM)      │
└───────────────┘      └──────────────┘      └──────────────┘
        ▲                      ▲                      ▲
        │                      │                      │
        └──────────────────────┴──────────────────────┘
                               │
                        ┌──────▼───────┐
                        │  React Web   │
                        │      UI      │
                        └──────────────┘
```

## 🔐 Security Best Practices

1. **Never commit `.env` files** - They contain sensitive credentials
2. **Use Azure Key Vault** in production for credential management
3. **Rotate API keys** every 90 days
4. **Enable Azure Managed Identities** for Function Apps (eliminates need for connection strings)
5. **Use HTTPS only** for all communications
6. **Implement rate limiting** to prevent abuse
7. **Review Azure RBAC** permissions regularly

## 💰 Cost Optimization

- **Serverless Functions**: Pay only for execution time
- **Cosmos DB Serverless**: Pay per request
- **Token Limiting**: Max 4000 tokens per documentation request
- **Embedding Caching**: Embeddings are stored and reused
- **Basic Search Tier**: $75/month for vector search

**Estimated Monthly Cost**: $100-150 for moderate usage (50 projects, 1000 doc generations)

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## 🚀 Deployment

### Deploy Backend (Azure Functions)

```bash
cd backend
func azure functionapp publish <your-function-app-name>
```

### Deploy Frontend (Azure App Service)

```bash
cd frontend
npm run build

# Deploy using Azure CLI
az webapp up --name <your-app-name> --resource-group codexai-rg
```

## 📊 Monitoring

- **Application Insights**: Automatically enabled for Azure Functions
- **Azure Monitor**: Set up alerts for failures and performance
- **Cost Management**: Monitor spending with budget alerts

## 🐛 Troubleshooting

### CLI Upload Fails

- **Check**: Azure Storage connection string is correct
- **Check**: Storage container `codebases` exists
- **Check**: Network connectivity to Azure

### Ingestion Not Triggering

- **Check**: Blob trigger is properly configured in Function App
- **Check**: Function App is running
- **Check**: Review Function App logs in Azure Portal

### Documentation Generation Fails

- **Check**: Azure OpenAI API key is valid
- **Check**: Deployments exist for both embedding and chat models
- **Check**: Cognitive Search index is created
- **Check**: Token limits are not exceeded

### Frontend Can't Connect to Backend

- **Check**: `VITE_API_URL` environment variable points to Function App URL
- **Check**: CORS is enabled on Function App
- **Check**: Function App authentication allows requests from frontend

## 📚 API Documentation

### POST /api/generate-documentation

Generate documentation for a file.

**Request Body**:
```json
{
  "project_id": "proj_abc123",
  "file_path": "src/api.py",
  "target": "file"
}
```

**Response**:
```json
{
  "documentation_id": "doc_001",
  "content": "# API Reference\n\n...",
  "metadata": {
    "prompt_tokens": 1500,
    "completion_tokens": 800,
    "total_tokens": 2300,
    "context_chunks": 5
  }
}
```

### GET /api/projects

List all projects.

**Response**:
```json
[
  {
    "id": "proj_abc123",
    "name": "MyProject",
    "status": "indexed",
    "upload_date": "2024-01-09T10:00:00Z",
    "file_count": 42,
    "chunk_count": 150
  }
]
```

### GET /api/projects/{project_id}/files

List files in a project.

**Response**:
```json
{
  "project_id": "proj_abc123",
  "project_name": "MyProject",
  "files": [
    {
      "id": "file_001",
      "file_path": "src/api.py",
      "language": "python",
      "status": "indexed",
      "chunk_count": 5
    }
  ]
}
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review Azure documentation

## 🎯 Roadmap

- [ ] Support for more programming languages
- [ ] Incremental updates (only re-index changed files)
- [ ] Documentation versioning
- [ ] Custom documentation templates
- [ ] IDE plugins (VS Code, JetBrains)
- [ ] CI/CD integration
- [ ] Multi-tenant support
- [ ] Natural language queries

---

**Built with ❤️ using Azure Cloud Services**