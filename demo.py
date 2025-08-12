#!/usr/bin/env python3
"""
Demo script for the 45Q Tax Credit application.
This script demonstrates the key features of the system.
"""

import asyncio
import json
from app.services.eligibility_service import EligibilityService
from app.services.forecasting_service import ForecastingService
from app.services.rag_service import RAGService


async def demo_eligibility_assessment():
    """Demonstrate the eligibility assessment workflow."""
    print("\n" + "="*60)
    print("DEMO: 45Q Eligibility Assessment")
    print("="*60)
    
    eligibility_service = EligibilityService()
    
    # Start assessment
    assessment = eligibility_service.start_assessment()
    print(f"Started assessment with session ID: {assessment.session_id}")
    
    # Example facility data
    example_answers = {
        "facility_name": "GreenTech Carbon Capture Facility",
        "location_city": "Houston",
        "location_state": "Texas",
        "facility_type": "Industrial facility (cement, steel, chemicals, etc.)",
        "ownership": "You (the taxpayer)",
        "technology_ownership": "You (the taxpayer)",
        "capture_method": "Post-combustion capture",
        "annual_co2_captured": 50.0,
        "capture_efficiency": 85.0,
        "facility_construction_date": "2020-01-15",
        "carbon_capture_operation_date": "2024-06-01",
        "sequestration_method": "Geologic storage (underground injection)",
        "sequestration_location": "Permitted injection well in Texas",
        "domestic_content": 45.0,
        "energy_community": True
    }
    
    # Submit answers
    print("\nSubmitting facility information...")
    for question_id, answer in example_answers.items():
        result = eligibility_service.submit_answer(assessment.session_id, question_id, answer)
        if result["is_complete"]:
            break
    
    # Get eligibility result
    if assessment.eligibility_result:
        result = assessment.eligibility_result
        print(f"\n✅ Eligibility Assessment Complete!")
        print(f"Eligible: {result.is_eligible}")
        print(f"Confidence Score: {result.confidence_score:.2f}")
        print(f"Estimated Credit Rate: ${result.estimated_credit_rate:.2f}/ton")
        
        print(f"\nApplicable Provisions:")
        for provision in result.applicable_provisions:
            print(f"  - {provision}")
        
        print(f"\nReasons for Eligibility:")
        for reason in result.reasons:
            print(f"  - {reason}")
        
        if result.requirements_not_met:
            print(f"\nRequirements Not Met:")
            for req in result.requirements_not_met:
                print(f"  - {req}")
        
        print(f"\nRecommendations:")
        for rec in result.recommendations:
            print(f"  - {rec}")


async def demo_credit_forecasting():
    """Demonstrate the credit forecasting workflow."""
    print("\n" + "="*60)
    print("DEMO: 45Q Credit Forecasting")
    print("="*60)
    
    forecasting_service = ForecastingService()
    
    # Example facility information
    facility_info = {
        "facility_name": "GreenTech Carbon Capture Facility",
        "facility_type": "Industrial facility (cement, steel, chemicals, etc.)",
        "location_state": "Texas",
        "ownership": "You (the taxpayer)",
        "technology_ownership": "You (the taxpayer)",
        "capture_method": "Post-combustion capture",
        "annual_co2_captured": 50.0,
        "sequestration_method": "Geologic storage (underground injection)"
    }
    
    # Example forecasting data
    forecasting_data = {
        "annual_co2_captured": 50.0,
        "capture_efficiency": 0.85,
        "sequestration_method": "Geologic storage (underground injection)",
        "sequestration_location": "Permitted injection well in Texas",
        "start_date": "2024-06-01",
        "domestic_content_percentage": 45.0,
        "energy_community_eligible": True
    }
    
    print("Generating credit forecast...")
    forecast = await forecasting_service.generate_forecast(facility_info, forecasting_data)
    
    print(f"\n✅ Credit Forecast Generated!")
    print(f"Facility: {forecast.facility_info['facility_name']}")
    print(f"Annual CO2 Capture: {forecasting_data['annual_co2_captured']} metric tons")
    
    print(f"\nCredit Summary:")
    print(f"  10-Year Total: ${forecast.total_credits_10_years:,.2f}")
    print(f"  12-Year Total: ${forecast.total_credits_12_years:,.2f}")
    print(f"  Average Annual: ${forecast.average_annual_value:,.2f}")
    
    print(f"\nBonus Opportunities:")
    for opportunity in forecast.bonus_opportunities:
        print(f"  - {opportunity['description']}")
        print(f"    Potential Bonus: {opportunity['potential_bonus']}")
    
    print(f"\nAssumptions:")
    for key, value in forecast.assumptions.items():
        print(f"  - {key}: {value}")
    
    print(f"\nRecommendations:")
    for rec in forecast.recommendations[:5]:  # Show first 5
        print(f"  - {rec}")


