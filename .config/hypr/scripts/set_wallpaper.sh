#!/bin/bash

# التحقق من إدخال مسار الصورة
if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/image.jpg"
    exit 1
fi

WP=$1

# 1. تحديث الألوان باستخدام wal دون تغيير الخلفية نفسها من خلاله
wal -i "$WP" -n

# 2. تغيير الخلفية باستخدام awww (البرنامج الذي تستخدمه)
# تأكد من أن awww-daemon يعمل في الخلفية بالفعل
awww img "$WP" --transition-type grow --transition-pos 0.5,0.5 --transition-step 90

# 3. إعادة تحميل Waybar لتحديث الألوان
killall -SIGUSR2 waybar || (pkill waybar && waybar & disown)

# 4. إعادة تحميل إعدادات وألوان SwayNC
swaync-client -rs

# 5. تحديث ألوان تطبيقات GTK و Qt و Discord و Spotify (بالتوازي لسرعة أكبر)
~/.config/hypr/scripts/pywal_hyprland_sync.py &
~/.config/hypr/scripts/pywal_qt_sync.py &
~/.config/hypr/scripts/pywal_cursor_sync.py &
~/.config/hypr/scripts/pywal_discord_sync.py 2>/dev/null &
~/.config/hypr/scripts/pywal_spicetify_sync.py 2>/dev/null &
wait
gsettings set org.gnome.desktop.interface gtk-theme '' 2>/dev/null
gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita' 2>/dev/null

# 5. إذا كنت تستخدم hyprpaper بدلاً من awww أزل التعليق عن الأسطر التالية:
# hyprctl hyprpaper unload all
# hyprctl hyprpaper preload "$WP"
# hyprctl hyprpaper wallpaper ",$WP"

echo "Wallpaper and colors updated successfully!"
