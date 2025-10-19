<div align="center">
  <img src="static/images/logo.svg" width="64" alt="ScriptAI logo" />
  <h1>ScriptAI</h1>
  <p>Natural Language → Production Code</p>
  <p>
    <a href="https://scriptai-production.up.railway.app">Live Demo</a> ·
    <a href="#quick-start">Quick Start</a> ·
    <a href="https://github.com/qtaura/ScriptAI">GitHub</a>
  </p>

  <img src="static/images/readme-hero.png" alt="ScriptAI UI (v1.7.0) — Hero and Quick Start" width="900" />
</div>

## Overview
ScriptAI is a small web app and HTTP API that turns plain‑English instructions into working code. Type a prompt in the browser or call `POST /generate` and you’ll get back code you can copy, run, or save. It supports multiple model providers, includes safe defaults (validation and rate limits), and gives you metrics for basic observability.

What you can do:
- Generate functions, scripts, and boilerplate directly from requirements.
- Compare outputs across providers to pick the best fit.
- Automate generation from CI or your own tools via the API.

## Highlights
- Multi‑model adapters: OpenAI, Anthropic, Hugging Face, Google, plus a Local stub
- Clean UI for prompt testing with quick model switching
- Guardrails: input validation, sanitization, per‑IP rate limiting
- Observability: JSON logs, Prometheus metrics, health/stats endpoints
- Extensible: simple plugin system for custom adapters

## Live Demo
- Visit: [scriptai-production.up.railway.app](https://scriptai-production.up.railway.app)
- Notes: Cloud providers require API keys; dev uses in‑memory rate limiting

## Quick Start
Requirements: Python `3.11+`, Node `18+`.

```bash
pip install -r requirements.txt
py -3 app.py
# SPA (optional)
cd frontend
npm install
npm run dev
```

## API (Basics)
- `GET /models` — available adapters
- `GET /model-profiles` — UI model metadata
- `POST /generate` — body: `{ "prompt": "...", "model": "openai" }`
- `GET /metrics` — Prometheus metrics

## Architecture
```
ScriptAI/
├─ app.py              # Flask app serving SPA + APIs
├─ static/figmalol/    # Built SPA assets
├─ frontend/           # React/Vite SPA source (dev only)
├─ model_adapters.py   # Provider adapters
├─ security.py         # Validation, sanitization, rate limiting
├─ monitoring.py       # JSON logging + Prometheus
└─ plugins/            # Optional custom adapters
```

## License
MIT
