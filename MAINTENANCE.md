# 🔧 Maroof NFC System - دليل الصيانة الشامل

## 📋 نظرة عامة على المشروع

**اسم المشروع:** Maroof Digital Business Cards  
**الوظيفة:** نظام إنشاء بطاقات تعريف رقمية مع دعم NFC  
**التقنيات:** Python Flask, NFC (nfcpy), GitHub Pages, Git Submodule  
**الهاردوير:** Raspberry Pi + AITRIP PN532 NFC Reader  

---

## 🏗️ بنية المشروع (Git Submodule)
```
maroof-cards/                    # المشروع الرئيسي (الكود)
├── tools/
│   ├── web_app.py              # الخادم الرئيسي (Flask)
│   ├── create_card.py          # مولد البطاقات + Git operations
│   ├── nfc_writer.py           # تحكم بقارئ NFC
│   └── requirements.txt
├── templates/
│   ├── pages/
│   │   ├── home.html           # صفحة الإنشاء (Admin)
│   │   ├── register.html       # صفحة التسجيل (العملاء)
│   │   ├── dashboard.html      # لوحة التحكم
│   │   └── edit.html           # تعديل البطاقات
│   └── cards/                  # قوالب البطاقات
│       ├── professional.html
│       ├── friendly.html
│       ├── luxury.html
│       ├── modern.html
│       ├── classic.html
│       ├── Gaming.html
│       ├── Japan70s.html
│       └── it.html
├── clients/ → maroof-cards-data (Submodule)  # ⭐ بيانات العملاء في repo منفصل!
│   └── [username]/
│       ├── index.html
│       ├── data.json
│       ├── contact.vcf
│       ├── photo.jpg (optional)
│       └── cv.pdf (optional)
└── MAINTENANCE.md              # هذا الملف
```

---

## 🎯 **مفهوم Git Submodule - مهم جداً!**

### لماذا استخدمنا Submodule؟

**المشكلة:**
- تحديثات الكود (من Codespaces) تتعارض مع بيانات العملاء (من Pi)
- خطر فقدان بيانات العملاء عند التحديثات

**الحل:**
```
maroof-cards (repo 1)          → الكود فقط
    ↓
clients/ → maroof-cards-data (repo 2)  → بيانات العملاء فقط
```

### كيف يعمل؟

1. **في Pi:**
   - عند إنشاء بطاقة جديدة → يحفظ في `clients/`
   - `create_card.py` يرفع تلقائياً على `maroof-cards-data`

2. **في Codespaces:**
   - تعديلات الكود → ترفع على `maroof-cards`
   - لا يمس `clients/` أبداً

3. **النتيجة:**
   - ✅ لا تعارض
   - ✅ لا فقدان بيانات
   - ✅ نسخ احتياطي مستقل

---

## ⚠️ قواعد ذهبية - اقرأها قبل أي تعديل!

### 🚫 ممنوعات صارمة:

1. **لا تعدّل `clients/` يدوياً من Codespaces!**
   - ❌ الخطأ: `git add clients/` في Codespaces
   - ✅ الصحيح: اتركها للنظام التلقائي في Pi

2. **لا تحذف `.gitmodules`!**
   - هذا الملف يربط `clients/` بـ `maroof-cards-data`

3. **لا تكتب نص عربي داخل الكود أبداً!**
   - ❌ الخطأ: `document.getElementById('result').textContent = 'تم النجاح'`
   - ✅ الصحيح: `document.getElementById('result').textContent = 'Success'`

4. **لا تنسى حذف Python cache بعد التعديل!**
```bash
   rm -rf tools/__pycache__
   find . -name "*.pyc" -delete
```

---

## 🔄 إجراءات التحديث الصحيحة

### 📝 **تحديث الكود (في Codespaces):**
```bash
cd /workspaces/maroof-cards

# 1. عدّل الملفات (tools/, templates/, إلخ)
nano tools/web_app.py

# 2. ارفع التحديثات
git add tools/ templates/
git commit -m "وصف التحديل"
git push origin main

# ⚠️ لا تمس clients/ هنا!
```

---

