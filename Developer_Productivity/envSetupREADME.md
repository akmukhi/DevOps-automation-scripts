# Environment Setup Automation

A comprehensive Python tool to automate the setup of local development environments. This tool handles virtual environment creation, dependency installation, development tools setup, and environment configuration.

## Features

### 🚀 Core Functionality
- **Virtual Environment Management** - Create and manage Python virtual environments
- **Dependency Installation** - Install requirements from requirements.txt files
- **Development Tools** - Automatically install and configure development tools
- **Environment Variables** - Set up .env files with project-specific variables
- **Post-Setup Commands** - Run custom commands after setup completion
- **Cross-Platform Support** - Works on Windows, macOS, and Linux

### 🛠️ Supported Tools
- **Code Quality**: pre-commit, black, flake8, pylint
- **Testing**: pytest, pytest-cov
- **Formatting**: black, isort
- **Documentation**: sphinx
- **Containerization**: Docker (instructions)
- **Node.js**: Installation instructions

### 📊 Features
- **Progress Tracking** - Real-time setup progress with detailed logging
- **Error Handling** - Comprehensive error reporting and recovery
- **Configuration Management** - JSON-based configuration files
- **Flexible Setup** - Command-line arguments and config file support
- **Setup Summary** - Detailed report of completed steps and issues

## Installation

No installation required! This is a standalone Python script that uses only the standard library.

```bash
# Clone or download the script
git clone <repository>
cd Developer_Productivity

# Make executable (Unix/Linux/macOS)
chmod +x envSetupAutomation.py
```

## Quick Start

### Basic Usage

```bash
# Run with default settings
python envSetupAutomation.py

# Create a configuration template
python envSetupAutomation.py --create-template

# Use a custom configuration file
python envSetupAutomation.py --config setup-config-example.json
```

### Command Line Options

```bash
# Basic setup with custom project name
python envSetupAutomation.py --project-name "MyApp"

# Specify Python version and virtual environment
python envSetupAutomation.py --python-version "3.9" --virtual-env-name "myenv"

# Install specific tools
python envSetupAutomation.py --tools pre-commit black pytest

# Use custom requirements file
python envSetupAutomation.py --requirements-file "my-requirements.txt"
```

## Configuration

### Configuration File Format

Create a JSON configuration file to customize your setup:

```json
{
  "projectName": "MyAwesomeProject",
  "pythonVersion": "3.9",
  "virtualEnvName": "venv",
  "requirementsFile": "requirements.txt",
  "devRequirementsFile": "requirements-dev.txt",
  "gitRepo": "https://github.com/username/my-awesome-project.git",
  "additionalTools": [
    "pre-commit",
    "black",
    "flake8",
    "pytest",
    "docker"
  ],
  "postSetupCommands": [
    "echo 'Environment setup completed successfully!'",
    "git init",
    "pre-commit install"
  ],
  "environmentVariables": {
    "PYTHONPATH": ".",
    "DEBUG": "True",
    "DATABASE_URL": "sqlite:///dev.db",
    "API_KEY": "your-api-key-here"
  }
}
```

### Configuration Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `projectName` | string | Name of the project | "MyProject" |
| `pythonVersion` | string | Required Python version | "3.8" |
| `virtualEnvName` | string | Virtual environment directory name | "venv" |
| `requirementsFile` | string | Path to requirements.txt | "requirements.txt" |
| `devRequirementsFile` | string | Path to dev requirements file | null |
| `gitRepo` | string | Git repository URL | null |
| `additionalTools` | array | List of tools to install | [] |
| `postSetupCommands` | array | Commands to run after setup | [] |
| `environmentVariables` | object | Environment variables for .env file | {} |

## Usage Examples

### Example 1: Basic Flask Project Setup

```bash
# Create configuration
python envSetupAutomation.py --create-template

# Edit setup-config.json with your Flask project details
# Then run setup
python envSetupAutomation.py --config setup-config.json
```

### Example 2: FastAPI Project with Development Tools

```bash
python envSetupAutomation.py \
  --project-name "FastAPI-App" \
  --python-version "3.9" \
  --tools pre-commit black flake8 pytest \
  --requirements-file "requirements.txt"
```

### Example 3: Django Project with Custom Environment

```bash
python envSetupAutomation.py \
  --project-name "Django-Blog" \
  --virtual-env-name "django_env" \
  --tools black isort pytest \
  --post-setup-commands "python manage.py migrate" "python manage.py createsuperuser"
```

## Supported Tools

### Code Quality Tools

#### pre-commit
- Installs pre-commit hooks
- Automatically configures if `.pre-commit-config.yaml` exists
- Runs code quality checks before commits

#### black
- Code formatter
- Installs with isort for import sorting
- Configurable line length

#### flake8
- Linter for style guide enforcement
- Checks PEP 8 compliance
- Configurable rules

#### pylint
- Advanced static analysis
- Code quality scoring
- Detailed error reporting

