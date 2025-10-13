# Changelog

All notable changes to ScriptAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [1.2.0] - Unreleased

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

### Documentation
- Clarified multi-model/modular AI backends status: partially implemented.
  Modular structure exists, but flexibility isn’t fully demonstrated; only the
  primary model is tested. README guidance updated to avoid implying full
  flexibility.
 - Polished README: added Quickstart section, clarified adapter selection and
   testing coverage, and updated Python requirement to 3.9+
 - Documented anti-abuse measures: Flask-Limiter defaults, JSON 429 handler, and CLI notes

### Planned
- User authentication system
- Cloud-based snippet storage
- Team collaboration features
- API endpoint for third-party integration
- Advanced analytics and reporting
- Plugin system for custom models