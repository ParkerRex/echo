# Video Processor Backend

## Development Setup (Mac)

1. **Python Version Management with pyenv**:
   ```bash
   # Ensure you're using the correct Python version
   pyenv install 3.12.7  # If not already installed
   pyenv local 3.12.7    # Sets Python version for this directory
   ```

2. **Virtual Environment Setup**:
   ```bash
   # Create venv using pyenv's Python
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   make install-dev
   ```

## VS Code Python Interpreter Setup

When VS Code asks you to select a Python interpreter:

1. **For Mac Users**:
   - Select the interpreter that shows "(pyenv)" in its path
   - It should be `.../pyenv/versions/3.12.7/bin/python`
   - This ensures you're using the pyenv-managed Python version
   - DO NOT select system Python or other versions

2. **After pyenv selection**:
   - VS Code will automatically find the virtual environment in `backend/venv`
   - You'll see "venv" in the status bar once it's properly configured

## Development Tools

We use specific versions of development tools to ensure consistency:

1. **Python Version**:
   - Python 3.12.7 (managed via pyenv)
   - Used for all backend development

2. **Code Quality Tools**:
   - Black v24.1.1 (formatter)
   - Ruff v0.2.1 (linter)
   - pytest 7.4.0 (testing)

These versions are pinned in requirements.txt for consistency across the team.

### Available Commands

Use `make` commands to run code quality tools:

```bash
# Format code (Black + Ruff)
make format

# Run linter checks
make lint

# Run tests
make test

# Run all checks (format, lint, test)
make check
```

### Tool Configuration

- Black and Ruff configurations are in `pyproject.toml`
- VS Code settings are in `.vscode/settings.json`
- Extension recommendations are in `.vscode/extensions.json`

## Troubleshooting

If you encounter Python/VS Code issues:

1. **Wrong Python Version**:
   ```bash
   # Check your current Python version
   python --version  # Should show 3.12.7
   
   # If incorrect, ensure pyenv is set:
   pyenv local 3.12.7
   ```

2. **Virtual Environment Issues**:
   ```bash
   # Recreate the virtual environment if needed
   deactivate  # If already in a venv
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **VS Code Integration**:
   - Command Palette → "Python: Select Interpreter"
   - Choose the pyenv version (3.12.7) from the list
   - Look for the path containing "pyenv/versions/3.12.7"
   - VS Code should then detect and use the venv automatically
   - Reload VS Code if settings aren't taking effect
