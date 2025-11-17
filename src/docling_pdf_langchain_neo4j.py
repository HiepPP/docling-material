#!/usr/bin/env python3
"""
PDF to Neo4j vector store using Docling and LangChain.
Extracts text from PDF files, chunks it, and stores in Neo4j for vector search.
"""

import sys
import os
from pathlib import Path
from typing import Optional

from docling.document_converter import DocumentConverter
from docling.datamodel.document import DoclingDocument

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document


def read_pdf_with_docling(pdf_path: str) -> Optional[DoclingDocument]:
    """
    Read PDF file using Docling library.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        DoclingDocument object or None if failed
    """
    try:
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        return result.document

    except Exception as e:
        print(f"Error reading PDF '{pdf_path}': {str(e)}")
        return None


def chunk_document_content(doc: DoclingDocument, filename: str) -> list[Document]:
    """
    Chunk document content using RecursiveCharacterTextSplitter.

    Args:
        doc: DoclingDocument object
        filename: Source filename for metadata

    Returns:
        List of Document objects with chunks and metadata
    """
    try:
        # Get markdown content from Docling
        markdown_content = doc.export_to_markdown()

        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        # Split text into chunks
        texts = text_splitter.split_text(markdown_content)

        # Create Document objects with metadata
        documents = []
        for i, text in enumerate(texts):
            # Calculate character positions (approximate)
            start_char = sum(len(t) for t in texts[:i])
            end_char = start_char + len(text)

            metadata = {
                'source': filename,
                'chunk_id': i,
                'start_char': start_char,
                'end_char': end_char,
                'page_count': len(doc.pages) if hasattr(doc, 'pages') else 0
            }

            documents.append(Document(page_content=text, metadata=metadata))

        print(f"Created {len(documents)} chunks from document")
        return documents

    except Exception as e:
        print(f"Error chunking document: {str(e)}")
        return []


def store_chunks_in_neo4j(documents: list[Document]) -> bool:
    """
    Store document chunks in Neo4j vector store.

    Args:
        documents: List of Document objects to store

    Returns:
        True if successful, False otherwise
    """
    try:
        # Neo4j connection settings - using environment variables
        neo4j_url = os.getenv('NEO4J_URL', 'bolt://localhost:7687')
        neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
        neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')

        # Initialize embeddings
        embeddings = OpenAIEmbeddings()

        # Create Neo4j vector store
        vector_store = Neo4jVector.from_documents(
            documents,
            embeddings,
            url=neo4j_url,
            username=neo4j_user,
            password=neo4j_password,
            index_name='document_chunks',
            node_label='DocumentChunk',
            text_node_property='text',
            embedding_node_property='embedding'
        )

        print(f"Successfully stored {len(documents)} chunks in Neo4j")
        return True

    except Exception as e:
        print(f"Error storing chunks in Neo4j: {str(e)}")
        return False


def main():
    """Main function to process PDF and store in Neo4j."""
    # PDF file path relative to project root
    pdf_path = 'docs_sample/KBV_ITA_VGEX_Anforderungskatalog_KVDT.pdf'

    # Check if file exists
    if not Path(pdf_path).exists():
        print(f"PDF file not found: {pdf_path}")
        sys.exit(1)

    # Get filename for metadata
    filename = Path(pdf_path).name

    # Read the PDF file
    print(f"Reading PDF: {pdf_path}")
    doc = read_pdf_with_docling(pdf_path)

    if doc is None:
        print("Failed to read PDF document")
        sys.exit(1)

    # Chunk the document
    print("Chunking document content...")
    documents = chunk_document_content(doc, filename)

    if not documents:
        print("No document chunks created")
        sys.exit(1)

    # Store in Neo4j
    print("Storing chunks in Neo4j...")
    success = store_chunks_in_neo4j(documents)

    if success:
        print("PDF processing and Neo4j storage completed successfully!")
    else:
        print("Failed to store document chunks in Neo4j")
        sys.exit(1)


if __name__ == "__main__":
    main()