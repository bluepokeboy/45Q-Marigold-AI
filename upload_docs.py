#!/usr/bin/env python3
"""
Script to upload existing documents to the vector store.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.rag_service import RAGService
from app.utils.document_loader import DocumentProcessor

def main():
    """Upload documents to the vector store."""
    print("📄 Uploading documents to vector store...")
    
    # Initialize services
    rag_service = RAGService()
    document_processor = DocumentProcessor()
    
    # Process documents
    documents_dir = "app/data/documents"
    
    if not os.path.exists(documents_dir):
        print(f"❌ Documents directory not found: {documents_dir}")
        return
    
    # Get list of documents
    doc_files = [f for f in os.listdir(documents_dir) if f.endswith(('.pdf', '.txt', '.docx'))]
    
    if not doc_files:
        print("❌ No documents found in the documents directory")
        return
    
    print(f"Found {len(doc_files)} documents: {doc_files}")
    
    # Process documents
    result = document_processor.process_documents_for_rag(documents_dir)
    
    if not result["success"]:
        print(f"❌ Failed to process documents: {result.get('error', 'Unknown error')}")
        return
    
    print(f"✅ Processed {result['documents_processed']} documents")
    print(f"✅ Created {result['chunks_created']} chunks")
    
    # Add documents to vector store
    if result["chunks"]:
        rag_service.add_documents(result["chunks"])
        print("✅ Documents added to vector store")
        
        # Get vector store stats
        stats = rag_service.get_vector_store_stats()
        print(f"📊 Vector store stats: {stats}")
    else:
        print("❌ No chunks to add to vector store")
    
    print("🎉 Document upload complete!")

if __name__ == "__main__":
    main() 