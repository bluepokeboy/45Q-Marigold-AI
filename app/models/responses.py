from pydantic import BaseModel
from typing import Optional, Any, Dict, List


class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


class QuestionRequest(BaseModel):
    question: str
    context: Optional[str] = None


class HealthResponse(BaseResponse):
    status: str
    version: str
    timestamp: str


class ErrorResponse(BaseResponse):
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class RAGResponse(BaseResponse):
    answer: str
    sources: List[Dict[str, Any]]
    confidence_score: float
    context_used: List[str]


class DocumentUploadResponse(BaseResponse):
    documents_processed: int
    total_chunks: int
    vector_db_updated: bool
    processing_time: float 