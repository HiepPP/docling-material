#!/usr/bin/env python3
"""
Docling-Chroma Integration Script

This script processes PDF documents using docling, chunks the extracted content,
and stores the chunks in a Chroma vector database for semantic search.

Dependencies:
- docling: PDF processing and document understanding
- chromadb: Vector database for embeddings
- sentence-transformers: Text embeddings
- python-dotenv: Environment configuration
"""

import os
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass
import hashlib

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import DoclingDocument
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingConfig:
    """Configuration for PDF processing and chunking"""
    chunk_size: int = 800
    chunk_overlap: int = 200
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection_name: str = "pdf_documents"
    pdf_directory: str = "./pdfs"

    @classmethod
    def from_env(cls) -> 'ProcessingConfig':
        """Load configuration from environment variables"""
        return cls(
            chunk_size=int(os.getenv('CHUNK_SIZE', 800)),
            chunk_overlap=int(os.getenv('CHUNK_OVERLAP', 200)),
            embedding_model=os.getenv('EMBEDDING_MODEL', "all-MiniLM-L6-v2"),
            chroma_host=os.getenv('CHROMA_HOST', 'localhost'),
            chroma_port=int(os.getenv('CHROMA_PORT', 8000)),
            chroma_collection_name=os.getenv('CHROMA_COLLECTION_NAME', 'pdf_documents'),
            pdf_directory=os.getenv('PDF_DIRECTORY', './pdfs')
        )

class PDFProcessor:
    """Processes PDF documents using docling"""

    def __init__(self):
        """Initialize the PDF processor with docling"""
        # Configure PDF pipeline options
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True  # Enable OCR for better text extraction
        pipeline_options.do_table_structure = True  # Extract table structures

        # Initialize document converter with custom backend
        self.converter = DocumentConverter(
            format_options={
                "pdf": pipeline_options
            }
        )
        logger.info("PDF Processor initialized with docling")

    def process_pdf(self, pdf_path: Path) -> DoclingDocument:
        """
        Process a single PDF file and extract structured content

        Args:
            pdf_path: Path to the PDF file

        Returns:
            DoclingDocument: Processed document with structured content
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"Processing PDF: {pdf_path}")

        try:
            result = self.converter.convert(str(pdf_path))
            logger.info(f"Successfully processed PDF: {pdf_path}")
            return result.document
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise

    def extract_full_text(self, document: DoclingDocument) -> str:
        """
        Extract full text content from processed document

        Args:
            document: Processed docling document

        Returns:
            str: Full text content
        """
        text_content = []

        # Extract text from all text elements
        for page in document.pages:
            for element in page.elements:
                if hasattr(element, 'text') and element.text:
                    text_content.append(element.text)
                elif hasattr(element, 'body') and element.body:
                    text_content.append(str(element.body))

        return "\n\n".join(text_content)

    def get_document_metadata(self, document: DoclingDocument, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from processed document

        Args:
            document: Processed docling document
            pdf_path: Original PDF file path

        Returns:
            Dict[str, Any]: Document metadata
        """
        metadata = {
            "file_name": pdf_path.name,
            "file_path": str(pdf_path),
            "file_size": pdf_path.stat().st_size,
            "document_hash": self._calculate_file_hash(pdf_path),
            "num_pages": len(document.pages),
            "processed_at": str(os.path.getctime(pdf_path))
        }

        # Extract title if available
        if hasattr(document, 'title') and document.title:
            metadata['title'] = document.title

        return metadata

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of the file for deduplication"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

class TextChunker:
    """Chunks text content for embedding and storage"""

    def __init__(self, config: ProcessingConfig):
        """
        Initialize text chunker

        Args:
            config: Processing configuration
        """
        self.chunk_size = config.chunk_size
        self.chunk_overlap = config.chunk_overlap
        self.config = config

        logger.info(f"TextChunker initialized: chunk_size={self.chunk_size}, overlap={self.chunk_overlap}")

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks

        Args:
            text: Input text to chunk
            metadata: Document metadata to attach to each chunk

        Returns:
            List[Dict[str, Any]]: List of text chunks with metadata
        """
        if not text or not text.strip():
            return []

        chunks = []
        words = text.split()

        if len(words) <= self.chunk_size:
            # Text is smaller than chunk size, return as single chunk
            chunks.append({
                "text": text,
                "chunk_id": f"{metadata.get('file_name', 'doc')}_0",
                "chunk_index": 0,
                "start_pos": 0,
                "end_pos": len(text),
                **{k: v for k, v in metadata.items() if k != 'processed_at'}
            })
            return chunks

        # Create overlapping chunks
        current_pos = 0
        chunk_index = 0

        while current_pos < len(words):
            # Calculate chunk boundaries
            end_pos = min(current_pos + self.chunk_size, len(words))
            chunk_words = words[current_pos:end_pos]
            chunk_text = " ".join(chunk_words)

            # Create chunk metadata
            chunk_data = {
                "text": chunk_text,
                "chunk_id": f"{metadata.get('file_name', 'doc')}_{chunk_index}",
                "chunk_index": chunk_index,
                "start_word": current_pos,
                "end_word": end_pos - 1,
                "word_count": len(chunk_words),
                **{k: v for k, v in metadata.items() if k != 'processed_at'}
            }

            chunks.append(chunk_data)
            chunk_index += 1

            # Move position with overlap
            if end_pos >= len(words):
                break
            current_pos = end_pos - self.chunk_overlap

        logger.info(f"Created {len(chunks)} chunks from {len(words)} words")
        return chunks

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chunk multiple documents

        Args:
            documents: List of documents with text and metadata

        Returns:
            List[Dict[str, Any]]: All chunks from all documents
        """
        all_chunks = []

        for doc in documents:
            text = doc.get('text', '')
            metadata = doc.get('metadata', {})
            chunks = self.chunk_text(text, metadata)
            all_chunks.extend(chunks)

        return all_chunks

