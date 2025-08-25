# Code Quality Checker

A comprehensive Python code quality analysis tool that checks for various code quality issues, style violations, and provides detailed metrics.

## Features

### Code Analysis
- **Syntax Error Detection**: Identifies Python syntax errors
- **Style Checking**: Enforces PEP 8 style guidelines
- **Complexity Analysis**: Calculates cyclomatic complexity for functions and classes
- **Naming Convention Checks**: Validates PEP 8 naming conventions
- **Line Length Validation**: Checks for lines exceeding maximum length

### Metrics Calculation
- Lines of code (LOC)
- Comment and blank line counts
- Function and class counts
- Cyclomatic complexity
- Maintainability index

### External Tool Integration
- **Flake8 Integration**: Runs flake8 if available for additional checks
- **Extensible**: Easy to add more external tools

### Reporting
- **Text Output**: Human-readable detailed reports
- **JSON Output**: Machine-readable format for CI/CD integration
- **Quality Score**: Overall project quality score (0-100)
- **Issue Categorization**: Issues grouped by severity and type

## Installation

No additional dependencies required beyond Python standard library. For enhanced functionality:

```bash
# Install flake8 for additional checks
pip install flake8

# Install optional dependencies for better analysis
pip install pylint
```

## Usage

### Basic Usage

```bash
# Analyze current directory
python code_quality_checker.py .

# Analyze specific project
python code_quality_checker.py /path/to/project

# Output in JSON format
python code_quality_checker.py . --format json
```

### Advanced Usage

```bash
# Custom line length
python code_quality_checker.py . --max-line-length 100

# Custom complexity threshold
python code_quality_checker.py . --max-function-complexity 15

# Use custom configuration file
python code_quality_checker.py . --config code_quality_config.json
```

### Configuration File

Create a `code_quality_config.json` file to customize the checker:

```json
{
    "max_line_length": 79,
    "max_function_complexity": 10,
    "max_class_complexity": 20,
    "ignore_patterns": [
        "__pycache__",
        ".git",
        "venv"
    ],
    "severity_weights": {
        "error": 3,
        "warning": 2,
        "info": 1
    }
}
```

## Output Examples

### Text Output