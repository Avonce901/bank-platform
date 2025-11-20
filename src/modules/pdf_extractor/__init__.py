"""
PDF Extractor Module
Extracts text and tables from PDF files
"""
import io
import json
from typing import Dict, List, Any, Optional
import pdfplumber  # pyright: ignore
from werkzeug.datastructures import FileStorage  # pyright: ignore


class PDFExtractor:
    """Extract data from PDF files"""

    def __init__(self):
        self.extracted_data = {}

    def extract_text(self, pdf_file: FileStorage) -> str:
        """
        Extract all text from PDF
        
        Args:
            pdf_file: FileStorage object containing PDF
            
        Returns:
            Extracted text as string
        """
        try:
            text_content = []
            pdf_bytes = pdf_file.read()
            
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_content.append(f"--- Page {page_num} ---\n{text}")
            
            return "\n".join(text_content)
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    def extract_tables(self, pdf_file: FileStorage) -> List[List[Dict[str, str]]]:
        """
        Extract all tables from PDF
        
        Args:
            pdf_file: FileStorage object containing PDF
            
        Returns:
            List of tables with extracted data
        """
        try:
            tables = []
            pdf_bytes = pdf_file.read()
            
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table_idx, table in enumerate(page_tables, 1):
                            # Convert table to list of dicts
                            if table:
                                headers = table[0]
                                rows = table[1:]
                                table_data = [
                                    {headers[i]: row[i] for i in range(len(headers))}
                                    for row in rows
                                ]
                                tables.append({
                                    'page': page_num,
                                    'table_index': table_idx,
                                    'data': table_data
                                })
            
            return tables
        except Exception as e:
            raise ValueError(f"Failed to extract tables from PDF: {str(e)}")

    def extract_metadata(self, pdf_file: FileStorage) -> Dict[str, Any]:
        """
        Extract metadata from PDF
        
        Args:
            pdf_file: FileStorage object containing PDF
            
        Returns:
            Dictionary with PDF metadata
        """
        try:
            pdf_bytes = pdf_file.read()
            
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                metadata = {
                    'total_pages': len(pdf.pages),
                    'metadata': pdf.metadata if pdf.metadata else {}
                }
            
            return metadata
        except Exception as e:
            raise ValueError(f"Failed to extract metadata from PDF: {str(e)}")

    def extract_all(self, pdf_file: FileStorage) -> Dict[str, Any]:
        """
        Extract text, tables, and metadata from PDF
        
        Args:
            pdf_file: FileStorage object containing PDF
            
        Returns:
            Dictionary with all extracted data
        """
        try:
            # Reset file pointer
            pdf_file.seek(0)
            text = self.extract_text(pdf_file)
            
            pdf_file.seek(0)
            tables = self.extract_tables(pdf_file)
            
            pdf_file.seek(0)
            metadata = self.extract_metadata(pdf_file)
            
            return {
                'success': True,
                'text': text,
                'tables': tables,
                'metadata': metadata,
                'extraction_status': 'completed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'extraction_status': 'failed'
            }


def extract_pdf(pdf_file: FileStorage) -> Dict[str, Any]:
    """
    Main function to extract data from PDF
    
    Args:
        pdf_file: FileStorage object containing PDF
        
    Returns:
        Dictionary with extracted data
    """
    extractor = PDFExtractor()
    return extractor.extract_all(pdf_file)
