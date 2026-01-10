# 📘 Maroof NFC System - دليل إعداد وصيانة شامل

## 📋 معلومات المشروع

**اسم المشروع:** Maroof - Digital Business Cards with NFC  
**التاريخ:** يناير 2026  
**المنصة:** Raspberry Pi 5  
**نظام التشغيل:** Raspberry Pi OS (Debian Bookworm)  
**لغة البرمجة:** Python 3.11

---

## 🔌 المعدات المستخدمة

### قارئ NFC

**الموديل:** AITRIP 2Sets PN532 V2.0 NFC RFID Wireless Module  
**المواصفات الكاملة:**
- نوع الشريحة: PN532 (NXP Semiconductors)
- التردد: 13.56 MHz
- البروتوكولات المدعومة: ISO/IEC 14443 Type A & B
- البطاقات المدعومة: NTAG213/215/216, Mifare Classic, Mifare Ultralight

**واجهات الاتصال المتاحة:**
- ✅ **UART (HSU)** - تم استخدامها بنجاح
- I2C (IIC)
- SPI
- USB Type-C

**محول USB المستخدم:**
- CH340 Serial Converter
- معرف USB: `1a86:7523` (QinHeng Electronics CH340)
- المنفذ: `/dev/ttyUSB0`

---

## 🔧 إعدادات الجهاز الفيزيائية

### مفاتيح DIP (مهم جداً!)

يحتوي قارئ AITRIP PN532 على مفاتيح DIP للتبديل بين وضعيات الاتصال:

```
للوضع UART/HSU (المستخدم في هذا المشروع):
┌─────────┐
│ 1: ON   │  ← Switch 1
│ 2: OFF  │  ← Switch 2
└─────────┘

للوضع I2C:
┌─────────┐
│ 1: OFF  │
│ 2: ON   │
└─────────┘

للوضع SPI:
┌─────────┐
│ 1: OFF  │
│ 2: OFF  │
└─────────┘
```

**⚠️ ملاحظة حرجة:** إذا كانت المفاتيح في وضع خاطئ، لن يعمل القارئ!

---

## 📦 المكتبات والتبعيات

### المشكلة الرئيسية التي واجهناها

**المشكلة:**
```python
ImportError: cannot import name 'message_decoder' from 'ndef'
```

**السبب:**
- `nfcpy` يعتمد على مكتبة `ndeflib` (وليس `ndef`)
- كانت مكتبة `ndef` القديمة (v0.2) مثبتة
- `nfcpy` يبحث عن دوال موجودة فقط في `ndeflib`

**الحل النهائي:**
```bash
# 1. حذف المكتبة القديمة
pip3 uninstall --break-system-packages -y ndef

# 2. إعادة تثبيت nfcpy (سيثبت ndeflib تلقائياً)
pip3 install --break-system-packages nfcpy

# 3. التحقق
pip3 list | grep ndef
# يجب أن ترى: ndeflib (وليس ndef)
```

### قائمة التبعيات النهائية

في ملف `tools/requirements.txt`:

```txt
# Maroof - Digital Business Cards with NFC
flask>=2.3.0
nfcpy>=1.0.4
qrcode>=7.4.2
Pillow>=10.0.0
```

**المكتبات المثبتة تلقائياً مع nfcpy:**
- `ndeflib==0.3.3` (مهم!)
- `libusb1`
- `pyserial`
- `pydes`

---

## 🔍 طريقة اكتشاف المنفذ الصحيح

### المحاولة والخطأ

جربنا المنافذ التالية:

| المنفذ | النتيجة | الملاحظات |
|--------|---------|-----------|
| `usb` | ❌ فشل | [Errno 19] No such device |
| `usb:1a86:7523` | ❌ فشل | القارئ ليس USB مباشر |
| `tty:/dev/ttyUSB0:pn532` | ❌ فشل | [Errno 19] No such device |
| **`tty:USB0:pn532`** | ✅ **نجح!** | المنفذ الصحيح |

### كود الاختبار الذي نجح

