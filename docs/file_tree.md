# CodexAI Project File Structure

```
codexai/
├── README.md                          # Main project documentation
├── .env.template                      # Environment variable template
├── .gitignore                         # Git ignore rules
│
├── cli/                               # CLI Tool for code upload
│   ├── __init__.py
│   ├── upload.py                      # Main upload script
│   ├── gitignore_parser.py            # .gitignore parsing logic
│   ├── requirements.txt               # Python dependencies
│   └── README.md                      # CLI usage guide
│
├── backend/                           # Azure Functions backend
│   ├── host.json                      # Function app configuration
│   ├── local.settings.json            # Local development settings
│   ├── requirements.txt               # Python dependencies
│   │
│   ├── shared/                        # Shared utilities
│   │   ├── __init__.py
│   │   ├── config.py                  # Environment variable loader
│   │   ├── azure_clients.py           # Azure SDK client initialization
│   │   ├── chunking.py                # Code chunking logic
│   │   ├── embedding.py               # Embedding generation
│   │   └── token_counter.py           # Token counting utilities
│   │
│   ├── blob_upload_trigger/           # Blob created event trigger
│   │   ├── __init__.py
│   │   ├── function.json              # Function binding configuration
│   │   └── __main__.py                # Trigger handler
│   │
│   ├── ingestion_function/            # Code ingestion pipeline
│   │   ├── __init__.py
│   │   ├── function.json
│   │   ├── __main__.py                # Main ingestion logic
│   │   ├── code_parser.py             # AST-based code parsing
│   │   └── indexer.py                 # Cognitive Search indexing
│   │
│   ├── rag_inference_function/        # RAG documentation generation
│   │   ├── __init__.py
│   │   ├── function.json
│   │   ├── __main__.py                # Main RAG logic
│   │   ├── retriever.py               # Vector search retrieval
│   │   ├── prompt_builder.py          # Prompt construction
│   │   └── llm_client.py              # OpenAI API wrapper
│   │
│   └── api_gateway_function/          # HTTP API endpoints
│       ├── __init__.py
│       ├── function.json
│       ├── __main__.py                # API route handler
│       ├── routes/
│       │   ├── projects.py            # Project endpoints
│       │   ├── files.py               # File endpoints
│       │   └── documentation.py       # Documentation endpoints
│       └── middleware/
│           ├── error_handler.py       # Error handling
│           └── validator.py           # Request validation
│
├── frontend/                          # React web application
│   ├── package.json                   # NPM dependencies
│   ├── vite.config.ts                 # Vite configuration
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── index.html                     # HTML entry point
│   │
│   ├── public/                        # Static assets
│   │   ├── favicon.ico
│   │   └── logo.png
│   │
│   ├── src/
│   │   ├── main.tsx                   # React entry point
│   │   ├── App.tsx                    # Root component
│   │   ├── vite-env.d.ts              # Vite type definitions
│   │   │
│   │   ├── components/                # React components
│   │   │   ├── ProjectList.tsx        # Project list view
│   │   │   ├── FileExplorer.tsx       # File tree component
│   │   │   ├── DocumentationViewer.tsx # Markdown viewer
│   │   │   ├── GenerateDocModal.tsx   # Doc generation dialog
│   │   │   ├── LoadingSpinner.tsx     # Loading indicator
│   │   │   └── ErrorBoundary.tsx      # Error handling
│   │   │
│   │   ├── services/                  # API services
│   │   │   ├── api.ts                 # Base API client
│   │   │   ├── projectService.ts      # Project API calls
│   │   │   ├── fileService.ts         # File API calls
│   │   │   └── docService.ts          # Documentation API calls
│   │   │
│   │   ├── types/                     # TypeScript types
│   │   │   ├── project.ts             # Project types
│   │   │   ├── file.ts                # File types
│   │   │   └── documentation.ts       # Documentation types
│   │   │
│   │   ├── hooks/                     # Custom React hooks
│   │   │   ├── useProjects.ts         # Project data hook
│   │   │   ├── useFiles.ts            # File data hook
│   │   │   └── useDocumentation.ts    # Documentation hook
│   │   │
│   │   ├── context/                   # React context
│   │   │   └── AppContext.tsx         # Global state
│   │   │
│   │   ├── utils/                     # Utility functions
│   │   │   ├── formatters.ts          # Data formatting
│   │   │   └── validators.ts          # Input validation
│   │   │
│   │   └── styles/                    # CSS/Tailwind styles
│   │       ├── index.css              # Global styles
│   │       └── tailwind.css           # Tailwind imports
│   │
│   └── README.md                      # Frontend setup guide
│
├── docs/                              # Documentation
│   ├── prd.md                         # Product Requirements Document
│   ├── system_design.md               # System design (this file)
│   ├── architect.plantuml             # Architecture diagram
│   ├── class_diagram.plantuml         # Class diagram
│   ├── sequence_diagram.plantuml      # Sequence diagram
│   ├── er_diagram.plantuml            # ER diagram
│   ├── file_tree.md                   # File structure (this file)
│   └── api_reference.md               # API documentation
│
├── infrastructure/                    # Infrastructure as Code (optional)
│   ├── terraform/                     # Terraform scripts
│   │   ├── main.tf                    # Main configuration
│   │   ├── variables.tf               # Variable definitions
│   │   └── outputs.tf                 # Output values
│   │
│   └── bicep/                         # Azure Bicep templates
│       ├── main.bicep                 # Main template
│       └── modules/                   # Reusable modules
│           ├── storage.bicep
│           ├── functions.bicep
│           └── cosmos.bicep
│
├── tests/                             # Test suites
│   ├── unit/                          # Unit tests
│   │   ├── test_chunking.py
│   │   ├── test_embedding.py
│   │   └── test_rag.py
│   │
│   ├── integration/                   # Integration tests
│   │   ├── test_ingestion.py
│   │   └── test_api.py
│   │
│   └── e2e/                           # End-to-end tests
│       └── test_workflow.py
│
└── scripts/                           # Utility scripts
    ├── setup_azure.sh                 # Azure resource setup
    ├── deploy.sh                      # Deployment script
    └── seed_data.py                   # Sample data seeding
```

