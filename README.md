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

### 1.4.0 Highlights
- JSON structured logging with per-request `request_id` for traceability.
- `X-Request-ID` header support and automatic UUID generation when absent.
- Monitoring logs now include `request_id` and model labels.
- Black/MyPy compliance improvements; test suite verified.

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
- Multi-model adapters: OpenAI, HuggingFace, Anthropic Claude, Google Gemini, and Local.
- Modern SPA with theme support, keyboard-friendly UX, and syntax highlighting.
- CLI with interactive sessions and direct command mode.
- Prometheus metrics (`/metrics`) and lightweight dashboards.
- Rate limiting via Flask-Limiter and strict JSON error handling.
- Comprehensive tests and CI for reliability.

## Dynamic Model Registry

The UI model list is driven by a single JSON config and filtered by backend availability:

- Edit `frontend/public/modelCards.json` to add or update models. Use adapter IDs: `openai`, `huggingface`, `local`.
- The UI loads this config and intersects it with the server `GET /models` endpoint. The server lists models based on environment configuration.
- If there’s no intersection, the UI falls back to the server’s list; if neither is available, a local placeholder is shown.

Backend availability is controlled via environment variables:

- `OPENAI_API_KEY` enables the `openai` adapter.
- `HUGGINGFACE_API_KEY` enables the `huggingface` adapter.
- `ANTHROPIC_API_KEY` enables the `anthropic` adapter.
- `GOOGLE_API_KEY` enables the `gemini` adapter.
- `local` is always available as a placeholder.

This approach keeps one source of truth for display names and metadata while ensuring only configured providers are selectable.

Model Profiles API:
- `GET /model-profiles` returns `{ models: [ { id, name, speed, quality, cost, available, badge, icon, features[] } ], timestamp }`.
- Fields are categorical and meant for UI display; `available` reflects configured credentials.

Provider SDKs (optional adapters):
- Install Anthropic and Gemini SDKs when using these adapters:
  - `pip install anthropic google-generativeai`
  - If not installed, the server returns a clear error indicating the missing package.

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
- `GET /model-profiles` — Dynamic provider metadata (speed, cost, quality, availability)
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

## Logging

- Centralized structured logging is configured via `monitoring.MonitoringManager`.
- Default config loads from `logging.json` (or `logging.yaml`/`logging.yml` if present). Falls back to a JSON console logger and optional file logger.

Environment variables:
- `LOG_LEVEL`: Set severity (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). Default: `INFO`.
- `LOG_TO_FILE`: Enable/disable file logging (`true|false`). Default: `true`.
- `LOG_FILE_PATH`: Path for the log file when enabled. Default: `scriptai.log`.
- `LOGGING_CONFIG`: Override logging config file path (JSON/YAML), e.g. `logging.json`.

JSON config example (`logging.json`):
```
{
  "version": 1,
  "disable_existing_loggers": false,
  "formatters": { "json": { "()": "monitoring.JSONFormatter" } },
  "handlers": {
    "console": { "class": "logging.StreamHandler", "level": "INFO", "formatter": "json" },
    "file":    { "class": "logging.FileHandler",  "level": "INFO", "formatter": "json", "filename": "scriptai.log" }
  },
  "root": { "level": "INFO", "handlers": ["console", "file"] },
  "loggers": { "ScriptAI": { "level": "INFO", "propagate": true } }
}
```

Notes:
- When `LOG_TO_FILE=false`, the file handler is disabled even if present in `logging.json`.

CLI flags (shortcut to set `LOG_LEVEL`):
- `--verbose` sets `LOG_LEVEL=INFO`
- `--debug` sets `LOG_LEVEL=DEBUG`
- `--trace` sets `LOG_LEVEL=TRACE` (extra-verbose; custom level supported)
- `monitoring.JSONFormatter` outputs consistent fields: `timestamp`, `level`, `logger`, `message`, plus optional context like `request_id`, `model_name`, and `response_time`.

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
- `--model` (`openai|huggingface|anthropic|gemini|local`)
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

