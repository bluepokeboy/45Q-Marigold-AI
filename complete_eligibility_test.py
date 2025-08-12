#!/usr/bin/env python3
"""
Complete eligibility assessment test script.
Answers all questions and shows the final results.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
SESSION_ID = "complete-test-123"

def start_assessment():
    """Start a new eligibility assessment."""
    print("🚀 Starting eligibility assessment...")
    
    response = requests.post(
        f"{BASE_URL}/assess-eligibility",
        json={"session_id": SESSION_ID}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Assessment started: {result['session_id']}")
        return result
    else:
        print(f"❌ Failed to start assessment: {response.text}")
        return None

def submit_answer(question_id, answer):
    """Submit an answer to a question."""
    response = requests.post(
        f"{BASE_URL}/submit-answer",
        json={
            "session_id": SESSION_ID,
            "question_id": question_id,
            "answer": answer
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        current_q = result.get('current_question', {})
        progress = result.get('progress', 0) * 100
        
        print(f"✅ Answered: {current_q.get('question', 'Unknown')}")
        print(f"   Progress: {progress:.1f}%")
        
        if result.get('is_complete'):
            print("🎉 Assessment completed!")
            return result
        else:
            return result
    else:
        print(f"❌ Failed to submit answer: {response.text}")
        return None

def get_progress():
    """Get current assessment progress."""
    response = requests.get(f"{BASE_URL}/assessment-progress/{SESSION_ID}")
    
    if response.status_code == 200:
        result = response.json()
        data = result.get('data', {})
        print(f"📊 Progress: {data.get('progress', 0) * 100:.1f}% ({data.get('answers_provided', 0)}/{data.get('total_questions', 0)} questions)")
        return data
    else:
        print(f"❌ Failed to get progress: {response.text}")
        return None

def get_detailed_guidance():
    """Get detailed guidance for the assessment."""
    print("\n🔍 Getting detailed guidance...")
    
    response = requests.post(f"{BASE_URL}/detailed-guidance/{SESSION_ID}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Detailed guidance received!")
        return result
    else:
        print(f"❌ Failed to get guidance: {response.text}")
        return None

def main():
    """Run the complete eligibility assessment."""
    print("🧪 Complete 45Q Eligibility Assessment Test")
    print("=" * 50)
    
    # Start assessment
    assessment = start_assessment()
    if not assessment:
        return
    
    # Define all answers for a Direct Air Capture facility
    answers = [
        ("facility_name", "Carbon Capture Facility Alpha"),
        ("location_city", "Houston"),
        ("location_state", "Texas"),
        ("facility_type", "Direct air capture facility"),
        ("ownership", "You (the taxpayer)"),
        ("technology_ownership", "You (the taxpayer)"),
        ("annual_co2_captured", "100000"),  # metric tons
        ("capture_method", "Direct air capture"),
        ("sequestration_method", "Geological storage"),
        ("sequestration_location", "Texas"),
        ("start_date", "2025-01-01"),
        ("domestic_content_percentage", "75"),
        ("energy_community_eligible", "true"),
        ("carbon_intensity_data", "Available"),
        ("additional_requirements", "All requirements met")
    ]
    
    print(f"\n📋 Answering {len(answers)} questions...")
    print("-" * 30)
    
    # Submit all answers
    for question_id, answer in answers:
        print(f"\n❓ Question ID: {question_id}")
        print(f"💡 Answer: {answer}")
        
        result = submit_answer(question_id, answer)
        
        if result and result.get('is_complete'):
            print("\n🎉 Assessment completed! Getting final results...")
            break
        
        time.sleep(0.5)  # Small delay between requests
    
    # Get final progress
    print("\n" + "=" * 50)
    final_progress = get_progress()
    
    # Get detailed guidance
    guidance = get_detailed_guidance()
    
    if guidance:
        print("\n📋 DETAILED GUIDANCE RESULTS:")
        print("=" * 50)
        guidance_data = guidance.get('data', {})
        
        if 'eligibility_determination' in guidance_data:
            print(f"✅ Eligibility: {guidance_data['eligibility_determination']}")
        
        if 'recommendations' in guidance_data:
            print(f"\n💡 Recommendations:")
            for rec in guidance_data['recommendations']:
                print(f"   • {rec}")
        
        if 'requirements' in guidance_data:
            print(f"\n📋 Requirements:")
            for req in guidance_data['requirements']:
                print(f"   • {req}")
        
        if 'estimated_credits' in guidance_data:
            print(f"\n💰 Estimated Credits: ${guidance_data['estimated_credits']:,.2f}")
    
    print("\n🎯 Assessment Complete!")
    print("You can now use this session ID for further analysis.")

if __name__ == "__main__":
    main() 