```python
#!/usr/bin/env python3
import nfc
import time

print("Testing PN532 connection...")
print("=" * 50)

transports = [
    'tty:/dev/ttyUSB0:pn532',
    'tty:USB0:pn532',           # ← هذا نجح!
    'tty:/dev/ttyUSB0',
]

for transport in transports:
    try:
        print(f"\nTrying: {transport}")
        clf = nfc.ContactlessFrontend(transport)
        print(f"SUCCESS! Device: {clf}")
        
        print("\nPlace NFC card now (5 seconds)...")
        start = time.time()
        tag = None
        
        while time.time() - start < 5:
            try:
                tag = clf.connect(rdwr={'on-connect': lambda t: False})
                if tag:
                    break
            except:
                time.sleep(0.1)
        
        if tag:
            print(f"Card detected: {tag}")
            print(f"UID: {tag.identifier.hex()}")
        else:
            print("No card detected (timeout)")
        
        clf.close()
        print(f"\nUse this transport: {transport}")
        break
        
    except Exception as e:
        print(f"Failed: {e}")

print("\n" + "=" * 50)
```

**النتيجة الناجحة:**
```
Trying: tty:USB0:pn532
SUCCESS! Device: PN532 on /dev/ttyUSB0

Place NFC card now (5 seconds)...
Card detected: Type2Tag ID=9421FAE5
UID: 9421fae5

Use this transport: tty:USB0:pn532
```

---

## 🚀 إعداد النظام من الصفر

### 1. التحقق من اتصال USB

```bash
# فحص أجهزة USB
lsusb

# يجب أن ترى:
# Bus 003 Device 008: ID 1a86:7523 QinHeng Electronics CH340 serial converter

# فحص المنافذ Serial
ls -la /dev/ttyUSB*

# يجب أن ترى:
# crw-rw---- 1 root dialout 188, 0 Jan  8 15:30 /dev/ttyUSB0
```

### 2. إضافة المستخدم لمجموعة dialout

```bash
# إضافة المستخدم
sudo usermod -a -G dialout $USER

# التحقق
groups

# يجب أن ترى: dialout في القائمة

# ⚠️ مهم: قد تحتاج لإعادة تسجيل الدخول
```

### 3. تثبيت التبعيات

```bash
cd ~/maroof/maroof-cards

# تثبيت المكتبات
pip3 install --break-system-packages -r tools/requirements.txt

# التحقق من nfcpy
python3 -c "import nfc; print('nfc works')"

# يجب أن ترى: nfc works
```

### 4. اختبار القارئ

```bash
# اختبار الاتصال
python3 tools/nfc_writer.py --read

# اختبار الكتابة
python3 tools/nfc_writer.py --url "https://example.com"
```

---

## 📝 بنية المشروع

```
maroof-cards/
├── tools/
│   ├── create_card.py      # مولد البطاقات
│   ├── nfc_writer.py       # معالج NFC (محدث!)
│   ├── web_app.py          # واجهة الويب (محدث!)
│   └── requirements.txt    # التبعيات (محدث!)
├── templates/
│   ├── modern.html         # قالب عصري
│   ├── classic.html        # قالب كلاسيكي
│   └── minimal.html        # قالب بسيط
├── clients/
│   └── [username]/
│       ├── index.html      # صفحة البطاقة
│       ├── data.json       # بيانات البطاقة
│       └── contact.vcf     # ملف vCard
├── .gitignore              # (جديد!)
└── README.md
```

---

## 🔧 الأكواد المحدثة

### nfc_writer.py (النسخة النهائية)

**التحديثات الرئيسية:**

1. **المنفذ الصحيح:**
```python
transports = [
    ('tty:USB0:pn532', 'PN532 on USB0'),        # ← المنفذ الذي يعمل
    ('tty:/dev/ttyUSB0:pn532', 'PN532 backup'), # منفذ احتياطي
]
```

2. **دوال ترجع قيمتين:**
```python
def write_url(self, url: str, timeout: int = 10) -> Tuple[bool, str]:
    """Returns (success, message)"""
    # ...
    return True, "Successfully written to NFC"

def read_card(self, timeout: int = 10) -> Tuple[Optional[Dict], str]:
    """Returns (data, message)"""
    # ...
    return result, "Successfully read card"
```

3. **استخدام ndeflib بشكل صحيح:**
```python
import ndeflib

# إنشاء سجل URI
uri_record = ndeflib.Record('urn:nfc:wkt:U', data=url.encode())
message = [uri_record]
```

### web_app.py (النسخة النهائية)

**التحديثات الرئيسية:**

1. **كائن NFC عام:**
```python
# Global NFC writer instance
nfc_writer = None

def get_nfc_writer():
    """Get or create NFC writer instance"""
    global nfc_writer
    if nfc_writer is None:
        nfc_writer = NFCWriter()
        if not nfc_writer.connect():
            return None
    return nfc_writer
```

