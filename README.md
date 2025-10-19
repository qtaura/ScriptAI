<div align="center">
  <img src="static/images/logo.svg" width="64" alt="ScriptAI logo" />
  <h1>ScriptAI</h1>
  <p>Natural Language → Production Code</p>
  <p>
    <a href="https://scriptai-production.up.railway.app">Live Demo</a> ·
    <a href="#quick-start">Quick Start</a> ·
    <a href="https://github.com/qtaura/ScriptAI">GitHub</a>
  </p>
  <img src="docs/assets/readme-hero.png" alt="ScriptAI UI (v1.7.0)" width="900" />
</div>

## Overview
ScriptAI turns natural language into production-ready scripts with multi-model support. It ships a Flask API and a Vite SPA, with adapters for popular AI providers.

## Live Demo
- URL: `https://scriptai-production.up.railway.app`
- Notes: Cloud providers require API keys; dev uses in-memory rate limiting.

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

## Features
- Multi-model generation (OpenAI, Anthropic, Hugging Face, Google)
- Prompt validation and metrics dashboard
- Extensible adapter/plugin system
- Rate limiting, logging, and basic observability
- Lightweight UI for testing prompts

## License
MIT
