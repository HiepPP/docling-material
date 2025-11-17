# PDF to Markdown Converter - Astro App

A simple web application for converting PDF files to Markdown format using the Docling library.

## Features

- 📄 Upload PDF files via drag-and-drop or file picker
- ✨ Real-time progress tracking
- 🎨 Beautiful, responsive UI
- ⚡ Fast conversion using Docling
- 📥 Automatic markdown file download
- 🛡️ File validation (type and size limits)
- 🧹 Automatic temporary file cleanup

## Prerequisites

- Node.js (v18 or higher)
- Python 3.13+ with Poetry
- Docling and dependencies installed (from parent project)

## Setup

### 1. Fix npm cache permissions (if needed)

If you encounter npm permission errors, run:

```bash
sudo chown -R $(id -u):$(id -g) "$HOME/.npm"
```

### 2. Install dependencies

```bash
cd app
npm install
```

### 3. Verify Python script is accessible

The app expects the Python script at:
```
../src/docling_pdf_simple.py
```

Make sure the Python environment is set up and the script works:

```bash
cd ..
poetry shell
python src/docling_pdf_simple.py --help
```

## Running the App

### Development mode

```bash
npm run dev
```

The app will be available at `http://localhost:4321`

### Build for production

```bash
npm run build
npm run preview
```

## How to Use

1. Open the app in your browser (default: http://localhost:4321)
2. Click the upload area or drag-and-drop a PDF file
3. Click the "Upload" button
4. Wait for the conversion to complete (progress bar will show status)
5. The converted markdown file will automatically download

## File Structure

```
app/
├── src/
│   └── pages/
│       ├── index.astro          # Frontend UI with upload form
│       └── api/
│           └── convert.ts        # Backend API endpoint
├── public/                       # Static assets
├── astro.config.mjs             # Astro configuration (SSR enabled)
├── package.json                  # Dependencies and scripts
├── tsconfig.json                 # TypeScript configuration
└── README.md                     # This file
```

## Configuration

### File Size Limit

Default: 50MB

To change, update `MAX_FILE_SIZE` in:
- Frontend: `src/pages/index.astro` (line ~236)
- Backend: `src/pages/api/convert.ts` (line ~6)

### Python Script Path

If your Python script is in a different location, update `PYTHON_SCRIPT_PATH` in:
- `src/pages/api/convert.ts` (line ~7)

## Troubleshooting

### "Module not found" errors

Make sure you've installed dependencies:
```bash
npm install
```

### Python script errors

1. Verify the Python script path is correct
2. Make sure Poetry environment is activated
3. Test the script manually:
```bash
python3 ../src/docling_pdf_simple.py \
  --input test.pdf \
  --output test.md
```

### Port already in use

If port 4321 is busy, Astro will automatically try the next available port.

## Technical Details

### Frontend
- Astro static site generator
- Vanilla JavaScript for interactivity
- Drag-and-drop file upload
- Client-side validation

### Backend
- Astro API routes (SSR)
- Node.js child_process for Python execution
- Temporary file management with automatic cleanup
- Streaming response for file download

### Python Integration
- Uses `spawn()` for non-blocking execution
- Passes file paths via command-line arguments
- Captures stdout/stderr for logging
- Proper exit code handling

## Security Features

- File type validation (MIME type + extension)
- File size limits (50MB default)
- Sanitized temporary file paths (UUID-based)
- No arbitrary code execution (fixed Python script path)
- Automatic cleanup of temporary files

## License

Same as parent project
