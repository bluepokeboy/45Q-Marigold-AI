from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class FacilityType(str, Enum):
    ELECTRIC_GENERATION = "electric_generation"
    INDUSTRIAL = "industrial"
    DIRECT_AIR_CAPTURE = "direct_air_capture"
    OTHER = "other"


class OwnershipType(str, Enum):
    OWNER = "owner"
    CLIENT = "client"
    THIRD_PARTY = "third_party"


class TechnologyOwnership(str, Enum):
    OWNER = "owner"
    LICENSED = "licensed"
    THIRD_PARTY = "third_party"


class CaptureMethod(str, Enum):
    POST_COMBUSTION = "post_combustion"
    PRE_COMBUSTION = "pre_combustion"
    OXY_FUEL = "oxy_fuel"
    DIRECT_AIR = "direct_air"
    OTHER = "other"


class QuestionType(str, Enum):
    TEXT = "text"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    NUMBER = "number"
    BOOLEAN = "boolean"


class EligibilityQuestion(BaseModel):
    id: str
    question: str
    type: QuestionType
    required: bool = True
    options: Optional[List[str]] = None
    help_text: Optional[str] = None
    depends_on: Optional[str] = None  # Question ID this depends on
    condition: Optional[Dict[str, Any]] = None  # Condition for showing this question


class EligibilityAssessment(BaseModel):
    session_id: str
    current_question_index: int = 0
    questions: List[EligibilityQuestion]
    answers: Dict[str, Any] = {}
    is_complete: bool = False
    eligibility_result: Optional[Dict[str, Any]] = None


class FacilityInfo(BaseModel):
    facility_name: str
    location_city: str
    location_state: str
    facility_type: FacilityType
    ownership: OwnershipType
    technology_ownership: TechnologyOwnership
    capture_method: CaptureMethod
    annual_co2_captured_metric_tons: Optional[float] = None
    capture_efficiency_percentage: Optional[float] = None
    facility_construction_date: Optional[str] = None
    carbon_capture_operation_date: Optional[str] = None
    sequestration_method: Optional[str] = None
    sequestration_location: Optional[str] = None
    additional_facilities: Optional[List[str]] = None


class EligibilityResult(BaseModel):
    is_eligible: bool
    applicable_provisions: List[str] = []
    reasons: List[str] = []
    requirements_not_met: List[str] = []
    recommendations: List[str] = []
    estimated_credit_rate: Optional[float] = None
    confidence_score: float = Field(ge=0.0, le=1.0)


class AssessmentRequest(BaseModel):
    session_id: Optional[str] = None


class AnswerSubmission(BaseModel):
    session_id: str
    question_id: str
    answer: Any


class AssessmentResponse(BaseModel):
    session_id: str
    current_question: Optional[EligibilityQuestion] = None
    progress: float = Field(ge=0.0, le=1.0)
    is_complete: bool = False
    eligibility_result: Optional[EligibilityResult] = None
    next_question: Optional[EligibilityQuestion] = None 