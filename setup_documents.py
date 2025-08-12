#!/usr/bin/env python3
"""
Setup script for 45Q Tax Credit application.
This script helps initialize the system and process documents.
"""

import os
import sys
from pathlib import Path
from app.utils.document_loader import DocumentProcessor
from app.services.rag_service import RAGService


def setup_directories():
    """Create necessary directories."""
    directories = [
        "app/data/documents",
        "vector_db",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def process_documents(documents_path: str):
    """Process documents for the RAG system."""
    print(f"\nProcessing documents from: {documents_path}")
    
    if not os.path.exists(documents_path):
        print(f"❌ Documents directory not found: {documents_path}")
        return False
    
    # Initialize document processor
    processor = DocumentProcessor()
    
    # Process documents
    result = processor.process_documents_for_rag(documents_path)
    
    if result["success"]:
        print(f"✓ Successfully processed {result['documents_processed']} documents")
        print(f"✓ Created {result['chunks_created']} chunks")
        
        # Initialize RAG service and add documents
        rag_service = RAGService()
        rag_service.add_documents(result["chunks"])
        print("✓ Documents added to vector store")
        
        # Get document summary
        summary = processor.get_document_summary(result["documents"])
        print(f"\nDocument Summary:")
        print(f"  - Total documents: {summary['total_documents']}")
        print(f"  - File types: {summary['file_types']}")
        print(f"  - Total content length: {summary['total_content_length']:,} characters")
        
        # Validate content
        validation = processor.validate_document_content(result["documents"])
        print(f"\nContent Validation:")
        print(f"  - Relevant documents: {validation['relevant_documents']}")
        print(f"  - Irrelevant documents: {validation['irrelevant_documents']}")
        print(f"  - Keywords found: {validation['keywords_found']}")
        
        return True
    else:
        print(f"❌ Failed to process documents: {result.get('error', 'Unknown error')}")
        return False


def check_environment():
    """Check if environment is properly configured."""
    print("Checking environment configuration...")
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. Please copy env.example to .env and configure your API keys.")
        return False
    
    # Check if documents directory exists
    documents_dir = "app/data/documents"
    if not os.path.exists(documents_dir):
        print(f"⚠️  Documents directory not found: {documents_dir}")
        print("   Please add your 45Q documents to this directory.")
        return False
    
    # Check if documents exist
    documents = list(Path(documents_dir).glob("*"))
    if not documents:
        print(f"⚠️  No documents found in {documents_dir}")
        print("   Please add your 45Q documents (PDF, TXT, DOCX) to this directory.")
        return False
    
    print("✓ Environment appears to be configured")
    return True


def main():
    """Main setup function."""
    print("45Q Tax Credit Application Setup")
    print("=" * 40)
    
    # Setup directories
    setup_directories()
    
    # Check environment
    if not check_environment():
        print("\nSetup incomplete. Please address the issues above.")
        return
    
    # Process documents
    documents_path = "app/data/documents"
    if process_documents(documents_path):
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Configure your LLM API keys in .env file")
        print("2. Run the application: uvicorn app.main:app --reload")
        print("3. Access the API documentation at: http://localhost:8000/docs")
    else:
        print("\n❌ Setup failed. Please check the errors above.")


if __name__ == "__main__":
    main() 