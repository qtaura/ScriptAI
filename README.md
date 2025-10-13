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

## What's New in 1.1.0
- Enhanced local model support with improved runtime behavior and fallbacks
- Advanced security improvements: stricter headers and safer defaults
- Performance optimizations across request handling and rendering paths
- Extended monitoring dashboard with richer metrics and charts

## How It Works

ScriptAI follows a streamlined pipeline from user input to generated code:

### 🔄 **Internal Flow**
```
User Prompt → Model Selection → AI Processing → Code Generation → Syntax Highlighting → Output
     ↓              ↓                ↓              ↓                    ↓              ↓
Natural Language → API Call → AI Response → Code Extraction → Prism.js → Formatted Code
```

### 🧠 **Model Processing**
1. **Input Validation**: Sanitizes and validates user prompts
2. **Model Routing**: Routes requests to selected AI model (OpenAI/HuggingFace/Local)
3. **Prompt Engineering**: Optimizes prompts for code generation
4. **Response Processing**: Extracts and cleans generated code
5. **Language Detection**: Automatically detects programming language
6. **Syntax Highlighting**: Applies appropriate syntax highlighting

### 🔧 **Architecture**

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
├── examples/              # Sample prompts and outputs
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

## Examples & Sample Outputs

### 🎯 **Sample Prompts & Generated Code**

#### **Python Data Processing**
**Prompt**: "Create a Python function that reads a CSV file, filters rows where the 'age' column is greater than 30, and writes the result to a new CSV file."

**Generated Code** (OpenAI GPT-3.5):
```python
import pandas as pd

def filter_csv_by_age(input_file, output_file, min_age=30):
    """
    Read a CSV file, filter rows where age > min_age, and save to new file.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
        min_age (int): Minimum age threshold (default: 30)
    """
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)
        
        # Filter rows where age > min_age
        filtered_df = df[df['age'] > min_age]
        
        # Write filtered data to new CSV file
        filtered_df.to_csv(output_file, index=False)
        
        print(f"Filtered {len(filtered_df)} rows and saved to {output_file}")
        return filtered_df
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        return None
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    filter_csv_by_age("data.csv", "filtered_data.csv", min_age=30)
```

#### **React Component**
**Prompt**: "Write a React component that displays a paginated list of items fetched from an API endpoint."

