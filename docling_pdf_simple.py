#!/usr/bin/env python3
"""
Simple PDF reader using Docling library.
Extracts text and metadata from PDF files.
"""

import sys
from pathlib import Path
import argparse
from typing import Optional

try:
    from docling.document import Document
    from docling.datamodel.base_models import DoclingDocument
except ImportError:
    print("Error: Docling library not found. Please install it with: pip install docling")
    sys.exit(1)


def read_pdf_with_docling(pdf_path: str) -> Optional[DoclingDocument]:
    """
    Read PDF file using Docling library.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        DoclingDocument object or None if failed
    """
    try:
        # Validate file exists
        path = Path(pdf_path)
        if not path.exists():
            print(f"Error: File not found: {pdf_path}")
            return None

        if not path.is_file():
            print(f"Error: Path is not a file: {pdf_path}")
            return None

        if path.suffix.lower() != '.pdf':
            print(f"Error: File is not a PDF: {pdf_path}")
            return None

        print(f"Reading PDF: {pdf_path}")

        # Load document using Docling
        doc = Document.from_path(str(path))

        return doc

    except Exception as e:
        print(f"Error reading PDF '{pdf_path}': {str(e)}")
        return None


def extract_text_and_metadata(doc: DoclingDocument) -> dict:
    """
    Extract text and metadata from Docling document.

    Args:
        doc: DoclingDocument object

    Returns:
        Dictionary containing extracted content
    """
    result = {
        'text': '',
        'page_count': 0,
        'title': '',
        'metadata': {}
    }

    try:
        # Extract full text
        result['text'] = doc.text()

        # Get page count
        result['page_count'] = len(doc.pages)

        # Extract title if available
        if hasattr(doc, 'title') and doc.title:
            result['title'] = doc.title

        # Extract metadata
        if hasattr(doc, 'meta') and doc.meta:
            result['metadata'] = {
                'author': getattr(doc.meta, 'author', ''),
                'subject': getattr(doc.meta, 'subject', ''),
                'creator': getattr(doc.meta, 'creator', ''),
                'producer': getattr(doc.meta, 'producer', ''),
                'creation_date': getattr(doc.meta, 'creation_date', ''),
                'modification_date': getattr(doc.meta, 'modification_date', '')
            }

        return result

    except Exception as e:
        print(f"Error extracting content: {str(e)}")
        return result


def print_document_info(content: dict, show_full_text: bool = False):
    """
    Print document information in a readable format.

    Args:
        content: Dictionary with extracted content
        show_full_text: Whether to print the full text content
    """
    print("\n" + "=" * 50)
    print("PDF DOCUMENT INFORMATION")
    print("="*50)

    print(f"Title: {content['title'] or 'N/A'}")
    print(f"Page Count: {content['page_count']}")

    if content['metadata']:
        print("\nMetadata:")
        for key, value in content['metadata'].items():
            if value:
                print(f"  {key.replace('_', ' ').title()}: {value}")

    print(f"\nText Length: {len(content['text'])} characters")

    if show_full_text and content['text']:
        print("\n" + "=" * 50)
        print("FULL TEXT CONTENT")
        print("="*50)
        print(content['text'])
    elif content['text']:
        # Show first 500 characters as preview
        preview = content['text'][:500]
        print("\nText Preview (first 500 characters):")
        print("-" * 30)
        print(preview)
        if len(content['text']) > 500:
            print("... (use --full-text to see complete content)")


def save_to_file(content: dict, output_path: str):
    """
    Save extracted content to a text file.

    Args:
        content: Dictionary with extracted content
        output_path: Path for the output file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("PDF Document Information\n")
            f.write("="*50 + "\n")
            f.write(f"Title: {content['title'] or 'N/A'}\n")
            f.write(f"Page Count: {content['page_count']}\n")

            if content['metadata']:
                f.write("\nMetadata:\n")
                for key, value in content['metadata'].items():
                    if value:
                        f.write(f"  {key.replace('_', ' ').title()}: {value}\n")

            f.write(f"\nText Length: {len(content['text'])} characters\n")
            f.write("\n" + "="*50 + "\n")
            f.write("FULL TEXT CONTENT\n")
            f.write("="*50 + "\n")
            f.write(content['text'])

        print(f"\nContent saved to: {output_path}")

    except Exception as e:
        print(f"Error saving to file: {str(e)}")


def main():
    """Main function to handle command line interface."""
    parser = argparse.ArgumentParser(
        description="Read PDF files using Docling library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python docling_pdf_simple.py "document.pdf"
  python docling_pdf_simple.py "document.pdf" --full-text
  python docling_pdf_simple.py "document.pdf" --output "extracted_text.txt"
  python docling_pdf_simple.py "document.pdf" --full-text --output "full_content.txt"
        """
    )

    parser.add_argument(
        'pdf_path',
        help='Path to the PDF file to read'
    )

    parser.add_argument(
        '--full-text',
        action='store_true',
        help='Display the full text content (default: show preview only)'
    )

    parser.add_argument(
        '--output', '-o',
        help='Save extracted content to a text file'
    )

    args = parser.parse_args()

    # Read the PDF file
    doc = read_pdf_with_docling(args.pdf_path)

    if doc is None:
        sys.exit(1)

    # Extract content
    content = extract_text_and_metadata(doc)

    # Display information
    print_document_info(content, args.full_text)

    # Save to file if requested
    if args.output:
        save_to_file(content, args.output)

    print("\nPDF processing completed successfully!")


if __name__ == "__main__":
    main()