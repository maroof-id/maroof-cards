# 🔧 Maroof NFC System - دليل الصيانة الشامل

## 📋 نظرة عامة على المشروع

**اسم المشروع:** Maroof Digital Business Cards  
**الوظيفة:** نظام إنشاء بطاقات تعريف رقمية مع دعم NFC  
**التقنيات:** Python Flask, NFC (nfcpy), GitHub Pages  
**الهاردوير:** Raspberry Pi + AITRIP PN532 NFC Reader  

---

## ⚠️ قواعد ذهبية - اقرأها قبل أي تعديل!

### 🚫 ممنوعات صارمة:

1. **لا تكتب نص عربي داخل الكود أبداً!**
   - ❌ الخطأ: `document.getElementById('result').textContent = 'تم النجاح'`
   - ✅ الصحيح: `document.getElementById('result').textContent = 'Success'`
   - **السبب:** النص العربي يكسر JavaScript encoding ويسبب syntax errors

2. **لا تستخدم `\n` في JavaScript strings داخل Python!**
   - ❌ الخطأ: `textContent = result.message + '\n\nError'`
   - ✅ الصحيح: `textContent = result.message + ' --- Error'`
   - **السبب:** Python يحول `\n` لـ newline حقيقي في HTML

3. **لا تضع تعليقات Python (`#`) داخل JavaScript!**
   - ❌ الخطأ: `# Fixed line` داخل `<script>`
   - ✅ الصحيح: `// Fixed line` أو لا شيء
   - **السبب:** JavaScript لا يفهم `#`

4. **لا تنسى حذف Python cache بعد التعديل!**
```bash
   rm -rf tools/__pycache__
   find . -name "*.pyc" -delete
```

---

## 🏗️ بنية المشروع
```
maroof-cards/
├── tools/
│   ├── web_app.py           # الخادم الرئيسي (Flask)
│   ├── create_card.py       # مولد البطاقات + Git operations
│   ├── nfc_writer.py        # تحكم بقارئ NFC
│   └── requirements.txt     # مكتبات Python
├── templates/
│   ├── modern.html          # قالب عصري
│   ├── classic.html         # قالب كلاسيكي
│   └── minimal.html         # قالب بسيط
├── clients/
│   └── [username]/          # مجلدات البطاقات المنشأة
│       ├── index.html
│       ├── data.json
│       └── contact.vcf
└── MAINTENANCE.md           # هذا الملف
```

---

## 🔌 إعدادات الهاردوير

### AITRIP PN532 NFC Reader:
- **DIP Switch 1:** ON (UART mode)
- **DIP Switch 2:** OFF
- **USB Port:** CH340 converter (Device ID: 1a86:7523)
- **Serial Device:** `/dev/ttyUSB0` أو `/dev/ttyUSB1`
- **Transport Path:** `tty:USB0:pn532`

### البطاقات المدعومة:
- ✅ NTAG213/215/216 (للكتابة)
- ✅ Mifare Ultralight (قراءة فقط)
- ❌ Mifare Classic (غير متوافق مع NDEF)

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

### الطريقة اليدوية (للتطوير):
```bash
cd ~/maroof/maroof-cards
python3 tools/web_app.py
```

### الوصول:
- **من الجهاز:** `http://localhost:7070`
- **من الشبكة:** `http://192.168.8.9:7070`
- **DNS المحلي:** `http://raspberrypi.local:7070`

---

## 🐛 المشاكل الشائعة وحلولها

### 1️⃣ الأزرار لا تعمل (testReader/readCard undefined)

**السبب:** JavaScript مكسور أو cache قديم

**التشخيص:**
```bash
curl http://localhost:7070/settings 2>/dev/null | grep -c "function testReader"
# يجب أن يطبع 1 أو أكثر
```

**الحل:**
```bash
# 1. تحقق من الكود
grep -n "function testReader" tools/web_app.py

# 2. امسح cache
rm -rf tools/__pycache__
sudo systemctl restart maroof.service

# 3. في المتصفح: Ctrl+Shift+Delete → Clear cache
```

