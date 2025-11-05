# PDF LangChain Neo4j RAG System Design

## Overview

Design for a simple RAG (Retrieval-Augmented Generation) system that processes PDF documents using Docling, stores embeddings in Neo4j vector database, and provides question-answering using ChatGPT API.

## Architecture

The script follows a straightforward pipeline architecture with four main components working sequentially:

1. **PDF Processor**: Uses existing Docling setup to extract and chunk PDF content
2. **Embedding Service**: Converts text chunks into vectors using sentence-transformers
3. **Neo4j Vector Store**: Handles storage and similarity search functionality
4. **RAG Engine**: Coordinates retrieval and generation using OpenAI ChatGPT API

This design keeps dependencies minimal by using Neo4j's native vector capabilities and avoids complex setups with external services.

## Components and Data Flow

### PDF Processing & Chunking
Building on existing Docling code to extract markdown content and split into meaningful chunks:
- Chunk size: 500-1000 characters with overlap
- Maintains metadata: source document, page numbers, position
- Uses text splitter for consistent chunk creation

### Vector Storage in Neo4j
Each text chunk becomes a node with:
- Text content property
- Metadata properties (source doc, page, position)
- Vector embedding property
- Vector index for similarity search
- Relationships back to source document

### RAG Query Pipeline
For incoming questions:
1. Embed question using same model as chunks
2. Search Neo4j for similar chunks (vector similarity)
3. Format retrieved chunks as context
4. Send question + context to ChatGPT via OpenAI API
5. Return answer with source chunks used

## Error Handling

- PDF parsing errors with meaningful messages
- Neo4j connection validation and error handling
- Embedding model failure handling
- OpenAI API error management
- Input validation for file paths and credentials

## Command Line Interface

Using argparse with two main modes:

```bash
# Ingest a PDF document
python docling_pdf_langchain_neo4j.py --ingest "document.pdf"

# Query the system
python docling_pdf_langchain_neo4j.py --query "What is the main topic?"
```

Configuration options:
- `--neo4j-uri`: Neo4j database URI
- `--neo4j-user`: Neo4j username
- `--neo4j-password`: Neo4j password
- `--openai-api-key`: OpenAI API key
- `--chunk-size`: Text chunk size (default: 800)
- Environment variables supported for sensitive data

## Dependencies

New dependencies to add:
- `neo4j-driver`: Neo4j database connection
- `openai`: ChatGPT API integration
- `langchain`: Text splitting and utilities
- `sentence-transformers`: Text embedding generation
- `tiktoken`: Text processing for OpenAI

Works alongside existing docling setup.