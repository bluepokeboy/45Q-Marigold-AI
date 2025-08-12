import os
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    DirectoryLoader
)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from app.config import settings
from app.services.llm_service import LLMService


class RAGService:
    """RAG service for document retrieval and question answering."""

    def __init__(self):
        self.vector_store = None
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={'device': 'cpu'}
        )
        self.llm_service = LLMService()
        self._initialize_vector_store()

    def _initialize_vector_store(self):
        """Initialize the vector store."""
        if os.path.exists(settings.vector_db_path):
            self.vector_store = Chroma(
                persist_directory=settings.vector_db_path,
                embedding_function=self.embeddings
            )
        else:
            # Create empty vector store
            self.vector_store = Chroma(
                persist_directory=settings.vector_db_path,
                embedding_function=self.embeddings
            )

    def load_documents(self, directory_path: str) -> List[Document]:
        """Load documents from a directory."""
        documents = []

        # Load PDF files
        try:
            pdf_loader = DirectoryLoader(
                directory_path,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader
            )
            documents.extend(pdf_loader.load())
        except Exception as e:
            print(f"Error loading PDFs: {e}")

        # Load text files
        try:
            text_loader = DirectoryLoader(
                directory_path,
                glob="**/*.txt",
                loader_cls=TextLoader
            )
            documents.extend(text_loader.load())
        except Exception as e:
            print(f"Error loading text files: {e}")

        # Load Word documents
        try:
            docx_loader = DirectoryLoader(
                directory_path,
                glob="**/*.docx",
                loader_cls=Docx2txtLoader
            )
            documents.extend(docx_loader.load())
        except Exception as e:
            print(f"Error loading Word documents: {e}")

        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )
        return text_splitter.split_documents(documents)

    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store."""
        if not documents:
            return

        # Split documents into chunks
        chunks = self.split_documents(documents)

        # Add to vector store (Chroma automatically persists)
        self.vector_store.add_documents(chunks)

    def update_knowledge_base(self, documents_directory: str) -> Dict[str, Any]:
        """Update the knowledge base with new documents."""
        documents = self.load_documents(documents_directory)
        chunks = self.split_documents(documents)

        # Clear existing documents and add new ones
        self.vector_store = Chroma(
            persist_directory=settings.vector_db_path,
            embedding_function=self.embeddings
        )

        self.add_documents(documents)

        return {
            "documents_processed": len(documents),
            "total_chunks": len(chunks),
            "vector_db_updated": True
        }

    def retrieve_relevant_documents(self, query: str, top_k: int = None) -> List[Document]:
        """Retrieve relevant documents for a query."""
        if top_k is None:
            top_k = settings.top_k_retrieval

        if not self.vector_store:
            return []

        # Create retriever with contextual compression
        base_retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k}
        )

        # For now, return documents directly without compression
        # to avoid the LLM service access issue
        return base_retriever.get_relevant_documents(query)

    async def answer_question(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Answer a question using RAG."""
        relevant_docs = []
        
        if not context:
            # Retrieve relevant documents
            relevant_docs = self.retrieve_relevant_documents(question)
            context = "\n\n".join([doc.page_content for doc in relevant_docs])

        # Generate answer using LLM
        answer = await self.llm_service.generate_response(question, context)

        # Calculate confidence score (simplified)
        confidence_score = self._calculate_confidence(question, answer, context)

        return {
            "answer": answer,
            "context": context,
            "confidence_score": confidence_score,
            "sources": [{"content": doc.page_content, "metadata": doc.metadata} for doc in relevant_docs]
        }

    def _calculate_confidence(self, question: str, answer: str, context: str) -> float:
        """Calculate confidence score for the answer."""
        # Simple heuristic-based confidence calculation
        # In a production system, you might use more sophisticated methods

        if not context or not answer:
            return 0.0

        # Check if answer contains key terms from question
        question_terms = set(question.lower().split())
        answer_terms = set(answer.lower().split())

        term_overlap = len(question_terms.intersection(answer_terms))
        term_coverage = term_overlap / len(question_terms) if question_terms else 0

        # Check answer length (reasonable answers are not too short or too long)
        answer_length_score = min(len(answer.split()) / 50, 1.0)  # Normalize to 0-1

        # Check if context is substantial
        context_length_score = min(len(context.split()) / 100, 1.0)

        # Combine scores
        confidence = (term_coverage * 0.4 + answer_length_score * 0.3 + context_length_score * 0.3)

        return min(confidence, 1.0)

    async def get_eligibility_guidance(self, facility_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific guidance for 45Q eligibility based on facility information."""
        query = f"""
        Based on the following facility information, determine 45Q tax credit eligibility:

        Facility Type: {facility_info.get('facility_type', 'Unknown')}
        Location: {facility_info.get('location_state', 'Unknown')}
        Ownership: {facility_info.get('ownership', 'Unknown')}
        Technology Ownership: {facility_info.get('technology_ownership', 'Unknown')}
        Capture Method: {facility_info.get('capture_method', 'Unknown')}
        Annual CO2 Captured: {facility_info.get('annual_co2_captured', 'Unknown')} metric tons

        Please provide:
        1. Eligibility determination
        2. Applicable 45Q provisions
        3. Requirements that must be met
        4. Estimated credit rates
        5. Recommendations for qualification
        """

        return await self.answer_question(query)

    async def get_credit_calculation_guidance(self, facility_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get guidance for credit calculation and forecasting."""
        query = f"""
        For a facility with the following characteristics, provide detailed 45Q credit calculation guidance:

        Facility Type: {facility_info.get('facility_type', 'Unknown')}
        Annual CO2 Captured: {facility_info.get('annual_co2_captured', 'Unknown')} metric tons
        Capture Method: {facility_info.get('capture_method', 'Unknown')}
        Sequestration Method: {facility_info.get('sequestration_method', 'Unknown')}

        Please provide:
        1. Base credit rates for different time periods
        2. Bonus credit opportunities
        3. Calculation methodology
        4. Timeline considerations
        5. Documentation requirements
        """

        return await self.answer_question(query)

    def get_vector_store_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        if not self.vector_store:
            return {"total_documents": 0, "collection_name": None}

        collection = self.vector_store._collection
        metadata = collection.metadata if hasattr(collection, 'metadata') else {}
        
        return {
            "total_documents": collection.count(),
            "collection_name": collection.name,
            "embedding_dimension": metadata.get("hnsw:space", "unknown") if metadata else "unknown"
        } 