<div align="center">
  <img src="assets/images/logo.svg" alt="ScriptAI Logo" width="200"/>
  <h1>ScriptAI</h1>
  <p><strong>Enterprise-Grade AI-Powered Code Generation Platform</strong></p>
  <p>
    <a href="#features">Features</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#installation">Installation</a> •
    <a href="#usage">Usage</a> •
    <a href="#testing">Testing</a> •
    <a href="#roadmap">Roadmap</a> •
    <a href="#license">License</a>
  </p>
</div>

---

## Overview

ScriptAI is a sophisticated code generation platform that leverages state-of-the-art AI models to transform natural language descriptions into production-ready code. Designed for developers, by developers, ScriptAI streamlines the coding process by generating boilerplate code, complex algorithms, and functional components across multiple programming languages.

## Features

### Core Capabilities
- **Multi-Model AI Integration**: Seamlessly switch between OpenAI GPT-3.5, HuggingFace StarCoder, or local models
- **Intelligent Code Generation**: Create complex algorithms and functional components from natural language descriptions
- **Language Detection**: Automatically identifies programming languages for proper syntax highlighting
- **Syntax Highlighting**: Implements Prism.js for beautiful, readable code presentation
- **Multi-Platform Support**: Access via intuitive web interface or powerful command-line tool

### Developer Experience
- **Dual Interface Options**: Choose between web UI or CLI based on your workflow
- **Interactive CLI Mode**: Maintain context across multiple code generation requests
- **Code Export**: Save generated code directly to files or copy to clipboard
- **Customizable Models**: Configure which AI models to use based on your requirements

## Architecture

ScriptAI employs a modular architecture designed for extensibility and performance:

```
ScriptAI/
├── app.py                 # Web application entry point (Flask)
├── cli.py                 # Command-line interface
├── static/                # Static assets
│   ├── css/               # Styling and UI components
│   └── js/                # Client-side functionality and Prism.js integration
├── templates/             # HTML templates
├── tests/                 # Comprehensive test suite
│   ├── test_app.py        # Web application tests
│   └── test_cli.py        # CLI functionality tests
└── requirements.txt       # Dependency management
```

## Installation

### Prerequisites
- Python 3.6+
- pip (Python package manager)
- API keys for selected AI providers (OpenAI and/or HuggingFace)

### Setup Process

1. **Clone the repository**
   ```bash
   git clone https://github.com/jailk123/ScriptAI.git
   cd ScriptAI
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows activation
   venv\Scripts\activate
   
   # macOS/Linux activation
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API credentials**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```
   
   API keys can be obtained from:
   - OpenAI: https://platform.openai.com/api-keys
   - HuggingFace: https://huggingface.co/settings/tokens

## Usage

### Web Interface

1. **Launch the application server**
   ```bash
   python app.py
   ```

2. **Access the web interface**
   ```
   http://127.0.0.1:5000/
   ```

3. **Generate code**
   - Enter your requirements in natural language
   - Select your preferred AI model
   - Click "Generate Code"
   - View syntax-highlighted results
   - Save or copy the generated code

### Command Line Interface

#### Interactive Mode
```bash
python cli.py -i
```

This launches an interactive session with the following capabilities:
- Submit multiple prompts while maintaining context
- Switch models with `model openai|huggingface|local`
- Save output with `save filename.ext`
- Exit with `exit` or `quit`

#### Direct Command Mode
```bash
python cli.py "Create a Python function that implements quicksort" --model openai --file quicksort.py
```

**Available options:**
- `--model`, `-m`: Specify AI model (openai, huggingface, local)
- `--file`, `-f`: Save output directly to specified file
- `--interactive`, `-i`: Launch interactive mode

## Testing

ScriptAI includes a comprehensive test suite to ensure reliability and performance:

```bash
# Run all tests
python -m unittest discover tests

# Run with coverage report
coverage run -m unittest discover tests
coverage report
```

## Roadmap

### Q1 2025
- ✅ Multi-model AI integration
- ✅ Web and CLI interfaces
- ✅ Syntax highlighting with Prism.js
- ✅ Comprehensive test suite

### Q2 2025
- 🔄 Local model support via llama.cpp
- 🔄 Language-specific code templates
- 🔄 Code optimization suggestions

### Q3 2025
- 📅 User authentication system
- 📅 Cloud-based snippet storage
- 📅 Team collaboration features
- 📅 API endpoint for third-party integration

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">
  <p>Developed with ❤️ by ScriptAI Team</p>
  <p>
    <a href="https://github.com/jailk123/ScriptAI/issues">Report Bug</a> •
    <a href="https://github.com/jailk123/ScriptAI/issues">Request Feature</a>
  </p>
</div>
