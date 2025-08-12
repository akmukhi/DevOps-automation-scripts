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