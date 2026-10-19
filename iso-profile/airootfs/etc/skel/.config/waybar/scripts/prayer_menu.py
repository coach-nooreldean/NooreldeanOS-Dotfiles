#!/usr/bin/env python3
import json
import os
import subprocess
from datetime import datetime, timedelta

cache_file = "/tmp/prayer_timings.json"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "prayer_config.json")
USER_CONFIG = os.path.expanduser("~/.config/waybar/scripts/prayer_config.json")

IQAMA_DELAYS = {
    "Fajr": 20,
    "Dhuhr": 20,
    "Asr": 20,
    "Maghrib": 10,
    "Isha": 20
}
LANGUAGE = "ar"

for config_path in [USER_CONFIG, CONFIG_FILE]:
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            IQAMA_DELAYS.update(cfg.get("iqama_delays", {}))
            LANGUAGE = cfg.get("language", LANGUAGE)
            break
        except Exception:
            pass

ARABIC_NAMES = {
    "Fajr": "الفجر",
    "Sunrise": "الشروق",
    "Dhuhr": "الظهر",
    "Asr": "العصر",
    "Maghrib": "المغرب",
    "Isha": "العشاء"
}

if not os.path.exists(cache_file):
    err_title = "🕋 مواقيت الصلاة" if LANGUAGE == "ar" else "🕋 Prayer Times"
    err_msg = "جاري جلب المواقيت، يرجى المحاولة بعد قليل..." if LANGUAGE == "ar" else "Fetching prayer data, please wait..."
    subprocess.run(["notify-send", "-a", "Prayer", "-t", "4000", err_title, err_msg])
    exit()

try:
    with open(cache_file, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    exit()

timings = data.get("timings", {})
prayer_names = ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
icons = ['🌅', '☀️', '🌤️', '⛅', '🌇', '🌙']

def format_12h(time_str):
    time_obj = datetime.strptime(time_str, "%H:%M")
    if LANGUAGE == "ar":
        period = "ص" if time_obj.hour < 12 else "م"
        h = time_obj.strftime("%I").lstrip('0') or "12"
        m = time_obj.strftime("%M")
        return f"{h}:{m} {period}"
    return time_obj.strftime("%I:%M %p").lstrip('0')

options = []
now = datetime.now()

for idx, name in enumerate(prayer_names):
    time_str = timings.get(name, "")
    if time_str:
        formatted_time = format_12h(time_str)
        display_name = ARABIC_NAMES.get(name, name) if LANGUAGE == "ar" else name
        
        # Calculate Iqama
        iqama_info = ""
        if name in IQAMA_DELAYS:
            t_obj = datetime.strptime(time_str, "%H:%M")
            iqama_obj = t_obj + timedelta(minutes=IQAMA_DELAYS[name])
            iqama_str = iqama_obj.strftime("%H:%M")
            formatted_iqama = format_12h(iqama_str)
            label = "الإقامة" if LANGUAGE == "ar" else "Iqama"
            iqama_info = f"  <span color='#818cf8' size='small'>({label}: {formatted_iqama})</span>"

        options.append(f"{icons[idx]}  <span weight='bold'>{display_name}</span>  -  <span color='#BF8C76' weight='bold'>{formatted_time}</span>{iqama_info}")

options_str = "\n".join(options)
prompt_title = "🕋  مواقيت الصلاة والإقامة" if LANGUAGE == "ar" else "🕋  Prayer & Iqama"

rofi_cmd = [
    "rofi",
    "-no-config",
    "-dmenu",
    "-markup-rows",
    "-p", prompt_title,
    "-theme", os.path.expanduser("~/.config/rofi/prayer.rasi")
]

subprocess.run(rofi_cmd, input=options_str.encode("utf-8"))
