# Docling Material

A comprehensive PDF processing toolkit that combines powerful document extraction capabilities with a modern web interface. This project leverages the Docling library to extract text and metadata from PDFs, offering both programmatic access via Python scripts and a user-friendly web UI built with Astro.

## Features

### Python Backend
- Extract text content from PDF files
- Extract document metadata (author, title, creation date, etc.)
- Display document information in a readable format
- Save extracted content to markdown files
- Support for both preview and full text display
- Error handling and validation
- Vector store integration (Chroma, Neo4j) for RAG pipelines

### Web Interface (Astro UI)
- 📄 Drag-and-drop PDF upload
- ✨ Real-time conversion progress tracking
- 🎨 Beautiful, responsive UI
- ⚡ Fast server-side PDF processing
- 📥 Automatic markdown file download
- 🛡️ File validation (type and size limits)
- 🧹 Automatic temporary file cleanup

## Setup

### Prerequisites

- **Python 3.13+** - For PDF processing backend
- **Node.js 18+** - For Astro web interface
- **Poetry** - Python dependency management

### Python Backend Setup

1. **Clone & Install Python Dependencies**:
   ```bash
   git clone <repo-url>
   cd docling-material
   python -m venv .venv  # Create isolated environment
   source .venv/bin/activate  # Activate (Windows: .venv\Scripts\activate)
   pip install poetry  # If not installed
   poetry install  # Install dependencies from pyproject.toml
   ```

2. **Verify Installation**:
   ```bash
   poetry run python src/docling_pdf_simple.py --help
   ```

### Astro Web UI Setup

1. **Navigate to the app directory**:
   ```bash
   cd app
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Verify the setup**:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:4321`

### Quick Start (Both Components)

To run the complete system:

1. **Terminal 1 - Ensure Python backend is ready**:
   ```bash
   cd docling-material
   source .venv/bin/activate
   poetry shell
   ```

2. **Terminal 2 - Start Astro web server**:
   ```bash
   cd docling-material/app
   npm run dev
   ```

3. **Open browser** and navigate to `http://localhost:4321`

## Usage

### Option 1: Web Interface (Recommended for Most Users)

The easiest way to convert PDFs to Markdown:

1. **Start the web server**:
   ```bash
   cd app
   npm run dev
   ```

2. **Open your browser** and navigate to `http://localhost:4321`

3. **Upload and convert**:
   - Click the upload area or drag-and-drop a PDF file (max 50MB)
   - Click the "Upload" button
   - Wait for the conversion (progress bar shows status)
   - The markdown file will automatically download

4. **Features**:
   - Visual feedback with progress indicators
   - File size and type validation
   - Automatic markdown file naming
   - Clean, intuitive interface

### Option 2: Command Line (For Automation & Scripting)

Use the Python scripts directly for programmatic access:

#### Simple PDF Extraction

```bash
# Activate Python environment
poetry shell

# Convert PDF to markdown (saves to exported/ directory)
python src/docling_pdf_simple.py --input "document.pdf" --output "output.md"

# Show full text content
python src/docling_pdf_simple.py --input "document.pdf" --full-text
```

#### Chroma RAG Pipeline

```bash
# Process PDFs and store in Chroma vector database
python src/docling_pdf_chroma.py
```

#### Neo4j Vector Store

```bash
# Process PDFs and store in Neo4j graph database
python src/docling_pdf_langchain_neo4j.py
```

### Command Line Options

**docling_pdf_simple.py**:
- `--input`: Path to the PDF file to process (required)
- `--output`: Output markdown file path (required)
- `--full-text`: Display the full text content (optional)

## Example Output

