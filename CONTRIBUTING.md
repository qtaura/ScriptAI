# Contributing to ScriptAI

Thank you for your interest in contributing to ScriptAI! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues
- Use the GitHub issue tracker
- Provide detailed reproduction steps
- Include system information (OS, Python version, etc.)
- Use appropriate labels (bug, feature, enhancement)

### Suggesting Features
- Check existing issues first
- Provide clear use cases and benefits
- Consider implementation complexity
- Be specific about requirements

### Code Contributions
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit with clear messages
7. Push to your fork
8. Create a Pull Request

## 🛠️ Development Setup

### Prerequisites
- Python 3.6+
- Git
- Virtual environment (recommended)

### Setup Steps
```bash
# Clone your fork
git clone https://github.com/yourusername/ScriptAI.git
cd ScriptAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m unittest discover tests -v
```

### Development Dependencies
Create `requirements-dev.txt`:
```
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0
pre-commit>=2.20.0
```

## 📝 Code Style Guidelines

### Python Code
- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions small and focused
- Use meaningful variable names

### Example:
```python
def generate_code(prompt: str, model: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate code using specified AI model.
    
    Args:
        prompt: User input prompt
        model: AI model to use ('openai', 'huggingface', 'local')
        
    Returns:
        Tuple of (generated_code, error_message)
    """
    # Implementation here
    pass
```

### JavaScript Code
- Use modern ES6+ features
- Follow consistent indentation
- Add comments for complex logic
- Use meaningful function names

### CSS Code
- Use consistent naming conventions
- Organize styles logically
- Use CSS variables for theming
- Keep selectors specific

## 🧪 Testing Guidelines

### Test Coverage
- Aim for >80% code coverage
- Test both success and error cases
- Include edge cases
- Test with different inputs

### Test Structure
```python
class TestCodeGenerator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.generator = CodeGenerator()
    
    def test_successful_generation(self):
        """Test successful code generation"""
        # Test implementation
        pass
    
    def test_error_handling(self):
        """Test error handling"""
        # Test implementation
        pass
```

### Running Tests
```bash
# Run all tests
python -m unittest discover tests -v

# Run with coverage
coverage run -m unittest discover tests
coverage report
coverage html  # Generate HTML report
```

## 🔧 Adding New Features

### New AI Models
1. Create a new generator class in `cli.py`
2. Follow the existing pattern
3. Add tests for the new model
4. Update documentation

### New UI Features
1. Modify templates and static files
2. Add JavaScript functionality
3. Update CSS for styling
4. Test across different browsers

### New CLI Commands
1. Add new argument parser options
2. Implement command logic
3. Add help text and examples
4. Write tests

## 📚 Documentation

### Code Documentation
- Use docstrings for all functions and classes
- Include parameter descriptions
- Provide usage examples
- Document return values

### README Updates
- Keep installation instructions current
- Update feature lists
- Add new examples
- Update screenshots if UI changes

### API Documentation
- Document all endpoints
- Include request/response examples
- List error codes
- Provide authentication info

## 🐛 Bug Reports

### Before Reporting
1. Check existing issues
2. Try latest version
3. Reproduce the issue
4. Check logs for errors

### Bug Report Template
```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen.

**Actual Behavior**
What actually happens.

**Environment**
- OS: [e.g., Windows 10]
- Python: [e.g., 3.11.7]
- ScriptAI Version: [e.g., 1.0.0]

**Additional Context**
Any other relevant information.
```

## 🚀 Feature Requests

### Feature Request Template
```markdown
**Feature Description**
A clear description of the feature.

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this feature work?

**Alternatives**
Other solutions you've considered.

**Additional Context**
Any other relevant information.
```

## 📋 Pull Request Process

### Before Submitting
1. Ensure all tests pass
2. Update documentation if needed
3. Add tests for new features
4. Follow code style guidelines
5. Update CHANGELOG.md

### PR Template
```markdown
**Description**
Brief description of changes.

**Type of Change**
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

**Testing**
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Manual testing completed

**Checklist**
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## 🏷️ Release Process

### Version Numbering
- Follow Semantic Versioning (MAJOR.MINOR.PATCH)
- Update VERSION file
- Update CHANGELOG.md
- Create GitHub release

### Release Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Version bumped
- [ ] CHANGELOG updated
- [ ] GitHub release created
- [ ] PyPI package updated (if applicable)

## 🤔 Questions?

- Check existing issues and discussions
- Join our community Discord (if available)
- Contact maintainers directly
- Check the documentation

## 📄 License

By contributing to ScriptAI, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- GitHub contributors page
- Release notes
- Project documentation

Thank you for contributing to ScriptAI! 🎉