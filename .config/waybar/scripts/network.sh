#!/bin/bash

IFACE=$(ip route | awk '/default/ {print $5}')

if [[ -z "$IFACE" ]]; then
    echo '{"text":"󰁅 0 B/s 󰁝 0 B/s"}'
    exit
fi

RX=$(cat /sys/class/net/$IFACE/statistics/rx_bytes 2>/dev/null || echo 0)
TX=$(cat /sys/class/net/$IFACE/statistics/tx_bytes 2>/dev/null || echo 0)

STATE=/tmp/waybar_net

if [[ -f "$STATE" ]]; then
    read OLD_RX OLD_TX OLD_TIME < "$STATE"
else
    echo "$RX $TX $(date +%s)" > "$STATE"
    echo '{"text":"󰁅 0 KB/s 󰁝 0 KB/s"}'
    exit
fi

NOW=$(date +%s)
DIFF=$((NOW-OLD_TIME))
((DIFF==0)) && DIFF=1

DOWN=$(((RX-OLD_RX)/DIFF))
UP=$(((TX-OLD_TX)/DIFF))

echo "$RX $TX $NOW" > "$STATE"

human() {
    if (( $1 > 1048576 )); then
        printf "%.1f MB/s" "$(echo "$1/1048576" | bc -l)"
    elif (( $1 > 1024 )); then
        printf "%.0f KB/s" "$(echo "$1/1024" | bc -l)"
    else
        printf "%d B/s" "$1"
    fi
}

echo "{\"text\":\"󰁅 $(human $DOWN) 󰁝 $(human $UP)\"}"