2. **استخدام الكائن العام:**
```python
@app.route('/api/nfc/write', methods=['POST'])
def nfc_write():
    writer = get_nfc_writer()  # ← لا ننشئ كائن جديد
    if not writer:
        return jsonify({'success': False, 'message': 'NFC reader not connected'}), 500
    
    ok, msg = writer.write_url(url, timeout=10)
    # ...
```

3. **تهيئة NFC عند بدء التشغيل:**
```python
if __name__ == '__main__':
    # Initialize NFC on startup
    print("Initializing NFC reader...")
    writer = get_nfc_writer()
    if writer:
        print("NFC reader ready!")
    else:
        print("Warning: NFC reader not connected")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
```

---

## 🐛 الأخطاء الشائعة وحلولها

### خطأ 1: ImportError: cannot import name 'message_decoder'

**السبب:** مكتبة `ndef` القديمة مثبتة بدلاً من `ndeflib`

**الحل:**
```bash
pip3 uninstall --break-system-packages -y ndef
pip3 install --break-system-packages nfcpy
```

---

### خطأ 2: [Errno 19] No such device

**السبب:** المنفذ المستخدم غير صحيح

**الحل:** استخدم `tty:USB0:pn532` بدلاً من `tty:/dev/ttyUSB0:pn532`

---

### خطأ 3: Permission denied on /dev/ttyUSB0

**السبب:** المستخدم ليس في مجموعة dialout

**الحل:**
```bash
sudo usermod -a -G dialout $USER
# ثم أعد تسجيل الدخول
```

---

### خطأ 4: NFC reader not connected (في web_app)

**السبب:** يتم إنشاء كائن NFCWriter جديد في كل طلب بدون الاتصال

**الحل:** استخدام كائن عام مع دالة `get_nfc_writer()`

---

### خطأ 5: Port 5001 already in use

**السبب:** خادم Flask يعمل بالفعل

**الحل:**
```bash
# إيقاف العملية
sudo lsof -t -i:5001 | xargs sudo kill -9

# أو استخدام منفذ مختلف
python3 tools/web_app.py --port 5002
```

---

## 🧪 اختبارات التحقق

### اختبار 1: تثبيت المكتبات

```bash
# التحقق من nfcpy
python3 -c "import nfc; print('✅ nfc OK')"

# التحقق من ndeflib
python3 -c "import ndeflib; print('✅ ndeflib OK')"

# التحقق من flask
python3 -c "import flask; print('✅ flask OK')"
```

---

### اختبار 2: اتصال NFC

```bash
# اختبار قراءة
python3 tools/nfc_writer.py --read

# النتيجة المتوقعة:
# Searching for NFC reader...
# Trying PN532 on USB0...
# Connected: PN532 on /dev/ttyUSB0
# 
# Place card on reader to read...
# Card detected: Type2Tag ID=9421FAE5
# UID: 9421fae5
```

---

### اختبار 3: كتابة NFC

```bash
# اختبار كتابة
python3 tools/nfc_writer.py --url "https://maroof-id.github.io/maroof-cards/test"

# النتيجة المتوقعة:
# Ready to write: https://maroof-id.github.io/maroof-cards/test
# Place card on reader...
# Card detected: Type2Tag ID=9421FAE5
# Successfully written to NFC!
```

---

### اختبار 4: تطبيق الويب

```bash
# تشغيل الخادم
python3 tools/web_app.py

# النتيجة المتوقعة:
# Initializing NFC reader...
# Searching for NFC reader...
# Trying PN532 on USB0...
# Connected: PN532 on /dev/ttyUSB0
# NFC reader ready!
# * Serving Flask app 'web_app'
# * Debug mode: on
# * Running on all addresses (0.0.0.0)
# * Running on http://127.0.0.1:5001
# * Running on http://192.168.x.x:5001
```

افتح المتصفح: `http://raspberrypi.local:5001`

---

## 🔄 سير العمل اليومي

### إنشاء بطاقة جديدة

1. افتح `http://raspberrypi.local:5001`
2. املأ البيانات (الاسم، الهاتف، البريد، إلخ)
3. اضغط "Create Card"
4. سيتم رفع البطاقة تلقائياً إلى GitHub Pages
5. اضغط "Write to NFC"
6. ضع البطاقة على القارئ
7. انتظر رسالة "Successfully written"

### قراءة بطاقة موجودة

1. افتح `http://raspberrypi.local:5001/settings`
2. اضغط "Read Card"
3. ضع البطاقة على القارئ
4. ستظهر بيانات البطاقة

