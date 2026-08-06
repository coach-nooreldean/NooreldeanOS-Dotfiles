# 🚀 NooreldeanOS Dotfiles

يا هلا بيك في الـ Dotfiles بتاعتي! المستودع ده فيه كل الإعدادات والـ Configurations اللي بستخدمها عشان أروق على نظام لينكس بتاعي وأخليه شغال زي الفل وشكله يفتح النفس.

## 🛠️ الـ Stack اللي بستخدمه

الـ Setup ده مبني على شوية أدوات خفيفة وسريعة وشكلها شيك جداً:
- **الواجهة (Window Manager):** [Hyprland](https://hyprland.org/) - عشان الأنميشنز اللي بتاخد العقل.
- **الشريط العلوي (Status Bar):** [Waybar](https://github.com/Alexays/Waybar) - متظبط ومتقستف.
- **الـ Launcher:** [Rofi](https://github.com/davatorium/rofi) - عشان أفتح البرامج بسرعة وبشياكة.
- **الـ Terminal:** [Kitty](https://sw.kovidgoyal.net/kitty/) - سريع جداً ومريح للعين.
- **شكل الـ Prompt:** [Starship](https://starship.rs/) - عشان التيرمينال يبقى شيك ومفيد.
- **الـ Themes:** [Kvantum](https://github.com/tsujan/Kvantum) - عشان التطبيقات يبقى شكلها متناسق.
- **الإشعارات (Notifications):** [SwayNC](https://github.com/ErikReider/SwayNotificationCenter) - مركز إشعارات أنيق جداً.
- **قائمة الخروج (Logout Menu):** [Wlogout](https://github.com/ArtsyMacaw/wlogout) - متكستمة ومظبوطة.
- **معلومات النظام:** [Fastfetch](https://github.com/fastfetch-cli/fastfetch) - بيعرض معلومات الجهاز بشكل روش.
- **شاشة الدخول (Login Manager):** [SDDM](https://github.com/sddm/sddm) - مع ثيم [Astronaut](https://github.com/Keyitdev/sddm-astronaut-theme) الفضائي الروعة.
- **الخلفيات والألوان:** [Pywal](https://github.com/dylanaraps/pywal) - بيغير ألوان النظام كله أوتوماتيك بناءً على الخلفية اللي بتختارها! 🎨

## 📁 لفة في الفولدرات

- `.config/`: هنا الخلاصة كلها، إعدادات كل البرامج اللي فوق دي متجمعة هنا بالإضافة لإعدادات النظام زي `Thunar`، و `qt5ct`/`qt6ct`، و `mimeapps.list` عشان البرامج الافتراضية.
- `applications/`: فيها ملفات الـ `.desktop` الكاستم بتاعتي (زي اختصار تنظيف النظام أو التحديث) عشان تظهر في الـ Launcher.
- `scripts/`: سكربتات باش بتسهل حياتك:
  - `system-cleanup.sh` — بينضف كاش النظام والباكدجات اللي ملهاش لازمة.
  - `system-update.sh` — بيعمل أبديت للنظام كله (pacman + AUR + Flatpak) بضغطة واحدة.
- `wallpapers/`: مجموعة خلفيات شيك جداً جاهزة للاستخدام مع الـ Wallpaper Picker.
- `pacman-packages.txt` و `flatpak-packages.txt`: لستة بكل البرامج اللي بستخدمها، عشان لو فرمت الجهاز أرجع كل حاجة في ثواني.

## ✨ فيتشرز حلوة

- 🎨 **Pywal Integration**: لما تغير الخلفية، النظام بيغير ألوان **كل حاجة** أوتوماتيك — Hyprland، Waybar، SwayNC، Qt Apps، Discord، Spotify، وحتى الـ Cursor!
- 🖼️ **Wallpaper Picker**: أداة بـ GUI بتختار منها الخلفية وبتطبق الألوان لوحدها.
- 🧹 **System Cleaner**: بينضف الكاش والباكدجات اليتيمة بضغطة من الـ Launcher.
- 📦 **System Updater**: بيعمل أبديت لكل حاجة (pacman + AUR + Flatpak) بضغطة واحدة.
- 🔒 **Hyprlock**: شاشة قفل شيك مع بلور والألوان بتاعة الـ Pywal.

## 🛡️ أمان الهاردوير (Hardware Agnostic)

حلاوة الـ Dotfiles دي إنها **مفلترة ومتنضفة** من أي باكدجات أو تعريفات خاصة بالهاردوير بتاعي (زي تعريفات كروت الشاشة Nvidia، وتحديثات المعالج، والـ Kernel، وحاجات الـ Boot). 
يعني تقدر تاخد الملفات دي وتسطبها على أي جهاز تاني وأنت مطمن إنها مش هتبوظلك النظام أو تعمل تعارض مع الهاردوير بتاعك! 💯

> ⚠️ **ملاحظة مهمة:** الاسكريبتات دي بتعمل اليوزر باسم `nooreldean`. لو اسمك مختلف، هتحتاج تغيره في `post-install.sh` والـ `.desktop` files في فولدر `applications/` قبل التسطيب.

## ⚙️ إزاي تسطب العظمة دي؟

عندك طريقتين للتسطيب، تختار بينهم على حسب حالتك:

### 1️⃣ تسطيب نظام Arch بالكامل من الصفر (بضغطة زرار) 🪄
لو أنت لسه محمل أسطوانة Arch Linux (ISO) وعايز تفرمت وتنزل النظام كله وتسطب NooreldeanOS مرة واحدة، هتحتاج الأول تشبك نت:
- **لو كابل:** هيكون شغال لوحده.
- **لو واي فاي:** اكتب أمر `iwctl`، وبعدين `station wlan0 connect "اسم_الشبكة"` واكتب الباسورد واخرج بـ `exit`.

بعد ما تشبك النت، اكتب الأمر السحري ده في التيرمينال بتاع الأسطوانة:
```bash
bash <(curl -sL https://raw.githubusercontent.com/coach-nooreldean/NooreldeanOS-Dotfiles/main/start.sh)
```
الاسكريبت هيسألك هتنزل النظام على أنهي هارد، وبعدها هيفرمت، ينزل Arch، يسوي الإعدادات الأساسية (الشبكة، الوقت، المستخدم root و nooreldean) ويظبط Dotfiles كلها أوتوماتيك!

### 2️⃣ التسطيب على نظام Arch شغال بالفعل (سطر واحد بس!) 🏎️
لو أنت مسطب Arch Linux أصلاً وعايز تركب الـ Dotfiles دي بس، كل اللي عليك تكتبه:
```bash
git clone https://github.com/coach-nooreldean/NooreldeanOS-Dotfiles.git ~/NooreldeanOS-Dotfiles && cd ~/NooreldeanOS-Dotfiles && bash install.sh
```

الاسكريبت هيعمل كل حاجة لوحده:
1. 📦 هيسطب `yay` لو مش موجود.
2. 📥 هيسطب كل البرامج من اللستة (pacman + AUR + Flatpak).
3. 💾 هياخد باك أب من إعداداتك القديمة الأول (متقلقش!).
4. 🔄 هينقل كل الإعدادات والسكربتات والخلفيات لمكانها الصح.
5. 🔧 هيظبط SDDM والسيرفسز والـ Firewall.

## ⌨️ أهم الاختصارات

| الاختصار | الوظيفة |
|----------|---------|
| `Super + Return` | فتح التيرمينال (Kitty) |
| `Super + R` | فتح الـ Launcher (Rofi) |
| `Super + Q` | قفل النافذة |
| `Super + E` | مدير الملفات (Yazi) |
| `Super + B` | فتح المتصفح (Chrome) |
| `Super + T` | فتح تليجرام |
| `Super + L` | قفل الشاشة (Hyprlock) |
| `Super + V` | الحافظة (CopyQ) |
| `Super + S` | سكرين شوت منطقة |
| `Print Screen` | سكرين شوت الشاشة كلها |
| `Super + F` | تحويل النافذة لـ Float |
| `Super + Shift + F` | ملء الشاشة |
| `Super + N` | مركز الإشعارات |
| `Super + Escape` | قائمة الخروج (Wlogout) |
| `Super + 1-0` | التنقل بين الـ Workspaces |
| `Alt + Shift` | تبديل اللغة (EN/AR) |

---
**💡 ملاحظة أخيرة:**
لو لقيت حاجة مش شغالة أو حابب تعدل على الألوان والستايلات، عيش حياتك جوة فولدر `.config`، الكود بتاعك والنظام نظامك! 😉
