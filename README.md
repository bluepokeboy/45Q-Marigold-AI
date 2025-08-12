# 45Q Tax Credit Eligibility & Forecasting System

A model-agnostic RAG application that helps companies assess eligibility for 45Q Tax Credits for Carbon Sequestration and provides credit forecasting.

## Features

- **Model Agnostic**: Easily swap between different LLM providers (OpenAI, Anthropic, Google, etc.)
- **RAG-Powered**: Uses Retrieval-Augmented Generation for accurate responses based on 45Q documentation
- **Eligibility Assessment**: Comprehensive questionnaire to determine 45Q eligibility
- **Credit Forecasting**: Calculate potential tax credits, timelines, and savings
- **Provision Analysis**: Identify applicable 45Q provisions based on facility type and operations

## 🚀 Complete Setup Guide for Beginners

This guide assumes you're starting with a fresh laptop and have no coding experience. Follow these steps exactly in order.

### Step 1: Download the Application

1. **Go to GitHub**: Open your web browser and go to: https://github.com/bluepokeboy/45Q-Marigold-AI
2. **Download the code**: Click the green "Code" button, then click "Download ZIP"
3. **Extract the ZIP**: Find the downloaded file (usually in Downloads folder), right-click it, and select "Extract All" or "Extract Here"
4. **Rename the folder**: Rename the extracted folder to `marigold` for simplicity

### Step 2: Install Python (if not already installed)

#### For Windows:
1. **Go to python.org**: Open https://www.python.org/downloads/
2. **Download Python**: Click "Download Python 3.11.x" (latest version)
3. **Run the installer**: Double-click the downloaded file
4. **Important**: Check the box that says "Add Python to PATH" during installation
5. **Complete installation**: Click "Install Now" and wait for it to finish

#### For Mac:
1. **Install Homebrew** (if you don't have it):
   - Open Terminal (press Cmd+Space, type "Terminal", press Enter)
   - Copy and paste this command: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
   - Press Enter and follow the prompts
2. **Install Python**: In Terminal, type: `brew install python@3.11`
3. **Press Enter** and wait for installation to complete

#### For Linux:
1. **Open Terminal**: Press Ctrl+Alt+T
2. **Install Python**: Type: `sudo apt update && sudo apt install python3 python3-pip`
3. **Press Enter** and wait for installation to complete

### Step 3: Verify Python Installation

1. **Open Terminal/Command Prompt**:
   - **Windows**: Press Win+R, type `cmd`, press Enter
   - **Mac**: Press Cmd+Space, type "Terminal", press Enter
   - **Linux**: Press Ctrl+Alt+T

2. **Check Python**: Type this command and press Enter:
   ```bash
   python3 --version
   ```
   You should see something like "Python 3.11.x"

3. **Check pip**: Type this command and press Enter:
   ```bash
   pip3 --version
   ```
   You should see pip version information

### Step 4: Navigate to the Application Folder

1. **In Terminal/Command Prompt**, navigate to where you extracted the marigold folder:
   
   **Windows example**:
   ```bash
   cd C:\Users\YourName\Downloads\marigold
   ```
   
   **Mac/Linux example**:
   ```bash
   cd ~/Downloads/marigold
   ```
   
   **Note**: Replace "YourName" with your actual username, and adjust the path if you extracted it somewhere else

2. **Verify you're in the right place**: Type `ls` (Mac/Linux) or `dir` (Windows) and press Enter. You should see files like `requirements.txt`, `README.md`, etc.

### Step 5: Install Required Packages

1. **Install the packages**: Type this command and press Enter:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Wait for installation**: This may take 5-10 minutes. You'll see lots of text scrolling as packages are downloaded and installed.

3. **If you get errors**: 
   - **Windows**: Try `python -m pip install -r requirements.txt`
   - **Mac/Linux**: Try `pip install -r requirements.txt`

### Step 6: Set Up Your API Key

1. **Get an OpenAI API key**:
   - Go to https://platform.openai.com/
   - Sign up or log in
   - Go to "API Keys" section
   - Click "Create new secret key"
   - Copy the key (it looks like: sk-...)

2. **Create environment file**:
   - In Terminal/Command Prompt, type: `cp .env.example .env`
   - Press Enter

3. **Edit the environment file**:
   - **Windows**: Type `notepad .env` and press Enter
   - **Mac**: Type `open -e .env` and press Enter
   - **Linux**: Type `nano .env` and press Enter

4. **Add your API key**: In the file, find the line that says `OPENAI_API_KEY=` and add your key after the equals sign:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

5. **Save the file**:
   - **Windows**: Press Ctrl+S, then close Notepad
   - **Mac**: Press Cmd+S, then close TextEdit
   - **Linux**: Press Ctrl+X, then Y, then Enter

### Step 7: Run the Application

1. **Start the application**: Type this command and press Enter:
   ```bash
   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Wait for startup**: You'll see text like:
   ```
   INFO: Uvicorn running on http://0.0.0.0:8000
   INFO: Application startup complete.
   ```

3. **Open your web browser**: Go to: http://localhost:8000

4. **You should see**: The 45Q Marigold AI application interface

### Step 8: Test the Application

1. **Try the web interface**: Click around the interface at http://localhost:8000
2. **Check API documentation**: Go to http://localhost:8000/docs
3. **Test health check**: Go to http://localhost:8000/health

### Troubleshooting

#### If Python is not found:
- **Windows**: Restart Command Prompt after installing Python
- **Mac/Linux**: Try `python` instead of `python3`

#### If pip is not found:
- **Windows**: Try `python -m pip` instead of `pip3`
- **Mac/Linux**: Try `pip` instead of `pip3`

#### If packages fail to install:
- **Update pip first**: `pip3 install --upgrade pip`
- **Try installing one by one**: `pip3 install fastapi uvicorn openai`

#### If the app won't start:
- **Check port 8000**: If it says "port already in use", try port 8001:
  ```bash
  python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
  ```
- **Check API key**: Make sure your OpenAI API key is correct in the `.env` file

#### If you get API errors:
- **Check your OpenAI account**: Make sure you have credits in your OpenAI account
- **Check the key**: Make sure the API key in `.env` is correct

### Stopping the Application

- **In Terminal/Command Prompt**: Press `Ctrl+C` to stop the application
- **Close Terminal**: You can close the Terminal/Command Prompt window

### Running Again Later

1. **Open Terminal/Command Prompt**
2. **Navigate to the marigold folder**: `cd path/to/marigold`
3. **Start the app**: `python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
4. **Open browser**: Go to http://localhost:8000

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
│   │   └── documents/         # 45Q documents (included)
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── document_loader.py # Document processing
│       └── prompts.py         # LLM prompts
├── tests/                     # Test files
├── requirements.txt           # Dependencies
├── run_app.py                # Simple launcher script
└── .env.example              # Environment variables template
```

## Quick Start for Developers

If you already have Python and coding experience:

```bash
# Clone the repository
git clone https://github.com/bluepokeboy/45Q-Marigold-AI.git
cd 45Q-Marigold-AI

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your OpenAI API key

# Run the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

- `GET /` - Main web interface
- `GET /docs` - Interactive API documentation
- `GET /health` - Health check
- `POST /assess-eligibility` - Start eligibility assessment
- `POST /submit-answers` - Submit questionnaire answers
- `POST /forecast-credits` - Generate credit forecast
- `POST /rag-query` - Ask questions about 45Q documents
- `POST /upload-document` - Upload additional documents

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