The web app routes requests based on `{ "model": "local|openai|huggingface|anthropic|gemini" }`.

### Fallback System
- If the primary provider fails, the server automatically retries with backup models in a preferred order: `openai → anthropic → gemini → huggingface → local`.
- Responses include `model_used` and `fallback_from` when a fallback is applied.
- Toggle with `ENABLE_FALLBACK=true|false` (defaults to enabled).

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

### Request Signatures
- Optional HMAC verification using `REQUEST_SIGNATURE_SECRET` (or `SIGNING_SECRET`).
- Headers: `X-Signature: v1=<hex>` and `X-Signature-Timestamp: <epoch_seconds>`.
- Base string: `v1:{timestamp}:{body}`; digest: HMAC SHA256 hex.
- If no secret is configured, verification is skipped unless explicitly required by the caller.

### Security Endpoints
- `GET /health` — System health check
- `GET /security-stats` — Security statistics

## Monitoring
- `GET /metrics` — Prometheus text format (standard exposition)
- `GET /metrics-json` — Combined usage, performance, health for dashboards
- `GET /stats` — Usage statistics (last 24h)
- `GET /performance` — Latency, throughput, percentiles

### Centralized Logging Config
- Configure logging globally via `LOGGING_CONFIG` env var or drop-in files:
  - Detection order: `LOGGING_CONFIG` → `logging.yaml` → `logging.yml` → `logging.json`.
  - If no config is found, ScriptAI falls back to JSON logs with console + file handlers (`scriptai.log`).
- JSON format uses the built-in `monitoring.JSONFormatter` for structured output.
- YAML support requires `PyYAML`. If YAML parsing fails, the app falls back to JSON or defaults.

Included sample: `logging.json`
```json
{
  "version": 1,
  "disable_existing_loggers": false,
  "formatters": {"json": {"()": "monitoring.JSONFormatter"}},
  "handlers": {
    "console": {"class": "logging.StreamHandler", "level": "INFO", "formatter": "json", "stream": "ext://sys.stdout"},
    "file":    {"class": "logging.FileHandler", "level": "INFO", "formatter": "json", "filename": "scriptai.log", "encoding": "utf-8"}
  },
  "root": {"level": "INFO", "handlers": ["console", "file"]},
  "loggers": {"ScriptAI": {"level": "INFO", "propagate": true}, "ScriptAI.Security": {"level": "INFO", "propagate": true}}
}
```

Use a custom config path
```bash
# Windows PowerShell
$env:LOGGING_CONFIG = "C:\\path\\to\\logging.json"
py -3 app.py
```

### Structured Logging & Request IDs
- Logs are emitted in compact JSON to ease ingestion and analysis.
- Each request carries a `request_id` (from `X-Request-ID` or auto-generated UUID) propagated into logs and echoed back in responses.

Example log line
```json
{"level":"info","ts":"2025-10-15T12:34:56.789Z","message":"request","request_id":"demo-123","method":"POST","path":"/generate","status":200,"duration_ms":123,"model":"openai"}
```

Pass a custom request ID
```bash
curl -H "X-Request-ID: demo-123" http://127.0.0.1:5000/health -v
```

## Testing & Quality
- Run tests: `py -3 -m pytest -q`.
- Formatting: Black (23.12.1) for consistent style.
- Type checking: MyPy; linting: Flake8; security scanning: Bandit.

## CI/CD Pipeline
- Automated tests on every commit
- Security scanning and code quality checks
- Release tags (e.g., `v1.4.0`) published via GitHub

## Roadmap

### Released (v1.4.0)
- Structured JSON logging with `request_id` field across request lifecycle.
- `X-Request-ID` middleware and header propagation in responses.
- Monitoring logs enriched with model labels and request IDs.
- Black/MyPy cleanups validated in CI.

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