class ChromaIndexer:
    """Handles Chroma vector database operations"""

    def __init__(self, config: ProcessingConfig):
        """
        Initialize Chroma indexer

        Args:
            config: Processing configuration
        """
        self.config = config
        self.client = None
        self.collection = None
        self.embedder = None

        self._initialize()

    def _initialize(self):
        """Initialize Chroma client and embedding model"""
        try:
            # Initialize Chroma client
            self.client = chromadb.HttpClient(
                host=self.config.chroma_host,
                port=self.config.chroma_port
            )

            # Initialize embedding model
            self.embedder = SentenceTransformer(self.config.embedding_model)
            logger.info(f"Embedding model loaded: {self.config.embedding_model}")

            # Get or create collection
            try:
                self.collection = self.client.get_collection(self.config.chroma_collection_name)
                logger.info(f"Using existing collection: {self.config.chroma_collection_name}")
            except Exception:
                self.collection = self.client.create_collection(
                    name=self.config.chroma_collection_name,
                    metadata={"description": "PDF documents processed with docling"}
                )
                logger.info(f"Created new collection: {self.config.chroma_collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize Chroma indexer: {str(e)}")
            raise

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text chunks

        Args:
            texts: List of text chunks

        Returns:
            List[List[float]]: Embeddings for each text
        """
        logger.info(f"Generating embeddings for {len(texts)} text chunks")

        try:
            embeddings = self.embedder.encode(
                texts,
                batch_size=32,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Add text chunks to Chroma collection

        Args:
            chunks: List of text chunks with metadata

        Returns:
            int: Number of chunks added
        """
        if not chunks:
            logger.warning("No chunks to add to Chroma")
            return 0

        logger.info(f"Adding {len(chunks)} chunks to Chroma collection")

        try:
            # Extract texts and metadata
            texts = [chunk['text'] for chunk in chunks]
            chunk_ids = [chunk['chunk_id'] for chunk in chunks]
            metadatas = []

            for chunk in chunks:
                metadata = {k: v for k, v in chunk.items() if k != 'text'}
                metadatas.append(metadata)

            # Generate embeddings
            embeddings = self.generate_embeddings(texts)

            # Add to collection
            self.collection.add(
                ids=chunk_ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )

            logger.info(f"Successfully added {len(chunks)} chunks to Chroma")
            return len(chunks)

        except Exception as e:
            logger.error(f"Error adding chunks to Chroma: {str(e)}")
            raise

    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Search for similar text chunks

        Args:
            query: Search query
            n_results: Number of results to return

        Returns:
            Dict[str, Any]: Search results
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Error searching Chroma: {str(e)}")
            return {}

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the Chroma collection"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.config.chroma_collection_name,
                "total_chunks": count,
                "embedding_model": self.config.embedding_model
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {}

