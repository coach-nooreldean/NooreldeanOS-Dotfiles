#!/usr/bin/env python3
import json
import os
import subprocess
from datetime import datetime

cache_file = "/tmp/prayer_timings.json"

if not os.path.exists(cache_file):
    subprocess.run(["notify-send", "-a", "Prayer", "-t", "5000", "🕋 Prayer Times", "No prayer data available yet. Please wait for the module to fetch it."])
    exit()

try:
    with open(cache_file, "r") as f:
        data = json.load(f)
except:
    exit()

timings = data.get("timings", {})
prayer_names = ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
icons = ['🌅', '☀️', '🌤️', '⛅', '🌇', '🌙']

options = []
for idx, name in enumerate(prayer_names):
    time_str = timings.get(name, "")
    if time_str:
        time_obj = datetime.strptime(time_str, "%H:%M")
        time_formatted = time_obj.strftime("%I:%M %p").lstrip('0')
        padding = " " * (10 - len(name))
        time_padding = " " * (8 - len(time_formatted))
        options.append(f"{icons[idx]}   <span weight='bold'>{name}</span>{padding}  <span color='#BF8C76' weight='bold'>{time_padding}{time_formatted}</span>")

options_str = "\n".join(options)

rofi_cmd = [
    "rofi",
    "-no-config",
    "-dmenu",
    "-markup-rows",
    "-p", "🕋  Prayer Times",
    "-theme", "/home/nooreldean/.config/rofi/prayer.rasi"
]

subprocess.run(rofi_cmd, input=options_str.encode("utf-8"))
