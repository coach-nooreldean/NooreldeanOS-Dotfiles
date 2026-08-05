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

## 📁 لفة في الفولدرات

- `.config/`: هنا الخلاصة كلها، إعدادات كل البرامج اللي فوق دي متجمعة هنا بالإضافة لإعدادات النظام زي `Thunar`، و `qt5ct`/`qt6ct`، و `mimeapps.list` عشان البرامج الافتراضية.
- `applications/`: فيها ملفات الـ `.desktop` الكاستم بتاعتي (زي اختصار تنظيف النظام أو التحديث) عشان تظهر في الـ Launcher.
- `scripts/`: شوية سكربتات باش (Bash) بتسهل عليا حياتي، زي `system-cleanup.sh` اللي بينضف كاش النظام والباكدجات اللي ملهاش لازمة و `backup-dotfiles.sh` اللي بياخد باك أب ويرفعه على جيت هاب.
- `pacman-packages.txt` و `flatpak-packages.txt`: لستة بكل البرامج اللي بستخدمها، عشان لو فرمت الجهاز أرجع كل حاجة في ثواني.

## 🛡️ أمان الهاردوير (Hardware Agnostic)

حلاوة الـ Dotfiles دي إنها **مفلترة ومتنضفة** من أي باكدجات أو تعريفات خاصة بالهاردوير بتاعي (زي تعريفات كروت الشاشة Nvidia، وتحديثات المعالج، والـ Kernel، وحاجات الـ Boot). 
يعني تقدر تاخد الملفات دي وتسطبها على أي جهاز تاني وأنت مطمن إنها مش هتبوظلك النظام أو تعمل تعارض مع الهاردوير بتاعك! 💯

## ⚙️ إزاي تسطب العظمة دي؟

الموضوع أبسط مما تتخيل، أنا عامل سكربت [install.sh](./install.sh) هيقوم بالواجب كله:
1. هيعمل Update للنظام.
2. هيسطب كل البرامج من اللستة (باستخدام `yay` و `flatpak`).
3. هيعمل Symlinks (ربط) لكل الإعدادات والسكربتات في مكانها الصح جوة الـ Home بتاعك.

كل اللي عليك تعمله إنك تفتح التيرمينال وتكتب الأمرين دول:
```bash
git clone https://github.com/coach-nooreldean/NooreldeanOS-Dotfiles.git
cd NooreldeanOS-Dotfiles
./install.sh
```

---
**💡 ملاحظة أخيرة:**
لو لقيت حاجة مش شغالة أو حابب تعدل على الألوان والستايلات، عيش حياتك جوة فولدر `.config`، الكود بتاعك والنظام نظامك! 😉
