# 🛠️ NooreldeanOS - Technical Documentation

هذا المستند موجه للمطورين (Developers) ومهندسي الأنظمة (System Engineers) الذين يرغبون في فهم معمارية (Architecture) المشروع، كيفية عمل سكريبت التثبيت، وطريقة التعديل عليه.

## 🏗️ المعمارية (Architecture)

يعتمد NooreldeanOS على نظام تثبيت تركيبي (Modular Installation System) لضمان سهولة الصيانة وقابلية التوسع (Scalability). بدلاً من الاعتماد على سكريبت واحد ضخم، تم تقسيم المنطق (Logic) إلى عدة ملفات مساعدة تحت مجلد `lib/`.

### 📂 الهيكل التنظيمي (Directory Structure)

```text
NooreldeanOS-Dotfiles/
├── install.sh            # نقطة الإدخال الرئيسية للتثبيت (Entry point)
├── post-install.sh       # يعمل داخل chroot عند تثبيت النظام من الصفر
├── start.sh              # سكريبت التقسيم والتثبيت الكامل لـ Arch Linux
├── uninstall.sh          # منطق إزالة التثبيت واستعادة النسخ الاحتياطية
├── lib/                  # المجلد الأساسي للـ Modules
│   ├── config.conf       # ملف الإعدادات الافتراضية
│   ├── logger.sh         # نظام الطباعة وتسجيل الأخطاء
│   ├── core_install.sh   # منطق تثبيت الحزم (pacman, yay, flatpak)
│   ├── backup.sh         # منطق أخذ النسخ الاحتياطية الآمنة
│   ├── symlinks.sh       # منطق توزيع وربط ملفات الإعدادات
│   └── services.sh       # تفعيل الخدمات (systemd, ufw, docker)
├── .github/workflows/    # أتمتة الـ CI/CD (مثل ShellCheck)
```

## ⚙️ دورة حياة التثبيت (Installation Lifecycle)

عند تشغيل `install.sh`، يمر النظام بالخطوات التالية:

1. **Initialization & Privilege Escalation:**
   - يمنع تشغيل السكريبت كـ `root` لتجنب كسر مجلدات الـ Home.
   - يطلب صلاحيات `sudo` مرة واحدة ويقوم بتشغيل `keep-alive loop` بالخلفية لضمان عدم انتهاء الجلسة أثناء التثبيت الطويل.

2. **Error Handling (Trap Mechanism):**
   - يستخدم `set -eo pipefail` لإيقاف السكريبت عند أول خطأ.
   - يتم تتبع الخطوة الحالية عبر المتغير `CURRENT_STEP`.
   - في حالة حدوث خطأ، يتم تفعيل الـ `trap` لطباعة الخطوة التي فشلت ومسار السطر (Line Number) لمساعدة المطور على تتبع الخطأ.

3. **Loading Configurations & Logger:**
   - يتم عمل `source lib/config.conf` لاستدعاء المتغيرات.
   - يتم عمل `source lib/logger.sh` لتمكين دوال التسجيل الملونة (`log_info`, `log_error`، الخ) والتي تكتب الإخراج في الـ Terminal وتخزنه في `/var/log/nooreldeanos-install.log`.

4. **Module Execution:**
   - **`core_install.sh`**: يتم التحقق من وجود `yay`، ثم قراءة `pacman-packages.txt` و `flatpak-packages.txt` لتثبيت الحزم بالترتيب.
   - **`backup.sh`**: يتم إنشاء مجلد `~/.NooreldeanOS-backup-TIMESTAMP` ونسخ أي ملفات ستتأثر (Idempotency in mind).
   - **`symlinks.sh`**: يُسأل المستخدم عن رغبته في استخدام `Symlinks` (Developer Mode) أو `rsync/cp` (Stable Mode).
   - **`services.sh`**: يقوم بإعداد `zram-generator`، `docker`، `ufw`، و `sddm`.

## 📝 نظام التسجيل (Logging System)

تم بناء `lib/logger.sh` لفصل الإخراج المرئي (Visual Output) عن الإخراج الفعلي للبيانات.

```bash
log_info "This is an info message"     # أزرق
log_success "Operation successful"     # أخضر
log_warning "This is a warning"        # أصفر
log_error "Critical failure"           # أحمر (يفعل الـ Trap عادة)
```
جميع هذه الدوال تضيف ختماً زمنياً (Timestamp) وتخزن السجلات في مسار `LOG_FILE` المعرف في `config.conf`.

## 🔄 التكامل المستمر (CI/CD)

يحتوي المستودع على **GitHub Actions Workflow** (`.github/workflows/ci.yml`):
- يراقب أي عملية رفع (Push) أو سحب (Pull Request) تحتوي على ملفات `.sh`.
- يقوم بتشغيل فحص **ShellCheck** لضمان عدم وجود أخطاء صياغة (Syntax Errors) أو ممارسات سيئة (Bad Practices) في أكواد Bash، مما يحافظ على جودة الكود (Code Quality).

## 🚀 كيفية المساهمة أو التعديل

1. **تعديل الإعدادات الافتراضية:** 
   إذا كنت تريد تغيير مسار الـ Timezone الافتراضي أو تعطيل UFW بشكل افتراضي، فقط قم بتعديل `lib/config.conf`. لن تحتاج للمس الأكواد الأساسية.

2. **إضافة برامج جديدة:**
   قم بإضافة اسم البرنامج إلى `pacman-packages.txt` (من المستودعات الرسمية أو AUR) أو `flatpak-packages.txt`. سيتكفل `core_install.sh` بالباقي.

3. **إضافة وحدة جديدة (New Module):**
   - أنشئ ملف `lib/my_module.sh`.
   - قم بكتابة منطقك داخل دالة `my_new_feature()`.
   - قم باستدعائه (source) في `install.sh` وأضفه إلى تسلسل التنفيذ.