async def demo_rag_question_answering():
    """Demonstrate RAG-based question answering."""
    print("\n" + "="*60)
    print("DEMO: RAG Question Answering")
    print("="*60)
    
    rag_service = RAGService()
    
    # Example questions about 45Q
    questions = [
        "What are the minimum CO2 capture requirements for 45Q eligibility?",
        "How do bonus credits work for domestic content?",
        "What is the credit rate for direct air capture facilities?",
        "What documentation is required for claiming 45Q credits?"
    ]
    
    print("Note: This demo will work best if you have uploaded 45Q documents.")
    print("Without documents, the system will provide general guidance.\n")
    
    for question in questions:
        print(f"Q: {question}")
        try:
            result = await rag_service.answer_question(question)
            print(f"A: {result['answer'][:200]}...")
            print(f"Confidence: {result['confidence_score']:.2f}")
            print(f"Sources: {len(result['sources'])} documents")
            print()
        except Exception as e:
            print(f"Error: {e}")
            print()


async def demo_detailed_analysis():
    """Demonstrate detailed analysis with RAG guidance."""
    print("\n" + "="*60)
    print("DEMO: Detailed Analysis with RAG Guidance")
    print("="*60)
    
    forecasting_service = ForecastingService()
    
    # Example facility for detailed analysis
    facility_info = {
        "facility_name": "Advanced Carbon Solutions Plant",
        "facility_type": "Direct air capture facility",
        "location_state": "California",
        "ownership": "You (the taxpayer)",
        "technology_ownership": "Licensed from another party",
        "capture_method": "Direct air capture",
        "annual_co2_captured": 10.0,
        "sequestration_method": "Geologic storage (underground injection)"
    }
    
    forecasting_data = {
        "annual_co2_captured": 10.0,
        "capture_efficiency": 0.90,
        "sequestration_method": "Geologic storage (underground injection)",
        "sequestration_location": "Permitted injection well in California",
        "start_date": "2024-01-01",
        "domestic_content_percentage": 60.0,
        "energy_community_eligible": False
    }
    
    print("Generating detailed forecast analysis...")
    analysis = await forecasting_service.get_detailed_forecast_analysis(facility_info, forecasting_data)
    
    print(f"\n✅ Detailed Analysis Complete!")
    print(f"Facility: {facility_info['facility_name']}")
    print(f"Type: {facility_info['facility_type']}")
    
    summary = analysis["summary"]
    print(f"\nSummary:")
    print(f"  Total Potential Credits: {summary['total_potential_credits']:,.2f}")
    print(f"  Total Potential Value: ${summary['total_potential_value']:,.2f}")
    print(f"  Average Annual Value: ${summary['average_annual_value']:,.2f}")
    print(f"  Bonus Opportunities: {summary['bonus_opportunities_count']}")
    print(f"  Confidence Score: {summary['confidence_score']:.2f}")
    
    # Show timeline projections
    timeline = analysis["timeline_projections"]
    print(f"\nTimeline Projections (first 5 years):")
    for i, year_data in enumerate(timeline[:5]):
        print(f"  Year {year_data['year']}: ${year_data['cumulative_value']:,.2f}")


async def main():
    """Run all demos."""
    print("45Q Tax Credit Application - Demo")
    print("This demo shows the key features of the system.")
    print("Note: Some features require uploaded 45Q documents for best results.")
    
    try:
        # Run demos
        await demo_eligibility_assessment()
        await demo_credit_forecasting()
        await demo_rag_question_answering()
        await demo_detailed_analysis()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE!")
        print("="*60)
        print("\nTo use the full system:")
        print("1. Add your 45Q documents to app/data/documents/")
        print("2. Configure your LLM API keys in .env")
        print("3. Run: uvicorn app.main:app --reload")
        print("4. Access the API at: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("This might be due to missing API keys or documents.")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    asyncio.run(main()) 