import os
import pdfplumber
import docx
from typing import List, Dict

class ResumeProcessor:
    """Handles text extraction from PDF and DOCX files."""

    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extracts text from a given file path based on its extension."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return ResumeProcessor._extract_from_pdf(file_path)
        elif ext == '.docx':
            return ResumeProcessor._extract_from_docx(file_path)
        elif ext == '.txt':
            return ResumeProcessor._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        doc = docx.Document(file_path)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return "\n".join(text).strip()

    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Simple sliding window chunking."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

if __name__ == "__main__":
    # Quick test
    # print(ResumeProcessor.extract_text("path/to/resume.pdf"))
    pass
