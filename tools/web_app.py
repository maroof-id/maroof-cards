#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maroof Web App - Fixed for AITRIP PN532
"""

from flask import Flask, request, jsonify, render_template_string
import os
import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from create_card import CardGenerator
from nfc_writer import NFCWriter

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

generator = CardGenerator()

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
        }
        .nfc-btn {
            margin-top: 10px;
            background: #4CAF50;
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
            <button class="btn nfc-btn" id="nfcBtn" onclick="writeNFC()" style="display:none;">
                <i class="fas fa-wifi"></i> كتابة على NFC
            </button>
        </div>
    </div>
    
    <script>
        let currentUrl = '';
        
        document.getElementById('cardForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('submitBtn').disabled = true;
            
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
                    document.getElementById('result').className = 'result show success';
                    document.getElementById('resultTitle').textContent = '✅ تمت الإنشاء بنجاح!';
                    document.getElementById('resultMessage').innerHTML = 
                        `<strong>الرابط:</strong> <a href="${result.url}" target="_blank">${result.url}</a>`;
                    document.getElementById('nfcBtn').style.display = 'block';
                    document.getElementById('cardForm').reset();
                } else {
                    document.getElementById('result').className = 'result show error';
                    document.getElementById('resultTitle').textContent = '❌ حدث خطأ';
                    document.getElementById('resultMessage').textContent = result.error || 'خطأ غير معروف';
                    document.getElementById('nfcBtn').style.display = 'none';
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('submitBtn').disabled = false;
                document.getElementById('result').className = 'result show error';
                document.getElementById('resultTitle').textContent = '❌ خطأ في الاتصال';
                document.getElementById('resultMessage').textContent = error.toString();
                document.getElementById('nfcBtn').style.display = 'none';
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
            nfcBtn.innerHTML = '<div class="spinner"></div> جاري الكتابة...';
            
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
                    alert('✅ ' + result.message);
                } else {
                    alert('❌ ' + result.message);
                }
            } catch (error) {
                nfcBtn.disabled = false;
                nfcBtn.innerHTML = originalText;
                alert('❌ خطأ في الاتصال: ' + error);
            }
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
        <button class="btn" onclick="readCard()" id="readBtn">
            <i class="fas fa-book"></i> قراءة بطاقة NFC
        </button>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>جاري قراءة البطاقة...</p>
        </div>
        
        <div id="result" class="result">
            <h3 id="resultTitle"></h3>
            <pre id="resultContent"></pre>
        </div>
    </div>
    
    <script>
        async function readCard() {
            const readBtn = document.getElementById('readBtn');
            readBtn.disabled = true;
            document.getElementById('loading').style.display = 'block';
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

        # Git push in background with callback
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

    except ValueError as e:
        return jsonify({
            'success': False, 
            'error': f'❌ {str(e)}'
        }), 400
    except Exception as e:
        error_msg = str(e)
        return jsonify({
            'success': False, 
            'error': f'❌ خطأ: {error_msg} / Error: {error_msg}'
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

        writer = get_nfc_writer()
        if not writer:
            return jsonify({
                'success': False, 
                'message': '❌ قارئ NFC غير متصل / NFC reader not connected'
            }), 503

        ok, msg = writer.write_url(url, timeout=15)

        if ok:
            # Git push in background with callback
            def git_callback(success, git_msg):
                if not success:
                    print(f"⚠️ تحذير: فشل دفع البيانات / Warning: {git_msg}")
            
            generator.git_push_background(f"Write to NFC: {url}", callback=git_callback)
            return jsonify({'success': True, 'message': msg}), 200
        else:
            return jsonify({'success': False, 'message': msg}), 500

    except Exception as e:
        error_msg = str(e)
        return jsonify({
            'success': False, 
            'message': f'❌ خطأ: {error_msg} / Error: {error_msg}'
        }), 500

@app.route('/api/nfc/read', methods=['GET'])
def nfc_read():
    try:
        writer = get_nfc_writer()
        if not writer:
            return jsonify({
                'success': False, 
                'message': '❌ قارئ NFC غير متصل / NFC reader not connected'
            }), 503

        data, msg = writer.read_card(timeout=15)

        if data:
            return jsonify({'success': True, 'data': data, 'message': msg}), 200
        else:
            return jsonify({
                'success': False, 
                'message': msg
            }), 404

    except Exception as e:
        error_msg = str(e)
        return jsonify({
            'success': False, 
            'message': f'❌ خطأ: {error_msg} / Error: {error_msg}'
        }), 500

if __name__ == '__main__':
    # Initialize NFC on startup
    print("Initializing NFC reader...")
    writer = get_nfc_writer()
    if writer:
        print("✅ NFC reader ready!")
    else:
        print("⚠️ NFC reader not connected - some features may not work")
    
    # Run Flask app without debug mode in production
    app.run(host='0.0.0.0', port=5001, debug=False)


