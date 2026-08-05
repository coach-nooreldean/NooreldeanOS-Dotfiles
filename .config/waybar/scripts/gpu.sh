#!/bin/bash

export LC_ALL=C

IFS=',' read -r UTIL MEM_USED MEM_TOTAL TEMP <<< \
"$(nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits | tr -d ' ')"

UTIL=$(echo "$UTIL" | tr -d ',')
MEM_USED=$(echo "$MEM_USED" | tr -d ',')
MEM_TOTAL=$(echo "$MEM_TOTAL" | tr -d ',')
TEMP=$(echo "$TEMP" | tr -d ',')

echo "{\"text\":\"󰢮 ${UTIL}%\", \"tooltip\":\"Memory: ${MEM_USED}/${MEM_TOTAL}MiB\\nTemperature: ${TEMP}°C\"}"
