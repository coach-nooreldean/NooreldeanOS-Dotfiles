#!/bin/bash

read USED AVAIL PERCENT <<< $(df -h / | awk 'NR==2{print $3,$4,$5}')

echo "{\"text\":\"󰋊 ${AVAIL}\",\"tooltip\":\"Used: ${USED}\nFree: ${AVAIL}\nUsage: ${PERCENT}\"}"