---

### 2️⃣ NFC Reader غير متصل

**الأعراض:**
- `[Errno 110] Connection timed out`
- `Cannot connect to NFC reader`

**التشخيص:**
```bash
# تحقق من USB
ls -la /dev/ttyUSB*

# تحقق من الصلاحيات
groups | grep dialout
```

**الحل:**
```bash
# 1. فصل USB وانتظر 5 ثواني
# 2. وصّل USB مرة أخرى
# 3. انتظر 3 ثواني

# إذا لم ينجح - أضف المستخدم لـ dialout
sudo usermod -a -G dialout $USER
# ثم أعد تسجيل الدخول
```

---

### 3️⃣ المنفذ مشغول (Port already in use)

**الأعراض:**
```
OSError: [Errno 98] Address already in use
```

**الحل:**
```bash
# اقتل كل Python
sudo pkill -9 python3

# أو اقتل المنفذ المحدد
sudo lsof -ti:7070 | xargs sudo kill -9

# ثم أعد تشغيل الخادم
sudo systemctl restart maroof.service
```

---

### 4️⃣ Git push failures

**الأعراض:**
- `fatal: could not read Username`
- `Authentication failed`

**الحل:**
```bash
# تحقق من credentials
cat ~/.git-credentials

# إذا لم تكن موجودة - أنشئها:
cat > ~/.git-credentials << 'CREDS'
https://USERNAME:TOKEN@github.com
CREDS

chmod 600 ~/.git-credentials
git config --global credential.helper store
```

---

### 5️⃣ النتيجة لا تظهر بعد إنشاء البطاقة

**السبب:** `display: none` في inline style

**التشخيص:**
```bash
# في المتصفح Console:
document.getElementById('result').style.display
# إذا طبعت 'none' - هذه المشكلة
```

**الحل:**
تأكد أن JavaScript يستخدم:
```javascript
document.getElementById('result').style.display = 'block';
```
بدلاً من الاعتماد على CSS class فقط.

---

### 6️⃣ Syntax Error في السطر 192

**السبب الأكثر شيوعاً:**
- String مكسور على سطرين
- تعليق Python في وسط JavaScript
- Quote مفتوحة ومش مسكرة

**التشخيص:**
```bash
# اختبر من الخادم
curl http://localhost:7070/settings 2>/dev/null | sed -n '190,195p'

# ابحث عن quotes مكسورة
grep "result.message + '" tools/web_app.py
```

**الحل:**
```bash
# تأكد أن كل string في سطر واحد
# ابحث عن السطر المكسور وأصلحه في nano
nano tools/web_app.py
```

---

## 🔄 إجراءات الصيانة الدورية

### تحديث الكود:
```bash
cd ~/maroof/maroof-cards

# اسحب آخر تحديثات
git pull origin main

# امسح cache
rm -rf tools/__pycache__
find . -name "*.pyc" -delete

# أعد تشغيل
sudo systemctl restart maroof.service
```

### فحص صحة النظام:
```bash
# 1. حالة الخادم
sudo systemctl status maroof.service

# 2. اختبار NFC
curl http://localhost:7070/api/nfc/test | jq

# 3. اختبار إنشاء بطاقة
curl -X POST http://localhost:7070/api/create \
  -H "Content-Type: application/json" \
  -d '{"name":"Test"}' | jq

# 4. شوف السجلات
sudo journalctl -u maroof.service -n 50
```

### نسخ احتياطي:
```bash
# نسخ المشروع
cd ~
tar -czf maroof-backup-$(date +%Y%m%d).tar.gz maroof/

# نقل للجهاز الآخر
scp maroof-backup-*.tar.gz user@server:/backups/
```

---

## 🔧 تعديل الكود بشكل آمن

### الخطوات الصحيحة:

