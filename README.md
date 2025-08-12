# 45Q Tax Credit Eligibility & Forecasting System

A model-agnostic RAG application that helps companies assess eligibility for 45Q Tax Credits for Carbon Sequestration and provides credit forecasting.

## Features

- **Model Agnostic**: Easily swap between different LLM providers (OpenAI, Anthropic, Google, etc.)
- **RAG-Powered**: Uses Retrieval-Augmented Generation for accurate responses based on 45Q documentation
- **Eligibility Assessment**: Comprehensive questionnaire to determine 45Q eligibility
- **Credit Forecasting**: Calculate potential tax credits, timelines, and savings
- **Provision Analysis**: Identify applicable 45Q provisions based on facility type and operations

## Architecture

```
marigold/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration management
│   ├── models/                # Pydantic models
│   │   ├── __init__.py
│   │   ├── eligibility.py     # Eligibility assessment models
│   │   ├── forecasting.py     # Credit forecasting models
│   │   └── responses.py       # API response models
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── rag_service.py     # RAG implementation
│   │   ├── eligibility_service.py  # Eligibility logic
│   │   ├── forecasting_service.py  # Credit calculation
│   │   └── llm_service.py     # Model-agnostic LLM interface
│   ├── data/                  # Document storage
│   │   └── documents/         # 45Q documents (to be added)
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── document_loader.py # Document processing
│       └── prompts.py         # LLM prompts
├── tests/                     # Test files
├── requirements.txt           # Dependencies
└── .env.example              # Environment variables template
```

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Add 45Q documents**:
   - Place your 45Q tax credit documents in `app/data/documents/`
   - Supported formats: PDF, TXT, DOCX

4. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

- `POST /assess-eligibility`: Start eligibility assessment
- `POST /submit-answers`: Submit questionnaire answers
- `POST /forecast-credits`: Generate credit forecast
- `GET /health`: Health check

## Usage Workflow

1. **Eligibility Assessment**: System asks comprehensive questions about facility, ownership, technology, etc.
2. **Eligibility Determination**: Based on answers, determines if 45Q applies and which provisions
3. **Credit Forecasting**: If eligible, calculates potential credits, timelines, and savings
4. **Recommendations**: Provides guidance on maximizing credits and next steps

## Model Configuration

The system supports multiple LLM providers. Configure in `.env`:

```env
# OpenAI
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4

# Anthropic
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-sonnet

# Google
GOOGLE_API_KEY=your_key_here
GOOGLE_MODEL=gemini-pro
```

## Development

- **Adding new LLM providers**: Extend `LLMService` in `app/services/llm_service.py`
- **Customizing prompts**: Modify templates in `app/utils/prompts.py`
- **Adding new eligibility criteria**: Update `EligibilityService` in `app/services/eligibility_service.py` 