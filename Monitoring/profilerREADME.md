# Python Profiler

## Overview

The `profiler.py` script is a comprehensive Python profiling tool that analyzes the performance of Python scripts and functions. It provides detailed metrics including execution time, memory usage, and function call statistics to help identify performance bottlenecks and optimize code.

## Features

- 🔍 **Complete Module Profiling**: Profile entire Python modules
- 🎯 **Function-Specific Profiling**: Profile individual functions within modules
- 📊 **Memory Usage Tracking**: Monitor memory consumption during execution
- ⏱️ **Execution Time Measurement**: Precise timing of code execution
- 📈 **Detailed Statistics**: Comprehensive call statistics and performance metrics
- 💾 **Results Export**: Save profiling results to files
- 🛠️ **Command Line Interface**: Easy-to-use CLI with various options

## Prerequisites

- **Python 3.6+**: Required for type hints and modern features
- **psutil**: For memory usage tracking
- **cProfile**: Built-in Python profiling module
- **pstats**: Built-in Python statistics module

## Installation

1. **Install required dependencies**:
   ```bash
   pip install psutil
   ```

2. **Make the script executable** (optional):
   ```bash
   chmod +x profiler.py
   ```

## Usage

### Basic Usage

1. **Profile an entire Python module**:
   ```bash
   python profiler.py target_script.py
   ```

2. **Profile a specific function**:
   ```bash
   python profiler.py target_script.py -f function_name
   ```

3. **Save results to a file**:
   ```bash
   python profiler.py target_script.py -o results.txt
   ```

4. **Limit detailed output**:
   ```bash
   python profiler.py target_script.py -l 10
   ```

### Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `targetFile` | Python file to profile (required) | `script.py` |
| `-o, --output` | Output file for profiling results | `-o results.txt` |
| `-f, --function` | Specific function to profile | `-f my_function` |
| `-l, --limit` | Limit number of lines in detailed output (default: 20) | `-l 15` |

### Example Output
