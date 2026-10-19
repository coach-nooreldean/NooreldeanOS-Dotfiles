#!/usr/bin/env python3
import urllib.request, urllib.parse, json
import os, subprocess, time
from datetime import datetime, timedelta

# Configuration paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "prayer_config.json")
USER_CONFIG = os.path.expanduser("~/.config/waybar/scripts/prayer_config.json")

# Default values
CITY, COUNTRY, METHOD = "Cairo", "Egypt", 5
LANGUAGE = "ar"
PRE_REMINDER_MINUTES = 20
IQAMA_DELAYS = {
    "Fajr": 20,
    "Dhuhr": 20,
    "Asr": 20,
    "Maghrib": 10,
    "Isha": 20
}

# Load config
for config_path in [USER_CONFIG, CONFIG_FILE]:
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            CITY = cfg.get("city", CITY)
            COUNTRY = cfg.get("country", COUNTRY)
            METHOD = cfg.get("method", METHOD)
            LANGUAGE = cfg.get("language", LANGUAGE)
            PRE_REMINDER_MINUTES = cfg.get("pre_prayer_reminder_minutes", PRE_REMINDER_MINUTES)
            IQAMA_DELAYS.update(cfg.get("iqama_delays", {}))
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
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("date") == date_str:
                    return data["timings"]
        except Exception:
            pass

    # Fetch from API
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=10).read().decode()
        timings = json.loads(res)['data']['timings']
        
        # Save to cache
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"date": date_str, "timings": timings}, f)
            
        return timings
    except Exception as e:
        # Fallback to existing cache if available
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)["timings"]
            except Exception:
                pass
        raise e

