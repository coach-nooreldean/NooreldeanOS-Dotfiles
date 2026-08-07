#!/bin/bash

# Ensure LOG_FILE is defined (fallback to /tmp if not)
LOG_FILE="${LOG_FILE:-/tmp/nooreldeanos-install.log}"

# Create log file and its directory if they don't exist
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

# Logging Functions
log_msg() {
    local color="$1"
    local prefix="$2"
    local message="$3"
    
    # Print to console with color
    echo -e "${color}${prefix}${message}\e[0m"
    
    # Strip color and print to log file
    echo "$(date '+%Y-%m-%d %H:%M:%S') ${prefix}${message}" >> "$LOG_FILE"
}

log_info() {
    log_msg "\e[34m" "ℹ️ " "$1"
}

log_success() {
    log_msg "\e[32m" "✅ " "$1"
}

log_warning() {
    log_msg "\e[33m" "⚠️ " "$1"
}

log_error() {
    log_msg "\e[31m" "❌ " "$1"
}

log_step() {
    log_msg "\e[1;36m" "🚀 " "$1"
}

# Used to log user input prompts
log_prompt() {
    log_msg "\e[35m" "👉 " "$1"
}
