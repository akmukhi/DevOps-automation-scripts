#!/usr/bin/env python3
"""
Environment Setup Automation for Local Development
A comprehensive tool to automate the setup of development environments.
"""

import os
import sys
import subprocess
import argparse
import json
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import urllib.request
import zipfile
import tarfile

@dataclass
class SetupConfig:
    """Configuration for environment setup."""
    projectName: str
    pythonVersion: str
    virtualEnvName: str
    requirementsFile: str
    devRequirementsFile: Optional[str]
    gitRepo: Optional[str]
    additionalTools: List[str]
    postSetupCommands: List[str]
    environmentVariables: Dict[str, str]

@dataclass
class SetupResult:
    """Result of environment setup operation."""
    success: bool
    message: str
    stepsCompleted: List[str]
    errors: List[str]
    warnings: List[str]
    setupTime: float

class EnvironmentSetupAutomation:
    """Main class for environment setup automation."""
    
    def __init__(self, config: SetupConfig):
        self.config = config
        self.projectPath = Path.cwd()
        self.venvPath = self.projectPath / config.virtualEnvName
        self.results = SetupResult(
            success=False,
            message="",
            stepsCompleted=[],
            errors=[],
            warnings=[],
            setupTime=0.0
        )
        
    def setupEnvironment(self) -> SetupResult:
        """Main method to set up the development environment."""
        import time
        startTime = time.time()
        
        print(f"🚀 Setting up development environment for: {self.config.projectName}")
        print(f"📁 Project path: {self.projectPath}")
        print(f"🐍 Python version: {self.config.pythonVersion}")
        
        try:
            # Check system requirements
            if not self._checkSystemRequirements():
                return self.results
            
            # Create virtual environment
            if not self._createVirtualEnvironment():
                return self.results
            
            # Install dependencies
            if not self._installDependencies():
                return self.results
            
            # Setup additional tools
            if not self._setupAdditionalTools():
                return self.results
            
            # Setup environment variables
            if not self._setupEnvironmentVariables():
                return self.results
            
            # Run post-setup commands
            if not self._runPostSetupCommands():
                return self.results
            
            # Generate setup summary
            self._generateSetupSummary()
            
            self.results.success = True
            self.results.message = "Environment setup completed successfully!"
            
        except Exception as e:
            self.results.errors.append(f"Setup failed: {str(e)}")
            self.results.message = "Environment setup failed!"
        
        self.results.setupTime = time.time() - startTime
        return self.results
    
    def _checkSystemRequirements(self) -> bool:
        """Check if system meets requirements."""
        print("\n🔍 Checking system requirements...")
        
        # Check Python version
        pythonVersion = platform.python_version()
        if not self._versionCheck(pythonVersion, self.config.pythonVersion):
            self.results.errors.append(
                f"Python version {pythonVersion} does not meet requirement {self.config.pythonVersion}"
            )
            return False
        
        self.results.stepsCompleted.append("System requirements check")
        print("✅ System requirements met")
        return True
    
    def _versionCheck(self, current: str, required: str) -> bool:
        """Check if current version meets required version."""
        currentParts = [int(x) for x in current.split('.')]
        requiredParts = [int(x) for x in required.split('.')]
        
        for i in range(max(len(currentParts), len(requiredParts))):
            currentPart = currentParts[i] if i < len(currentParts) else 0
            requiredPart = requiredParts[i] if i < len(requiredParts) else 0
            
            if currentPart > requiredPart:
                return True
            elif currentPart < requiredPart:
                return False
        
        return True
    
    def _createVirtualEnvironment(self) -> bool:
        """Create Python virtual environment."""
        print(f"\n🐍 Creating virtual environment: {self.config.virtualEnvName}")
        
        if self.venvPath.exists():
            print(f"⚠️  Virtual environment already exists at {self.venvPath}")
            response = input("Do you want to recreate it? (y/N): ").lower()
            if response == 'y':
                shutil.rmtree(self.venvPath)
            else:
                self.results.warnings.append("Using existing virtual environment")
                self.results.stepsCompleted.append("Virtual environment creation")
                return True
        
        try:
            subprocess.run([
                sys.executable, '-m', 'venv', str(self.venvPath)
            ], check=True, capture_output=True, text=True)
            
            self.results.stepsCompleted.append("Virtual environment creation")
            print("✅ Virtual environment created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.results.errors.append(f"Failed to create virtual environment: {e.stderr}")
            return False
    
    def _getPythonExecutable(self) -> str:
        """Get the Python executable path for the virtual environment."""
        if platform.system() == "Windows":
            return str(self.venvPath / "Scripts" / "python.exe")
        else:
            return str(self.venvPath / "bin" / "python")
    
    def _getPipExecutable(self) -> str:
        """Get the pip executable path for the virtual environment."""
        if platform.system() == "Windows":
            return str(self.venvPath / "Scripts" / "pip.exe")
        else:
            return str(self.venvPath / "bin" / "pip")
    
    def _installDependencies(self) -> bool:
        """Install Python dependencies."""
        print("\n📦 Installing dependencies...")
        
        pipExec = self._getPipExecutable()
        
        # Upgrade pip first
        try:
            subprocess.run([
                pipExec, 'install', '--upgrade', 'pip'
            ], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            self.results.warnings.append(f"Failed to upgrade pip: {e.stderr}")
        
        # Install requirements
        if self.config.requirementsFile and Path(self.config.requirementsFile).exists():
            try:
                subprocess.run([
                    pipExec, 'install', '-r', self.config.requirementsFile
                ], check=True, capture_output=True, text=True)
                
                self.results.stepsCompleted.append("Dependencies installation")
                print("✅ Dependencies installed successfully")
                
            except subprocess.CalledProcessError as e:
                self.results.errors.append(f"Failed to install dependencies: {e.stderr}")
                return False
        
        # Install dev requirements
        if self.config.devRequirementsFile and Path(self.config.devRequirementsFile).exists():
            try:
                subprocess.run([
                    pipExec, 'install', '-r', self.config.devRequirementsFile
                ], check=True, capture_output=True, text=True)
                
                self.results.stepsCompleted.append("Development dependencies installation")
                print("✅ Development dependencies installed successfully")
                
            except subprocess.CalledProcessError as e:
                self.results.warnings.append(f"Failed to install dev dependencies: {e.stderr}")
        
        return True
    
    def _setupAdditionalTools(self) -> bool:
        """Setup additional development tools."""
        if not self.config.additionalTools:
            return True
        
        print(f"\n🛠️  Setting up additional tools: {', '.join(self.config.additionalTools)}")
        
        for tool in self.config.additionalTools:
            if not self._installTool(tool):
                self.results.warnings.append(f"Failed to install tool: {tool}")
        
        self.results.stepsCompleted.append("Additional tools setup")
        return True
    
    def _installTool(self, tool: str) -> bool:
        """Install a specific development tool."""
        print(f"  Installing {tool}...")
        
        try:
            if tool == "pre-commit":
                return self._installPreCommit()
            elif tool == "black":
                return self._installCodeFormatter()
            elif tool == "flake8":
                return self._installLinter()
            elif tool == "pytest":
                return self._installTestingFramework()
            elif tool == "docker":
                return self._installDocker()
            elif tool == "nodejs":
                return self._installNodeJS()
            else:
                # Try to install via pip
                pipExec = self._getPipExecutable()
                subprocess.run([pipExec, 'install', tool], check=True, capture_output=True, text=True)
                print(f"    ✅ {tool} installed successfully")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"    ❌ Failed to install {tool}: {e.stderr}")
            return False
    
    def _installPreCommit(self) -> bool:
        """Install and setup pre-commit hooks."""
        try:
            pipExec = self._getPipExecutable()
            subprocess.run([pipExec, 'install', 'pre-commit'], check=True, capture_output=True, text=True)
            
            # Setup pre-commit hooks if .pre-commit-config.yaml exists
            if Path('.pre-commit-config.yaml').exists():
                preCommitExec = str(self.venvPath / "bin" / "pre-commit") if platform.system() != "Windows" else str(self.venvPath / "Scripts" / "pre-commit.exe")
                subprocess.run([preCommitExec, 'install'], check=True, capture_output=True, text=True)
            
            print("    ✅ pre-commit installed and configured")
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _installCodeFormatter(self) -> bool:
        """Install code formatting tools."""
        try:
            pipExec = self._getPipExecutable()
            subprocess.run([pipExec, 'install', 'black', 'isort'], check=True, capture_output=True, text=True)
            print("    ✅ Code formatters (black, isort) installed")
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _installLinter(self) -> bool:
        """Install linting tools."""
        try:
            pipExec = self._getPipExecutable()
            subprocess.run([pipExec, 'install', 'flake8', 'pylint'], check=True, capture_output=True, text=True)
            print("    ✅ Linters (flake8, pylint) installed")
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _installTestingFramework(self) -> bool:
        """Install testing framework."""
        try:
            pipExec = self._getPipExecutable()
            subprocess.run([pipExec, 'install', 'pytest', 'pytest-cov'], check=True, capture_output=True, text=True)
            print("    ✅ Testing framework (pytest) installed")
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _installDocker(self) -> bool:
        """Install Docker (platform-specific)."""
        system = platform.system()
        if system == "Darwin":  # macOS
            print("    ℹ️  Please install Docker Desktop for macOS manually")
            return True
        elif system == "Windows":
            print("    ℹ️  Please install Docker Desktop for Windows manually")
            return True
        elif system == "Linux":
            print("    ℹ️  Please install Docker for Linux manually")
            return True
        return False
    
    def _installNodeJS(self) -> bool:
        """Install Node.js (platform-specific)."""
        system = platform.system()
        if system == "Darwin":  # macOS
            print("    ℹ️  Please install Node.js via Homebrew: brew install node")
            return True
        elif system == "Windows":
            print("    ℹ️  Please install Node.js from https://nodejs.org/")
            return True
        elif system == "Linux":
            print("    ℹ️  Please install Node.js via package manager")
            return True
        return False
    
    def _setupEnvironmentVariables(self) -> bool:
        """Setup environment variables."""
        if not self.config.environmentVariables:
            return True
        
        print("\n🔧 Setting up environment variables...")
        
        envFile = self.projectPath / '.env'
        envContent = []
        
        for key, value in self.config.environmentVariables.items():
            envContent.append(f"{key}={value}")
        
        try:
            with open(envFile, 'w') as f:
                f.write('\n'.join(envContent))
            
            self.results.stepsCompleted.append("Environment variables setup")
            print("✅ Environment variables configured")
            return True
            
        except Exception as e:
            self.results.errors.append(f"Failed to setup environment variables: {str(e)}")
            return False
    
    def _runPostSetupCommands(self) -> bool:
        """Run post-setup commands."""
        if not self.config.postSetupCommands:
            return True
        
        print("\n⚡ Running post-setup commands...")
        
        for command in self.config.postSetupCommands:
            try:
                print(f"  Running: {command}")
                subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
                print(f"    ✅ Command completed: {command}")
            except subprocess.CalledProcessError as e:
                self.results.warnings.append(f"Post-setup command failed: {command} - {e.stderr}")
        
        self.results.stepsCompleted.append("Post-setup commands")
        return True
    
    def _generateSetupSummary(self) -> None:
        """Generate setup summary."""
        print("\n" + "="*60)
        print("SETUP SUMMARY")
        print("="*60)
        print(f"Project: {self.config.projectName}")
        print(f"Virtual Environment: {self.venvPath}")
        print(f"Python Version: {platform.python_version()}")
        print(f"Setup Time: {self.results.setupTime:.2f} seconds")
        
        print(f"\nSteps Completed ({len(self.results.stepsCompleted)}):")
        for step in self.results.stepsCompleted:
            print(f"  ✅ {step}")
        
        if self.results.warnings:
            print(f"\nWarnings ({len(self.results.warnings)}):")
            for warning in self.results.warnings:
                print(f"  ⚠️  {warning}")
        
        if self.results.errors:
            print(f"\nErrors ({len(self.results.errors)}):")
            for error in self.results.errors:
                print(f"  ❌ {error}")
        
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("1. Activate the virtual environment:")
        if platform.system() == "Windows":
            print(f"   {self.venvPath}\\Scripts\\activate")
        else:
            print(f"   source {self.venvPath}/bin/activate")
        
        print("2. Verify installation:")
        print("   python --version")
        print("   pip list")
        
        if self.config.gitRepo:
            print("3. Clone the repository:")
            print(f"   git clone {self.config.gitRepo}")
        
        print("4. Start developing! 🚀")

def createDefaultConfig() -> SetupConfig:
    """Create a default configuration."""
    return SetupConfig(
        projectName="MyProject",
        pythonVersion="3.8",
        virtualEnvName="venv",
        requirementsFile="requirements.txt",
        devRequirementsFile="requirements-dev.txt",
        gitRepo=None,
        additionalTools=["pre-commit", "black", "flake8", "pytest"],
        postSetupCommands=[],
        environmentVariables={
            "PYTHONPATH": ".",
            "DEBUG": "True"
        }
    )

def loadConfig(configFile: str) -> SetupConfig:
    """Load configuration from JSON file."""
    try:
        with open(configFile, 'r') as f:
            data = json.load(f)
        
        return SetupConfig(
            projectName=data.get('projectName', 'MyProject'),
            pythonVersion=data.get('pythonVersion', '3.8'),
            virtualEnvName=data.get('virtualEnvName', 'venv'),
            requirementsFile=data.get('requirementsFile', 'requirements.txt'),
            devRequirementsFile=data.get('devRequirementsFile'),
            gitRepo=data.get('gitRepo'),
            additionalTools=data.get('additionalTools', []),
            postSetupCommands=data.get('postSetupCommands', []),
            environmentVariables=data.get('environmentVariables', {})
        )
    except Exception as e:
        print(f"Error loading config: {e}")
        return createDefaultConfig()

def createConfigTemplate() -> None:
    """Create a configuration template file."""
    config = createDefaultConfig()
    
    template = {
        "projectName": "MyProject",
        "pythonVersion": "3.8",
        "virtualEnvName": "venv",
        "requirementsFile": "requirements.txt",
        "devRequirementsFile": "requirements-dev.txt",
        "gitRepo": "https://github.com/username/repo.git",
        "additionalTools": ["pre-commit", "black", "flake8", "pytest"],
        "postSetupCommands": [
            "echo 'Setup complete!'",
            "python -c 'print(\"Hello, World!\")'"
        ],
        "environmentVariables": {
            "PYTHONPATH": ".",
            "DEBUG": "True",
            "DATABASE_URL": "sqlite:///dev.db"
        }
    }
    
    with open('setup-config.json', 'w') as f:
        json.dump(template, f, indent=2)
    
    print("✅ Configuration template created: setup-config.json")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Environment Setup Automation for Local Development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python envSetupAutomation.py
  python envSetupAutomation.py --config my-config.json
  python envSetupAutomation.py --create-template
  python envSetupAutomation.py --project-name "MyApp" --python-version "3.9"
        """
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration JSON file'
    )
    
    parser.add_argument(
        '--create-template',
        action='store_true',
        help='Create a configuration template file'
    )
    
    parser.add_argument(
        '--project-name',
        help='Project name'
    )
    
    parser.add_argument(
        '--python-version',
        help='Required Python version'
    )
    
    parser.add_argument(
        '--virtual-env-name',
        help='Virtual environment name'
    )
    
    parser.add_argument(
        '--requirements-file',
        help='Requirements file path'
    )
    
    parser.add_argument(
        '--tools',
        nargs='+',
        help='Additional tools to install'
    )
    
    args = parser.parse_args()
    
    if args.create_template:
        createConfigTemplate()
        return 0
    
    # Load or create configuration
    if args.config:
        config = loadConfig(args.config)
    else:
        config = createDefaultConfig()
    
    # Override with command line arguments
    if args.project_name:
        config.projectName = args.project_name
    if args.python_version:
        config.pythonVersion = args.python_version
    if args.virtual_env_name:
        config.virtualEnvName = args.virtual_env_name
    if args.requirements_file:
        config.requirementsFile = args.requirements_file
    if args.tools:
        config.additionalTools = args.tools
    
    # Run setup
    setup = EnvironmentSetupAutomation(config)
    result = setup.setupEnvironment()
    
    if result.success:
        print(f"\n🎉 {result.message}")
        return 0
    else:
        print(f"\n❌ {result.message}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
