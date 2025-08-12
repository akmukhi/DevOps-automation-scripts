# Automation Log Analysis Script

## Overview

The `automation_log_analysis.sh` script is a real-time log monitoring and analysis tool designed for DevOps environments. It automatically detects log files in a specified directory, monitors them for changes, and provides real-time analysis of error patterns, failures, and warnings.

## Features

- 🔍 **Real-time Monitoring**: Continuously monitors log files for changes
- 📊 **Automatic Analysis**: Counts errors, failures, and warnings in log files
- 📈 **Live Updates**: Displays the last 10 lines when changes are detected
- 🎯 **Multiple Log Support**: Automatically detects and processes `.log` files
- ⚡ **Resource Efficient**: Uses file modification timestamps for change detection
- 🛑 **Graceful Exit**: Handles Ctrl+C interruption with proper cleanup

## Prerequisites

- **Operating System**: Linux (uses `stat -c %Y` command)
- **Shell**: Bash
- **Permissions**: Read access to log files
- **Directory Structure**: Log files should be in a `logs/` subdirectory

## Directory Structure

```
Monitoring/
├── automation_log_analysis.sh
├── README.md
└── Logs/
    └── *.log files
```

## Script Content

```bash
#!/bin/bash

#Log file
currentDirectory=$(pwd)
logDir="$currentDirectory/logs"
logFile=""

analyzeLog() {
    echo "Analyzing Logs Please find Summary Below:"
    echo "==========================================="

    #Number of errors 
    errors=$(grep -c -Ei "Error" "$logFile")

    #Number of Failures
    failed=$(grep -c -Ei "Failed" "$logFile")

    #Number of Warnings
    warning=$(grep -c -Ei "Warning" "$logFile")

    #Printing the results
    echo "Log File Name: $(basename "$logFile")"
    echo "Total Number of Lines: $(wc -l < "$logFile")"
    echo "Total Number of Errors: $errors"
    echo "Total Number of Failed Instances: $failed"
    echo "Total Number of Warnings: $warning"

    echo "=============================================="   
}

selectLogFile() {
    local logFilePath=$1
    echo "Now Monitoring the Log File: $logFilePath"

    if [ ! -f "$logFilePath" ]; then
        echo "Error: Log File Not Found"
        exit 1
    fi

    local modificationTime=$(stat -c %Y "$logFilePath")

    while true; do

        #Checking if the log file exists
        local currentModificationTime=$(stat -c %Y "$logFilePath")
        if [ $currentModificationTime -gt $modificationTime ]; then
            clear
            #only display the last 10 lines
            tail -n 10 "$logFilePath"
            #Run function
            logFile="$logFilePath"
            analyzeLog
            #update the modification time
            modificationTime=$currentModificationTime
        fi

        sleep 2
    done

    #Setting trap to prevent resource overages

}
trap 'echo -e "\nNow Exiting Log Analyzer"; exit 0' SIGINT

echo "Listing All Found Log Files in Appropriate Directory"
for logFile in "$logDir"/*.log; do
    if [[ -f "$logFile" ]]; then
        #Modification time
        modificationTime=$(stat -c %Y "$logFile")
        echo "Found Log File: "$logFile"
        echo "Log File Size: $(du -h "$logFile" | cut -f1)"
        echo "Log Last Modified: "$modificationTime"
        echo "Log Line Count: $(wc -l < "$logFile")"
        selectLogFile "$logFile"
    fi
done
```

## Script Breakdown

### Global Variables
- `currentDirectory`: Gets the current working directory
- `logDir`: Points to the `logs/` subdirectory
- `logFile`: Global variable to store the current log file path

### Functions

#### `analyzeLog()`
Performs comprehensive log analysis:
- Counts errors using `grep -c -Ei "Error"`
- Counts failures using `grep -c -Ei "Failed"`
- Counts warnings using `grep -c -Ei "Warning"`
- Displays summary statistics including total lines

#### `selectLogFile(logFilePath)`
Handles real-time monitoring:
- Validates file existence
- Tracks file modification timestamps
- Monitors for changes every 2 seconds
- Updates display when changes are detected
- Calls analysis function when changes occur

### Main Execution Flow
1. Sets up signal trap for graceful exit
2. Scans `logs/` directory for `.log` files
3. Displays file information for each found log
4. Starts monitoring the first log file
5. Continuously monitors for changes

