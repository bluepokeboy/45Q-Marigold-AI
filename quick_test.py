#!/usr/bin/env python3
"""
Quick test script to try out the 45Q Tax Credit application features.
"""

import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint."""
    print("🏥 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_upload_documents():
    """Test document upload."""
    print("📄 Testing Document Upload...")
    
    # Check if there are documents in the documents directory
    docs_dir = "app/data/documents"
    if not os.path.exists(docs_dir):
        print("❌ No documents directory found")
        return
    
    files = [f for f in os.listdir(docs_dir) if f.endswith(('.pdf', '.txt', '.docx'))]
    
    if not files:
        print("❌ No documents found in app/data/documents/")
        print("   Please add some 45Q documents (PDF, TXT, or DOCX) to test upload")
        return
    
    print(f"Found {len(files)} documents: {files}")
    
    # For now, just show what we found
    print("✅ Documents ready for upload")
    print()

def test_ask_question():
    """Test asking a question."""
    print("❓ Testing Question Answering...")
    
    question = "What is the 45Q tax credit and who is eligible?"
    
    try:
        response = requests.post(
            f"{BASE_URL}/ask-question",
            params={"question": question}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Answer: {result.get('answer', 'No answer provided')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_eligibility_assessment():
    """Test eligibility assessment."""
    print("📋 Testing Eligibility Assessment...")
    
    try:
        # Start assessment
        response = requests.post(
            f"{BASE_URL}/assess-eligibility",
            json={"session_id": "test-session-123"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Session ID: {result.get('session_id')}")
            print(f"Current Question: {result.get('current_question', {}).get('text', 'No question')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_credit_forecast():
    """Test credit forecasting."""
    print("💰 Testing Credit Forecasting...")
    
    forecast_data = {
        "session_id": "test-session-123",
        "facility_info": {
            "facility_type": "Direct Air Capture",
            "location": "Texas",
            "ownership": "Private",
            "technology_ownership": "Owned"
        },
        "annual_co2_captured": 100000,  # metric tons
        "capture_efficiency": 0.85,
        "sequestration_method": "Geological Storage",
        "sequestration_location": "Texas",
        "start_date": "2025-01-01",
        "domestic_content_percentage": 75.0,
        "energy_community_eligible": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/forecast-credits",
            json=forecast_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            forecast = result.get('forecast', {})
            print(f"Total Credits (10 years): ${forecast.get('total_credits_10_years', 0):,.2f}")
            print(f"Total Value (10 years): ${forecast.get('total_value_10_years', 0):,.2f}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    print()

def main():
    """Run all tests."""
    print("🧪 45Q Tax Credit Application - Quick Test")
    print("=" * 50)
    
    tests = [
        test_health,
        test_upload_documents,
        test_ask_question,
        test_eligibility_assessment,
        test_credit_forecast
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print()
    
    print("🎉 Testing complete!")
    print("\n📖 Next steps:")
    print("1. Open http://localhost:8000/docs for interactive API documentation")
    print("2. Upload your 45Q documents using the /upload-documents endpoint")
    print("3. Ask questions about 45Q using the /ask-question endpoint")
    print("4. Start an eligibility assessment using /assess-eligibility")
    print("5. Calculate credit forecasts using /forecast-credits")

if __name__ == "__main__":
    main() 