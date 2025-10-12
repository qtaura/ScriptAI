---
description: Repository Information Overview
alwaysApply: true
---

# ScriptAI Information

## Summary
ScriptAI is an intelligent code generation tool that creates code snippets from natural language prompts. It offers both a web interface and a command-line interface (CLI), supporting multiple AI models including OpenAI GPT-3.5, HuggingFace StarCoder, and a placeholder for future local model implementation.

## Structure
- **app.py**: Flask web application with routes for homepage and code generation API
- **cli.py**: Command-line interface with interactive and one-off command modes
- **templates/**: Contains HTML templates for the web interface
- **static/**: Contains CSS and JavaScript files for the web interface
- **.env & .env.example**: Environment configuration for API keys
- **.gitignore**: Specifies files to exclude from version control
- **requirements.txt**: Python dependencies

## Language & Runtime
**Language**: Python 3.6+
**Web Framework**: Flask 2.0.1
**Package Manager**: pip
**Key Libraries**: 
- openai 0.27.0
- python-dotenv 0.19.0
- requests 2.28.1
- argparse 1.4.0

## Dependencies
**Main Dependencies**:
- Flask: Web framework for the application interface
- OpenAI: Client library for OpenAI API integration
- Requests: HTTP library for API calls to HuggingFace
- python-dotenv: For loading environment variables from .env file

## Build & Installation
```bash
# Create virtual environment (optional)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up API keys
cp .env.example .env
# Edit .env with your API keys
```

## Usage
**Web Interface**:
```bash
python app.py
# Access at http://127.0.0.1:5000/
```

**CLI - Interactive Mode**:
```bash
python cli.py -i
```

**CLI - One-off Command**:
```bash
python cli.py "Write a Python function to calculate Fibonacci numbers" --model huggingface
```

## Features
- Multiple AI model support (OpenAI, HuggingFace, local placeholder)
- Web interface with model selection and code generation
- Interactive CLI with model switching
- Code saving to files
- Copy to clipboard functionality

## Project Components

### Web Interface
- **Main File**: app.py
- **Template**: templates/index.html
- **JavaScript**: static/js/script.js
- **CSS**: static/css/style.css
- **Features**: Model selection, code generation, copy to clipboard, save to file

### Command Line Interface
- **Main File**: cli.py
- **Features**: Interactive mode, one-off commands, model switching, file saving

### AI Integration
- **OpenAI**: Integration with GPT-3.5 for commercial code generation
- **HuggingFace**: Integration with StarCoder as a free alternative
- **Local Model**: Placeholder for future implementation