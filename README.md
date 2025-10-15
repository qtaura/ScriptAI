<div align="center">
  <img src="static/images/logo.svg" alt="ScriptAI Logo" width="200"/>
  <h1>ScriptAI</h1>
  <p><strong>Enterprise-Grade AI-Powered Code Generation Platform</strong></p>
  <p>
    <a href="#features">Features</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#quickstart">Quickstart</a> •
    <a href="#usage">Usage</a> •
    <a href="#api">API</a> •
    <a href="#testing--quality">Testing</a> •
    <a href="#roadmap">Roadmap</a> •
    <a href="#license">License</a>
  </p>
</div>

AI-powered code generation platform — fast, reliable, and extensible.

[![CI](https://github.com/qtaura/ScriptAI/actions/workflows/ci.yml/badge.svg)](https://github.com/qtaura/ScriptAI/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](pyproject.toml)

---

## Overview

ScriptAI turns natural language requirements into production-ready code. It ships a modern React SPA, a robust Flask API, and a convenient CLI — all backed by modular model adapters, security guardrails, and observability.

### 1.3.0 Highlights
- React SPA is now the default GUI at `/`.
- Dark mode implemented via CSS tokens (shadcn-style) with persisted theme.
- Model Select dropdown spacing fixed (no content overlap).
- Updated tests and routes to reflect SPA-first experience.

## Table of Contents
- Features
- Architecture
- Quickstart
- Usage (Web & CLI)
- API
- Security
- Monitoring
- Testing & Quality
- Roadmap
- Contributing
- License

## Features
- Multi-model adapters: OpenAI, HuggingFace, and Local.
- Modern SPA with theme support, keyboard-friendly UX, and syntax highlighting.
- CLI with interactive sessions and direct command mode.
- Prometheus metrics (`/metrics`) and lightweight dashboards.
- Rate limiting via Flask-Limiter and strict JSON error handling.
- Comprehensive tests and CI for reliability.

## Architecture

```
ScriptAI/
├── app.py                 # Flask app serving SPA and APIs
├── cli.py                 # Command-line interface
├── frontend/              # React/Vite SPA (source)
│   ├── src/               # Components, styles, tokens
│   └── vite.config.ts     # Build config
├── static/figmalol/       # Compiled SPA assets served at '/'
├── templates/             # Legacy templates (kept for compatibility)
├── tests/                 # Pytest suite (web + CLI)
└── requirements.txt       # Dependencies
```

Key endpoints:
- `GET /` — React SPA
- `GET /models` — Available model adapters
- `POST /generate` — Code generation
- `GET /metrics` — Prometheus metrics
- `GET /health` — Health check

## Quickstart

1) Install dependencies
```
pip install -r requirements.txt
```

2) Configure credentials
```
cp .env.example .env
# Edit .env with your API keys (OpenAI/HuggingFace)
```

3) Run the app
```
# On Windows use: py -3 app.py
python app.py
# Open http://127.0.0.1:5000/
```

## Usage

### Web (SPA)
- Open `http://127.0.0.1:5000/`.
- Enter a prompt, choose a model, generate code.
- Toggle dark mode; theme persists across sessions.

### CLI
Interactive mode
```
python cli.py -i
```

Direct command
```
python cli.py "Create a Python quicksort" --model openai --file quicksort.py
```

Options
- `--model` (`openai|huggingface|local`)
- `--file`  save output to file
- `--interactive` launch interactive mode

## Examples & Sample Outputs

### Python Data Processing
Prompt: "Create a Python function that reads a CSV file, filters rows where the 'age' column is greater than 30, and writes the result to a new CSV file."

Generated Code (OpenAI GPT-3.5):
```python
import pandas as pd

def filter_csv_by_age(input_file, output_file, min_age=30):
    """
    Read a CSV file, filter rows where age > min_age, and save to new file.
    """
    try:
        df = pd.read_csv(input_file)
        filtered_df = df[df['age'] > min_age]
        filtered_df.to_csv(output_file, index=False)
        return filtered_df
    except FileNotFoundError:
        return None
    except Exception as e:
        return None
```

### React Component
Prompt: "Write a React component that displays a paginated list of items fetched from an API endpoint."

