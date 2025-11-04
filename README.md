# Docling Material

A Python project for extracting text and metadata from PDF files using the Docling library. This project provides a simple command-line interface to read PDF documents and extract their content in a structured format.

## Features

- Extract text content from PDF files
- Extract document metadata (author, title, creation date, etc.)
- Display document information in a readable format
- Save extracted content to text files
- Support for both preview and full text display
- Error handling and validation

## Setup

1. **Clone & Install**:
   ```bash
   git clone <repo-url>
   cd docling-material
   python -m venv .venv  # Create isolated env
   source .venv/bin/activate  # Activate (Windows: .venv\Scripts\activate)
   pip install poetry  # If not installed
   poetry install  # Install deps from pyproject.toml
   ```

2. **Run**:
   ```bash
   poetry run python docling_pdf_simple.py "document.pdf"  # Or poetry shell for interactive
   ```

3. **Add Deps**:
   ```bash
   poetry add requests  # Main dep
   poetry add --group dev pytest  # Dev tool
   ```

## Usage

### Basic Usage

```bash
# Read a PDF file and show preview
python docling_pdf_simple.py "document.pdf"

# Show full text content
python docling_pdf_simple.py "document.pdf" --full-text

# Save extracted content to file
python docling_pdf_simple.py "document.pdf" --output "extracted_text.txt"

# Show full text and save to file
python docling_pdf_simple.py "document.pdf" --full-text --output "full_content.txt"
```

### Command Line Options

- `pdf_path`: Path to the PDF file to read (required)
- `--full-text`: Display the full text content (default: show preview only)
- `--output`, `-o`: Save extracted content to a text file

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

## Development

- **Test**: `poetry run pytest`
- **Deactivate Env**: `deactivate`

## Requirements

- Python 3.13 or higher
- Docling library (>=2.60.0)

## Git

Pushed via GH CLI: `gh repo create ... --private --push`.

*Note*: Use `.gitignore` for `.venv/`, `__pycache__/`. Export reqs: `poetry export -f requirements.txt -o requirements.txt`.

## License

This project is licensed under the MIT License.