### 📥 **سحب التحديثات (في Pi):**
```bash
cd ~/maroof/maroof-cards

# 1. سحب تحديثات الكود
git pull origin main

# 2. تحديث submodule (بيانات العملاء)
git submodule update --remote

# 3. مسح cache
rm -rf tools/__pycache__
find . -name "*.pyc" -delete

# 4. إعادة تشغيل
sudo systemctl restart maroof.service
```

---

### 🎴 **إنشاء بطاقة جديدة (تلقائي):**

عند إنشاء بطاقة من `http://raspberrypi.local:7070`:
1. ✅ تُحفظ في `clients/username/`
2. ✅ `create_card.py` يرفعها تلقائياً على `maroof-cards-data`
3. ✅ تظهر في GitHub Pages خلال دقائق

**لا تحتاج عمل شيء يدوي!** ⚡

---

### 🔍 **التحقق من حالة Submodule:**
```bash
cd ~/maroof/maroof-cards

# عرض حالة submodule
git submodule status

# يجب أن ترى:
# [commit-hash] clients (heads/main)

# عرض محتوى clients
ls -la clients/

# التحقق من آخر commit
cd clients
git log -1
cd ..
```

---

## 🐛 المشاكل الشائعة وحلولها

### 1️⃣ **بيانات العملاء لا تظهر على GitHub Pages**

**السبب:** لم يتم رفعها على `maroof-cards-data`

**التشخيص:**
```bash
# في Pi
cd ~/maroof/maroof-cards/clients
git log -1
# تحقق من التاريخ - هل حديث؟
```

**الحل:**
```bash
cd ~/maroof/maroof-cards/clients
git status
git add .
git commit -m "Add missing cards"
git push origin main
```

---

### 2️⃣ **التعارض عند git pull**

**الأعراض:**
```
error: Your local changes would be overwritten by merge
```

**الحل:**
```bash
cd ~/maroof/maroof-cards

# احفظ التغييرات المحلية
git stash

# اسحب التحديثات
git pull origin main
git submodule update --remote

# استرجع التغييرات
git stash pop

# أعد تشغيل
sudo systemctl restart maroof.service
```

---

### 3️⃣ **clients/ فارغ بعد git clone**

**السبب:** لم يتم تهيئة submodule

**الحل:**
```bash
cd ~/maroof/maroof-cards
git submodule update --init --recursive
```

---

### 4️⃣ **Submodule detached HEAD**

**الأعراض:**
```
(HEAD detached at [commit])
```

**الحل:**
```bash
cd ~/maroof/maroof-cards/clients
git checkout main
git pull origin main
cd ..
```

---

## 🔧 تعديل الكود بشكل آمن

### في Codespaces:
```bash
# 1. عدّل الملفات
nano tools/web_app.py

# 2. اختبر محلياً (اختياري)
python3 tools/web_app.py

# 3. ارفع
git add tools/
git commit -m "Fix: ..."
git push origin main

# ⚠️ لا تعدّل clients/ هنا!
```

### في Pi:
```bash
# 1. أوقف الخادم
sudo systemctl stop maroof.service

# 2. اسحب التحديثات
git pull origin main
git submodule update --remote

# 3. مسح cache
rm -rf tools/__pycache__

# 4. شغّل الخادم
sudo systemctl start maroof.service
```

---

## 📊 فهم بنية البيانات

### ملف `data.json` (لكل عميل):
```json
{
  "NAME": "محمد عبدالله",
  "JOB_TITLE": "مدير تسويق",
  "COMPANY": "شركة معروف",
  "PHONE": "0501234567",
  "PHONE2": "0507654321",
  "EMAIL": "email@example.com",
  "INSTAGRAM": "username",
  "LINKEDIN": "username",
  "TWITTER": "username",
  "YOUTUBE": "channel",
  "TIKTOK": "username",
  "SNAPCHAT": "username",
  "GITHUB": "username",
  "WEBSITE": "https://example.com",
  "CUSTOM_LINK": "https://link.com",
  "BIO": "نبذة تعريفية",
  "PHOTO": "./photo.jpg",
  "CV": "./cv.pdf",
  "template": "professional",
  "created_at": "2026-01-19T07:45:00",
  "source": "admin",
  "status": "pending",
  "print_count": 0,
  "print_history": []
}
```

---

## 🚀 تشغيل الخادم

