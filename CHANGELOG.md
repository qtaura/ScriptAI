# Changelog

All notable changes to ScriptAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Table of Contents
- [Unreleased](#unreleased)
- [1.6.0 - 2025-10-16](#160---2025-10-16)
- [1.5.0 - 2025-10-16](#150---2025-10-16)
- [1.4.5 - 2025-10-15](#145---2025-10-15)
- [1.4.0 - 2025-10-15](#140---2025-10-15)
- [1.3.0 - 2025-10-14](#130---2025-10-14)
- [1.2.0 - 2025-10-13](#120---2025-10-13)
- [1.1.0 - 2025-10-13](#110---2025-10-13)
- [1.0.0 - 2025-10-11](#100---2025-10-11)

## [Unreleased]

<!-- No unreleased changes at this time. -->

## [1.6.0] - 2025-10-16

### Added
- Data Privacy Mode across backend and CLI. Set `DATA_PRIVACY_MODE=true` to disable file logging and usage stats persistence in the backend (skip `scriptai_stats.json` load/save) while retaining console JSON logs. CLI `--privacy` sets the environment and avoids creating/updating `~/.scriptai/config.json` and `history.json`.

### Documentation
- Rewrote README to lead with a clearer value proposition and more professional structure (concise Quickstart, Usage, API, Security & Observability, Configuration, Development).
- Added Data Privacy Mode guidance documenting `DATA_PRIVACY_MODE` and `--privacy`, and how to disable file logging (`LOG_TO_FILE=false`).
- Clarified Windows Quickstart and Vercel routing note (`/api/*` in production vs root locally).
- Preserved existing logo and simplified anchors for better scanability.

### Fixed
- Vercel configuration: removed invalid `functions.runtime` from `vercel.json` and rely on Vercel’s built‑in Python runtime selection (fixes “Function Runtimes must have a valid version”).
- Black formatting compliance across Python 3.8/3.9/3.10: adjusted top‑level blank lines in `cli.py` to satisfy Black 23.12.1.

### Build
- Remove duplicate `playwright` package from frontend devDependencies; keep `@playwright/test`. Regenerated `frontend/package-lock.json` to resolve conflicts and ensure reproducible `npm ci` in CI.

### Testing
- Add `window.matchMedia` polyfill in `frontend/src/setupTests.ts` for jsdom to stabilize Vitest.
- Update `frontend/src/App.test.tsx` to use role-based selectors and scoped queries to avoid duplicate text matches (hero heading “Production Code”, scoped “Prompt” within the generator section).
- Constrain Vitest to only `src/**/*.{test,spec}.{ts,tsx}` and exclude `e2e/**` to prevent collecting Playwright specs (fixes “test() called in an unexpected context”).
- Playwright config is ESM-safe: derive directory from `import.meta.url` via `fileURLToPath` and use it for `webServer.cwd` in `frontend/playwright.config.ts`.
- Stabilize Playwright smoke test selectors in `frontend/e2e/smoke.spec.ts`:
  - Use hero heading `getByRole('heading', { name: /Production Code/i })` instead of a non-existent “ScriptAI” heading.
  - Keep generator heading `getByRole('heading', { name: /Try the Code Generator/i })`.
  - Scope “Prompt” assertion to `#generator` to avoid duplicate matches from the How It Works flow.

### CI
- Frontend unit and Playwright e2e jobs are unblocked and no longer interfere with each other; Vitest no longer collects e2e specs.

### Notes
- Planned follow-ups: expand frontend unit tests for model selection/prompt behavior; add integration/e2e tests for `/generate` including provider success and 429 rate‑limits; publish CI artifacts (Playwright traces/videos) on failures.

## [1.5.0] - 2025-10-16

### Added
- CLI `benchmark` subcommand to compare models’ average generation time and output characteristics.
- CLI logging flags: `--verbose`, `--debug`, and `--trace` wired to centralized logging.
- TRACE logging level for ultra-verbose diagnostics.

### Changed
- Web UI version labels updated to `v1.5.0` across Hero and Footer.
- Centralized logging honors `LOG_LEVEL`, `LOG_TO_FILE`, `LOG_FILE_PATH`, `LOGGING_CONFIG`.

### Fixed
- Minor CLI argparse naming collision avoided by using a dedicated benchmark prompt arg.

### Documentation
- README updated with benchmark usage examples and options.

### Notes
- Providers without configured API keys are skipped during benchmarking; invalid keys report clear errors.
 

## [1.4.5] - 2025-10-15

### Fixed
- Select dropdown layering with `z-index` increase to avoid overlap with the Generate button and prompt text.
- Robust frontend mapping of `/models` response to canonical IDs (supports legacy string lists and object-based schema). Ensures Local Model appears enabled when server reports availability.

### Changed
- Model selector displays all models from `modelCards.json` while disabling those not reported by `/models`; disabled entries show “(requires key)”.
- Block generation attempts for disabled/unavailable models and show a clear error banner.
- Graceful fallback if `/models` fails: UI still renders model cards, marks unknown ones disabled.

### Build
- Rebuilt frontend assets under `static/figmalol` to include the selector fixes.

## [1.4.0] - 2025-10-15

### Added
- JSON structured logging formatter emitting compact, machine-parseable logs with `request_id`.
- Request ID middleware: honors `X-Request-ID` header or generates a UUID when absent; echoes header in responses.
- Monitoring logs now include `request_id` and model labels for end-to-end traceability.
- Animated hover effects for model cards (background glow, badge, and icon transitions).

### Changed
- Standardized logging across the app to structured JSON for consistency and easier ingestion.
- ModelComparison UI reworked: replaced scrollbar overflow with an auto-paging carousel (4–6 cards per page depending on viewport).
- Added page fade transitions for carousel; autoplay advances every 5s and pauses on hover.
- Grid adapts to screen width (4 cards on small screens, 6 on large).
- UI version labels updated to `v1.4.0` across Hero and Footer.

### Fixed
- Removed unused `type: ignore` in `monitoring.py` to satisfy MyPy on py311.
- Black formatting compliance: added blank line before nested `JSONFormatter` class.

### Accessibility
- Carousel and hover animations respect `prefers-reduced-motion` and reduce/disable motion accordingly.

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

<!-- 1.2.0 moved above for chronological order -->

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