#!/usr/bin/env python3
"""
Simple PDF reader using Docling library.
Extracts text and metadata from PDF files.
"""

import sys
import os
from pathlib import Path
import argparse
from typing import Optional

from docling.document_converter import DocumentConverter
from docling.datamodel.document import DoclingDocument


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
        result['text'] = doc.text_to_markdown()

        # Get page count
        result['page_count'] = len(doc.pages)

        # Extract title if available
        if hasattr(doc, 'title') and doc.title:
            result['title'] = doc.title

        # Extract metadata
        if hasattr(doc, 'file_info') and doc.file_info:
            result['metadata'] = {
                'author': getattr(doc.file_info, 'author', ''),
                'subject': getattr(doc.file_info, 'subject', ''),
                'creator': getattr(doc.file_info, 'creator', ''),
                'producer': getattr(doc.file_info, 'producer', ''),
                'creation_date': getattr(doc.file_info, 'creation_date', ''),
                'modification_date': getattr(doc.file_info, 'modification_date', '')
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


def save_doc_to_file(doc: DoclingDocument, output_path: str):
    """
    Save raw DoclingDocument to a text file.

    Args:
        doc: DoclingDocument object
        output_path: Path for the output file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("Raw DoclingDocument Content\n")
            f.write("="*50 + "\n")
            f.write(str(doc))

        print(f"\nRaw doc saved to: {output_path}")

    except Exception as e:
        print(f"Error saving doc to file: {str(e)}")


def export_to_markdown(doc: DoclingDocument, output_path: str, include_metadata: bool = True) -> bool:
    """
    Export DoclingDocument to markdown format and save to file.

    Args:
        doc: DoclingDocument object
        output_path: Path for the output markdown file
        include_metadata: Whether to include document metadata in the output

    Returns:
        True if successful, False otherwise
    """
    try:
        markdown_content = []

        # Add title if available
        if include_metadata and hasattr(doc, 'title') and doc.title:
            markdown_content.append(f"# {doc.title}\n")

        # Add metadata section if requested
        if include_metadata and hasattr(doc, 'file_info') and doc.file_info:
            markdown_content.append("## Document Metadata\n")
            metadata_fields = [
                ('Author', getattr(doc.file_info, 'author', None)),
                ('Subject', getattr(doc.file_info, 'subject', None)),
                ('Creator', getattr(doc.file_info, 'creator', None)),
                ('Producer', getattr(doc.file_info, 'producer', None)),
                ('Creation Date', getattr(doc.file_info, 'creation_date', None)),
                ('Modification Date', getattr(doc.file_info, 'modification_date', None)),
                ('Page Count', len(doc.pages) if hasattr(doc, 'pages') else None)
            ]

            for field_name, field_value in metadata_fields:
                if field_value:
                    markdown_content.append(f"- **{field_name}**: {field_value}")
            markdown_content.append("")

        # Add the main content as markdown
        markdown_content.append("## Document Content\n")
        markdown_content.append(doc.export_to_markdown())

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_content))

        print(f"Markdown exported successfully to: {output_path}")
        return True

    except Exception as e:
        print(f"Error exporting to markdown: {str(e)}")
        return False


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
  python docling_pdf_simple.py
  python docling_pdf_simple.py --full-text
  python docling_pdf_simple.py --output "extracted_text.txt"
  python docling_pdf_simple.py --full-text --output "full_content.txt"
        """
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

    # Hard-coded PDF file path
    # pdf_path = '/Users/hiep/Project/docling-material/docs_sample/Prompt Engineering Guide.pdf'
    pdf_path = '/Users/hiep/Project/docling-material/docs_sample/EXT_ITA_VGEX_Anforderungskatalog_Heilmittel.pdf'

    # Generate markdown filename based on PDF filename
    pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    markdown_path = f'/Users/hiep/Project/docling-material/{pdf_filename}.md'

    # Read the PDF file
    doc = read_pdf_with_docling(pdf_path)

    if doc is None:
        sys.exit(1)

    # Write raw doc to file immediately after getting it
    save_doc_to_file(doc, '/Users/hiep/Project/docling-material/doc.txt')

    # Export to markdown using the new function
    print(f"Exporting markdown to: {markdown_path}")
    export_to_markdown(doc, markdown_path, include_metadata=True)

    # # Extract content
    # content = extract_text_and_metadata(doc)

    # # Display information
    # print_document_info(content, args.full_text)

    # # Save to file if requested
    # if args.output:
    #     save_to_file(content, args.output)

    print("\nPDF processing completed successfully!")


if __name__ == "__main__":
    main()