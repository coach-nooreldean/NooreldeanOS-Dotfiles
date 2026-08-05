#!/usr/bin/env python3
import urllib.request
import json
import os
import subprocess
from datetime import datetime

def get_icon(code):
    if code == 0: return "☀️"
    if code in [1]: return "🌤️"
    if code in [2]: return "⛅"
    if code in [3]: return "☁️"
    if code in [45, 48]: return "🌫️"
    if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return "🌧️"
    if code in [71, 73, 75, 77, 85, 86]: return "❄️"
    if code in [95, 96, 99]: return "⛈️"
    return "🌡️"

# Automatically get user coordinates
try:
    loc_res = urllib.request.urlopen("http://ip-api.com/json/", timeout=5).read().decode()
    loc_data = json.loads(loc_res)
    lat = loc_data.get('lat', 30.06)
    lon = loc_data.get('lon', 31.25)
except:
    lat, lon = 30.06, 31.25

url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,weather_code&timezone=auto&forecast_days=2"

try:
    res = urllib.request.urlopen(url, timeout=5).read().decode()
    data = json.loads(res)
except Exception as e:
    subprocess.run(["notify-send", "Error fetching weather data."])
    exit()

hourly = data["hourly"]
times = hourly["time"]
temps = hourly["temperature_2m"]
codes = hourly["weather_code"]

now = datetime.now()
now_str = now.strftime("%Y-%m-%dT%H:00")

# Find current hour index
now_idx = 0
for i, t in enumerate(times):
    if t >= now_str:
        now_idx = i
        break

options = []
# Show next 8 hours
for i in range(now_idx, min(now_idx + 8, len(times))):
    t_str = times[i]
    t_obj = datetime.strptime(t_str, "%Y-%m-%dT%H:%M")
    display_time = t_obj.strftime("%I:%M %p").lstrip('0')
    
    # Format 'Today' or 'Tomorrow' nicely if needed, but since it's next 8 hours we keep it simple
    temp = f"{round(temps[i])}°C"
    icon = get_icon(codes[i])
    
    # Use fixed formatting with non-breaking spaces to avoid rofi bugs
    time_padded = display_time.ljust(8).replace(" ", "\u00A0")
    temp_padded = temp.rjust(7).replace(" ", "\u00A0")
    
    options.append(f"\u00A0\u00A0\u00A0\u00A0{icon}\u00A0\u00A0\u00A0\u00A0{time_padded}\u00A0\u00A0\u00A0\u00A0\u00A0{temp_padded}")

options_str = "\n".join(options)

rofi_cmd = [
    "rofi",
    "-no-config",
    "-dmenu",
    "-p", "⛅  Hourly Forecast",
    "-theme", "/home/nooreldean/.config/rofi/prayer.rasi",
    "-theme-str", "listview { lines: 8; }"
]

subprocess.run(rofi_cmd, input=options_str.encode("utf-8"))
