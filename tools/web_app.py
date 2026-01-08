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
                alert('Error: ' + error);
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
        }
        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 30px;
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
            margin-bottom: 10px;
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
        <button class="btn" onclick="readCard()">📖 قراءة بطاقة / Read Card</button>
    </div>
    
    <script>
        async function readCard() {
            try {
                const response = await fetch('/api/nfc/read');
                const result = await response.json();
                
                if (result.success && result.data) {
                    alert('Card data:\\n' + JSON.stringify(result.data, null, 2));
                } else {
                    alert('No data: ' + result.message);
                }
            } catch (error) {
                alert('Error: ' + error);
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

        generator.git_push_background(f"Add card: {name}")

        return jsonify({
            'success': True,
            'url': result['url'],
            'username': result['username']
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/nfc/write', methods=['POST'])
def nfc_write():
    try:
        data = request.get_json() or {}
        url = data.get('url', '')

        if not url:
            return jsonify({'success': False, 'message': 'URL is required'}), 400

        writer = get_nfc_writer()
        if not writer:
            return jsonify({'success': False, 'message': 'NFC reader not connected'}), 500

        ok, msg = writer.write_url(url, timeout=10)

        if ok:
            generator.git_push_background(f"Write to NFC: {url}")
            return jsonify({'success': True, 'message': msg}), 200
        else:
            return jsonify({'success': False, 'message': msg}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/nfc/read', methods=['GET'])
def nfc_read():
    try:
        writer = get_nfc_writer()
        if not writer:
            return jsonify({'success': False, 'message': 'NFC reader not connected'}), 500

        data, msg = writer.read_card(timeout=10)

        if data:
            return jsonify({'success': True, 'data': data}), 200
        else:
            return jsonify({'success': False, 'message': msg}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    # Initialize NFC on startup
    print("Initializing NFC reader...")
    writer = get_nfc_writer()
    if writer:
        print("NFC reader ready!")
    else:
        print("Warning: NFC reader not connected")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
ENDPY

