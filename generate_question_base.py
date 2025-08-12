#!/usr/bin/env python3
"""
Script to generate a comprehensive question base for 45Q eligibility assessment
by querying the LLM about the documents.
"""

import os
import sys
import json
import asyncio
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.config import settings

async def generate_question_base():
    """Generate a comprehensive question base for 45Q eligibility assessment."""
    
    print("🔍 Generating 45Q Eligibility Question Base...")
    print("=" * 60)
    
    # Initialize services
    llm_service = LLMService()
    rag_service = RAGService()
    
    # Comprehensive prompt to analyze documents and generate questions
    analysis_prompt = """
You are an expert in 45Q tax credits for carbon sequestration. Based on the documents in your knowledge base, I need you to create a comprehensive framework for determining eligibility.

Please provide:

1. **CRITICAL ELIGIBILITY CRITERIA** - What are the absolute must-have requirements?
2. **FACILITY TYPE QUESTIONS** - What questions help determine the type of facility?
3. **TECHNICAL REQUIREMENTS** - What technical specifications matter?
4. **OWNERSHIP & PERMITTING** - What ownership and legal questions are needed?
5. **QUANTIFICATION QUESTIONS** - How do we measure CO2 capture and sequestration?
6. **TIMELINE & OPERATIONS** - What operational details matter?
7. **BONUS CREDIT FACTORS** - What questions help identify bonus opportunities?
8. **FOLLOW-UP LOGIC** - What are the key decision points that determine next questions?

For each category, provide:
- Specific questions to ask
- Why each question matters
- What the answer tells us about eligibility
- What follow-up questions that answer should trigger

Be thorough and specific. This will be used to create an intelligent assessment system.
"""
    
    try:
        print("📚 Analyzing documents for eligibility criteria...")
        
        # Get the answer from the RAG system
        result = await rag_service.answer_question(analysis_prompt)
        
        print("✅ Analysis complete!")
        print("\n" + "=" * 60)
        print("📋 GENERATED QUESTION BASE:")
        print("=" * 60)
        
        # Save the result
        question_base = {
            "generated_at": datetime.now().isoformat(),
            "analysis_prompt": analysis_prompt,
            "question_framework": result["answer"],
            "sources": result["sources"],
            "confidence_score": result["confidence_score"]
        }
        
        # Save to file
        with open("question_base.json", "w") as f:
            json.dump(question_base, f, indent=2)
        
        print(result["answer"])
        print("\n" + "=" * 60)
        print(f"💾 Question base saved to question_base.json")
        print(f"📊 Confidence score: {result['confidence_score']:.2%}")
        print(f"📚 Sources used: {len(result['sources'])}")
        
        return question_base
        
    except Exception as e:
        print(f"❌ Error generating question base: {e}")
        import traceback
        traceback.print_exc()
        return None

async def generate_assessment_prompt():
    """Generate an improved assessment prompt based on the question base."""
    
    print("\n🎯 Generating Improved Assessment Prompt...")
    print("=" * 60)
    
    try:
        # Load the question base
        with open("question_base.json", "r") as f:
            question_base = json.load(f)
        
        # Create an improved prompt
        improved_prompt = f"""
You are an expert 45Q tax credit eligibility assessor. Your job is to determine if a company qualifies for 45Q credits and provide a complete assessment.

IMPORTANT RULES:
- NEVER refer users to tax professionals or external consultants
- ALWAYS provide complete eligibility assessments when you have enough information
- Ask specific, targeted questions based on the framework below
- Continue asking questions until you can make a definitive determination
- Give comprehensive assessments with clear yes/no eligibility and reasoning

QUESTION FRAMEWORK (use this to guide your questioning):
{question_base['question_framework']}

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

Remember: You are the expert. Provide complete guidance, don't defer to others.
"""
        
        # Save the improved prompt
        assessment_prompt = {
            "generated_at": datetime.now().isoformat(),
            "improved_prompt": improved_prompt,
            "based_on_question_base": True
        }
        
        with open("assessment_prompt.json", "w") as f:
            json.dump(assessment_prompt, f, indent=2)
        
        print("✅ Improved assessment prompt generated!")
        print(f"💾 Saved to assessment_prompt.json")
        
        return improved_prompt
        
    except Exception as e:
        print(f"❌ Error generating assessment prompt: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Main function to run the question base generation."""
    
    print("🚀 Starting 45Q Question Base Generation...")
    print("=" * 60)
    
    # Step 1: Generate question base
    question_base = await generate_question_base()
    
    if question_base:
        # Step 2: Generate improved assessment prompt
        assessment_prompt = await generate_assessment_prompt()
        
        if assessment_prompt:
            print("\n🎉 SUCCESS! Question base and assessment prompt generated.")
            print("\n📁 Files created:")
            print("   - question_base.json (comprehensive question framework)")
            print("   - assessment_prompt.json (improved assessment prompt)")
            print("\n🔧 Next steps:")
            print("   1. Review the generated content")
            print("   2. Update the interactive assessment with the new prompt")
            print("   3. Test the improved assessment flow")
        else:
            print("❌ Failed to generate assessment prompt")
    else:
        print("❌ Failed to generate question base")

if __name__ == "__main__":
    asyncio.run(main()) 