## Usage

### Basic Usage

1. **Navigate to the Monitoring directory**:
   ```bash
   cd Monitoring
   ```

2. **Make the script executable** (if not already):
   ```bash
   chmod +x automation_log_analysis.sh
   ```

3. **Run the script**:
   ```bash
   ./automation_log_analysis.sh
   ```

### Expected Output

The script will:
1. List all found log files with their details
2. Start monitoring the first log file
3. Display real-time updates when changes occur
4. Show analysis summary including:
   - Total number of lines
   - Error count
   - Failure count
   - Warning count

### Example Output

```
Listing All Found Log Files in Appropriate Directory
Found Log File: /path/to/logs/application.log
Log File Size: 2.5M
Log Last Modified: 1703123456
Log Line Count: 15420
Now Monitoring the Log File: /path/to/logs/application.log

[When changes are detected, the screen clears and shows:]
[Last 10 lines of the log file]

Analyzing Logs Please find Summary Below:
===========================================
Log File Name: application.log
Total Number of Lines: 15425
Total Number of Errors: 15
Total Number of Failed Instances: 3
Total Number of Warnings: 8
==============================================
```

## Configuration

### Log Directory
The script automatically looks for log files in:
```bash
logDir="$currentDirectory/logs"
```

### Monitoring Interval
The script checks for changes every 2 seconds:
```bash
sleep 2
```

### Display Lines
Shows the last 10 lines when changes are detected:
```bash
tail -n 10 "$logFilePath"
```

### Analysis Patterns
The script searches for these patterns (case-insensitive):
- **Errors**: Lines containing "Error"
- **Failures**: Lines containing "Failed"
- **Warnings**: Lines containing "Warning"

## Error Handling

- **File Not Found**: Script exits with error message if log file is missing
- **Interruption**: Graceful exit on Ctrl+C with cleanup message
- **No Log Files**: Script will not start if no `.log` files are found

## Limitations

1. **Single File Monitoring**: Currently monitors only the first log file found
2. **Linux Only**: Uses Linux-specific `stat` command
3. **Case Sensitivity**: Analysis is case-insensitive but pattern-specific
4. **Real-time Only**: No historical analysis, only current state

## Troubleshooting

### Common Issues

1. **"Log File Not Found"**
   - Ensure log files exist in the `logs/` directory
   - Check file permissions

2. **No Output**
   - Verify log files have `.log` extension
   - Check if directory structure is correct

3. **Permission Denied**
   - Ensure script has read access to log files
   - Run with appropriate permissions

4. **Script Not Working on macOS**
   - The script uses Linux-specific `stat -c %Y`
   - For macOS, change to `stat -f %m`

### Debug Mode

To debug issues, you can add `set -x` at the beginning of the script to enable debug output:

```bash
#!/bin/bash
set -x  # Enable debug mode
# ... rest of script
```

### Testing the Script

1. **Create a test log file**:
   ```bash
   mkdir -p logs
   echo "This is a test log entry" > logs/test.log
   echo "Error: Something went wrong" >> logs/test.log
   echo "Warning: This is a warning" >> logs/test.log
   ```

2. **Run the script**:
   ```bash
   ./automation_log_analysis.sh
   ```

3. **Add more entries to test real-time monitoring**:
   ```bash
   echo "Failed: Operation failed" >> logs/test.log
   ```

## Future Enhancements

- [ ] Support for multiple log file monitoring
- [ ] Cross-platform compatibility (macOS/Windows)
- [ ] Configurable analysis patterns
- [ ] Historical trend analysis
- [ ] Email/Slack notifications for critical errors
- [ ] Web interface for monitoring
- [ ] Log rotation support
- [ ] Customizable monitoring intervals
- [ ] Export analysis results to files

## Contributing

Feel free to submit issues and enhancement requests. When contributing:

1. Test on Linux environments
2. Maintain backward compatibility
3. Update documentation for new features
4. Follow bash scripting best practices

## License

This script is part of the DevOps automation scripts collection. See the main LICENSE file for details.

## Support

For issues, questions, or contributions:
1. Check the troubleshooting section above
2. Review the script content for understanding
3. Test with sample log files
4. Submit issues with detailed error messages and system information