Generated Code (HuggingFace StarCoder):
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
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (page) => setCurrentPage(page);

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
        <button onClick={() => handlePageChange(currentPage - 1)} disabled={currentPage === 1}>Previous</button>
        <span>Page {currentPage} of {totalPages}</span>
        <button onClick={() => handlePageChange(currentPage + 1)} disabled={currentPage === totalPages}>Next</button>
      </div>
    </div>
  );
};

export default PaginatedList;
```

### SQL Query
Prompt: "Create a SQL query that joins three tables (users, orders, products) and returns the total amount spent by each user on each product category."

Generated Code (Local Model):
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

### Model Comparison

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| OpenAI GPT-3.5 | Fast | High | Paid | Production code, complex algorithms |
| HuggingFace StarCoder | Medium | Good | Free | Open source, code completion |
| Local Model | Slow | Variable | Free | Privacy, offline use |

## API

Generate code
```
POST /generate
{
  "prompt": "Build a Python function that validates emails",
  "model": "local"
}
```

List models
```
GET /models
```

Errors are returned as compact JSON with appropriate HTTP status codes.

## Customization & Extensions

### Web (Flask) Adapters

Adapters live in `model_adapters.py` and follow a simple interface:

```python
class ModelAdapter:
    def generate(self, prompt: str):
        raise NotImplementedError

class CustomAdapter(ModelAdapter):
    def generate(self, prompt: str):
        return "# your generated code", None
```

The web app routes requests based on `{ "model": "local|openai|huggingface" }`.

### CLI Generators

Extend the CLI in `cli.py` with a custom generator:

```python
class CustomModelGenerator(CodeGenerator):
    def generate(self, prompt: str):
        # Integrate your provider here
        return self.format_code("// code"), None
```

## Customizing the Web Interface

- Styling: `frontend/src/index.css` (SPA) and `static/css/style.css` (legacy)
- Functionality: `frontend/src/components/*`
- Templates: `templates/index.html` (legacy alias, SPA now default)

## Configuration Options

Create `config.json` for advanced settings:
```json
{
  "models": {
    "openai": { "temperature": 0.7, "max_tokens": 1500, "model": "gpt-3.5-turbo" },
    "huggingface": { "temperature": 0.7, "max_tokens": 500, "model": "bigcode/starcoder" }
  },
  "security": { "max_prompt_length": 1000, "rate_limit": 100, "sanitize_input": true }
}
```

## Security
### Input Validation & Sanitization
- Prompt validation for malicious content and size
- XSS protection: escaping and script removal

### Rate Limiting & Abuse Prevention
- Default `100/hour` per IP; stricter test limits on `/generate`
- 429 responses: `{ "error": "Rate limit exceeded. Try again later." }`

### Security Endpoints
- `GET /health` — System health check
- `GET /security-stats` — Security statistics

## Monitoring
- `GET /metrics` — Prometheus text format (standard exposition)
- `GET /metrics-json` — Combined usage, performance, health for dashboards
- `GET /stats` — Usage statistics (last 24h)
- `GET /performance` — Latency, throughput, percentiles

## Testing & Quality
- Run tests: `py -3 -m pytest -q`.
- Formatting: Black (23.12.1) for consistent style.
- Type checking: MyPy; linting: Flake8; security scanning: Bandit.

## CI/CD Pipeline
- Automated tests on every commit
- Security scanning and code quality checks
- Release tags (e.g., `v1.3.0`) published via GitHub

## Roadmap

### Released (v1.3.0)
- SPA becomes the default UI served at `/`.
- Light/Dark theme tokens and early theme script.
- Dropdown spacing fix in CodeGenerator.
- Tests updated to assert SPA mount and `/models` API.

### Unreleased
- User authentication and role-based access controls.
- Cloud-based snippet storage with versioning.
- Team collaboration features (shared projects, permissions).
- Public API and API keys for third-party integration.
- Advanced analytics and reporting dashboards.
- Plugin system for custom model adapters.
- Redis-backed Flask-Limiter for distributed rate limiting.
- CLI rate limiting and improved offline mode documentation.

## Contributing
Pull requests are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
MIT — see [LICENSE](LICENSE).

---

<div align="center">
  <p>Developed with ❤️ by ScriptAI Team</p>
  <p>
    <a href="https://github.com/qtaura/ScriptAI/issues">Report Bug</a> •
    <a href="https://github.com/qtaura/ScriptAI/issues">Request Feature</a>
  </p>
</div>