---

## 📊 المعلومات التقنية المتقدمة

### تفاصيل بروتوكول UART

**الإعدادات:**
- Baud Rate: 115200 (افتراضي للـ PN532)
- Data Bits: 8
- Parity: None
- Stop Bits: 1
- Flow Control: None

### تنسيق NDEF

البطاقات تستخدم تنسيق NDEF (NFC Data Exchange Format):

```
NDEF Message:
└── Record (URI)
    ├── Type: urn:nfc:wkt:U (Well-Known Type: URI)
    ├── ID: (فارغ)
    └── Payload: https://maroof-id.github.io/maroof-cards/username
```

### أنواع البطاقات المدعومة

| النوع | الذاكرة | الاستخدام |
|------|---------|-----------|
| NTAG213 | 144 bytes | بطاقات عمل بسيطة |
| NTAG215 | 504 bytes | بطاقات عمل + بيانات إضافية |
| NTAG216 | 888 bytes | بطاقات متقدمة |
| Mifare Classic 1K | 1KB | بطاقات قديمة |

**موصى به:** NTAG215 أو NTAG216

---

## 🔐 الأمان وأفضل الممارسات

### 1. حماية GitHub Credentials

**❌ الطريقة غير الآمنة (الحالية):**
```bash
echo "https://USERNAME:TOKEN@github.com" > ~/.git-credentials
```

**✅ الطريقة الآمنة (موصى بها):**
```bash
# استخدام GitHub CLI
gh auth login

# أو استخدام SSH keys
ssh-keygen -t ed25519 -C "maroof@raspberrypi"
# ثم أضف المفتاح العام إلى GitHub
```

### 2. ملف .gitignore

```gitignore
# Python
__pycache__/
*.pyc
*.pyo

# Virtual Environment
venv/
env/

# Credentials
.env
.git-credentials
*.pem
*.key

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# Backup
*.bak
*.backup
```

### 3. متغيرات البيئة

```bash
# إنشاء ملف .env
cat > .env << 'EOF'
FLASK_SECRET_KEY=your-secret-key-here
GITHUB_USERNAME=maroof-id
GITHUB_REPO=maroof-cards
NFC_TIMEOUT=10
EOF

# تحميل في Python
from dotenv import load_dotenv
load_dotenv()
```

---

## 🔧 الصيانة والتحديثات

### تحديث المكتبات

```bash
# تحديث كل المكتبات
pip3 install --break-system-packages --upgrade flask nfcpy qrcode Pillow

# التحقق من الإصدارات
pip3 list | grep -E "(flask|nfcpy|ndeflib)"
```

### النسخ الاحتياطي

```bash
# نسخ احتياطي يومي
DATE=$(date +%Y%m%d)
cd ~/maroof
tar -czf maroof-backup-$DATE.tar.gz maroof-cards/

# الاحتفاظ بآخر 7 نسخ فقط
ls -t maroof-backup-*.tar.gz | tail -n +8 | xargs rm -f
```

### تنظيف النظام

```bash
# حذف ملفات Python المؤقتة
find ~/maroof/maroof-cards -type d -name __pycache__ -exec rm -rf {} +
find ~/maroof/maroof-cards -name "*.pyc" -delete

# حذف ملفات log القديمة
find ~/maroof/maroof-cards -name "*.log" -mtime +30 -delete
```

---

## 📚 مراجع ومصادر

### وثائق رسمية

1. **nfcpy Documentation**  
   https://nfcpy.readthedocs.io/

2. **PN532 User Manual**  
   https://www.nxp.com/docs/en/user-guide/141520.pdf

3. **NDEF Specification**  
   https://nfc-forum.org/our-work/specification-releases/

4. **Flask Documentation**  
   https://flask.palletsprojects.com/

### موارد إضافية

1. **AITRIP PN532 GitHub**  
   https://github.com/elechouse/PN532

2. **Raspberry Pi NFC Guide**  
   https://www.raspberrypi.com/documentation/

3. **ndeflib Examples**  
   https://github.com/nfcpy/ndeflib

---

## 🎓 الدروس المستفادة

### 1. تعارض المكتبات

**الدرس:** `ndef` و `ndeflib` مكتبتان مختلفتان لكن بأسماء متشابهة.  
**الحل:** دائماً تحقق من التبعيات الفعلية في `requirements.txt`

### 2. المنافذ في Linux

