#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maroof Web App - Enhanced NFC Stability
"""

import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from create_card import CardGenerator
from nfc_writer import NFCWriter

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

generator = CardGenerator()

# HTML Templates
HOME_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maroof - Create Card</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 10px;
        }
        .nav {
            max-width: 800px;
            margin: 0 auto 15px;
            display: flex;
            gap: 8px;
        }
        .nav-btn {
            flex: 1;
            padding: 12px 8px;
            background: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .nav-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 6px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }
        input, textarea, select {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:active { transform: translateY(0); }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .result {
            margin-top: 15px;
            padding: 15px;
            border-radius: 6px;
            display: none;
        }
        .result.show { display: block; }
        .result.success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .result.error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .result h3 {
            margin-bottom: 10px;
            font-size: 16px;
        }
        .result a {
            color: #667eea;
            word-break: break-all;
            text-decoration: underline;
        }
        .result p {
            font-size: 14px;
            line-height: 1.5;
            margin: 8px 0;
        }
        .nfc-btn {
            margin-top: 10px;
            background: #4CAF50;
        }
        .retry-btn {
            margin-top: 10px;
            background: #ff9800;
        }
        .loading {
            display: none;
            text-align: center;
            color: #667eea;
            margin: 15px 0;
        }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .help-box {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 12px;
            border-radius: 6px;
            margin: 10px 0;
            font-size: 13px;
            line-height: 1.6;
        }
        .help-box strong {
            display: block;
            margin-bottom: 5px;
        }
        @media (max-width: 600px) {
            .container { padding: 15px; }
            h1 { font-size: 1.5em; }
            .nav-btn { font-size: 12px; padding: 10px 6px; }
            input, textarea, select { font-size: 16px; }
        }
    </style>
</head>
<body>
    <div class="nav">
        <button class="nav-btn active" onclick="window.location.href='/'">
            <i class="fas fa-home"></i> الرئيسية
        </button>
        <button class="nav-btn" onclick="window.location.href='/settings'">
            <i class="fas fa-cog"></i> الإعدادات
        </button>
    </div>

    <div class="container">
        <h1>🎴 إنشاء بطاقة</h1>

        <form id="cardForm">
            <div class="form-group">
                <label>الاسم الكامل *</label>
                <input type="text" name="name" required placeholder="أدخل اسمك">
            </div>

            <div class="form-group">
                <label>رقم الجوال</label>
                <input type="tel" name="phone" placeholder="05xxxxxxxx">
            </div>

            <div class="form-group">
                <label>البريد الإلكتروني</label>
                <input type="email" name="email">
            </div>

            <div class="form-group">
                <label>Instagram</label>
                <input type="text" name="instagram" placeholder="username">
            </div>

            <div class="form-group">
                <label>LinkedIn</label>
                <input type="text" name="linkedin" placeholder="username">
            </div>

            <div class="form-group">
                <label>Twitter/X</label>
                <input type="text" name="twitter" placeholder="username">
            </div>

            <div class="form-group">
                <label>نبذة تعريفية</label>
                <textarea name="bio" placeholder="اكتب نبذة عنك"></textarea>
            </div>

            <div class="form-group">
                <label>القالب</label>
                <select name="template">
                    <option value="modern">عصري</option>
                    <option value="classic">كلاسيكي</option>
                    <option value="minimal">بسيط</option>
                </select>
            </div>

            <button type="submit" class="btn" id="submitBtn">إنشاء البطاقة</button>
        </form>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>جاري إنشاء البطاقة...</p>
        </div>

        <div id="result" class="result">
            <h3 id="resultTitle"></h3>
            <p id="resultMessage"></p>
            <div id="helpBox" class="help-box" style="display:none;"></div>
            <button class="btn nfc-btn" id="nfcBtn" onclick="writeNFC()" style="display:none;">
                <i class="fas fa-wifi"></i> كتابة على NFC
            </button>
            <button class="btn retry-btn" id="retryBtn" onclick="retryNFC()" style="display:none;">
                <i class="fas fa-redo"></i> إعادة المحاولة
            </button>
        </div>
    </div>

    <script>
        let currentUrl = '';
        let nfcRetryCount = 0;

        document.getElementById('cardForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);

            document.getElementById('loading').style.display = 'block';
            document.getElementById('submitBtn').disabled = true;
            document.getElementById('result').style.display = 'none';

            try {
                const response = await fetch('/api/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                document.getElementById('loading').style.display = 'none';
                document.getElementById('submitBtn').disabled = false;

                if (result.success) {
                    currentUrl = result.url;
                    nfcRetryCount = 0;
                    document.getElementById('result').className = 'result show success';
                    document.getElementById('resultTitle').textContent = '✅ تمت الإنشاء بنجاح!';
                    document.getElementById('resultMessage').innerHTML =
                        `<strong>الرابط:</strong> <a href="${result.url}" target="_blank">${result.url}</a>`;
                    document.getElementById('nfcBtn').style.display = 'block';
                    document.getElementById('retryBtn').style.display = 'none';
                    document.getElementById('helpBox').style.display = 'none';
                    document.getElementById('cardForm').reset();
                } else {
                    document.getElementById('result').className = 'result show error';
                    document.getElementById('resultTitle').textContent = '❌ حدث خطأ';
                    document.getElementById('resultMessage').textContent = result.error || 'خطأ غير معروف';
                    document.getElementById('nfcBtn').style.display = 'none';
                    document.getElementById('retryBtn').style.display = 'none';
                    document.getElementById('helpBox').style.display = 'none';
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('submitBtn').disabled = false;
                document.getElementById('result').className = 'result show error';
                document.getElementById('resultTitle').textContent = '❌ خطأ في الاتصال';
                document.getElementById('resultMessage').textContent = error.toString();
                document.getElementById('nfcBtn').style.display = 'none';
                document.getElementById('retryBtn').style.display = 'none';
                document.getElementById('helpBox').style.display = 'none';
            }
        });

        async function writeNFC() {
            if (!currentUrl) {
                alert('يرجى إنشاء بطاقة أولاً');
                return;
            }

            const nfcBtn = document.getElementById('nfcBtn');
            const originalText = nfcBtn.innerHTML;
            nfcBtn.disabled = true;
            nfcBtn.innerHTML = '<div class="spinner"></div> جاري الكتابة... ضع البطاقة على القارئ';

            document.getElementById('resultMessage').innerHTML =
                `<strong>الرابط:</strong> <a href="${currentUrl}" target="_blank">${currentUrl}</a><br>
                <em>⏳ جاري الكتابة... ضع بطاقة NFC على القارئ الآن</em>`;

            try {
                const response = await fetch('/api/nfc/write', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: currentUrl})
                });

                const result = await response.json();

                nfcBtn.disabled = false;
                nfcBtn.innerHTML = originalText;

                if (result.success) {
                    document.getElementById('result').className = 'result show success';
                    document.getElementById('resultTitle').textContent = '✅ نجحت الكتابة!';
                    document.getElementById('resultMessage').innerHTML =
                        `<strong>الرابط:</strong> <a href="${currentUrl}" target="_blank">${currentUrl}</a><br>
                        <strong>✅ ${result.message}</strong>`;
                    document.getElementById('helpBox').style.display = 'none';
                    document.getElementById('retryBtn').style.display = 'none';
                    nfcRetryCount = 0;
                } else {
                    nfcRetryCount++;
                    document.getElementById('result').className = 'result show error';
                    document.getElementById('resultTitle').textContent = '❌ فشلت الكتابة';
                    document.getElementById('resultMessage').innerHTML =
                        `<strong>❌ ${result.message}</strong>`;

                    // Show help based on error
                    const helpBox = document.getElementById('helpBox');
                    if (result.message.includes('Cannot connect') || result.message.includes('غير متصل')) {
                        helpBox.innerHTML = `
                            <strong>⚠️ القارئ غير متصل:</strong>
                            1. افصل قارئ NFC من USB<br>
                            2. انتظر 5 ثواني<br>
                            3. وصّله مرة أخرى<br>
                            4. اضغط "إعادة المحاولة"
                        `;
                        helpBox.style.display = 'block';
                        document.getElementById('retryBtn').style.display = 'block';
                    } else if (result.message.includes('NDEF') || result.message.includes('لا تدعم')) {
                        helpBox.innerHTML = `
                            <strong>⚠️ البطاقة غير مدعومة:</strong>
                            هذه البطاقة لا تدعم NDEF.<br>
                            استخدم بطاقة <strong>NTAG213</strong> أو <strong>NTAG215</strong> أو <strong>NTAG216</strong>
                        `;
                        helpBox.style.display = 'block';
                        document.getElementById('retryBtn').style.display = 'block';
                    } else if (result.message.includes('No card') || result.message.includes('لم يتم اكتشاف')) {
                        helpBox.innerHTML = `
                            <strong>⚠️ لم يتم اكتشاف بطاقة:</strong>
                            1. تأكد من وضع البطاقة بشكل صحيح على القارئ<br>
                            2. حاول مرة أخرى
                        `;
                        helpBox.style.display = 'block';
                        document.getElementById('retryBtn').style.display = 'block';
                    } else {
                        helpBox.style.display = 'none';
                        document.getElementById('retryBtn').style.display = 'block';
                    }
                }
            } catch (error) {
                nfcBtn.disabled = false;
                nfcBtn.innerHTML = originalText;
                document.getElementById('result').className = 'result show error';
                document.getElementById('resultTitle').textContent = '❌ خطأ في الاتصال';
                document.getElementById('resultMessage').textContent = error.toString();
                document.getElementById('retryBtn').style.display = 'block';
            }
        }

        function retryNFC() {
            if (nfcRetryCount >= 3) {
                if (confirm('تم المحاولة 3 مرات. هل تريد الذهاب لصفحة الإعدادات لاختبار القارئ؟')) {
                    window.location.href = '/settings';
                }
                return;
            }
            writeNFC();
        }
    </script>
</body>
</html>
"""

