#!/usr/bin/env python3
"""
Enhanced 45Q Assessment Question Generator
Uses ChatGPT to generate comprehensive questions for 45Q tax credit eligibility assessment.
"""

import os
import json
from openai import OpenAI
from typing import List, Dict, Any
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_questions_with_chatgpt(category: str, context: str) -> List[Dict[str, Any]]:
    """Generate questions for a specific category using ChatGPT."""
    
    prompt = f"""
You are an expert 45Q tax credit consultant. Generate comprehensive questions for the category: {category}

Context: {context}

Generate 5-8 detailed questions for this category. Each question should:
1. Be specific and actionable
2. Have multiple choice options where appropriate
3. Always include an "Other" option where users can type their own answer
4. Be relevant to 45Q tax credit eligibility
5. Help determine if a facility qualifies for 45Q credits

Format each question as a JSON object with:
- "id": unique identifier
- "question": the question text
- "type": "multiple_choice" or "text"
- "options": array of options (for multiple choice)
- "required": true/false
- "category": the category name

Return only valid JSON array of question objects.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a 45Q tax credit expert. Generate detailed assessment questions in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract and parse JSON from response
        content = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1]
        
        questions = json.loads(content)
        return questions
        
    except Exception as e:
        print(f"Error generating questions for {category}: {e}")
        return []

def generate_all_categories() -> Dict[str, List[Dict[str, Any]]]:
    """Generate questions for all 45Q assessment categories."""
    
    categories = {
        "facility_basic_info": {
            "name": "Facility Basic Information",
            "context": "Basic information about the facility, location, and ownership structure"
        },
        "facility_type_operations": {
            "name": "Facility Type and Operations", 
            "context": "Type of facility, industrial processes, and operational details"
        },
        "carbon_capture_technology": {
            "name": "Carbon Capture Technology",
            "context": "Carbon capture, utilization, and storage (CCUS) technology details"
        },
        "emissions_data": {
            "name": "Emissions Data and Monitoring",
            "context": "Current emissions, monitoring systems, and historical data"
        },
        "project_scope": {
            "name": "Project Scope and Timeline",
            "context": "Project details, timeline, and implementation plans"
        },
        "financial_considerations": {
            "name": "Financial Considerations",
            "context": "Investment requirements, costs, and financial projections"
        },
        "regulatory_compliance": {
            "name": "Regulatory Compliance",
            "context": "Environmental permits, regulations, and compliance requirements"
        },
        "technical_requirements": {
            "name": "Technical Requirements",
            "context": "Technical specifications, equipment, and engineering requirements"
        },
        "partnerships_contracts": {
            "name": "Partnerships and Contracts",
            "context": "Partnerships, contracts, and third-party relationships"
        },
        "risk_assessment": {
            "name": "Risk Assessment",
            "context": "Technical, financial, and regulatory risks"
        }
    }
    
    all_questions = {}
    
    print("🚀 Generating comprehensive 45Q assessment questions...")
    print("=" * 60)
    
    for category_key, category_info in categories.items():
        print(f"\n📋 Generating questions for: {category_info['name']}")
        questions = generate_questions_with_chatgpt(category_key, category_info['context'])
        
        if questions:
            # Add category info to each question
            for question in questions:
                question['category'] = category_info['name']
                question['category_key'] = category_key
            
            all_questions[category_key] = {
                'name': category_info['name'],
                'questions': questions
            }
            
            print(f"✅ Generated {len(questions)} questions")
        else:
            print(f"❌ Failed to generate questions for {category_info['name']}")
    
    return all_questions

def save_questions_to_file(questions: Dict[str, Any], filename: str = "enhanced_question_base.json"):
    """Save the generated questions to a JSON file."""
    
    output = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_categories": len(questions),
            "total_questions": sum(len(cat['questions']) for cat in questions.values()),
            "description": "Enhanced 45Q tax credit eligibility assessment questions generated using ChatGPT"
        },
        "categories": questions
    }
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Questions saved to: {filename}")

def create_clickup_format(questions: Dict[str, Any]) -> str:
    """Create a ClickUp-friendly format for the questions."""
    
    clickup_content = "# 45Q Tax Credit Eligibility Assessment\n\n"
    clickup_content += f"Generated on: {datetime.now().strftime('%B %d, %Y')}\n\n"
    
    for category_key, category_data in questions.items():
        clickup_content += f"## {category_data['name']}\n\n"
        
        for i, question in enumerate(category_data['questions'], 1):
            clickup_content += f"### {i}. {question['question']}\n"
            
            if question.get('type') == 'multiple_choice' and question.get('options'):
                for option in question['options']:
                    clickup_content += f"- {option}\n"
            else:
                clickup_content += "- [Text input]\n"
            
            clickup_content += f"\n**Required:** {'Yes' if question.get('required', False) else 'No'}\n\n"
    
    # Save ClickUp format
    with open("45Q_assessment_clickup.md", 'w') as f:
        f.write(clickup_content)
    
    print("📝 ClickUp format saved to: 45Q_assessment_clickup.md")
    return clickup_content

def main():
    """Main function to generate and save enhanced questions."""
    
    print("🎯 45Q Enhanced Question Generator")
    print("=" * 40)
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        return
    
    # Generate questions for all categories
    all_questions = generate_all_categories()
    
    if not all_questions:
        print("❌ No questions were generated. Please check your API key and try again.")
        return
    
    # Save to JSON file
    save_questions_to_file(all_questions)
    
    # Create ClickUp format
    clickup_content = create_clickup_format(all_questions)
    
    # Print summary
    total_questions = sum(len(cat['questions']) for cat in all_questions.values())
    print(f"\n🎉 Successfully generated {total_questions} questions across {len(all_questions)} categories!")
    print("\n📁 Files created:")
    print("  - enhanced_question_base.json (JSON format)")
    print("  - 45Q_assessment_clickup.md (ClickUp format)")
    
    print("\n📋 Categories covered:")
    for category_key, category_data in all_questions.items():
        print(f"  - {category_data['name']}: {len(category_data['questions'])} questions")

if __name__ == "__main__":
    main()
