# Contributing to smol-saas

Thank you for your interest in contributing to smol-saas! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful and considerate of others.

## How to Contribute

### Reporting Bugs

- Check if the bug has already been reported in the Issues section
- Use the bug report template if available
- Include detailed steps to reproduce the bug
- Include the exact version of smol-saas you're using
- Include any error messages or screenshots

### Suggesting Enhancements

- Check if the enhancement has already been suggested in the Issues section
- Use the feature request template if available
- Clearly describe the enhancement and why it would be valuable
- Consider including mockups or examples of how the enhancement might work

### Pull Requests

1. Fork the repository
2. Create a new branch for your changes (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run tests if available to ensure your changes don't break existing functionality
5. Commit your changes (`git commit -m 'Add your-feature-name'`)
6. Push to your branch (`git push origin feature/your-feature-name`)
7. Create a Pull Request against the `main` branch

### Development Setup

1. Clone the repository
2. Install the package in development mode:
   ```bash
   pip install -e ".[auto]"
   ```
3. Make your changes
4. Test your changes:
   ```bash
   python -m pytest
   ```

## Style Guidelines

- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Include docstrings for functions and classes
- Keep lines under 100 characters when possible

## Licensing

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License. 