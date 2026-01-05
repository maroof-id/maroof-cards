#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maroof Web App - Web interface for creating digital business cards
"""

from flask import Flask, request, jsonify, render_template_string, send_from_directory
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
            padding: 20px;
        }
        
        .nav {
            max-width: 800px;
            margin: 0 auto 20px;
            display: flex;
            gap: 10px;
        }
        
        .nav-btn {
            flex: 1;
            padding: 15px;
            background: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
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
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 30px;
            font-size: 2em;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .btn:hover { transform: translateY(-2px); }
        .btn:active { transform: translateY(0); }
        
        .result {
            margin-top: 20px;
            padding: 20px;
            background: #f0f7ff;
            border-radius: 8px;
            display: none;
        }
        
        .result.show { display: block; }
        .result h3 { color: #667eea; margin-bottom: 15px; }
        .result a { color: #667eea; word-break: break-all; }
        
        .nfc-btn {
            margin-top: 15px;
            background: #4CAF50;
        }
    </style>
</head>
<body>
    <div class="nav">
        <button class="nav-btn active" onclick="window.location.href='/'">
            <i class="fas fa-home"></i> الرئيسية / Home
        </button>
        <button class="nav-btn" onclick="window.location.href='/settings'">
            <i class="fas fa-cog"></i> الإعدادات / Settings
        </button>
    </div>
    
    <div class="container">
        <h1>🎴 إنشاء بطاقة / Create Card</h1>
        
        <form id="cardForm">
            <div class="form-group">
                <label>الاسم الكامل / Full Name *</label>
                <input type="text" name="name" required>
            </div>
            
            <div class="form-group">
                <label>رقم الجوال / Phone</label>
                <input type="tel" name="phone" placeholder="05xxxxxxxx">
            </div>
            
            <div class="form-group">
                <label>البريد الإلكتروني / Email</label>
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
                <label>نبذة تعريفية / Bio</label>
                <textarea name="bio"></textarea>
            </div>
            
            <div class="form-group">
                <label>القالب / Template</label>
                <select name="template">
                    <option value="modern">عصري / Modern</option>
                    <option value="classic">كلاسيكي / Classic</option>
                    <option value="minimal">بسيط / Minimal</option>
                </select>
            </div>
            
            <button type="submit" class="btn">إنشاء البطاقة / Create Card</button>
        </form>
        
        <div id="result" class="result">
            <h3>✅ تم إنشاء البطاقة بنجاح! / Card Created Successfully!</h3>
            <p><strong>الرابط / Link:</strong> <a id="cardUrl" href="#" target="_blank"></a></p>
            <button class="btn nfc-btn" onclick="writeNFC()">
                <i class="fas fa-wifi"></i> كتابة على NFC / Write to NFC
            </button>
        </div>
    </div>
    
    <script>
        let currentUrl = '';
        
        document.getElementById('cardForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    currentUrl = result.url;
                    document.getElementById('cardUrl').href = result.url;
                    document.getElementById('cardUrl').textContent = result.url;
                    document.getElementById('result').classList.add('show');
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Error: ' + error);
            }
        });
        
        async function writeNFC() {
            if (!currentUrl) {
                alert('Please create a card first');
                return;
            }
            
            try {
                const response = await fetch('/api/nfc/write', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: currentUrl})
                });
                
                const result = await response.json();
                alert(result.message);
            } catch (error) {
                alert('Write error: ' + error);
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
            padding: 20px;
        }
        
        .nav {
            max-width: 800px;
            margin: 0 auto 20px;
            display: flex;
            gap: 10px;
        }
        
        .nav-btn {
            flex: 1;
            padding: 15px;
            background: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
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
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 30px;
            font-size: 2em;
        }
        
        .action-grid {
            display: grid;
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .action-btn {
            padding: 20px;
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            cursor: pointer;
            font-size: 18px;
            font-weight: 600;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .action-btn i {
            font-size: 24px;
            width: 40px;
        }
        
        .read-btn { border-color: #2196F3; color: #2196F3; }
        .write-btn { border-color: #4CAF50; color: #4CAF50; }
        .duplicate-btn { border-color: #FF9800; color: #FF9800; }
        .manual-btn { border-color: #9C27B0; color: #9C27B0; }
        
        .card-data {
            display: none;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 12px;
            margin-top: 20px;
        }
        
        .card-data.show { display: block; }
        
        .card-info {
            margin-bottom: 15px;
            padding: 10px;
            background: white;
            border-radius: 8px;
        }
        
        .card-actions {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }
        
        .action-small-btn {
            padding: 12px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .delete-btn { background: #f44336; color: white; }
        .edit-btn { background: #2196F3; color: white; }
        .copy-btn { background: #FF9800; color: white; }
        
        .manual-input {
            display: none;
            margin-top: 20px;
        }
        
        .manual-input.show { display: block; }
        
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 15px;
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
    </style>
</head>
<body>
    <div class="nav">
        <button class="nav-btn" onclick="window.location.href='/'">
            <i class="fas fa-home"></i> الرئيسية / Home
        </button>
        <button class="nav-btn active">
            <i class="fas fa-cog"></i> الإعدادات / Settings
        </button>
    </div>
    
    <div class="container">
        <h1>⚙️ الإعدادات / Settings</h1>
        
        <div class="action-grid">
            <button class="action-btn read-btn" onclick="readCard()">
                <i class="fas fa-book-reader"></i>
                <div>قراءة بطاقة / Read Card</div>
            </button>
            
            <button class="action-btn duplicate-btn" onclick="duplicateCard()">
                <i class="fas fa-copy"></i>
                <div>نسخ بطاقة / Duplicate Card</div>
            </button>
            
            <button class="action-btn manual-btn" onclick="toggleManual()">
                <i class="fas fa-keyboard"></i>
                <div>كتابة يدوية / Manual Write</div>
            </button>
        </div>
        
        <div id="cardData" class="card-data">
            <h3>البيانات المقروءة / Card Data:</h3>
            <div id="dataDisplay"></div>
            
            <div class="card-actions">
                <button class="action-small-btn delete-btn" onclick="deleteCard()">
                    <i class="fas fa-trash"></i> حذف / Delete
                </button>
                <button class="action-small-btn edit-btn" onclick="editCard()">
                    <i class="fas fa-edit"></i> تعديل / Edit
                </button>
                <button class="action-small-btn copy-btn" onclick="copyCard()">
                    <i class="fas fa-copy"></i> نسخ / Copy
                </button>
            </div>
        </div>
        
        <div id="manualInput" class="manual-input">
            <h3>كتابة يدوية / Manual Write</h3>
            <input type="text" id="manualUrl" placeholder="Enter URL">
            <button class="btn" onclick="writeManual()">
                <i class="fas fa-wifi"></i> كتابة / Write to NFC
            </button>
        </div>
    </div>
    
    <script>
        let currentCardData = null;
        
        async function readCard() {
            try {
                const response = await fetch('/api/nfc/read');
                const result = await response.json();
                
                if (result.success && result.data.url) {
                    currentCardData = result.data;
                    displayCardData(result.data);
                } else {
                    alert('No data found on card');
                }
            } catch (error) {
                alert('Read error: ' + error);
            }
        }
        
        async function duplicateCard() {
            alert('Place existing card on reader...');
            await readCard();
        }
        
        function toggleManual() {
            const manual = document.getElementById('manualInput');
            manual.classList.toggle('show');
        }
        
        async function writeManual() {
            const url = document.getElementById('manualUrl').value;
            
            if (!url) {
                alert('Please enter URL');
                return;
            }
            
            try {
                const response = await fetch('/api/nfc/write', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                
                const result = await response.json();
                alert(result.message);
            } catch (error) {
                alert('Write error: ' + error);
            }
        }
        
        function displayCardData(data) {
            const display = document.getElementById('dataDisplay');
            display.innerHTML = `
                <div class="card-info">
                    <strong>URL:</strong> ${data.url}
                </div>
            `;
            document.getElementById('cardData').classList.add('show');
        }
        
        function deleteCard() {
            if (confirm('Are you sure you want to delete this card?')) {
                alert('Card deleted (not implemented yet)');
            }
        }
        
        function editCard() {
            if (currentCardData) {
                window.location.href = '/?edit=' + encodeURIComponent(currentCardData.url);
            }
        }
        
        function copyCard() {
            if (currentCardData) {
                window.location.href = '/?duplicate=' + encodeURIComponent(currentCardData.url);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Home page"""
    return render_template_string(HOME_PAGE)

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template_string(SETTINGS_PAGE)