1. **أوقف الخادم:**
```bash
sudo systemctl stop maroof.service
```

2. **عدّل الكود:**
```bash
cd ~/maroof/maroof-cards
nano tools/web_app.py
```

3. **اختبر يدوياً:**
```bash
python3 tools/web_app.py
# اضغط Ctrl+C للإيقاف
```

4. **إذا عمل - ارفع على GitHub:**
```bash
git add tools/web_app.py
git commit -m "وصف التعديل"
git push origin main
```

5. **شغّل الخادم:**
```bash
sudo systemctl start maroof.service
```

6. **امسح cache المتصفح:**
- Ctrl + Shift + Delete
- Clear cached images and files
- أو Ctrl + Shift + R (hard reload)

---

## 📊 فهم ملفات السجلات

### عرض السجلات:
```bash
# آخر 50 سطر
sudo journalctl -u maroof.service -n 50

# مباشر (real-time)
sudo journalctl -u maroof.service -f

# البحث عن أخطاء
sudo journalctl -u maroof.service | grep -i error
```

### فهم الرموز:
- `200 OK` - طلب ناجح
- `201 Created` - تم إنشاء مورد جديد (بطاقة)
- `404 Not Found` - الصفحة غير موجودة
- `500 Internal Server Error` - خطأ في الخادم
- `503 Service Unavailable` - الخدمة غير متاحة (NFC مثلاً)

---

## 🔐 الأمان

### ملاحظات أمنية:
1. **لا تشارك GitHub Token علناً**
2. **المنفذ 7070 مفتوح على الشبكة المحلية فقط**
3. **لا توجد مصادقة - للاستخدام الداخلي فقط**

### للاستخدام العام:
```bash
# أضف Basic Auth أو OAuth
# غيّر المنفذ لـ HTTPS مع certbot
# أضف rate limiting
```

---

## 📞 الدعم والمساعدة

### الموارد:
- **GitHub:** https://github.com/maroof-id/maroof-cards
- **nfcpy Docs:** https://nfcpy.readthedocs.io/
- **Flask Docs:** https://flask.palletsprojects.com/

### استكشاف الأخطاء:
1. **اقرأ السجلات أولاً:** `sudo journalctl -u maroof.service -n 50`
2. **تحقق من Console المتصفح:** F12 → Console
3. **اختبر من Terminal:** استخدم `curl` للاختبار المباشر
4. **امسح Cache دائماً:** بعد أي تعديل

---

## 📝 سجل التعديلات الكبرى

### يناير 2026:
- ✅ حل مشكلة String على سطرين في JavaScript
- ✅ حل مشكلة Python cache المستمر
- ✅ تغيير المنفذ من 8080 إلى 7070
- ✅ إضافة زر Test NFC Reader
- ✅ إصلاح display: none في result div
- ✅ منع النص العربي في الكود
- ✅ إضافة دليل الصيانة الشامل

---

## ⚡ نصائح للأداء

1. **لا تعيد تشغيل الخادم كثيراً** - يكفي عند التعديلات الكبيرة فقط
2. **استخدم Git بشكل منتظم** - commit صغيرة ومتكررة أفضل
3. **راقب استهلاك الذاكرة:** `htop` أو `free -h`
4. **نظف الـ cache دورياً:** كل أسبوع مرة

---

## 🎯 الخلاصة

### القواعد الذهبية الثلاث:
1. 🚫 **لا نص عربي في الكود**
2. 🧹 **امسح cache بعد كل تعديل**  
3. 🔄 **اختبر يدوياً قبل الرفع على GitHub**

### عند أي مشكلة:
1. اقرأ السجلات
2. امسح cache
3. أعد تشغيل الخادم
4. اختبر من متصفح نظيف

---

**تم إنشاء هذا الدليل:** يناير 2026  
**آخر تحديث:** يناير 2026  
**النسخة:** 1.0

🎉 **حظاً موفقاً في الصيانة!**