### الطريقة التلقائية (systemd service):
```bash
sudo systemctl status maroof.service    # حالة الخادم
sudo systemctl start maroof.service     # تشغيل
sudo systemctl stop maroof.service      # إيقاف
sudo systemctl restart maroof.service   # إعادة تشغيل
sudo journalctl -u maroof.service -f    # مشاهدة السجلات
```

### الوصول:
- **من Pi:** `http://localhost:7070`
- **من الشبكة:** `http://192.168.8.9:7070`
- **DNS المحلي:** `http://raspberrypi.local:7070`
- **GitHub Pages:** `https://maroof-id.github.io/maroof-cards/clients/[username]/`

---

## 📁 الملفات المهمة

### في `tools/create_card.py`:

**الدالة المهمة:**
```python
def git_push_background(self, message: str):
    """Push only to clients submodule repo"""
    def git_push():
        try:
            clients_dir = str(self.clients_path)
            
            # Add and commit in submodule
            subprocess.run(['git', 'add', '.'], cwd=clients_dir, check=False)
            subprocess.run(['git', 'commit', '-m', message], cwd=clients_dir, check=False)
            subprocess.run(['git', 'push', 'origin', 'main'], cwd=clients_dir, check=False)
            
            print(f"✅ Client data pushed: {message}")
        except Exception as e:
            print(f"⚠️ Git push error: {e}")
    
    thread = threading.Thread(target=git_push, daemon=True)
    thread.start()
```

**ماذا تفعل:**
1. تحفظ البطاقة في `clients/username/`
2. ترفعها تلقائياً على `maroof-cards-data`
3. تعمل في background thread (لا تبطئ الاستجابة)

---

## 🔐 ملف Git Credentials

**الموقع:** `~/.git-credentials`

**المحتوى:**
```
https://USERNAME:TOKEN@github.com
```

**التحقق:**
```bash
cat ~/.git-credentials
```

**إذا كان مفقوداً:**
```bash
cat > ~/.git-credentials << 'CREDS'
https://maroof-id:YOUR_TOKEN@github.com
CREDS

chmod 600 ~/.git-credentials
git config --global credential.helper store
```

---

## 🎯 الخلاصة للذكاء الاصطناعي المستقبلي

### القواعد الذهبية:

1. 🔄 **Submodule = clients/ في repo منفصل**
2. 💻 **Codespaces = تعديل الكود فقط**
3. 🥧 **Pi = تلقائي لبيانات العملاء**
4. 🚫 **لا نص عربي في الكود**
5. 🧹 **امسح cache بعد كل تعديل**

### عند أي مشكلة:

1. ✅ اقرأ السجلات: `sudo journalctl -u maroof.service -n 50`
2. ✅ تحقق من submodule: `git submodule status`
3. ✅ امسح cache: `rm -rf tools/__pycache__`
4. ✅ أعد تشغيل: `sudo systemctl restart maroof.service`

### البنية العامة:
```
┌─────────────────┐
│  Codespaces     │ → تعديل الكود
│  (maroof-cards) │ → git push origin main
└────────┬────────┘
         ↓
┌────────────────────────┐
│  GitHub                │
│  maroof-cards (الكود)  │
└────────┬───────────────┘
         ↓
┌────────────────────────┐
│  Pi                    │
│  git pull origin main  │
└────────┬───────────────┘
         ↓
┌──────────────────────────────┐
│  Pi - إنشاء بطاقة جديدة      │
│  create_card.py              │
│    ↓                         │
│  clients/ (submodule)        │
│    ↓                         │
│  git push → maroof-cards-data│
└──────────┬───────────────────┘
           ↓
┌──────────────────────────┐
│  GitHub Pages            │
│  البطاقة تظهر للعملاء    │
└──────────────────────────┘
```

---

## 📞 الموارد

- **GitHub (الكود):** https://github.com/maroof-id/maroof-cards
- **GitHub (البيانات):** https://github.com/maroof-id/maroof-cards-data
- **nfcpy Docs:** https://nfcpy.readthedocs.io/
- **Flask Docs:** https://flask.palletsprojects.com/

---

**تم إنشاء هذا الدليل:** يناير 2026  
**آخر تحديث:** يناير 2026  
**النسخة:** 2.0 (مع Git Submodule)

🎉 **حظاً موفقاً في الصيانة!**
