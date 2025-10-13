# Changelog

All notable changes to ScriptAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-12

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

## [Unreleased]

### Added
- GUI entry point: Added `main()` in `app.py` to support `scriptai-gui` and direct execution.

### Changed
- CI/CD: Switched release step to `softprops/action-gh-release` and enabled generated release notes.
- CI/CD: Granted `permissions: contents: write` for release workflow.

### Fixed
- Packaging: Removed legacy license classifier to comply with PEP 639; build succeeds.
- Release: Resolved "Resource not accessible by integration" by correcting permissions and action.

### Planned
- Local model support via llama.cpp
- Language-specific code templates
- Code optimization suggestions
- User authentication system
- Cloud-based snippet storage
- Team collaboration features
- API endpoint for third-party integration
- Advanced monitoring and analytics
- Enhanced security features
- Performance optimizations