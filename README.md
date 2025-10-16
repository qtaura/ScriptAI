<div align="center">
  <img src="static/images/logo.svg" alt="ScriptAI Logo" width="180" />
  <h1>ScriptAI</h1>
  <p><strong>Generate production‑ready code from plain English — Web, API, CLI.</strong></p>
  <p>Provider‑agnostic, secure by default, observable, and extensible.</p>

  <p>
    <a href="#what-is-scriptai">What is ScriptAI?</a> •
    <a href="#quickstart">Quickstart</a> •
    <a href="#features">Features</a> •
    <a href="#usage">Usage</a> •
    <a href="#api">API</a> •
    <a href="#security--observability">Security & Observability</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#development">Development</a> •
    <a href="#testing">Testing</a> •
    <a href="#license">License</a>
  </p>
</div>

[![CI](https://github.com/qtaura/ScriptAI/actions/workflows/ci.yml/badge.svg)](https://github.com/qtaura/ScriptAI/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](pyproject.toml)

---

## What is ScriptAI?

ScriptAI turns natural‑language requirements into working, production‑grade code. It includes:
- A modern React single‑page app for prompting and inspecting output.
- A robust Flask API with provider‑agnostic adapters (OpenAI, Anthropic, Gemini, HuggingFace, Local).
- A convenient CLI for batch or interactive workflows.

Built‑in guardrails (validation, sanitization, rate limiting), structured JSON logs with request IDs, and Prometheus metrics make it ready for teams and serious projects.

## Quickstart

Prerequisites
- Python `3.8+` and `pip`
- Optional for SPA development: Node.js `>=18`

1) Install dependencies
```
pip install -r requirements.txt
```

2) Configure credentials (optional; runs locally without them using the Local adapter)
```
copy .env.example .env   # on Windows
# then edit .env and set any of: OPENAI_API_KEY, HUGGINGFACE_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY
```

3) Run the app
```
py -3 app.py   # Windows
# then open http://127.0.0.1:5000/
```

Notes
- On Vercel, the API is available under `/api/*` (e.g., `/api/generate`). Locally it’s at the root (e.g., `/generate`).
- The SPA is served at `/` by default.

## Features
- Provider‑agnostic model adapters: OpenAI, Anthropic Claude, Google Gemini, HuggingFace, and a Local stub.
- Dynamic model registry: UI reads `modelCards.json` and intersects with server‑reported availability.
- Smart fallback chain: if a provider fails, configurable fallback attempts keep responses flowing.
- Strong guardrails: input validation, XSS sanitization, per‑IP rate limiting, strict JSON errors.
- First‑class observability: structured logs with `X‑Request‑ID`, Prometheus `/metrics`, and health/stats endpoints.
- Web, API, and CLI — use it your way.

## Usage

### Web (SPA)
- Open `http://127.0.0.1:5000/`, enter a prompt, choose a model, and generate code.
- Themeable, keyboard‑friendly UI with code highlighting.

### CLI
Interactive mode
```
python cli.py -i
```

Direct command
```
python cli.py "Create a Python quicksort" --model openai --file quicksort.py
```

Benchmark
```
python cli.py benchmark "Write a factorial function" --models all --iterations 3 --json
```

## API

Base URL
- Local: `http://127.0.0.1:5000`
- Vercel: prefix endpoints with `/api` (e.g., `/api/models`)

Endpoints
- `GET /models` — Available model adapters based on configured credentials.
- `GET /model-profiles` — Categorical metadata for UI (speed, quality, cost, availability).
- `POST /generate` — Generate code.
  - Request:
    ```json
    { "prompt": "Build a function that validates emails", "model": "openai" }
    ```
  - Response:
    ```json
    { "code": "# generated code ...", "model_used": "openai" }
    ```
- `GET /health` — Health check.
- `GET /metrics` — Prometheus metrics (text exposition format).

Errors
- Standard JSON: `{ "error": "message" }` with appropriate HTTP status.

## Security & Observability

Security
- Input validation, XSS sanitization, and per‑IP rate limiting (default `100/hour`).
- Security headers (CSP, frame/ content‑type protections) applied to all responses.
- Optional HMAC signatures (for external callers): set `REQUEST_SIGNATURE_SECRET` and send
  `X‑Signature: v1=<hex>` and `X‑Signature‑Timestamp: <epoch_seconds>` using base string
  `v1:{timestamp}:{body}` and HMAC‑SHA256.

Data privacy mode
- By default the app does not persist prompts or generations.
- Set `LOG_TO_FILE=false` to disable file logging entirely; logs will stream to console only.

Observability
- Structured JSON logs via `monitoring.JSONFormatter` with `request_id` propagation (`X‑Request‑ID`).
- Prometheus metrics at `/metrics` and lightweight usage/performance stats at `/stats` and `/performance`.

## Configuration

Common environment variables (optional)
- `OPENAI_API_KEY`, `HUGGINGFACE_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` — enable providers.
- `ENABLE_FALLBACK=true|false` — turn cross‑provider fallback on/off (default on).
- `LOG_LEVEL` (default `INFO`), `LOG_TO_FILE=true|false`, `LOG_FILE_PATH`.
- `REQUEST_SIGNATURE_SECRET` (or `SIGNING_SECRET`) — enable request signing for external callers.

## Architecture

```
ScriptAI/
├── app.py                 # Flask app serving SPA and APIs
├── cli.py                 # Command‑line interface
├── frontend/              # React/Vite SPA (source for local dev)
├── static/figmalol/       # Built SPA assets served at '/'
├── tests/                 # Pytest suite (web + CLI)
├── security.py            # Validation, sanitization, signatures, rate limiting
├── monitoring.py          # Structured logging and Prometheus metrics
└── model_adapters.py      # Provider adapters and local generator
```

## Development

Run the Flask app (default SPA already built under `static/figmalol`)
```
py -3 app.py
```

Develop the SPA (optional)
```
cd frontend
npm install
npm run dev
```

## Testing
- Run tests: `py -3 -m pytest -q`.
- Black, MyPy, Flake8, and Bandit are configured for consistent quality.

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
