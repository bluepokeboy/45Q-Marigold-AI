#!/usr/bin/env python3
"""
Debug script to test the LLM service directly.
"""

import os
import sys
import asyncio

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.llm_service import LLMService

async def test_llm():
    """Test the LLM service directly."""
    print("🧪 Testing LLM Service...")
    
    try:
        # Initialize LLM service
        llm_service = LLMService()
        
        # Test simple response
        print("Testing simple response...")
        response = await llm_service.generate_response("What is 2+2?")
        print(f"Response: {response}")
        
        # Test with context
        print("\nTesting with context...")
        context = "The 45Q tax credit is a federal tax credit for carbon sequestration."
        response = await llm_service.generate_response("What is the 45Q tax credit?", context)
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm()) 