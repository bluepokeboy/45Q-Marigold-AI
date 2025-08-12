import os
import logging
from typing import List, Dict, Any
from pathlib import Path
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    DirectoryLoader
)
from app.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Utility for processing and loading documents for the RAG system."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )
    
    def load_documents_from_directory(self, directory_path: str) -> List[Document]:
        """Load all supported documents from a directory."""
        documents = []
        directory = Path(directory_path)
        
        if not directory.exists():
            logger.warning(f"Directory {directory_path} does not exist")
            return documents
        
        # Load PDF files
        pdf_documents = self._load_pdf_documents(directory)
        documents.extend(pdf_documents)
        
        # Load text files
        text_documents = self._load_text_documents(directory)
        documents.extend(text_documents)
        
        # Load Word documents
        docx_documents = self._load_docx_documents(directory)
        documents.extend(docx_documents)
        
        logger.info(f"Loaded {len(documents)} documents from {directory_path}")
        return documents
    
    def _load_pdf_documents(self, directory: Path) -> List[Document]:
        """Load PDF documents from directory."""
        documents = []
        pdf_files = list(directory.glob("**/*.pdf"))
        
        for pdf_file in pdf_files:
            try:
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()
                
                # Add metadata
                for doc in docs:
                    doc.metadata.update({
                        "source": str(pdf_file),
                        "file_type": "pdf",
                        "file_name": pdf_file.name
                    })
                
                documents.extend(docs)
                logger.info(f"Loaded PDF: {pdf_file.name}")
                
            except Exception as e:
                logger.error(f"Error loading PDF {pdf_file}: {e}")
        
        return documents
    
    def _load_text_documents(self, directory: Path) -> List[Document]:
        """Load text documents from directory."""
        documents = []
        text_files = list(directory.glob("**/*.txt"))
        
        for text_file in text_files:
            try:
                loader = TextLoader(str(text_file))
                docs = loader.load()
                
                # Add metadata
                for doc in docs:
                    doc.metadata.update({
                        "source": str(text_file),
                        "file_type": "text",
                        "file_name": text_file.name
                    })
                
                documents.extend(docs)
                logger.info(f"Loaded text file: {text_file.name}")
                
            except Exception as e:
                logger.error(f"Error loading text file {text_file}: {e}")
        
        return documents
    
    def _load_docx_documents(self, directory: Path) -> List[Document]:
        """Load Word documents from directory."""
        documents = []
        docx_files = list(directory.glob("**/*.docx"))
        
        for docx_file in docx_files:
            try:
                loader = Docx2txtLoader(str(docx_file))
                docs = loader.load()
                
                # Add metadata
                for doc in docs:
                    doc.metadata.update({
                        "source": str(docx_file),
                        "file_type": "docx",
                        "file_name": docx_file.name
                    })
                
                documents.extend(docs)
                logger.info(f"Loaded Word document: {docx_file.name}")
                
            except Exception as e:
                logger.error(f"Error loading Word document {docx_file}: {e}")
        
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        if not documents:
            return []
        
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks
    
    def process_documents_for_rag(self, directory_path: str) -> Dict[str, Any]:
        """Complete document processing pipeline for RAG system."""
        # Load documents
        documents = self.load_documents_from_directory(directory_path)
        
        if not documents:
            return {
                "success": False,
                "error": "No documents found or loaded",
                "documents_processed": 0,
                "chunks_created": 0
            }
        
        # Split documents
        chunks = self.split_documents(documents)
        
        # Generate processing summary
        file_types = {}
        for doc in documents:
            file_type = doc.metadata.get("file_type", "unknown")
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        return {
            "success": True,
            "documents_processed": len(documents),
            "chunks_created": len(chunks),
            "file_types": file_types,
            "documents": documents,
            "chunks": chunks
        }
    
    def validate_document_content(self, documents: List[Document]) -> Dict[str, Any]:
        """Validate document content for 45Q relevance."""
        validation_results = {
            "total_documents": len(documents),
            "relevant_documents": 0,
            "irrelevant_documents": 0,
            "keywords_found": [],
            "validation_errors": []
        }
        
        # Keywords related to 45Q tax credits
        relevant_keywords = [
            "45q", "section 45q", "carbon sequestration", "co2 capture",
            "tax credit", "carbon capture", "geologic storage", "eor",
            "enhanced oil recovery", "direct air capture", "dac",
            "utilization", "carbon dioxide", "greenhouse gas"
        ]
        
        for doc in documents:
            content_lower = doc.page_content.lower()
            found_keywords = [keyword for keyword in relevant_keywords if keyword in content_lower]
            
            if found_keywords:
                validation_results["relevant_documents"] += 1
                validation_results["keywords_found"].extend(found_keywords)
            else:
                validation_results["irrelevant_documents"] += 1
        
        # Remove duplicates from keywords
        validation_results["keywords_found"] = list(set(validation_results["keywords_found"]))
        
        return validation_results
    
    def get_document_summary(self, documents: List[Document]) -> Dict[str, Any]:
        """Generate a summary of processed documents."""
        if not documents:
            return {"error": "No documents to summarize"}
        
        # File type distribution
        file_types = {}
        total_content_length = 0
        
        for doc in documents:
            file_type = doc.metadata.get("file_type", "unknown")
            file_types[file_type] = file_types.get(file_type, 0) + 1
            total_content_length += len(doc.page_content)
        
        # Average document length
        avg_length = total_content_length / len(documents) if documents else 0
        
        return {
            "total_documents": len(documents),
            "file_types": file_types,
            "total_content_length": total_content_length,
            "average_document_length": avg_length,
            "documents": [
                {
                    "file_name": doc.metadata.get("file_name", "unknown"),
                    "file_type": doc.metadata.get("file_type", "unknown"),
                    "content_length": len(doc.page_content),
                    "source": doc.metadata.get("source", "unknown")
                }
                for doc in documents
            ]
        } 