# ScriptAI

An intelligent code generation bot that can create scripts and code snippets from natural language prompts.

## Features

- Generate code from natural language descriptions
- Multiple AI model options:
  - OpenAI GPT-3.5 (requires API key)
  - HuggingFace StarCoder (free alternative, requires API key)
  - Local model placeholder (for future implementation)
- Web interface and CLI options
- Save generated code to files
- Copy code to clipboard

## Setup Instructions

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/jailk123/ScriptAI.git
   cd ScriptAI
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up API keys:
   - Copy the example environment file: `cp .env.example .env`
   - Edit the `.env` file and add your API keys
   - You only need one of these keys to use the application
   - Get OpenAI API key from: https://platform.openai.com/api-keys
   - Get HuggingFace API key from: https://huggingface.co/settings/tokens
   - **IMPORTANT**: Never commit your `.env` file with real API keys to GitHub

## Usage

### Web Interface

1. Start the web server:
   ```
   python app.py
   ```

2. Open your browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

3. Enter your prompt, select a model, and click "Generate Code"

### Command Line Interface

The CLI supports both interactive and one-off command modes:

#### Interactive Mode

```
python cli.py -i
```

This starts an interactive session where you can:
- Enter prompts and get code responses
- Switch between models with `model openai|huggingface|local`
- Save generated code to files
- Exit with `exit` or `quit`

#### One-off Command

```
python cli.py "Write a Python function to calculate Fibonacci numbers" --model huggingface
```

Options:
- `--model` or `-m`: Select the model (openai, huggingface, local)
- `--file` or `-f`: Save output to a file
- `--interactive` or `-i`: Start interactive mode

## Examples

Try these prompts:

1. "Write a Python function to find prime numbers up to n"
2. "Create a JavaScript function that validates email addresses"
3. "Make a simple HTML form with name, email, and submit button"
4. "Write a Java class for a basic banking system with deposit and withdraw methods"

## Future Enhancements

- Add syntax highlighting for generated code
- Implement local model support (e.g., using llama.cpp)
- Add more language-specific templates
- Implement user authentication and saved snippets
- Add unit tests

## License

MIT
