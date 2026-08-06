#!/bin/bash
# Safe screenshot script — always restores opacity even if hyprshot fails/cancels

MODE="${1:-region}"  # "region" or "output"

# Save original opacity and set to 1.0 for clean screenshot
hyprctl keyword decoration:inactive_opacity 1.0

# Ensure opacity is always restored, even on failure or cancellation
trap 'hyprctl keyword decoration:inactive_opacity 0.85' EXIT

hyprshot -m "$MODE"
