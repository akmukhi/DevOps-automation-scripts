#!/usr/bin/env python3
"""
Code Quality Checker for Python Projects
A comprehensive tool to analyze code quality, style, and potential issues.
"""

import os
import sys
import ast
import argparse
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import importlib.util

@dataclass
class CodeIssue:
    """Represents a code quality issue found during analysis."""
    file_path: str
    line_number: int
    issue_type: str
    severity: str  # 'error', 'warning', 'info'
    message: str
    suggestion: Optional[str] = None

@dataclass
class CodeMetrics:
    """Represents code metrics for a file or project."""
    lines_of_code: int
    comment_lines: int
    blank_lines: int
    function_count: int
    class_count: int
    complexity: float
    maintainability_index: float

@dataclass
class QualityReport:
    """Complete quality report for a project."""
    project_path: str
    total_files: int
    total_issues: int
    metrics: CodeMetrics
    issues: List[CodeIssue]
    summary: Dict[str, Any]

class CodeQualityChecker:
    """Main class for code quality analysis."""
    
    def __init__(self, project_path: str, config: Optional[Dict] = None):
        self.project_path = Path(project_path)
        self.config = config or self._get_default_config()
        self.issues: List[CodeIssue] = []
        self.metrics = defaultdict(lambda: CodeMetrics(0, 0, 0, 0, 0, 0.0, 0.0))
        
    def _get_default_config(self) -> Dict:
        """Get default configuration for the checker."""
        return {
            'max_line_length': 79,
            'max_function_complexity': 10,
            'max_class_complexity': 20,
            'ignore_patterns': [
                '__pycache__',
                '.git',
                '.venv',
                'venv',
                'node_modules',
                '*.pyc',
                '*.pyo'
            ],
            'severity_weights': {
                'error': 3,
                'warning': 2,
                'info': 1
            }
        }
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if a file should be ignored based on patterns."""
        for pattern in self.config['ignore_patterns']:
            if pattern in str(file_path):
                return True
        return False
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []
        for root, dirs, files in os.walk(self.project_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore_file(Path(root) / d)]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    if not self._should_ignore_file(file_path):
                        python_files.append(file_path)
        
        return python_files
    
    def analyze_syntax(self, file_path: Path) -> List[CodeIssue]:
        """Check for syntax errors in Python files."""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ast.parse(content)
        except SyntaxError as e:
            issues.append(CodeIssue(
                file_path=str(file_path),
                line_number=e.lineno or 0,
                issue_type='syntax_error',
                severity='error',
                message=f"Syntax error: {e.msg}",
                suggestion="Fix the syntax error to make the code valid Python"
            ))
        except Exception as e:
            issues.append(CodeIssue(
                file_path=str(file_path),
                line_number=0,
                issue_type='parsing_error',
                severity='error',
                message=f"Failed to parse file: {str(e)}",
                suggestion="Check file encoding and content"
            ))
        
        return issues
    
    def check_line_length(self, file_path: Path) -> List[CodeIssue]:
        """Check for lines that exceed the maximum length."""
        issues = []
        max_length = self.config['max_line_length']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if len(line.rstrip('\n')) > max_length:
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            issue_type='line_too_long',
                            severity='warning',
                            message=f"Line {line_num} is {len(line.rstrip())} characters long (max {max_length})",
                            suggestion="Break the line into multiple lines or use line continuation"
                        ))
        except Exception as e:
            issues.append(CodeIssue(
                file_path=str(file_path),
                line_number=0,
                issue_type='file_read_error',
                severity='error',
                message=f"Could not read file: {str(e)}"
            ))
        
        return issues
    
    def analyze_complexity(self, file_path: Path) -> List[CodeIssue]:
        """Analyze code complexity using AST."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    if complexity > self.config['max_function_complexity']:
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type='high_complexity',
                            severity='warning',
                            message=f"Function '{node.name}' has complexity {complexity} (max {self.config['max_function_complexity']})",
                            suggestion="Consider breaking down the function into smaller, simpler functions"
                        ))
                
                elif isinstance(node, ast.ClassDef):
                    complexity = self._calculate_class_complexity(node)
                    if complexity > self.config['max_class_complexity']:
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type='high_class_complexity',
                            severity='warning',
                            message=f"Class '{node.name}' has complexity {complexity} (max {self.config['max_class_complexity']})",
                            suggestion="Consider splitting the class into multiple classes"
                        ))
        
        except Exception as e:
            issues.append(CodeIssue(
                file_path=str(file_path),
                line_number=0,
                issue_type='complexity_analysis_error',
                severity='error',
                message=f"Failed to analyze complexity: {str(e)}"
            ))
        
        return issues
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _calculate_class_complexity(self, node: ast.ClassDef) -> int:
        """Calculate complexity of a class."""
        complexity = 0
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                complexity += self._calculate_complexity(item)
        return complexity
    
    def check_naming_conventions(self, file_path: Path) -> List[CodeIssue]:
        """Check for PEP 8 naming convention violations."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.islower() and '_' not in node.name:
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type='naming_convention',
                            severity='warning',
                            message=f"Function '{node.name}' should use snake_case naming",
                            suggestion="Rename function to use snake_case (e.g., 'my_function')"
                        ))
                
                elif isinstance(node, ast.ClassDef):
                    if not node.name[0].isupper() or '_' in node.name:
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type='naming_convention',
                            severity='warning',
                            message=f"Class '{node.name}' should use PascalCase naming",
                            suggestion="Rename class to use PascalCase (e.g., 'MyClass')"
                        ))
                
                elif isinstance(node, ast.Name):
                    if isinstance(node.ctx, ast.Store):  # Variable assignment
                        if not node.id.islower() and '_' not in node.id and not node.id.isupper():
                            issues.append(CodeIssue(
                                file_path=str(file_path),
                                line_number=node.lineno,
                                issue_type='naming_convention',
                                severity='info',
                                message=f"Variable '{node.id}' should use snake_case naming",
                                suggestion="Rename variable to use snake_case (e.g., 'my_variable')"
                            ))
        
        except Exception as e:
            issues.append(CodeIssue(
                file_path=str(file_path),
                line_number=0,
                issue_type='naming_analysis_error',
                severity='error',
                message=f"Failed to analyze naming conventions: {str(e)}"
            ))
        
        return issues
    
    def calculate_metrics(self, file_path: Path) -> CodeMetrics:
        """Calculate various code metrics for a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
            blank_lines = sum(1 for line in lines if line.strip() == '')
            code_lines = total_lines - comment_lines - blank_lines
            
            # Parse AST for function and class counts
            tree = ast.parse(''.join(lines))
            function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
            class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            
            # Calculate complexity
            complexity = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity += self._calculate_complexity(node)
            
            # Calculate maintainability index (simplified)
            maintainability = max(0, 171 - 5.2 * complexity - 0.23 * code_lines - 16.2 * function_count)
            
            return CodeMetrics(
                lines_of_code=code_lines,
                comment_lines=comment_lines,
                blank_lines=blank_lines,
                function_count=function_count,
                class_count=class_count,
                complexity=complexity,
                maintainability_index=maintainability
            )
        
        except Exception:
            return CodeMetrics(0, 0, 0, 0, 0, 0.0, 0.0)
    
    def run_external_tools(self, file_path: Path) -> List[CodeIssue]:
        """Run external code quality tools if available."""
        issues = []
        
        # Try to run flake8 if available
        try:
            result = subprocess.run(
                ['flake8', str(file_path), '--format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return issues  # No issues found
            
            try:
                flake8_issues = json.loads(result.stdout)
                for issue in flake8_issues:
                    issues.append(CodeIssue(
                        file_path=issue['filename'],
                        line_number=issue['line_number'],
                        issue_type='flake8',
                        severity='warning' if issue['code'].startswith('W') else 'error',
                        message=f"{issue['code']}: {issue['text']}"
                    ))
            except json.JSONDecodeError:
                # Parse text output if JSON fails
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split(':')
                        if len(parts) >= 3:
                            issues.append(CodeIssue(
                                file_path=parts[0],
                                line_number=int(parts[1]),
                                issue_type='flake8',
                                severity='warning',
                                message=':'.join(parts[2:]).strip()
                            ))
        
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass  # flake8 not available or failed
        
        return issues
    
    def analyze_file(self, file_path: Path) -> List[CodeIssue]:
        """Perform comprehensive analysis of a single file."""
        issues = []
        
        # Basic syntax check
        issues.extend(self.analyze_syntax(file_path))
        
        # Style checks
        issues.extend(self.check_line_length(file_path))
        issues.extend(self.check_naming_conventions(file_path))
        
        # Complexity analysis
        issues.extend(self.analyze_complexity(file_path))
        
        # External tools
        issues.extend(self.run_external_tools(file_path))
        
        # Calculate metrics
        self.metrics[str(file_path)] = self.calculate_metrics(file_path)
        
        return issues
    
    def run_analysis(self) -> QualityReport:
        """Run complete analysis of the project."""
        print(f"Analyzing code quality in: {self.project_path}")
        
        python_files = self.find_python_files()
        print(f"Found {len(python_files)} Python files to analyze")
        
        total_issues = 0
        all_issues = []
        
        for file_path in python_files:
            print(f"Analyzing: {file_path}")
            file_issues = self.analyze_file(file_path)
            all_issues.extend(file_issues)
            total_issues += len(file_issues)
        
        # Aggregate metrics
        total_metrics = CodeMetrics(0, 0, 0, 0, 0, 0.0, 0.0)
        for metrics in self.metrics.values():
            total_metrics.lines_of_code += metrics.lines_of_code
            total_metrics.comment_lines += metrics.comment_lines
            total_metrics.blank_lines += metrics.blank_lines
            total_metrics.function_count += metrics.function_count
            total_metrics.class_count += metrics.class_count
            total_metrics.complexity += metrics.complexity
        
        if len(self.metrics) > 0:
            total_metrics.maintainability_index = sum(
                m.maintainability_index for m in self.metrics.values()
            ) / len(self.metrics)
        
        # Generate summary
        summary = {
            'total_files': len(python_files),
            'total_issues': total_issues,
            'issues_by_severity': defaultdict(int),
            'issues_by_type': defaultdict(int),
            'quality_score': self._calculate_quality_score(all_issues, total_metrics)
        }
        
        for issue in all_issues:
            summary['issues_by_severity'][issue.severity] += 1
            summary['issues_by_type'][issue.issue_type] += 1
        
        return QualityReport(
            project_path=str(self.project_path),
            total_files=len(python_files),
            total_issues=total_issues,
            metrics=total_metrics,
            issues=all_issues,
            summary=dict(summary)
        )
    
    def _calculate_quality_score(self, issues: List[CodeIssue], metrics: CodeMetrics) -> float:
        """Calculate an overall quality score (0-100)."""
        if not issues:
            return 100.0
        
        # Calculate penalty based on issues
        total_penalty = 0
        for issue in issues:
            weight = self.config['severity_weights'].get(issue.severity, 1)
            total_penalty += weight
        
        # Calculate penalty based on metrics
        complexity_penalty = min(metrics.complexity * 2, 20)
        maintainability_penalty = max(0, 50 - metrics.maintainability_index)
        
        total_penalty += complexity_penalty + maintainability_penalty
        
        # Convert to score (0-100)
        score = max(0, 100 - total_penalty)
        return round(score, 2)
    
    def print_report(self, report: QualityReport, output_format: str = 'text'):
        """Print the quality report in the specified format."""
        if output_format == 'json':
            print(json.dumps(asdict(report), indent=2))
            return
        
        # Text format
        print("\n" + "="*60)
        print("CODE QUALITY REPORT")
        print("="*60)
        print(f"Project: {report.project_path}")
        print(f"Analysis Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Files: {report.total_files}")
        print(f"Total Issues: {report.total_issues}")
        print(f"Quality Score: {report.summary['quality_score']}/100")
        
        print("\n" + "-"*40)
        print("METRICS")
        print("-"*40)
        print(f"Lines of Code: {report.metrics.lines_of_code}")
        print(f"Comment Lines: {report.metrics.comment_lines}")
        print(f"Blank Lines: {report.metrics.blank_lines}")
        print(f"Functions: {report.metrics.function_count}")
        print(f"Classes: {report.metrics.class_count}")
        print(f"Total Complexity: {report.metrics.complexity}")
        print(f"Avg Maintainability Index: {report.metrics.maintainability_index:.2f}")
        
        print("\n" + "-"*40)
        print("ISSUES BY SEVERITY")
        print("-"*40)
        for severity, count in report.summary['issues_by_severity'].items():
            print(f"{severity.title()}: {count}")
        
        print("\n" + "-"*40)
        print("ISSUES BY TYPE")
        print("-"*40)
        for issue_type, count in report.summary['issues_by_type'].items():
            print(f"{issue_type.replace('_', ' ').title()}: {count}")
        
        if report.issues:
            print("\n" + "-"*40)
            print("DETAILED ISSUES")
            print("-"*40)
            
            # Group issues by file
            issues_by_file = defaultdict(list)
            for issue in report.issues:
                issues_by_file[issue.file_path].append(issue)
            
            for file_path, file_issues in issues_by_file.items():
                print(f"\n{file_path}:")
                for issue in sorted(file_issues, key=lambda x: x.line_number):
                    print(f"  Line {issue.line_number}: [{issue.severity.upper()}] {issue.message}")
                    if issue.suggestion:
                        print(f"    Suggestion: {issue.suggestion}")

def main():
    """Main entry point for the code quality checker."""
    parser = argparse.ArgumentParser(
        description="Python Code Quality Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python code_quality_checker.py /path/to/project
  python code_quality_checker.py . --format json
  python code_quality_checker.py /path/to/project --max-line-length 100
        """
    )
    
    parser.add_argument(
        'project_path',
        help='Path to the Python project to analyze'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--max-line-length',
        type=int,
        default=79,
        help='Maximum line length (default: 79)'
    )
    
    parser.add_argument(
        '--max-function-complexity',
        type=int,
        default=10,
        help='Maximum function complexity (default: 10)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration JSON file'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = None
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config file: {e}")
            return 1
    
    # Override config with command line arguments
    if config is None:
        config = {}
    
    config['max_line_length'] = args.max_line_length
    config['max_function_complexity'] = args.max_function_complexity
    
    # Run analysis
    try:
        checker = CodeQualityChecker(args.project_path, config)
        report = checker.run_analysis()
        checker.print_report(report, args.format)
        
        # Return appropriate exit code
        return 0 if report.total_issues == 0 else 1
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())