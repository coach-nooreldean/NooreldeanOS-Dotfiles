#!/bin/bash

export LC_ALL=C

if command -v nvidia-smi &> /dev/null; then
    IFS=',' read -r UTIL MEM_USED MEM_TOTAL TEMP <<< \
    "$(nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits | tr -d ' ')"
else
    # AMD GPU fallback
    UTIL=$(cat /sys/class/drm/card0/device/gpu_busy_percent 2>/dev/null || echo "0")
    TEMP=$(cat /sys/class/hwmon/hwmon*/temp1_input 2>/dev/null | head -n 1 | awk '{print int($1/1000)}' || echo "0")
    MEM_USED="?"
    MEM_TOTAL="?"
fi

UTIL=$(echo "$UTIL" | tr -d ',')
MEM_USED=$(echo "$MEM_USED" | tr -d ',')
MEM_TOTAL=$(echo "$MEM_TOTAL" | tr -d ',')
TEMP=$(echo "$TEMP" | tr -d ',')

echo "{\"text\":\"󰢮 ${UTIL}%\", \"tooltip\":\"Memory: ${MEM_USED}/${MEM_TOTAL}MiB\\nTemperature: ${TEMP}°C\"}"