## Directory Descriptions

### `/cli`
Command-line tool for uploading codebases. Users run this locally to zip and upload their projects to Azure Blob Storage.

### `/backend`
Azure Functions application containing all serverless backend logic:
- **shared/**: Common utilities used across functions
- **blob_upload_trigger/**: Triggered when a new codebase is uploaded
- **ingestion_function/**: Processes uploaded code, generates embeddings, and indexes
- **rag_inference_function/**: Generates documentation using RAG
- **api_gateway_function/**: HTTP API for frontend communication

### `/frontend`
React web application built with Vite and TypeScript:
- **components/**: Reusable UI components
- **services/**: API client logic
- **types/**: TypeScript type definitions
- **hooks/**: Custom React hooks for data fetching
- **context/**: Global state management

### `/docs`
All project documentation including PRD, system design, and PlantUML diagrams.

### `/infrastructure`
Infrastructure as Code (IaC) templates for provisioning Azure resources (optional for MVP).

### `/tests`
Comprehensive test suites covering unit, integration, and end-to-end testing.

### `/scripts`
Utility scripts for setup, deployment, and data management.

## Key Files

- **`.env.template`**: Template for environment variables (copy to `.env` and fill in values)
- **`README.md`**: Main project documentation with setup instructions
- **`host.json`**: Azure Functions host configuration
- **`local.settings.json`**: Local development settings for Azure Functions
- **`package.json`**: Frontend dependencies and scripts
- **`requirements.txt`**: Python dependencies for CLI and backend

## Development Workflow

1. **Setup**: Copy `.env.template` to `.env` and configure Azure credentials
2. **CLI**: Run `python cli/upload.py` to upload a codebase
3. **Backend**: Run `func start` in `/backend` for local development
4. **Frontend**: Run `npm run dev` in `/frontend` to start dev server
5. **Deploy**: Use `scripts/deploy.sh` to deploy to Azure

## Notes

- All Python code follows PEP8 style guidelines
- Frontend uses ESLint and Prettier for code formatting
- Sensitive files (`.env`, `local.settings.json`) are excluded via `.gitignore`
- PlantUML diagrams can be rendered using VS Code extensions or online tools