**Generated Code** (HuggingFace StarCoder):
```jsx
import React, { useState, useEffect } from 'react';

const PaginatedList = ({ apiEndpoint, itemsPerPage = 10 }) => {
  const [items, setItems] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [totalPages, setTotalPages] = useState(0);

  useEffect(() => {
    fetchItems();
  }, [currentPage, apiEndpoint]);

  const fetchItems = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiEndpoint}?page=${currentPage}&limit=${itemsPerPage}`);
      const data = await response.json();
      
      setItems(data.items || []);
      setTotalPages(Math.ceil(data.total / itemsPerPage));
    } catch (err) {
      setError('Failed to fetch items');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="paginated-list">
      <div className="items">
        {items.map((item, index) => (
          <div key={item.id || index} className="item">
            {JSON.stringify(item, null, 2)}
          </div>
        ))}
      </div>
      
      <div className="pagination">
        <button 
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          Previous
        </button>
        
        <span>Page {currentPage} of {totalPages}</span>
        
        <button 
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default PaginatedList;
```

#### **SQL Query**
**Prompt**: "Create a SQL query that joins three tables (users, orders, products) and returns the total amount spent by each user on each product category."

**Generated Code** (Local Model):
```sql
SELECT 
    u.user_id,
    u.username,
    p.category,
    SUM(o.quantity * p.price) as total_spent
FROM users u
INNER JOIN orders o ON u.user_id = o.user_id
INNER JOIN products p ON o.product_id = p.product_id
GROUP BY u.user_id, u.username, p.category
ORDER BY u.username, p.category;
```

### 🔧 **Model Comparison**

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| **OpenAI GPT-3.5** | Fast | High | Paid | Production code, complex algorithms |
| **HuggingFace StarCoder** | Medium | Good | Free | Open source, code completion |
| **Local Model** | Slow | Variable | Free | Privacy, offline use |

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

## Customization & Extensions

### 🔧 **Adding New Models**

To add a new AI model, create a new generator class in `cli.py`:

```python
class CustomModelGenerator(CodeGenerator):
    """Generate code using your custom model"""
    
    def __init__(self, api_key: str, model_name: str):
        super().__init__()
        self.api_key = api_key
        self.model_name = model_name
    
    def generate(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            # Your custom API integration here
            response = your_custom_api_call(prompt, self.api_key, self.model_name)
            return self.format_code(response), None
        except Exception as e:
            return None, f"Error with custom model: {str(e)}"
```

### 🎨 **Customizing the Web Interface**

1. **Styling**: Modify `static/css/style.css`
2. **Functionality**: Update `static/js/script.js`
3. **Templates**: Edit `templates/index.html`

### ⚙️ **Configuration Options**

Create a `config.json` file for advanced settings:

```json
{
  "models": {
    "openai": {
      "temperature": 0.7,
      "max_tokens": 1500,
      "model": "gpt-3.5-turbo"
    },
    "huggingface": {
      "temperature": 0.7,
      "max_tokens": 500,
      "model": "bigcode/starcoder"
    }
  },
  "security": {
    "max_prompt_length": 1000,
    "rate_limit": 100,
    "sanitize_input": true
  }
}
```

## Testing

ScriptAI includes a comprehensive test suite to ensure reliability and performance:

```bash
# Run all tests
python -m unittest discover tests

# Run with coverage report
coverage run -m unittest discover tests
coverage report
```

## 🔒 Security Features

### Input Validation & Sanitization
- **Prompt Validation**: Checks for malicious content and excessive length
- **XSS Protection**: HTML escaping and script tag removal
- **Rate Limiting**: Prevents abuse with configurable limits
- **Input Sanitization**: Removes dangerous patterns and scripts

### Security Endpoints
- `/health` - System health check
- `/stats` - Usage statistics
- `/performance` - Performance metrics
- `/security-stats` - Security statistics

### Monitoring & Logging
- **Request Logging**: Tracks all API requests with timing
- **Error Tracking**: Monitors and categorizes errors
- **Performance Metrics**: Response times and success rates
- **Prometheus Metrics**: Standard `/metrics` endpoint exposes counters and histograms
- **Security Events**: Logs suspicious activities

## 🚀 Production Features

### Monitoring Dashboard
Access real-time metrics at:
- `http://localhost:5000/health` - Health status
- `http://localhost:5000/stats` - Usage statistics
- `http://localhost:5000/performance` - Performance data
- `http://localhost:5000/metrics` - Prometheus metrics (text format)
- `http://localhost:5000/metrics-json` - Combined dashboard metrics (JSON)

### Configuration
Create `config.json` for advanced settings:
```json
{
  "security": {
    "max_prompt_length": 1000,
    "rate_limit": 100,
    "sanitize_input": true
  },
  "monitoring": {
    "log_file": "scriptai.log",
    "max_log_size": 10485760
  }
}
```

## 🧪 Testing & Quality

### Test Coverage
- **Unit Tests**: Comprehensive test suite
- **Integration Tests**: API endpoint testing
- **Security Tests**: Input validation testing
- **Performance Tests**: Load and stress testing

### Code Quality
- **Linting**: Flake8 for code style
- **Type Checking**: MyPy for type safety
- **Formatting**: Black for consistent code style
- **Security Scanning**: Bandit for security issues

### CI/CD Pipeline
- **Automated Testing**: Runs on every commit
- **Security Scanning**: Checks for vulnerabilities
- **Code Quality**: Enforces coding standards
- **Automated Releases**: GitHub Actions workflow

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Start for Contributors
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/ScriptAI.git
cd ScriptAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m unittest discover tests -v
```

## 📊 Roadmap

### ✅ Completed (v1.0.0)
- Multi-model AI integration
- Web and CLI interfaces
- Syntax highlighting with Prism.js
- Comprehensive test suite
- Security features and input validation
- Monitoring and logging
- CI/CD pipeline
- Community contribution guidelines

### 🔄 In Progress (v1.2.0)
- User authentication system
- Cloud-based snippet storage
- Team collaboration features
- API endpoint for third-party integration
- Advanced analytics and reporting
- Plugin system for custom models

### 📅 Planned (v1.3.0+)
- To be announced

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
