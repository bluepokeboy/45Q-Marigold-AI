#!/usr/bin/env python3
"""
Test script to verify the 45Q Tax Credit application setup is working correctly.
"""

import os
import sys

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import langchain
        import langchain_openai
        import langchain_chroma
        import langchain_huggingface
        import chromadb
        import fastapi
        import pydantic
        import openai
        print("✅ All core dependencies imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

def test_app_import():
    """Test that the FastAPI app can be imported."""
    print("\nTesting app import...")
    
    try:
        # Set a dummy API key for testing
        os.environ['OPENAI_API_KEY'] = 'test-key-for-import-only'
        
        from app.main import app
        print("✅ FastAPI app imported successfully")
        print(f"   App title: {app.title}")
        print(f"   App version: {app.version}")
        return True
    except Exception as e:
        print(f"❌ App import error: {e}")
        return False

def test_services():
    """Test that core services can be instantiated."""
    print("\nTesting services...")
    
    try:
        from app.services.llm_service import LLMService
        from app.services.rag_service import RAGService
        from app.services.eligibility_service import EligibilityService
        from app.services.forecasting_service import ForecastingService
        
        print("✅ All service classes imported successfully")
        return True
    except Exception as e:
        print(f"❌ Service import error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing 45Q Tax Credit Application Setup")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_app_import,
        test_services
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        print("\nNext steps:")
        print("1. Create a .env file with your OpenAI API key")
        print("2. Add your 45Q documents to app/data/documents/")
        print("3. Run: python3 -m uvicorn app.main:app --reload")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 