SETTINGS_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maroof - Settings</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 10px;
        }
        .nav {
            max-width: 800px;
            margin: 0 auto 15px;
            display: flex;
            gap: 8px;
        }
        .nav-btn {
            flex: 1;
            padding: 12px 8px;
            background: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
        }
        .nav-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 10px;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .btn-test {
            background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        }
        .result {
            margin-top: 15px;
            padding: 15px;
            border-radius: 6px;
            display: none;
        }
        .result.show { display: block; }
        .result.success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .result.error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .result pre {
            background: rgba(0,0,0,0.05);
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 12px;
        }
        .help-box {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 12px;
            border-radius: 6px;
            margin: 10px 0;
            font-size: 13px;
            line-height: 1.6;
        }
        .loading {
            display: none;
            text-align: center;
            color: #667eea;
        }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @media (max-width: 600px) {
            .container { padding: 15px; }
            h1 { font-size: 1.5em; }
            .nav-btn { font-size: 12px; padding: 10px 6px; }
        }
    </style>
</head>
<body>
    <div class="nav">
        <button class="nav-btn" onclick="window.location.href='/'">
            <i class="fas fa-home"></i> الرئيسية
        </button>
        <button class="nav-btn active">
            <i class="fas fa-cog"></i> الإعدادات
        </button>
    </div>

    <div class="container">
        <h1>⚙️ الإعدادات</h1>

        <button class="btn btn-test" onclick="testReader()" id="testBtn">
            <i class="fas fa-stethoscope"></i> اختبار قارئ NFC
        </button>

        <button class="btn" onclick="readCard()" id="readBtn">
            <i class="fas fa-book"></i> قراءة بطاقة NFC
        </button>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p id="loadingText">جاري الاختبار...</p>
        </div>

        <div id="result" class="result">
            <h3 id="resultTitle"></h3>
            <pre id="resultContent"></pre>
        </div>

        <div class="help-box" style="margin-top: 20px;">
            <strong>💡 نصائح:</strong><br>
            • إذا فشل الاتصال، افصل القارئ ووصّله مرة أخرى<br>
            • استخدم بطاقات NTAG213/215/216 للحصول على أفضل النتائج<br>
            • تأكد من وضع البطاقة بشكل صحيح على القارئ
        </div>
    </div>

    <script>
        async function testReader() {
            const testBtn = document.getElementById('testBtn');
            testBtn.disabled = true;
            document.getElementById('loading').style.display = 'block';
            document.getElementById('loadingText').textContent = 'جاري اختبار القارئ...';
            document.getElementById('result').style.display = 'none';

            try {
                const response = await fetch('/api/nfc/test');
                const result = await response.json();

                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
                testBtn.disabled = false;

                if (result.success) {
                    document.getElementById('result').className = 'result show success';
                    document.getElementById('resultTitle').textContent = '✅ القارئ يعمل بشكل صحيح';
                    document.getElementById('resultContent').textContent = result.message;
                } else {
                    document.getElementById('result').className = 'result show error';
                    document.getElementById('resultTitle').textContent = '❌ فشل الاتصال';
                    document.getElementById('resultContent').textContent = result.message + '\n\n⚠️ افصل القارئ من USB، انتظر 5 ثواني، ووصّله مرة أخرى ثم أعد المحاولة';
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
                document.getElementById('result').className = 'result show error';
                document.getElementById('resultTitle').textContent = '❌ خطأ في الاتصال';
                document.getElementById('resultContent').textContent = error.toString();
                testBtn.disabled = false;
            }
        }

        async function readCard() {
            const readBtn = document.getElementById('readBtn');
            readBtn.disabled = true;
            document.getElementById('loading').style.display = 'block';
            document.getElementById('loadingText').textContent = 'ضع البطاقة على القارئ...';
            document.getElementById('result').style.display = 'none';

            try {
                const response = await fetch('/api/nfc/read');
                const result = await response.json();

                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
                readBtn.disabled = false;

                if (result.success && result.data) {
                    document.getElementById('result').className = 'result show success';
                    document.getElementById('resultTitle').textContent = '✅ تمت القراءة بنجاح';
                    document.getElementById('resultContent').textContent = JSON.stringify(result.data, null, 2);
                } else {
                    document.getElementById('result').className = 'result show error';
                    document.getElementById('resultTitle').textContent = '❌ خطأ في القراءة';
                    document.getElementById('resultContent').textContent = result.message || 'خطأ غير معروف';
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
                document.getElementById('result').className = 'result show error';
                document.getElementById('resultTitle').textContent = '❌ خطأ في الاتصال';
                document.getElementById('resultContent').textContent = error.toString();
                readBtn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HOME_PAGE)

@app.route('/settings')
def settings():
    return render_template_string(SETTINGS_PAGE)

@app.route('/api/nfc/test', methods=['GET'])
def nfc_test():
    """Test NFC reader connection"""
    try:
        writer = NFCWriter()
        if writer.connect():
            writer.close()
            return jsonify({
                'success': True,
                'message': '✅ القارئ متصل ويعمل بشكل صحيح / NFC reader connected and working'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '❌ فشل الاتصال بالقارئ / Failed to connect to NFC reader'
            }), 503
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'❌ خطأ: {str(e)} / Error: {str(e)}'
        }), 500

@app.route('/api/create', methods=['POST'])
def create_card():
    try:
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()

        if not name:
            return jsonify({
                'success': False,
                'error': '❌ الاسم مطلوب / Name is required'
            }), 400

        result = generator.create_card(
            name=name,
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            instagram=data.get('instagram', ''),
            linkedin=data.get('linkedin', ''),
            twitter=data.get('twitter', ''),
            bio=data.get('bio', ''),
            template=data.get('template', 'modern')
        )

        def git_callback(success, msg):
            if not success:
                print(f"⚠️ تحذير: فشل دفع البيانات / Warning: {msg}")

        generator.git_push_background(f"Add card: {name}", callback=git_callback)

        return jsonify({
            'success': True,
            'url': result['url'],
            'username': result['username'],
            'message': '✅ تمت الإنشاء بنجاح / Card created successfully'
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'❌ خطأ: {str(e)} / Error: {str(e)}'
        }), 500

@app.route('/api/nfc/write', methods=['POST'])
def nfc_write():
    try:
        data = request.get_json() or {}
        url = data.get('url', '')

        if not url:
            return jsonify({
                'success': False,
                'message': '❌ الرابط مطلوب / URL is required'
            }), 400

        writer = NFCWriter()
        ok, msg = writer.write_url(url, timeout=15)
        writer.close()

        if ok:
            def git_callback(success, git_msg):
                if not success:
                    print(f"⚠️ تحذير: فشل دفع البيانات / Warning: {git_msg}")

            generator.git_push_background(f"Write to NFC: {url}", callback=git_callback)
            return jsonify({'success': True, 'message': msg}), 200
        else:
            return jsonify({'success': False, 'message': msg}), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'❌ خطأ: {str(e)} / Error: {str(e)}'
        }), 500

@app.route('/api/nfc/read', methods=['GET'])
def nfc_read():
    try:
        writer = NFCWriter()
        data, msg = writer.read_card(timeout=15)
        writer.close()

        if data:
            return jsonify({'success': True, 'data': data, 'message': msg}), 200
        else:
            return jsonify({
                'success': False,
                'message': msg
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'❌ خطأ: {str(e)} / Error: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🚀 Maroof NFC System Starting...")
    print("📍 Server will run on: http://0.0.0.0:8080")
    print("⚠️  Note: NFC reader will connect on-demand for better stability")
    app.run(host='0.0.0.0', port=8080, debug=False)