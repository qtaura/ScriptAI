# ScriptAI

AI-powered code generation platform — fast, reliable, and extensible.

[![CI](https://github.com/jailk123/ScriptAI/actions/workflows/ci.yml/badge.svg)](https://github.com/jailk123/ScriptAI/actions/workflows/ci.yml)
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

## Security
- Input validation and sanitization for unsafe patterns.
- Per-IP and per-route rate limiting via Flask-Limiter.
- Sensible defaults for headers and error handling.

## Monitoring
- Prometheus metrics exposed at `/metrics`.
- Request counters, error counts, and latency histograms.

## Testing & Quality
- Run tests: `py -3 -m pytest -q`.
- Formatting: Black (23.12.1) for consistent style.
- Type checking: MyPy; linting: Flake8; security scanning: Bandit.

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

Developed with care by the ScriptAI team.
