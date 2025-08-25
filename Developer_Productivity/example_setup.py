#!/usr/bin/env python3
"""
Example usage of the Environment Setup Automation
Demonstrates how to use the setup automation programmatically.
"""

from envSetupAutomation import EnvironmentSetupAutomation, SetupConfig

def example_basic_setup():
    """Example of basic environment setup."""
    print("=== Example 1: Basic Setup ===")
    
    # Create a basic configuration
    config = SetupConfig(
        projectName="MyBasicProject",
        pythonVersion="3.8",
        virtualEnvName="venv",
        requirementsFile="requirements.txt",
        devRequirementsFile=None,
        gitRepo=None,
        additionalTools=["black", "flake8"],
        postSetupCommands=[],
        environmentVariables={
            "PYTHONPATH": ".",
            "DEBUG": "True"
        }
    )
    
    # Run the setup
    setup = EnvironmentSetupAutomation(config)
    result = setup.setupEnvironment()
    
    print(f"Setup successful: {result.success}")
    print(f"Message: {result.message}")
    print(f"Setup time: {result.setupTime:.2f} seconds")
    print(f"Steps completed: {len(result.stepsCompleted)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")

def example_advanced_setup():
    """Example of advanced environment setup with multiple tools."""
    print("\n=== Example 2: Advanced Setup ===")
    
    # Create an advanced configuration
    config = SetupConfig(
        projectName="MyAdvancedProject",
        pythonVersion="3.9",
        virtualEnvName="advanced_env",
        requirementsFile="requirements.txt",
        devRequirementsFile="requirements-dev.txt",
        gitRepo="https://github.com/username/my-advanced-project.git",
        additionalTools=["pre-commit", "black", "flake8", "pytest", "docker"],
        postSetupCommands=[
            "echo 'Advanced setup completed!'",
            "python -c 'print(\"Hello from advanced project!\")'",
            "git init"
        ],
        environmentVariables={
            "PYTHONPATH": ".",
            "DEBUG": "True",
            "DATABASE_URL": "sqlite:///dev.db",
            "API_KEY": "your-api-key-here",
            "ENVIRONMENT": "development"
        }
    )
    
    # Run the setup
    setup = EnvironmentSetupAutomation(config)
    result = setup.setupEnvironment()
    
    print(f"Setup successful: {result.success}")
    print(f"Message: {result.message}")
    print(f"Setup time: {result.setupTime:.2f} seconds")
    
    if result.stepsCompleted:
        print("Steps completed:")
        for step in result.stepsCompleted:
            print(f"  ✅ {step}")
    
    if result.errors:
        print("Errors:")
        for error in result.errors:
            print(f"  ❌ {error}")
    
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")

def example_flask_project():
    """Example setup for a Flask web application."""
    print("\n=== Example 3: Flask Project Setup ===")
    
    config = SetupConfig(
        projectName="FlaskWebApp",
        pythonVersion="3.9",
        virtualEnvName="flask_env",
        requirementsFile="requirements.txt",
        devRequirementsFile="requirements-dev.txt",
        gitRepo=None,
        additionalTools=["black", "flake8", "pytest"],
        postSetupCommands=[
            "echo 'Flask project setup completed!'",
            "python -c 'import flask; print(f\"Flask version: {flask.__version__}\")'"
        ],
        environmentVariables={
            "PYTHONPATH": ".",
            "FLASK_APP": "app.py",
            "FLASK_ENV": "development",
            "DEBUG": "True",
            "SECRET_KEY": "your-secret-key-here"
        }
    )
    
    setup = EnvironmentSetupAutomation(config)
    result = setup.setupEnvironment()
    
    print(f"Flask project setup successful: {result.success}")
    if result.success:
        print("🎉 Flask project is ready for development!")

def example_fastapi_project():
    """Example setup for a FastAPI project."""
    print("\n=== Example 4: FastAPI Project Setup ===")
    
    config = SetupConfig(
        projectName="FastAPIApp",
        pythonVersion="3.9",
        virtualEnvName="fastapi_env",
        requirementsFile="requirements.txt",
        devRequirementsFile="requirements-dev.txt",
        gitRepo=None,
        additionalTools=["black", "flake8", "pytest", "pre-commit"],
        postSetupCommands=[
            "echo 'FastAPI project setup completed!'",
            "python -c 'import fastapi; print(f\"FastAPI version: {fastapi.__version__}\")'"
        ],
        environmentVariables={
            "PYTHONPATH": ".",
            "DEBUG": "True",
            "DATABASE_URL": "sqlite:///./fastapi.db",
            "API_PREFIX": "/api/v1"
        }
    )
    
    setup = EnvironmentSetupAutomation(config)
    result = setup.setupEnvironment()
    
    print(f"FastAPI project setup successful: {result.success}")
    if result.success:
        print("🚀 FastAPI project is ready for development!")

def main():
    """Run all examples."""
    print("Environment Setup Automation Examples")
    print("=" * 50)
    
    try:
        # Run examples
        example_basic_setup()
        example_advanced_setup()
        example_flask_project()
        example_fastapi_project()
        
        print("\n" + "=" * 50)
        print("All examples completed!")
        print("Check the output above for setup results.")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