**الدرس:** `/dev/ttyUSB0` و `USB0` ليسا نفس الشيء في `nfcpy`.  
**الحل:** جرّب صيغ متعددة واحفظ الناجحة

### 3. الكائنات العامة في Flask

**الدرس:** إنشاء كائن جديد في كل طلب HTTP مكلف ويسبب مشاكل.  
**الحل:** استخدم كائن عام مع دالة getter

### 4. مفاتيح DIP

**الدرس:** إعدادات الجهاز الفيزيائية بنفس أهمية الكود.  
**الحل:** دائماً وثّق الإعدادات الفيزيائية

### 5. الأوامر بالعربي

**الدرس:** الأوامر بالعربي تتحول إلى `???` في بعض الأنظمة.  
**الحل:** استخدم الإنجليزية في الأكواد والتعليقات الإنجليزية

---

## ✅ قائمة التحقق للإعداد الجديد

عند إعداد النظام على جهاز جديد، اتبع هذه الخطوات:

- [ ] توصيل قارئ NFC عبر USB
- [ ] التحقق من `lsusb` - يجب أن ترى CH340
- [ ] ضبط مفاتيح DIP: Switch 1=ON, Switch 2=OFF
- [ ] إضافة المستخدم لمجموعة dialout
- [ ] إعادة تسجيل الدخول
- [ ] استنساخ المشروع من GitHub
- [ ] تثبيت التبعيات من requirements.txt
- [ ] اختبار `python3 -c "import nfc"`
- [ ] اختبار قراءة NFC: `python3 tools/nfc_writer.py --read`
- [ ] اختبار كتابة NFC
- [ ] إعداد GitHub credentials
- [ ] اختبار تطبيق الويب
- [ ] إنشاء بطاقة تجريبية

---

## 📞 الدعم والمساعدة

### عند مواجهة مشكلة

1. راجع قسم "الأخطاء الشائعة"
2. تحقق من الإعدادات الفيزيائية (مفاتيح DIP)
3. شغّل التشخيص الكامل:

```bash
# سكريبت تشخيص شامل
cat > ~/diagnose.sh << 'BASH'
#!/bin/bash
echo "=== Maroof NFC Diagnostics ==="
echo ""
echo "1. USB Devices:"
lsusb | grep -i "ch340\|1a86"
echo ""
echo "2. Serial Ports:"
ls -la /dev/ttyUSB* 2>/dev/null
echo ""
echo "3. User Groups:"
groups | grep dialout && echo "✅ dialout OK" || echo "❌ dialout missing"
echo ""
echo "4. Python Packages:"
pip3 list | grep -E "(nfc|ndef)"
echo ""
echo "5. NFC Test:"
python3 -c "import nfc; print('✅ nfc OK')" 2>&1
echo ""
echo "6. Port Permissions:"
ls -la /dev/ttyUSB0 2>/dev/null
BASH

chmod +x ~/diagnose.sh
~/diagnose.sh
```

4. أرسل نتائج التشخيص للدعم

---

## 📅 سجل التحديثات

### v1.0 - 2026-01-08

- ✅ إصلاح مشكلة `ndef` vs `ndeflib`
- ✅ اكتشاف المنفذ الصحيح: `tty:USB0:pn532`
- ✅ تحديث `nfc_writer.py` للعمل مع AITRIP PN532
- ✅ تحديث `web_app.py` لاستخدام كائن NFC عام
- ✅ إضافة ملف `.gitignore`
- ✅ توثيق كامل للنظام

---

## 🎯 الخلاصة

**ما يعمل:**
- ✅ قارئ AITRIP PN532 عبر CH340 على `tty:USB0:pn532`
- ✅ مكتبة `nfcpy 1.0.4` مع `ndeflib 0.3.3`
- ✅ قراءة وكتابة بطاقات NTAG
- ✅ تطبيق ويب Flask للإدارة
- ✅ رفع تلقائي إلى GitHub Pages

**ما لا يعمل:**
- ❌ المنافذ: `usb`, `tty:/dev/ttyUSB0:pn532`
- ❌ مكتبة `ndef` القديمة (v0.2)

**نصيحة أخيرة:**
احتفظ بهذا الملف! إنه يحتوي على كل ما تعلمناه من التجربة والخطأ. ستوفر عليك ساعات عند الإعداد القادم! 🚀

---

**تم الإعداد بواسطة:** Claude AI  
**التاريخ:** 8 يناير 2026  
**الإصدار:** 1.0  
**الحالة:** ✅ مختبر وجاهز للإنتاج