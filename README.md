<div align="center">
  <img src="static/images/logo.svg" width="64" alt="ScriptAI logo" />
  <h1>ScriptAI</h1>
  <p>Natural Language → Production Code</p>
  <p>
    <a href="https://scriptai-production.up.railway.app">Live Demo</a> ·
    <a href="#quick-start">Quick Start</a> ·
    <a href="https://github.com/qtaura/ScriptAI">GitHub</a>
  </p>

  <!-- Screenshot (ensure file exists at static/images/readme-hero.png) -->
  <img src="static/images/readme-hero.png" alt="ScriptAI UI (v1.7.0) — Hero and Quick Start" width="900" />
</div>

## Overview
ScriptAI turns plain English into production-ready scripts. It ships a Flask API and a Vite SPA, with adapters for leading AI providers and a lightweight plugin system for custom models.

## Highlights
- Multi-model adapters: OpenAI, Anthropic, Hugging Face, Google, plus Local stub
- Clean UI for prompt testing with model profiles and quick switching
- Guardrails: prompt validation, sanitization, per-IP rate limiting
- Observability: structured JSON logs, Prometheus metrics, health/stats endpoints
- Extensible: drop-in plugins for custom adapters

## Live Demo
- Visit: [scriptai-production.up.railway.app](https://scriptai-production.up.railway.app)
- Notes: Cloud providers require API keys; dev uses in-memory rate limiting

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

## Screenshots
- Main UI: `static/images/readme-hero.png`
  - If the image doesn’t show, place the screenshot file at this exact path and commit.

## License
MIT
