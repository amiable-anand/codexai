# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-01-14

### Added

- **CLI Upload Tool** (`/cli`)
  - Python-based CLI for uploading local codebases to Azure Blob Storage
  - Automatic `.gitignore` filtering to exclude non-code files
  - Progress bar with colored terminal output
  - Configurable project naming

- **Backend - Azure Functions** (`/backend`)
  - Blob trigger for automatic ingestion on code upload
  - Language-aware code chunking (Python, JavaScript, TypeScript)
  - Vector embedding generation using Azure OpenAI `text-embedding-ada-002`
  - Azure Cognitive Search integration for vector indexing and hybrid search
  - RAG (Retrieval-Augmented Generation) documentation engine using `gpt-4o-mini`
  - RESTful API endpoints for project listing, file browsing, and doc generation
  - Cosmos DB integration for metadata and documentation storage
  - Token management with 4000-token limit per request

- **Frontend - React Web UI** (`/frontend`)
  - Modern React 18 + TypeScript + Vite application
  - Project browser with upload status indicators
  - File explorer with tree-view navigation
  - Documentation viewer with Markdown rendering and syntax highlighting
  - Copy-to-clipboard and download functionality
  - Responsive design with Tailwind CSS

- **Configuration & Security**
  - Environment variable-based configuration (zero hardcoded credentials)
  - `.env.template` with all required Azure service credentials
  - Comprehensive `.gitignore` for security and cleanliness

- **Documentation**
  - `README.md` with complete setup guide, usage flow, and troubleshooting
  - `docs/prd.md` - Product Requirements Document
  - `docs/system_design.md` - System architecture and design document
  - API documentation with request/response examples
  - Security best practices guide

### Security

- All API keys and connection strings managed via environment variables
- `.env` file excluded from version control
- HTTPS-only communication enforced
- Input validation and sanitization on all endpoints

---

## [Unreleased]

### Planned

- Multi-language support (Java, C++, Go, Rust, Ruby)
- Incremental updates (only re-process changed files)
- Documentation versioning and history
- Batch documentation generation for entire projects
- Custom documentation templates
- CI/CD integration (GitHub Actions, Azure DevOps)
- IDE plugins (VS Code, JetBrains)
- Multi-tenant architecture with data isolation
- Natural language queries across codebases
- Cost monitoring dashboard