def play_chime():
    sound_files = [
        "/usr/share/sounds/freedesktop/stereo/message.oga",
        "/usr/share/sounds/freedesktop/stereo/complete.oga",
        "/usr/share/sounds/freedesktop/stereo/bell.oga"
    ]
    for s in sound_files:
        if os.path.exists(s):
            if subprocess.call(["which", "pw-play"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                subprocess.Popen(["pw-play", s], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            elif subprocess.call(["which", "paplay"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                subprocess.Popen(["paplay", s], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            elif subprocess.call(["which", "mpv"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                subprocess.Popen(["mpv", "--really-quiet", s], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return

try:
    timings = get_timings()
    prayer_names = ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
    now = datetime.now()
    current_time_str = now.strftime("%H:%M")
    today = now.date()

    # Build datetime objects for today's timings
    prayer_dts = {}
    iqama_dts = {}

    for name in prayer_names:
        time_part = datetime.strptime(timings[name], "%H:%M").time()
        p_dt = datetime.combine(today, time_part)
        prayer_dts[name] = p_dt
        if name in IQAMA_DELAYS:
            iqama_dts[name] = p_dt + timedelta(minutes=IQAMA_DELAYS[name])

    # 1. Adhan Playback logic
    adhan_file = os.path.expanduser("~/.config/waybar/scripts/adhan.mp3")
    last_played_file = "/tmp/adhan_last_played.txt"
    last_played = ""
    if os.path.exists(last_played_file):
        try:
            with open(last_played_file, "r") as f:
                last_played = f.read().strip()
        except Exception:
            pass

    for name in prayer_names:
        if name != "Sunrise" and current_time_str == timings[name]:
            marker = f"{today.strftime('%Y-%m-%d')}_{name}"
            if last_played != marker and os.path.exists(adhan_file):
                subprocess.Popen(["mpv", adhan_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                with open(last_played_file, "w") as f:
                    f.write(marker)

    # 2. Check if currently in Iqama Window (between Adhan and Iqama)
    active_iqama_prayer = None
    iqama_remaining_sec = 0

    for name, i_dt in iqama_dts.items():
        p_dt = prayer_dts[name]
        if p_dt <= now < i_dt:
            active_iqama_prayer = name
            iqama_remaining_sec = (i_dt - now).total_seconds()
            break

    # 3. Find Next Prayer
    next_prayer = None
    next_dt = None

    for name in prayer_names:
        p_dt = prayer_dts[name]
        if p_dt > now:
            next_prayer = name
            next_dt = p_dt
            break

    # If all prayers for today passed, next is tomorrow's Fajr
    if next_prayer is None:
        next_prayer = "Fajr"
        tomorrow_fajr_time = datetime.strptime(timings["Fajr"], "%H:%M").time()
        next_dt = datetime.combine(today + timedelta(days=1), tomorrow_fajr_time)

    # 4. Pre-Prayer Reminder (20 minutes before next prayer)
    if next_prayer != "Sunrise" and next_dt:
        seconds_until_prayer = (next_dt - now).total_seconds()
        if 0 < seconds_until_prayer <= (PRE_REMINDER_MINUTES * 60):
            reminder_marker_file = f"/tmp/prayer_reminder_{today.strftime('%Y-%m-%d')}_{next_prayer}.txt"
            if not os.path.exists(reminder_marker_file):
                mins_left = int(seconds_until_prayer // 60) + 1
                pr_ar = ARABIC_NAMES.get(next_prayer, next_prayer)
                if LANGUAGE == "ar":
                    title = "🕋 اقتربت صلاة " + pr_ar
                    body = f"متبقي حوالي {mins_left} دقيقة على أذان {pr_ar}."
                else:
                    title = f"🕋 {next_prayer} Prayer Coming Soon"
                    body = f"Approximately {mins_left} minutes left until {next_prayer} Adhan."

                subprocess.Popen(["notify-send", "-a", "NooreldeanOS Prayer", "-u", "normal", "-i", "dialog-information", title, body])
                play_chime()

                with open(reminder_marker_file, "w") as f:
                    f.write("sent")

    # 5. Format Waybar Output
    if active_iqama_prayer:
        mins = int(iqama_remaining_sec // 60)
        pr_name = ARABIC_NAMES.get(active_iqama_prayer, active_iqama_prayer) if LANGUAGE == "ar" else active_iqama_prayer
        if LANGUAGE == "ar":
            text_output = f"إقامة {pr_name}: {mins} د"
        else:
            text_output = f"Iqama ({pr_name}): {mins}m"
        module_class = "iqama"
    else:
        diff = next_dt - now
        hours, remainder = divmod(int(diff.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        pr_name = ARABIC_NAMES.get(next_prayer, next_prayer) if LANGUAGE == "ar" else next_prayer
        if LANGUAGE == "ar":
            text_output = f"{pr_name} خلال {hours}:{minutes:02d}"
        else:
            text_output = f"{next_prayer} in {hours}:{minutes:02d}"
        module_class = next_prayer.lower()

    # 6. Build Rich Tooltip
    if LANGUAGE == "ar":
        tooltip = "<span size='large' weight='bold' color='#ffffff'>مواقيت الصلاة والإقامة</span>\n\n"
        for name in prayer_names:
            p_time_str = datetime.strptime(timings[name], "%H:%M").strftime("%I:%M %p").lstrip('0')
            ar_name = ARABIC_NAMES.get(name, name)
            is_active = (name == active_iqama_prayer) or (name == next_prayer and not active_iqama_prayer)
            color = "#8af09c" if is_active else "#dddddd"

            if name in IQAMA_DELAYS:
                iqama_time_str = iqama_dts[name].strftime("%I:%M %p").lstrip('0')
                tooltip += f"<span weight='bold'>{ar_name.ljust(8)}:</span> <span color='{color}'>{p_time_str}</span>  <span color='#818cf8' size='small'>(الإقامة: {iqama_time_str})</span>\n"
            else:
                tooltip += f"<span weight='bold'>{ar_name.ljust(8)}:</span> <span color='{color}'>{p_time_str}</span>\n"
    else:
        tooltip = "<span size='large' weight='bold' color='#ffffff'>Prayer & Iqama Times</span>\n\n"
        for name in prayer_names:
            p_time_str = datetime.strptime(timings[name], "%H:%M").strftime("%I:%M %p").lstrip('0')
            is_active = (name == active_iqama_prayer) or (name == next_prayer and not active_iqama_prayer)
            color = "#8af09c" if is_active else "#dddddd"

            if name in IQAMA_DELAYS:
                iqama_time_str = iqama_dts[name].strftime("%I:%M %p").lstrip('0')
                tooltip += f"<span weight='bold'>{name.ljust(9)}:</span> <span color='{color}'>{p_time_str}</span>  <span color='#818cf8' size='small'>(Iqama: {iqama_time_str})</span>\n"
            else:
                tooltip += f"<span weight='bold'>{name.ljust(9)}:</span> <span color='{color}'>{p_time_str}</span>\n"

    tooltip = tooltip.rstrip('\n')
    print(json.dumps({"text": text_output, "tooltip": tooltip, "class": module_class}, ensure_ascii=False), flush=True)

except Exception as e:
    err_text = "خطأ في المواقيت" if LANGUAGE == "ar" else "Prayer Error"
    print(json.dumps({"text": err_text, "tooltip": f"Error: {str(e)}", "class": "error"}, ensure_ascii=False), flush=True)
