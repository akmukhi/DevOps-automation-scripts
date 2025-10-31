#!/bin/bash

#Server Performance

#Color
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'

print_header(){
    echo -e "\n${CYAN}======================================="
    echo -e "${CYAN}$1"
    echo -e "${CYAN}========================================="

}

print_subheader(){
    echo -e "\n${BLUE}------- $1 --------"
}

clear

echo -e "${GREEN} SERVER PERFORMANCE STATS"
echo -e "Generated: $(date '+%Y-%m-%d %H:%M:%S)"

#System info
print_header "SYSTEM INFO"

echo -e "Hostname: ${YELLOW}$(hostname)"
echo -e "OS: ${YELLOW}$(grep PRETTY_NAME /etc/os-release 2>/dev/null | cut -d'"' -f2 || uname -s)"
echo -e "Kernel: ${YELLOW}$(uname -r)"
echo -e "Architecture: ${YELLOW}$(uname -m)"
echo -e "Uptime: ${YELLOW}$(uptime -p 2>/dev/null || uptime | awk -F'up ' '{print $2}' | awk -F',' '{print $1}')"


#CPU Usage
print_header "CPU Information"

cpu-model=$(grep "model name" /proc/cpuinfo | head -1 | cut -d':' -f2 | xargs)
cpu_cores=$(grep -c "^processor" /proc/cpuinfo)
echo -e "CPU Model: ${YELLOW}$cpu_model"
echo -e "CPU Cores: ${YELLOW}$cpu_cores"

#Calculate total CPU usage
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
cpu_idle=$(top -bn1 | grep "Cpu(s)" | awk '{print $8}' | cut -d'%' -f1)

echo -e "CPU Usage: ${YELLOW}${cpu_usage}%"
echo -e "CPU Idle: ${GREEN}${cpu_idle}%"

#Load Average
load_avg=$(uptime | awk -F'load average:' '{print $2}' | xargs)
echo -e "Load Average: ${YELLOW}$load_avg"

#Memory Usage
print_header "MEMORY USAGE"

mem_total=$(free -h | awk '/^Mem:/ {print $2}')
mem_used=$(free -h | awk '/^Mem:/ {print $3}')
mem_free=$(free -h | awk '/^Mem:/ {print $4}')
mem_available=$(free -h | awk '/^Mem:/ {print $7}')

mem_total_mb=$(free -h | awk '/^Mem:/ {print $2}')
mem_used_mb=$(free -h | awk '/^Mem:/ {print $3}')
mem_percent=$(awk "BEGIN {printf \"%.2f\", ($mem_used_mb/$mem_total_mb)*100})

echo -e "Total Memory: ${YELLOW}$mem_total"
echo -e "Used Memory: ${RED}$mem_used (${RED}${mem_percent}%)"
echo -e "Free Memory: ${GREEN}$mem_free"
echo -e "Available Memory: ${GREEN}$mem_available"

#Disk Usage
print_header "DISK USAGE"

df -h --output=source,fstype,size,used,avail,pcent,target -x tmpfs -x devtmpfs 2>/dev/null | while read -r line; do
    if echo "$line" | grep -q "Filesystem"; then
        echo -e "${YELLOW}$line"
    else
        percent=$(echo "$line" | awk '{print $(NF-1)}' | tr -d '%')
        if [ "$percent -ge 75 ] 2>/dev/null; then
            echo -e "${RED}$line"
        elif [ "$percent" -ge 75 ] 2>/dev/null; then
            echo -e "${YELLOW}$line"
        else
            echo -e "${GREEN}$line"
        fi
    fi
done

#Processes by CPU usage
print_header "Top 5 Proccesses sorted by CPU Usage"

echo -e "${YELLOW}%-10s %-10s %-10s %-s" "PID" "USER" "MEMORY" "COMMAND"
ps aux --sort=-%mem | head -6 | tail -5 | awk '{printf "%-10s %-10s %-10s %-10s %s\n", $2, $1, $4, $11}'


#Process Count
print_header "Process Information"

total_processes=$(ps aux | wc -l)
running_processes=$(ps aux | grep -c " R ")
sleeping_processes=$(ps aux | grep -c " S ")
zombie_processes=$(ps aux | grep -c " Z ")

echo -e "Total Processes: ${YELLOW}$total_processes"
echo -e "Running: ${GREEN}$running_processes | Sleeping: ${BLUE}$sleeping_processes | Zombie: ${RED}$zombie_processes"


#Footer

echo -e "\n${GREEN} Analysis Complete"