@app.route('/api/create', methods=['POST'])
def create_card():
    """API: Create new card"""
    try:
        data = request.get_json() or {}

        # Server-side validation
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400

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

        # Push in background so HTTP response isn't blocked
        generator.git_push_background(f"Add card: {name}")

        return jsonify({
            'success': True,
            'url': result['url'],
            'username': result['username']
        })

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/nfc/write', methods=['POST'])
def nfc_write():
    """API: Write to NFC"""
    try:
        data = request.get_json() or {}
        url = data.get('url', '')

        if not url:
            return jsonify({'success': False, 'message': 'URL is required'}), 400

        writer = NFCWriter()
        ok, msg = writer.write_url(url, timeout=5)
        try:
            writer.close()
        finally:
            # ensure clf reference cleared even if close didn't set it
            writer.clf = None

        if ok:
            # Run git push in background
            generator.git_push_background(f"Write to NFC: {url}")
            return jsonify({'success': True, 'message': '✅ Successfully written to NFC!'}), 200
        else:
            return jsonify({'success': False, 'message': f'❌ Write failed: {msg}'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/nfc/read', methods=['GET'])
def nfc_read():
    """API: Read from NFC"""
    try:
        writer = NFCWriter()
        data, msg = writer.read_card(timeout=5)
        try:
            writer.close()
        finally:
            writer.clf = None

        if data:
            return jsonify({'success': True, 'data': data}), 200
        else:
            return jsonify({'success': False, 'message': msg}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    # Changed default port to 5001 to avoid conflicts on Raspberry Pi
    app.run(host='0.0.0.0', port=5001, debug=True)