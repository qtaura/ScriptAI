# Changelog

All notable changes to ScriptAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- User authentication and role-based access controls
- Cloud-based snippet storage with versioning
- Team collaboration features (shared projects, permissions)
- Public API and API keys for third-party integration
- Advanced analytics and reporting dashboards
- Plugin system for custom model adapters
- Redis-backed Flask-Limiter for distributed rate limiting
- CLI rate limiting and improved offline mode documentation

## [1.5.0] - Unreleased

> A sneak peek at what’s landing in 1.5.0. Not final yet — details may evolve.

### Added
- CLI logging flags: `--verbose`, `--debug`, and `--trace` wired to centralized logging.
- TRACE logging level for ultra-verbose diagnostics, including `logger.trace(...)` support.
- Frontend error banners: destructive Alerts for model load/generation errors and misconfigured `modelCards.json` entries.

### Changed
- Centralized logging honors environment overrides (`LOG_LEVEL`, `LOG_TO_FILE`, `LOG_FILE_PATH`, `LOGGING_CONFIG`).
- CLI initializes logging but skips Prometheus metrics to avoid duplicate registry entries.
- Black-compliant formatting adjustments in `monitoring.py` for Python 3.9 CI stability.

### Fixed
- Vite import resolution: replace `class-variance-authority@0.7.1` with `class-variance-authority` in `frontend/src/components/ui/alert.tsx`.
- Robust removal of `file` handler from logging configs when `LOG_TO_FILE=false`.

### Documentation
- README updated: centralized logging controls, JSON config example, and new CLI flags.

### Teasers
- Subtle quality-of-life upgrades: toast notifications, centralized error registry, and improved offline mode for CLI.
- Better artifact handling for generated code (save/export and diff hints).
- Multi-remote push ergonomics to smooth out origin/upstream workflows.

## [1.4.0] - 2025-10-15

### Added
- JSON structured logging formatter emitting compact, machine-parseable logs with `request_id`.
- Request ID middleware: honors `X-Request-ID` header or generates a UUID when absent; echoes header in responses.
- Monitoring logs now include `request_id` and model labels for end-to-end traceability.

### Changed
- Standardized logging across the app to structured JSON for consistency and easier ingestion.

### Fixed
- Removed unused `type: ignore` in `monitoring.py` to satisfy MyPy on py311.
- Black formatting compliance: added blank line before nested `JSONFormatter` class.

### Security
- Verified `.env` is gitignored and repository contains no committed API keys (`sk-`/`api_key` patterns clean).

### Tests
- Pytest suite passes: 19 tests, 1 warning.

### Documentation
- README updated with structured logging and Request ID guidance; CI example tags reference `v1.4.0`.

## [1.3.0] - 2025-10-14

### Added
- React SPA becomes the primary GUI, now served at `/`.
- Light/Dark theme tokens defined in `frontend/src/index.css` (shadcn-style), enabling robust theming across components.
- Early theme application script in SPA to respect persisted choice or system preference before paint.
- Root asset routes (`/assets/<path>` and `/vite.svg`) to support SPA assets resolving correctly from `/`.

### Changed
- Flask root route switched from `templates/index.html` (Jinja) to `static/figmalol/index.html` (SPA).
- Frontend build artifacts updated under `static/figmalol/assets/` after rebuild.
- `frontend/src/components/CodeGenerator.tsx`: add dynamic bottom padding while the model Select is open to avoid overlaying content.

### Fixed
- Dark mode toggle is now functional across the app via CSS tokens; `.dark` class correctly drives theme.
- Model Select dropdown no longer overlaps example prompts thanks to responsive spacing.
- Tabs now highlight the active state consistently in Web vs CLI.
- UI version labels updated to `v1.3.0` for consistency across Hero and Footer.
- All GitHub links updated to new repository owner `qtaura/ScriptAI` (UI, templates, docs).

### Tests
- `tests/test_app.py`: update `test_home_page` to assert SPA mount point (`id="root"`).
- Replace template-based model check with `/models` API validation in `test_models_endpoint_lists_local_model`.

### Documentation
- README cleanup: consolidated Security and Monitoring sections, clarified Quickstart (Windows note) and CLI flags.
- CI badge and issue links updated to the new repository.

### Deprecations
- Legacy Jinja-based home page removed from `/`; the SPA is the default UI. The previous `/ui/new` remains as an alias.

## [1.1.0] - 2025-10-13

### Added
- Enhanced local model support (improved runtime, better fallback behavior)
- Extended monitoring dashboard with richer metrics and charts

### Changed
- Performance optimizations across request handling and rendering paths

### Security
- Advanced security features (expanded input validation, stricter headers, safer defaults)

## [1.0.0] - 2025-10-11

### Added
- Initial release of ScriptAI
- Multi-model AI integration (OpenAI GPT-3.5, HuggingFace StarCoder, Local models)
- Web interface with beautiful UI and syntax highlighting
- Command-line interface with interactive mode
- Comprehensive test suite
- Support for multiple programming languages
- Code export functionality (copy to clipboard, save to file)
- Automatic language detection
- Prism.js syntax highlighting integration

### Security
- Input validation and sanitization
- API key protection
- Rate limiting capabilities

### Documentation
- Comprehensive README with examples
- API documentation
- Installation and usage guides
- Customization instructions

## [1.2.0] - 2025-10-13

### Added
- Prometheus metrics integration: `/metrics` endpoint exposes counters and histograms
- Request instrumentation: counters, latency histogram, and error counts in `monitoring.py`
- Minimal API error handling: clean JSON errors for invalid JSON and unknown model
- Tests for `/metrics` endpoint and API error handling
- Flask-Limiter integration: per-IP rate limiting with per-route limits on `/generate`
- Tests validating 429 JSON responses when `/generate` exceeds configured limits

### Changed
- `/metrics` now serves Prometheus text; previous JSON moved to `/metrics-json`
- Applied Black 23.12.1 formatting to satisfy Python 3.10/3.11 CI
- Hooked Flask `before_request`/`after_request` to record request timing and labels
- Updated README to accurately describe monitoring endpoints
- README updated with Rate Limiting & Abuse Prevention section and guidance

### Fixed
- Resolved mypy typing errors around Prometheus metrics and Flask hooks on py310
- Eliminated Black diffs by normalizing import spacing and top-level separation
 - Resolved mypy typing errors around Flask-Limiter optional import on py311

### Documentation
- Clarified multi-model/modular AI backends status: partially implemented.
  Modular structure exists, but flexibility isn’t fully demonstrated; only the
  primary model is tested. README guidance updated to avoid implying full
  flexibility.
 - Polished README: added Quickstart section, clarified adapter selection and
   testing coverage, and updated Python requirement to 3.9+
 - Documented anti-abuse measures: Flask-Limiter defaults, JSON 429 handler, and CLI notes