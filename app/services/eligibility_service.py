import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.eligibility import (
    EligibilityQuestion, EligibilityAssessment, EligibilityResult,
    QuestionType, FacilityType, OwnershipType, TechnologyOwnership, CaptureMethod
)
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService


class EligibilityService:
    """Service for managing 45Q eligibility assessments."""
    
    def __init__(self):
        self.rag_service = RAGService()
        self.llm_service = LLMService()
        self.assessments: Dict[str, EligibilityAssessment] = {}
        self._initialize_questions()
    
    def _initialize_questions(self):
        """Initialize the eligibility questionnaire."""
        self.questions = [
            EligibilityQuestion(
                id="facility_name",
                question="What is the name of your facility/project?",
                type=QuestionType.TEXT,
                required=True,
                help_text="Enter the official name of your facility or project"
            ),
            EligibilityQuestion(
                id="location_city",
                question="What city is your project located in?",
                type=QuestionType.TEXT,
                required=True
            ),
            EligibilityQuestion(
                id="location_state",
                question="What state is your project located in?",
                type=QuestionType.TEXT,
                required=True
            ),
            EligibilityQuestion(
                id="facility_type",
                question="What type of facility is this?",
                type=QuestionType.SELECT,
                required=True,
                options=[
                    "Electric generation facility",
                    "Industrial facility (cement, steel, chemicals, etc.)",
                    "Direct air capture facility",
                    "Other"
                ],
                help_text="Select the primary type of facility"
            ),
            EligibilityQuestion(
                id="ownership",
                question="Who owns the facility?",
                type=QuestionType.SELECT,
                required=True,
                options=[
                    "You (the taxpayer)",
                    "Your client",
                    "A third party"
                ]
            ),
            EligibilityQuestion(
                id="technology_ownership",
                question="Who owns the carbon capture technology?",
                type=QuestionType.SELECT,
                required=True,
                options=[
                    "You (the taxpayer)",
                    "Licensed from another party",
                    "Owned by a third party"
                ]
            ),
            EligibilityQuestion(
                id="capture_method",
                question="What method is used to capture CO2?",
                type=QuestionType.SELECT,
                required=True,
                options=[
                    "Post-combustion capture",
                    "Pre-combustion capture",
                    "Oxy-fuel combustion",
                    "Direct air capture",
                    "Other"
                ]
            ),
            EligibilityQuestion(
                id="annual_co2_captured",
                question="How much CO2 do you capture annually (in metric tons)?",
                type=QuestionType.NUMBER,
                required=True,
                help_text="Enter the estimated annual CO2 capture in metric tons"
            ),
            EligibilityQuestion(
                id="capture_efficiency",
                question="What is the capture efficiency percentage?",
                type=QuestionType.NUMBER,
                required=False,
                help_text="Enter the percentage of CO2 captured from the total emissions"
            ),
            EligibilityQuestion(
                id="facility_construction_date",
                question="When was the facility originally constructed? (YYYY-MM-DD)",
                type=QuestionType.TEXT,
                required=False,
                help_text="Enter the date when the facility was first constructed"
            ),
            EligibilityQuestion(
                id="carbon_capture_operation_date",
                question="When did/will carbon capture operations begin? (YYYY-MM-DD)",
                type=QuestionType.TEXT,
                required=True,
                help_text="Enter the date when carbon capture operations started or will start"
            ),
            EligibilityQuestion(
                id="sequestration_method",
                question="How is the captured CO2 sequestered?",
                type=QuestionType.SELECT,
                required=True,
                options=[
                    "Geologic storage (underground injection)",
                    "Enhanced oil recovery (EOR)",
                    "Utilization in products",
                    "Other"
                ]
            ),
            EligibilityQuestion(
                id="sequestration_location",
                question="Where is the CO2 sequestered?",
                type=QuestionType.TEXT,
                required=True,
                help_text="Describe the location where CO2 is stored or utilized"
            ),
            EligibilityQuestion(
                id="domestic_content",
                question="What percentage of the facility components are manufactured in the US?",
                type=QuestionType.NUMBER,
                required=False,
                help_text="Enter the percentage of domestic content (0-100)"
            ),
            EligibilityQuestion(
                id="energy_community",
                question="Is the facility located in an energy community?",
                type=QuestionType.BOOLEAN,
                required=False,
                help_text="Energy communities include areas with coal mine/plant closures or high unemployment"
            )
        ]
    
    def start_assessment(self, session_id: Optional[str] = None) -> EligibilityAssessment:
        """Start a new eligibility assessment."""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        assessment = EligibilityAssessment(
            session_id=session_id,
            questions=self.questions,
            current_question_index=0
        )
        
        self.assessments[session_id] = assessment
        return assessment
    
    def get_current_question(self, session_id: str) -> Optional[EligibilityQuestion]:
        """Get the current question for an assessment."""
        if session_id not in self.assessments:
            return None
        
        assessment = self.assessments[session_id]
        if assessment.current_question_index >= len(assessment.questions):
            return None
        
        return assessment.questions[assessment.current_question_index]
    
    def submit_answer(self, session_id: str, question_id: str, answer: Any) -> Dict[str, Any]:
        """Submit an answer and get the next question or assessment result."""
        if session_id not in self.assessments:
            raise ValueError("Invalid session ID")
        
        assessment = self.assessments[session_id]
        
        # Store the answer
        assessment.answers[question_id] = answer
        
        # Move to next question
        assessment.current_question_index += 1
        
        # Check if assessment is complete
        if assessment.current_question_index >= len(assessment.questions):
            assessment.is_complete = True
            # Determine eligibility
            eligibility_result = self._determine_eligibility(assessment.answers)
            assessment.eligibility_result = eligibility_result
            
            return {
                "is_complete": True,
                "eligibility_result": eligibility_result,
                "progress": 1.0
            }
        else:
            # Return next question
            next_question = assessment.questions[assessment.current_question_index]
            progress = assessment.current_question_index / len(assessment.questions)
            
            return {
                "is_complete": False,
                "next_question": next_question,
                "progress": progress
            }
    
    def _determine_eligibility(self, answers: Dict[str, Any]) -> EligibilityResult:
        """Determine eligibility based on collected answers."""
        # Basic eligibility criteria
        is_eligible = True
        reasons = []
        requirements_not_met = []
        applicable_provisions = []
        
        # Check minimum CO2 capture requirement
        annual_co2 = answers.get("annual_co2_captured")
        if annual_co2:
            try:
                annual_co2 = float(annual_co2)
                if annual_co2 < 12.5:  # Minimum threshold for most facilities
                    is_eligible = False
                    requirements_not_met.append("Minimum CO2 capture requirement not met (12.5 metric tons)")
            except (ValueError, TypeError):
                requirements_not_met.append("Invalid CO2 capture amount format")
                is_eligible = False
        
        # Check facility type eligibility
        facility_type = answers.get("facility_type", "").lower()
        if "direct air capture" in facility_type:
            applicable_provisions.append("Section 45Q - Direct Air Capture")
            if annual_co2 and isinstance(annual_co2, (int, float)) and annual_co2 < 1.0:  # Lower threshold for DAC
                is_eligible = False
                requirements_not_met.append("Direct air capture minimum requirement not met (1.0 metric tons)")
        elif "electric generation" in facility_type:
            applicable_provisions.append("Section 45Q - Electric Generation")
        elif "industrial" in facility_type:
            applicable_provisions.append("Section 45Q - Industrial Facilities")
        else:
            applicable_provisions.append("Section 45Q - Other Facilities")
        
        # Check sequestration method
        sequestration_method = answers.get("sequestration_method", "").lower()
        if "geologic storage" in sequestration_method or "enhanced oil recovery" in sequestration_method:
            reasons.append("Qualified geologic storage or EOR sequestration")
        elif "utilization" in sequestration_method:
            reasons.append("CO2 utilization in qualified products")
        else:
            requirements_not_met.append("Qualified sequestration method required")
            is_eligible = False
        
        # Check operation date
        operation_date = answers.get("carbon_capture_operation_date")
        if operation_date:
            try:
                op_date = datetime.strptime(operation_date, "%Y-%m-%d")
                if op_date.year < 2023:
                    reasons.append("Facility operational before 2023")
                elif op_date.year > 2032:
                    requirements_not_met.append("Facility must be operational by 2032")
                    is_eligible = False
            except ValueError:
                requirements_not_met.append("Invalid operation date format")
        
        # Calculate estimated credit rate
        estimated_rate = self._calculate_credit_rate(answers)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(answers, is_eligible)
        
        return EligibilityResult(
            is_eligible=is_eligible,
            applicable_provisions=applicable_provisions,
            reasons=reasons,
            requirements_not_met=requirements_not_met,
            recommendations=recommendations,
            estimated_credit_rate=estimated_rate,
            confidence_score=0.85  # Base confidence score
        )
    
    def _calculate_credit_rate(self, answers: Dict[str, Any]) -> float:
        """Calculate estimated credit rate based on facility characteristics."""
        facility_type = answers.get("facility_type", "").lower()
        sequestration_method = answers.get("sequestration_method", "").lower()
        
        # Base rates (simplified - actual rates vary by year)
        if "direct air capture" in facility_type:
            base_rate = 85.0  # $85/ton for DAC
        else:
            base_rate = 60.0  # $60/ton for other facilities
        
        # Bonus multipliers
        multiplier = 1.0
        
        # Domestic content bonus
        domestic_content = answers.get("domestic_content")
        if domestic_content:
            try:
                domestic_content = float(domestic_content)
                if domestic_content >= 40:
                    multiplier += 0.1  # 10% bonus
            except (ValueError, TypeError):
                pass  # Skip bonus if invalid format
        
        # Energy community bonus
        energy_community = answers.get("energy_community")
        if energy_community:
            # Handle both string and boolean values
            if isinstance(energy_community, str):
                if energy_community.lower() in ['true', 'yes', '1']:
                    multiplier += 0.1  # 10% bonus
            elif isinstance(energy_community, bool) and energy_community:
                multiplier += 0.1  # 10% bonus
        
        return base_rate * multiplier
    
    def _generate_recommendations(self, answers: Dict[str, Any], is_eligible: bool) -> List[str]:
        """Generate recommendations based on assessment results."""
        recommendations = []
        
        if not is_eligible:
            recommendations.append("Review facility characteristics to meet eligibility requirements")
            recommendations.append("Consider increasing CO2 capture capacity if below minimum thresholds")
            recommendations.append("Ensure qualified sequestration method is used")
        
        # General recommendations
        recommendations.append("Consult with tax professionals for detailed guidance")
        recommendations.append("Maintain detailed documentation of capture and sequestration")
        recommendations.append("Consider domestic content requirements for bonus credits")
        
        # Specific recommendations based on facility type
        facility_type = answers.get("facility_type", "").lower()
        if "direct air capture" in facility_type:
            recommendations.append("Ensure DAC facility meets specific technical requirements")
        elif "industrial" in facility_type:
            recommendations.append("Verify industrial facility qualifies under Section 45Q")
        
        return recommendations
    
    async def get_detailed_guidance(self, session_id: str) -> Dict[str, Any]:
        """Get detailed guidance using RAG for a specific assessment."""
        if session_id not in self.assessments:
            raise ValueError("Invalid session ID")
        
        assessment = self.assessments[session_id]
        
        # Convert answers to facility info format
        facility_info = {
            "facility_name": assessment.answers.get("facility_name", "Unknown"),
            "facility_type": assessment.answers.get("facility_type", "Unknown"),
            "location_state": assessment.answers.get("location_state", "Unknown"),
            "ownership": assessment.answers.get("ownership", "Unknown"),
            "technology_ownership": assessment.answers.get("technology_ownership", "Unknown"),
            "capture_method": assessment.answers.get("capture_method", "Unknown"),
            "annual_co2_captured": assessment.answers.get("annual_co2_captured", 0),
            "sequestration_method": assessment.answers.get("sequestration_method", "Unknown")
        }
        
        # Get RAG-based guidance
        guidance = await self.rag_service.get_eligibility_guidance(facility_info)
        
        return {
            "facility_info": facility_info,
            "rag_guidance": guidance,
            "assessment_result": assessment.eligibility_result
        }
    
    def get_assessment_progress(self, session_id: str) -> Dict[str, Any]:
        """Get the current progress of an assessment."""
        if session_id not in self.assessments:
            raise ValueError("Invalid session ID")
        
        assessment = self.assessments[session_id]
        progress = assessment.current_question_index / len(assessment.questions)
        
        return {
            "session_id": session_id,
            "current_question_index": assessment.current_question_index,
            "total_questions": len(assessment.questions),
            "progress": progress,
            "is_complete": assessment.is_complete,
            "answers_provided": len(assessment.answers)
        } 