```
Reading PDF: document.pdf

==================================================
PDF DOCUMENT INFORMATION
==================================================
Title: Sample Document
Page Count: 5

Metadata:
  Author: John Doe
  Creation Date: 2024-01-15

Text Length: 2847 characters

Text Preview (first 500 characters):
------------------------------
This is the beginning of the document content...
```

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User's Browser                          │
│                  http://localhost:4321                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP (Upload PDF)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Astro Web Server (SSR)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Frontend: src/pages/index.astro                     │   │
│  │  - Drag-and-drop upload UI                           │   │
│  │  - Progress tracking                                 │   │
│  │  - File validation                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Backend API: src/pages/api/convert.ts               │   │
│  │  - Receive PDF upload                                │   │
│  │  - Save to temp directory                            │   │
│  │  - Call Python script via child_process              │   │
│  │  - Return markdown file                              │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ spawn('python3', [script, args])
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Backend (Docling)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  src/docling_pdf_simple.py                           │   │
│  │  - Read PDF file from temp path                      │   │
│  │  - Extract text via Docling library                  │   │
│  │  - Convert to markdown format                        │   │
│  │  - Save markdown to temp path                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
docling-material/
├── app/                              # Astro web interface
│   ├── src/
│   │   ├── pages/
│   │   │   ├── index.astro          # Main upload UI
│   │   │   └── api/
│   │   │       └── convert.ts        # PDF conversion endpoint
│   ├── public/                       # Static assets
│   ├── astro.config.mjs             # Astro SSR configuration
│   ├── package.json                  # Node.js dependencies
│   ├── tsconfig.json                 # TypeScript config
│   └── README.md                     # App-specific docs
│
├── src/                              # Python backend scripts
│   ├── docling_pdf_simple.py        # Simple PDF extraction
│   ├── docling_pdf_chroma.py        # Chroma RAG pipeline
│   └── docling_pdf_langchain_neo4j.py  # Neo4j integration
│
├── docs_sample/                      # Sample PDF files
├── exported/                         # Output directory
├── pyproject.toml                    # Python dependencies
├── poetry.lock                       # Locked Python versions
├── README.md                         # This file
└── CLAUDE.md                         # Development guidance
```

### Component Integration

**Web UI → Python Backend Flow:**

1. **User uploads PDF** via Astro frontend (index.astro)
2. **API endpoint receives file** (convert.ts)
   - Validates file type and size
   - Generates unique temp file paths using UUID
   - Saves PDF to system temp directory
3. **Spawns Python process** (child_process)
   - Executes: `python3 docling_pdf_simple.py --input temp.pdf --output temp.md`
   - Captures stdout/stderr for logging
   - Waits for completion
4. **Reads generated markdown** from temp file
5. **Streams markdown to browser** as downloadable file
6. **Cleans up temp files** automatically

**Key Technologies:**
- **Frontend**: Astro (static site generator), Vanilla JavaScript
- **Backend**: Node.js (API routes), Python 3.13+ (PDF processing)
- **PDF Processing**: Docling library
- **Vector Stores** (optional): Chroma, Neo4j
- **Embeddings** (optional): SentenceTransformers, OpenAI

## Development

### Python Development

- **Run tests**: `poetry run pytest`
- **Add dependency**: `poetry add <package-name>`
- **Add dev dependency**: `poetry add --group dev <package-name>`
- **Deactivate environment**: `deactivate`

### Astro Web UI Development

- **Start dev server**: `cd app && npm run dev`
- **Build for production**: `cd app && npm run build`
- **Preview production build**: `cd app && npm run preview`
- **Add dependency**: `cd app && npm install <package-name>`

### Configuration

**Astro App (`app/src/pages/api/convert.ts`)**:
- `MAX_FILE_SIZE`: File size limit (default: 50MB)
- `PYTHON_SCRIPT_PATH`: Path to Python conversion script

**Python Scripts**:
- Environment variables in `.env` file
- Chroma configuration: host, port, collection name
- Neo4j configuration: URL, credentials, OpenAI API key

## Requirements

### Python Backend
- Python 3.13 or higher
- Poetry for dependency management
- Docling library (>=2.60.0)
- Optional: ChromaDB server (for RAG pipeline)
- Optional: Neo4j database (for graph storage)

### Astro Web UI
- Node.js 18 or higher
- npm or yarn package manager
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Troubleshooting

### Web UI Issues

**Port 4321 already in use:**
- Astro will automatically try the next available port
- Or specify a custom port: `npm run dev -- --port 3000`

**"Python script not found" error:**
- Verify the Python script path in `app/src/pages/api/convert.ts` (line 9)
- Ensure Python environment is set up: `poetry install`
- Test the script manually: `poetry run python src/docling_pdf_simple.py --help`

**PDF upload fails:**
- Check file size (max 50MB by default)
- Verify file is a valid PDF
- Check browser console for errors
- Ensure Python backend is accessible

**npm permission errors:**
- Fix npm cache permissions:
  ```bash
  sudo chown -R $(id -u):$(id -g) "$HOME/.npm"
  ```

### Python Backend Issues

**Module not found errors:**
- Activate virtual environment: `source .venv/bin/activate`
- Install dependencies: `poetry install`

**Docling errors:**
- Ensure Python 3.13+ is installed
- Reinstall Docling: `poetry add docling@latest`

**Vector store connection errors:**
- Chroma: Ensure server is running on configured port
- Neo4j: Verify credentials and connection URL in environment variables

## Git

Repository created via GitHub CLI: `gh repo create docling-material --private --push`

**Important files in `.gitignore`:**
- `.venv/` - Python virtual environment
- `__pycache__/` - Python cache files
- `node_modules/` - Node.js dependencies
- `.env` - Environment variables (secrets)
- `exported/` - Generated output files

**Export Python requirements:**
```bash
poetry export -f requirements.txt -o requirements.txt
```

## License

This project is licensed under the MIT License.