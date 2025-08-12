import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import json

from app.config import settings, get_llm_config
from app.models.eligibility import (
    AssessmentRequest, AnswerSubmission, AssessmentResponse
)
from app.models.forecasting import ForecastingRequest, ForecastingResponse
from app.models.responses import (
    BaseResponse, 
    HealthResponse, 
    RAGResponse, 
    DocumentUploadResponse,
    QuestionRequest
)
from app.services.eligibility_service import EligibilityService
from app.services.forecasting_service import ForecastingService
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.utils.document_loader import DocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="45Q Tax Credit Eligibility & Forecasting System",
    description="A model-agnostic RAG application for 45Q tax credit analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize services
eligibility_service = EligibilityService()
forecasting_service = ForecastingService()
rag_service = RAGService()
llm_service = LLMService()
document_processor = DocumentProcessor()


@app.get("/")
async def root():
    """Serve the main HTML page."""
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    else:
        return {"message": "45Q Tax Credit Application API", "docs": "/docs"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check LLM service
        provider_info = llm_service.get_provider_info()
        
        return HealthResponse(
            success=True,
            message="Service is healthy",
            status="healthy",
            version="1.0.0",
            timestamp=datetime.now().isoformat(),
            data={
                "llm_provider": provider_info,
                "vector_store": {"status": "available"}
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            success=False,
            message="Service health check failed",
            status="unhealthy",
            version="1.0.0",
            timestamp=datetime.now().isoformat(),
            error=str(e)
        )


@app.post("/assess-eligibility", response_model=AssessmentResponse)
async def start_eligibility_assessment(request: AssessmentRequest):
    """Start a new eligibility assessment."""
    try:
        assessment = eligibility_service.start_assessment(request.session_id)
        current_question = eligibility_service.get_current_question(assessment.session_id)
        
        return AssessmentResponse(
            session_id=assessment.session_id,
            current_question=current_question,
            progress=0.0,
            is_complete=False
        )
    except Exception as e:
        logger.error(f"Error starting assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/submit-answer", response_model=AssessmentResponse)
async def submit_answer(submission: AnswerSubmission):
    """Submit an answer to the eligibility questionnaire."""
    try:
        result = eligibility_service.submit_answer(
            submission.session_id,
            submission.question_id,
            submission.answer
        )
        
        if result["is_complete"]:
            # Assessment is complete, return eligibility result
            return AssessmentResponse(
                session_id=submission.session_id,
                progress=1.0,
                is_complete=True,
                eligibility_result=result["eligibility_result"]
            )
        else:
            # Return next question
            return AssessmentResponse(
                session_id=submission.session_id,
                current_question=result["next_question"],
                progress=result["progress"],
                is_complete=False
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/assessment-progress/{session_id}")
async def get_assessment_progress(session_id: str):
    """Get the current progress of an assessment."""
    try:
        progress = eligibility_service.get_assessment_progress(session_id)
        return BaseResponse(
            success=True,
            message="Assessment progress retrieved",
            data=progress
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting assessment progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/forecast-credits", response_model=ForecastingResponse)
async def generate_credit_forecast(request: ForecastingRequest):
    """Generate a credit forecast based on facility information."""
    try:
        forecast = await forecasting_service.generate_forecast(
            request.facility_info,
            {
                "annual_co2_captured": request.annual_co2_captured,
                "capture_efficiency": request.capture_efficiency,
                "sequestration_method": request.sequestration_method,
                "sequestration_location": request.sequestration_location,
                "start_date": request.start_date,
                "domestic_content_percentage": request.domestic_content_percentage,
                "energy_community_eligible": request.energy_community_eligible,
                "carbon_intensity_data": request.carbon_intensity_data
            }
        )
        
        return ForecastingResponse(
            session_id=request.session_id,
            forecast=forecast,
            confidence_score=0.85,
            warnings=[],
            next_steps=[
                "Review forecast assumptions",
                "Consider bonus credit opportunities",
                "Consult with tax professionals"
            ]
        )
    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask-question", response_model=RAGResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question using the RAG system."""
    try:
        result = await rag_service.answer_question(request.question, request.context)
        
        return RAGResponse(
            success=True,
            message="Question answered successfully",
            answer=result["answer"],
            sources=result["sources"],
            confidence_score=result["confidence_score"],
            context_used=result["context"].split("\n\n") if result["context"] else []
        )
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-documents", response_model=DocumentUploadResponse)
async def upload_documents(files: list[UploadFile] = File(...)):
    """Upload and process documents for the RAG system."""
    try:
        # Create documents directory if it doesn't exist
        documents_dir = "app/data/documents"
        import os
        os.makedirs(documents_dir, exist_ok=True)
        
        documents_processed = 0
        total_chunks = 0
        
        for file in files:
            # Save uploaded file
            file_path = os.path.join(documents_dir, file.filename)
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            documents_processed += 1
        
        # Process documents for RAG
        processing_result = document_processor.process_documents_for_rag(documents_dir)
        
        if processing_result["success"]:
            # Update RAG system with new documents
            rag_service.add_documents(processing_result["chunks"])
            total_chunks = processing_result["chunks_created"]
        
        return DocumentUploadResponse(
            success=True,
            message=f"Successfully processed {documents_processed} documents",
            documents_processed=documents_processed,
            total_chunks=total_chunks,
            vector_db_updated=processing_result["success"],
            processing_time=0.0  # Could add actual timing
        )
    except Exception as e:
        logger.error(f"Error uploading documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vector-store-stats")
async def get_vector_store_stats():
    """Get statistics about the vector store."""
    try:
        stats = rag_service.get_vector_store_stats()
        return BaseResponse(
            success=True,
            message="Vector store statistics retrieved",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting vector store stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/llm-provider-info")
async def get_llm_provider_info():
    """Get information about the current LLM provider."""
    try:
        provider_info = llm_service.get_provider_info()
        return BaseResponse(
            success=True,
            message="LLM provider information retrieved",
            data=provider_info
        )
    except Exception as e:
        logger.error(f"Error getting LLM provider info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detailed-guidance/{session_id}")
async def get_detailed_guidance(session_id: str):
    """Get detailed guidance for a completed assessment."""
    try:
        guidance = await eligibility_service.get_detailed_guidance(session_id)
        return BaseResponse(
            success=True,
            message="Detailed guidance generated",
            data=guidance
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting detailed guidance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detailed-forecast-analysis")
async def get_detailed_forecast_analysis(request: ForecastingRequest):
    """Get detailed forecast analysis with RAG guidance."""
    try:
        analysis = await forecasting_service.get_detailed_forecast_analysis(
            request.facility_info,
            {
                "annual_co2_captured": request.annual_co2_captured,
                "capture_efficiency": request.capture_efficiency,
                "sequestration_method": request.sequestration_method,
                "sequestration_location": request.sequestration_location,
                "start_date": request.start_date,
                "domestic_content_percentage": request.domestic_content_percentage,
                "energy_community_eligible": request.energy_community_eligible,
                "carbon_intensity_data": request.carbon_intensity_data
            }
        )
        
        return BaseResponse(
            success=True,
            message="Detailed forecast analysis generated",
            data=analysis
        )
    except Exception as e:
        logger.error(f"Error generating detailed forecast analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/assessment-prompt")
async def get_assessment_prompt():
    """Get the generated assessment prompt for interactive assessments."""
    try:
        # Try to load the generated prompt
        prompt_file = "assessment_prompt.json"
        if os.path.exists(prompt_file):
            with open(prompt_file, "r") as f:
                data = json.load(f)
                return BaseResponse(
                    success=True,
                    message="Assessment prompt retrieved",
                    data={"prompt": data["improved_prompt"]}
                )
        else:
            # Return a default prompt if no generated one exists
            default_prompt = """You are an expert 45Q tax credit eligibility assessor. Your job is to determine if a company qualifies for 45Q credits and provide a complete assessment.

IMPORTANT RULES:
- NEVER refer users to tax professionals or external consultants
- ALWAYS provide complete eligibility assessments when you have enough information
- Ask specific, targeted questions based on the 45Q regulations
- Continue asking questions until you can make a definitive determination
- Give comprehensive assessments with clear yes/no eligibility and reasoning

ASSESSMENT PROCESS:
1. Start with general facility information
2. Ask targeted follow-up questions based on responses
3. Continue until you have enough information for a complete assessment
4. Provide a definitive eligibility determination with:
   - Eligible: Yes/No
   - Reasoning based on 45Q regulations
   - Specific provisions that apply
   - Estimated credit amounts if possible
   - Next steps for the company

Remember: You are the expert. Provide complete guidance, don't defer to others."""
            
            return BaseResponse(
                success=True,
                message="Default assessment prompt retrieved",
                data={"prompt": default_prompt}
            )
    except Exception as e:
        logger.error(f"Error getting assessment prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-enhanced-questions")
async def get_enhanced_questions():
    """Get the enhanced 45Q assessment questions."""
    try:
        # Load the enhanced questions from the generated file
        questions_file = "enhanced_question_base.json"
        if os.path.exists(questions_file):
            with open(questions_file, "r") as f:
                data = json.load(f)
                
                # Flatten all questions into a single array
                all_questions = []
                for category_key, category_data in data["categories"].items():
                    for question in category_data["questions"]:
                        all_questions.append(question)
                
                return BaseResponse(
                    success=True,
                    message="Enhanced questions loaded successfully",
                    data={
                        "questions": all_questions,
                        "total_questions": len(all_questions),
                        "categories": len(data["categories"])
                    }
                )
        else:
            raise HTTPException(status_code=404, detail="Enhanced questions file not found. Please run the question generator first.")
            
    except Exception as e:
        logger.error(f"Error loading enhanced questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/complete-enhanced-assessment")
async def complete_enhanced_assessment(request: dict):
    """Complete the enhanced assessment with all answers."""
    try:
        session_id = request.get("session_id")
        answers = request.get("answers", [])
        
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        if not answers:
            raise HTTPException(status_code=400, detail="At least one answer is required")
        
        # Create a comprehensive assessment prompt
        assessment_prompt = f"""
You are an expert 45Q tax credit eligibility assessor. Analyze the following facility information and provide a comprehensive eligibility assessment.

FACILITY ASSESSMENT DATA:
Session ID: {session_id}
Total Questions Answered: {len(answers)}

ANSWERS PROVIDED:
"""
        
        # Add all answers to the prompt
        for answer in answers:
            assessment_prompt += f"\nQuestion: {answer['question']}"
            assessment_prompt += f"\nAnswer: {answer['answer']}"
            assessment_prompt += f"\nCategory: {answer['category']}\n"
        
        assessment_prompt += """

ASSESSMENT REQUIREMENTS:
1. Determine if the facility is eligible for 45Q tax credits
2. Identify which specific 45Q provisions apply
3. Provide reasoning for eligibility determination
4. Estimate potential credit amounts if eligible
5. Identify any missing information that could affect eligibility
6. Provide specific next steps and recommendations

Please provide a comprehensive assessment with:
- ELIGIBILITY: Yes/No with clear reasoning
- APPLICABLE PROVISIONS: List specific 45Q provisions
- CREDIT ESTIMATES: Potential credit amounts if eligible
- MISSING INFORMATION: Any critical gaps
- NEXT STEPS: Specific recommendations
- RISK FACTORS: Any potential issues or concerns

Format your response in a clear, structured manner.
"""
        
        # Use the LLM service to generate the assessment
        llm_config = get_llm_config()
        assessment_result = await llm_service.generate_response(assessment_prompt, llm_config)
        
        return BaseResponse(
            success=True,
            message="Enhanced assessment completed successfully",
            data={
                "assessment": assessment_result,
                "session_id": session_id,
                "questions_answered": len(answers),
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error completing enhanced assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/regenerate-question-base")
async def regenerate_question_base():
    """Regenerate the question base by running the analysis script."""
    try:
        import subprocess
        import sys
        
        # Run the question base generation script
        result = subprocess.run([
            sys.executable, "generate_question_base.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            return BaseResponse(
                success=True,
                message="Question base regenerated successfully",
                data={"output": result.stdout}
            )
        else:
            return BaseResponse(
                success=False,
                message="Failed to regenerate question base",
                data={"error": result.stderr}
            )
    except Exception as e:
        logger.error(f"Error regenerating question base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 