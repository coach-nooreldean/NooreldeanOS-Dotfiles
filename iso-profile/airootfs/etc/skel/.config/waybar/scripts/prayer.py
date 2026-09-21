#!/usr/bin/env python3
import urllib.request, urllib.parse, json
import os, subprocess, time
from datetime import datetime, timedelta

# Load city/country/method from config file, with defaults
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "prayer_config.json")
# Also check the user's installed config location
USER_CONFIG = os.path.expanduser("~/.config/waybar/scripts/prayer_config.json")

CITY, COUNTRY, METHOD = "Cairo", "Egypt", 5
for config_path in [USER_CONFIG, CONFIG_FILE]:
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                cfg = json.load(f)
            CITY = cfg.get("city", CITY)
            COUNTRY = cfg.get("country", COUNTRY)
            METHOD = cfg.get("method", METHOD)
            break
        except Exception:
            pass

city_encoded = urllib.parse.quote(CITY)
country_encoded = urllib.parse.quote(COUNTRY)

url = f"http://api.aladhan.com/v1/timingsByCity?city={city_encoded}&country={country_encoded}&method={METHOD}"
cache_file = "/tmp/prayer_timings.json"

def get_timings():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    
    # Try reading cache
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
                if data.get("date") == date_str:
                    return data["timings"]
        except:
            pass

    # Fetch from API
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=10).read().decode()
        timings = json.loads(res)['data']['timings']
        
        # Save to cache
        with open(cache_file, "w") as f:
            json.dump({"date": date_str, "timings": timings}, f)
            
        return timings
    except Exception as e:
        # Fallback to old cache if available
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    return json.load(f)["timings"]
            except:
                pass
        raise e

try:
    timings = get_timings()
    
    prayer_names = ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
    prayers = {name: timings[name] for name in prayer_names}
    
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
    # Adhan playback logic
    adhan_file = os.path.expanduser("~/.config/waybar/scripts/adhan.mp3")
    last_played_file = "/tmp/adhan_last_played.txt"
    
    last_played = ""
    if os.path.exists(last_played_file):
        with open(last_played_file, "r") as f:
            last_played = f.read().strip()
            
    for name in prayer_names:
        # Don't play Adhan for Sunrise, only prayers
        if name != "Sunrise" and current_time == prayers[name]:
            played_marker = f"{now.strftime('%Y-%m-%d')}_{name}"
            if last_played != played_marker:
                subprocess.Popen(["mpv", adhan_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                with open(last_played_file, "w") as f:
                    f.write(played_marker)
    
    next_prayer = "Fajr"
    next_time = prayers["Fajr"]
    
    for name in prayer_names:
        if current_time < prayers[name]:
            next_prayer = name
            next_time = prayers[name]
            break
            
    t1 = datetime.strptime(current_time, "%H:%M")
    t2 = datetime.strptime(next_time, "%H:%M")
    
    if t2 < t1:
        t2 += timedelta(days=1)
        
    diff = t2 - t1
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    text_output = f"{next_prayer} in {hours}:{minutes:02d}"
    
    tooltip = "<span size='large' weight='bold' color='#ffffff'>Prayer Times</span>\n"
    for name in prayer_names:
        time_obj = datetime.strptime(prayers[name], "%H:%M")
        time_str = time_obj.strftime("%I:%M %p").lstrip('0')
        color = "#8af09c" if name == next_prayer else "#cccccc"
        tooltip += f"<span weight='bold'>{name.ljust(9)}:</span>\t<span color='{color}'>{time_str}</span>\n"
        
    tooltip = tooltip.rstrip('\n')
        
    print(json.dumps({"text": text_output, "tooltip": tooltip, "class": next_prayer.lower()}), flush=True)
except Exception as e:
    print(json.dumps({"text": "API Error", "tooltip": f"Error: {str(e)}"}), flush=True)