class PDFChromaPipeline:
    """Main pipeline orchestrating PDF processing and Chroma indexing"""

    def __init__(self, config: ProcessingConfig):
        """
        Initialize the complete pipeline

        Args:
            config: Processing configuration
        """
        self.config = config
        self.pdf_processor = PDFProcessor()
        self.text_chunker = TextChunker(config)
        self.chroma_indexer = ChromaIndexer(config)

        logger.info("PDF-Chroma pipeline initialized successfully")

    def process_single_pdf(self, pdf_path: Path) -> int:
        """
        Process a single PDF file and add to Chroma

        Args:
            pdf_path: Path to the PDF file

        Returns:
            int: Number of chunks added
        """
        try:
            # Process PDF with docling
            document = self.pdf_processor.process_pdf(pdf_path)

            # Extract text and metadata
            text = self.pdf_processor.extract_full_text(document)
            metadata = self.pdf_processor.get_document_metadata(document, pdf_path)

            if not text.strip():
                logger.warning(f"No text content found in PDF: {pdf_path}")
                return 0

            # Chunk the text
            chunks = self.text_chunker.chunk_text(text, metadata)

            if not chunks:
                logger.warning(f"No chunks created from PDF: {pdf_path}")
                return 0

            # Add to Chroma
            chunks_added = self.chroma_indexer.add_chunks(chunks)

            logger.info(f"Successfully processed PDF {pdf_path}: {chunks_added} chunks added")
            return chunks_added

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return 0

    def process_pdf_directory(self, pdf_directory: Optional[Path] = None) -> Dict[str, Any]:
        """
        Process all PDF files in a directory

        Args:
            pdf_directory: Directory containing PDF files (default: config.pdf_directory)

        Returns:
            Dict[str, Any]: Processing results
        """
        if pdf_directory is None:
            pdf_directory = Path(self.config.pdf_directory)

        if not pdf_directory.exists():
            raise FileNotFoundError(f"PDF directory not found: {pdf_directory}")

        # Find all PDF files
        pdf_files = list(pdf_directory.glob("*.pdf"))

        if not pdf_files:
            logger.warning(f"No PDF files found in directory: {pdf_directory}")
            return {"processed": 0, "total_chunks": 0, "files": []}

        logger.info(f"Found {len(pdf_files)} PDF files to process")

        results = {
            "processed": 0,
            "failed": 0,
            "total_chunks": 0,
            "files": []
        }

        for pdf_path in pdf_files:
            try:
                chunks_added = self.process_single_pdf(pdf_path)
                if chunks_added > 0:
                    results["processed"] += 1
                    results["total_chunks"] += chunks_added
                    results["files"].append({
                        "file": str(pdf_path),
                        "chunks": chunks_added,
                        "status": "success"
                    })
                else:
                    results["failed"] += 1
                    results["files"].append({
                        "file": str(pdf_path),
                        "chunks": 0,
                        "status": "failed"
                    })
            except Exception as e:
                logger.error(f"Failed to process PDF {pdf_path}: {str(e)}")
                results["failed"] += 1
                results["files"].append({
                    "file": str(pdf_path),
                    "chunks": 0,
                    "status": "error",
                    "error": str(e)
                })

        logger.info(f"Processing complete: {results['processed']} succeeded, {results['failed']} failed, {results['total_chunks']} total chunks")
        return results

    def search_documents(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Search in the indexed documents

        Args:
            query: Search query
            n_results: Number of results to return

        Returns:
            Dict[str, Any]: Search results
        """
        return self.chroma_indexer.search(query, n_results)

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        chroma_stats = self.chroma_indexer.get_collection_stats()
        return {
            "config": {
                "chunk_size": self.config.chunk_size,
                "chunk_overlap": self.config.chunk_overlap,
                "embedding_model": self.config.embedding_model,
                "pdf_directory": self.config.pdf_directory
            },
            "chroma": chroma_stats
        }

def main():
    """Main function demonstrating usage"""

    # Load configuration
    config = ProcessingConfig.from_env()

    # Initialize pipeline
    pipeline = PDFChromaPipeline(config)

    # Process all PDFs in directory
    try:
        results = pipeline.process_pdf_directory()

        print("\n" + "="*50)
        print("PROCESSING RESULTS")
        print("="*50)
        print(f"PDFs processed: {results['processed']}")
        print(f"PDFs failed: {results['failed']}")
        print(f"Total chunks added: {results['total_chunks']}")

        print("\nFile details:")
        for file_info in results['files']:
            status_symbol = "✓" if file_info['status'] == 'success' else "✗"
            print(f"  {status_symbol} {Path(file_info['file']).name}: {file_info['chunks']} chunks")

        # Get collection stats
        stats = pipeline.get_stats()
        print(f"\nCollection stats: {stats['chroma']}")

        # Example search
        if results['total_chunks'] > 0:
            print("\n" + "="*50)
            print("EXAMPLE SEARCH")
            print("="*50)

            # Try a generic search query
            try:
                search_results = pipeline.search_documents("document content", n_results=3)
                if search_results.get('documents') and search_results['documents'][0]:
                    print("\nTop 3 results for 'document content':")
                    for i, (doc, metadata, distance) in enumerate(zip(
                        search_results['documents'][0][:3],
                        search_results['metadatas'][0][:3],
                        search_results['distances'][0][:3]
                    )):
                        print(f"\nResult {i+1}:")
                        print(f"  File: {metadata.get('file_name', 'Unknown')}")
                        print(f"  Chunk {metadata.get('chunk_index', 'Unknown')}")
                        print(f"  Distance: {distance:.4f}")
                        print(f"  Preview: {doc[:100]}...")
                else:
                    print("No search results found")
            except Exception as e:
                print(f"Search failed: {str(e)}")

    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()