### Testing Tools

#### pytest
- Modern testing framework
- Includes pytest-cov for coverage
- Supports fixtures and parametrization

### Documentation Tools

#### sphinx
- Documentation generator
- Includes ReadTheDocs theme
- Supports multiple output formats

## File Structure

After running the setup, your project will have:

```
my-project/
├── venv/                    # Virtual environment
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── .env                     # Environment variables
├── .pre-commit-config.yaml  # Pre-commit configuration (if using)
└── setup-config.json        # Setup configuration
```

## Environment Variables

The tool creates a `.env` file with your specified environment variables:

```bash
# Example .env file
PYTHONPATH=.
DEBUG=True
DATABASE_URL=sqlite:///dev.db
API_KEY=your-api-key-here
ENVIRONMENT=development
```

## Post-Setup Commands

Run custom commands after setup completion:

```json
{
  "postSetupCommands": [
    "echo 'Setup complete!'",
    "python -c 'print(\"Hello, World!\")'",
    "git init",
    "pre-commit install",
    "python manage.py migrate"
  ]
}
```

## Error Handling

The tool provides comprehensive error handling:

- **System Requirements**: Checks Python version compatibility
- **Virtual Environment**: Handles existing environments gracefully
- **Dependencies**: Reports installation failures with details
- **Tools**: Continues setup even if some tools fail
- **Commands**: Logs failed post-setup commands

## Output Examples

### Successful Setup

```
🚀 Setting up development environment for: MyAwesomeProject
📁 Project path: /path/to/project
🐍 Python version: 3.9

🔍 Checking system requirements...
✅ System requirements met

🐍 Creating virtual environment: venv
✅ Virtual environment created successfully

📦 Installing dependencies...
✅ Dependencies installed successfully
✅ Development dependencies installed successfully

🛠️  Setting up additional tools: pre-commit, black, flake8, pytest
  Installing pre-commit...
    ✅ pre-commit installed and configured
  Installing black...
    ✅ Code formatters (black, isort) installed
  Installing flake8...
    ✅ Linters (flake8, pylint) installed
  Installing pytest...
    ✅ Testing framework (pytest) installed

🔧 Setting up environment variables...
✅ Environment variables configured

⚡ Running post-setup commands...
  Running: echo 'Environment setup completed successfully!'
    ✅ Command completed: echo 'Environment setup completed successfully!'

============================================================
SETUP SUMMARY
============================================================
Project: MyAwesomeProject
Virtual Environment: /path/to/project/venv
Python Version: 3.9.7
Setup Time: 45.23 seconds

Steps Completed (6):
  ✅ System requirements check
  ✅ Virtual environment creation
  ✅ Dependencies installation
  ✅ Development dependencies installation
  ✅ Additional tools setup
  ✅ Environment variables setup
  ✅ Post-setup commands

============================================================
NEXT STEPS
============================================================
1. Activate the virtual environment:
   source venv/bin/activate

2. Verify installation:
   python --version
   pip list

3. Start developing! 🚀

🎉 Environment setup completed successfully!
```

### Setup with Warnings

```
⚠️  Virtual environment already exists at /path/to/project/venv
Do you want to recreate it? (y/N): n

Warnings (1):
  ⚠️  Using existing virtual environment

Warnings (1):
  ⚠️  Failed to install tool: docker
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Setup Development Environment
on: [push, pull_request]

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Setup environment
      run: |
        python Developer_Productivity/envSetupAutomation.py \
          --config setup-config.json
    
    - name: Run tests
      run: |
        source venv/bin/activate
        pytest
```

### GitLab CI Example

```yaml
setup_environment:
  stage: setup
  script:
    - python Developer_Productivity/envSetupAutomation.py --config setup-config.json
  artifacts:
    paths:
      - venv/
```

## Troubleshooting

### Common Issues

#### Python Version Mismatch
```
Error: Python version 3.7.5 does not meet requirement 3.9
```
**Solution**: Upgrade Python or adjust the required version in configuration.

#### Virtual Environment Already Exists
```
⚠️  Virtual environment already exists at /path/to/venv
```
**Solution**: Choose to recreate or use existing environment.

#### Permission Errors
```
Error: Failed to create virtual environment: Permission denied
```
**Solution**: Check directory permissions or run with appropriate privileges.

#### Network Issues
```
Error: Failed to install dependencies: Connection timeout
```
**Solution**: Check internet connection or use a different package index.

### Performance Tips

1. **Use Requirements Files**: Pre-pin dependencies for faster installation
2. **Skip Optional Tools**: Only install tools you actually need
3. **Use Cached Environments**: Reuse existing virtual environments when possible
4. **Parallel Installation**: Some tools support parallel installation

## Contributing

To contribute to the environment setup automation:

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Ensure all quality checks pass

## License

This tool is part of the DevOps automation scripts project.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the configuration examples
3. Check system requirements
4. Verify file permissions

---

**Happy coding! 🚀**
