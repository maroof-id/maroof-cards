#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maroof - Web Interface for Card Creation
with Photo Upload and vCard Support
"""

from flask import Flask, render_template_string, request, jsonify, send_file, send_from_directory
import os
import sys
import qrcode
from io import BytesIO
from pathlib import Path
import base64

# Add tools path
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

# Repo path - auto detect
REPO_PATH = SCRIPT_DIR.parent
CLIENTS_PATH = REPO_PATH / 'clients'

# Ensure directory exists
CLIENTS_PATH.mkdir(parents=True, exist_ok=True)

print(f"📁 Script directory: {SCRIPT_DIR}")
print(f"📁 Repo path: {REPO_PATH}")
print(f"📁 Clients path: {CLIENTS_PATH}")

from create_card import CardGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'maroof-secret-key-2025'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>معروف - إنشاء بطاقة</title>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        body { font-family: 'Cairo', sans-serif; }
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        #photoPreview { display: none; }
        #photoPreview img { object-fit: cover; }
    </style>
</head>
<body class="bg-gradient-to-br from-purple-50 to-pink-50 min-h-screen p-4">
    
    <div class="max-w-lg mx-auto">
        
        <div class="gradient-bg rounded-t-3xl p-6 text-center shadow-xl">
            <h1 class="text-3xl font-black text-white mb-2">🎴 معروف</h1>
            <p class="text-white/90">إنشاء بطاقة تعريفية جديدة</p>
        </div>
        
        <div class="bg-white rounded-b-3xl shadow-2xl p-6">
            
            <form id="cardForm" enctype="multipart/form-data" class="space-y-4">
                
                <!-- الصورة الشخصية -->
                <div class="text-center mb-6">
                    <label class="block text-gray-700 font-bold mb-3">
                        <i class="fas fa-camera text-purple-600"></i> الصورة الشخصية
                    </label>
                    
                    <div id="photoPreview" class="mb-3">
                        <img id="previewImg" class="w-32 h-32 rounded-full mx-auto border-4 border-purple-200">
                    </div>
                    
                    <label for="photoInput" class="cursor-pointer inline-block bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-3 rounded-xl font-bold hover:shadow-lg transition-all">
                        <i class="fas fa-upload mr-2"></i> اختر صورة
                    </label>
                    <input type="file" id="photoInput" name="photo" accept="image/*" class="hidden">
                </div>
                
                <div>
                    <label class="block text-gray-700 font-bold mb-2">
                        <i class="fas fa-user text-purple-600"></i> الاسم الكامل *
                    </label>
                    <input type="text" name="name" required
                           class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none text-lg"
                           placeholder="محمد أحمد">
                </div>
                
                <div>
                    <label class="block text-gray-700 font-bold mb-2">
                        <i class="fas fa-phone text-green-600"></i> رقم الجوال
                    </label>
                    <input type="tel" name="phone" dir="ltr"
                           class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none text-lg"
                           placeholder="0501234567">
                </div>
                
                <div>
                    <label class="block text-gray-700 font-bold mb-2">
                        <i class="fas fa-envelope text-red-600"></i> البريد الإلكتروني
                    </label>
                    <input type="email" name="email" dir="ltr"
                           class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none text-lg"
                           placeholder="email@example.com">
                </div>
                
                <div>
                    <label class="block text-gray-700 font-bold mb-2">
                        <i class="fab fa-instagram text-pink-600"></i> Instagram
                    </label>
                    <input type="text" name="instagram" dir="ltr"
                           class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none text-lg"
                           placeholder="@username">
                </div>
                
                <div>
                    <label class="block text-gray-700 font-bold mb-2">
                        <i class="fab fa-linkedin text-blue-600"></i> LinkedIn
                    </label>
                    <input type="text" name="linkedin" dir="ltr"
                           class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none text-lg"
                           placeholder="username">
                </div>
                
                <div>
                    <label class="block text-gray-700 font-bold mb-2">
                        <i class="fab fa-x-twitter text-gray-700"></i> X (Twitter)
                    </label>
                    <input type="text" name="twitter" dir="ltr"
                           class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none text-lg"
                           placeholder="@username">
                </div>
                
                <div>
                    <label class="block text-gray-700 font-bold mb-2">
                        <i class="fas fa-info-circle text-indigo-600"></i> نبذة تعريفية
                    </label>
                    <textarea name="bio" rows="3"
                              class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none text-lg resize-none"
                              placeholder="مطور برمجيات، مهتم بالتقنية..."></textarea>
                </div>
                
                <div>
                    <label class="block text-gray-700 font-bold mb-3">
                        <i class="fas fa-paint-brush text-purple-600"></i> اختر التصميم
                    </label>
                    
                    <div class="grid grid-cols-3 gap-3">
                        <label class="cursor-pointer">
                            <input type="radio" name="template" value="modern" checked class="hidden peer">
                            <div class="border-2 border-gray-200 peer-checked:border-purple-600 peer-checked:bg-purple-50 rounded-xl p-4 text-center transition-all">
                                <div class="text-3xl mb-2">🌈</div>
                                <div class="font-bold text-sm">عصري</div>
                            </div>
                        </label>
                        
                        <label class="cursor-pointer">
                            <input type="radio" name="template" value="classic" class="hidden peer">
                            <div class="border-2 border-gray-200 peer-checked:border-purple-600 peer-checked:bg-purple-50 rounded-xl p-4 text-center transition-all">
                                <div class="text-3xl mb-2">🎴</div>
                                <div class="font-bold text-sm">كلاسيكي</div>
                            </div>
                        </label>
                        
                        <label class="cursor-pointer">
                            <input type="radio" name="template" value="minimal" class="hidden peer">
                            <div class="border-2 border-gray-200 peer-checked:border-purple-600 peer-checked:bg-purple-50 rounded-xl p-4 text-center transition-all">
                                <div class="text-3xl mb-2">⚪</div>
                                <div class="font-bold text-sm">بسيط</div>
                            </div>
                        </label>
                    </div>
                </div>
                
                <button type="submit" id="submitBtn"
                        class="w-full gradient-bg text-white font-black py-4 rounded-2xl hover:shadow-2xl transition-all text-lg mt-6">
                    <i class="fas fa-magic mr-2"></i>
                    <span>إنشاء البطاقة</span>
                </button>
                
            </form>
            
        </div>
        
        <div id="resultModal" class="hidden fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
            <div class="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl">
                <div class="text-center">
                    <div class="w-20 h-20 bg-gradient-to-br from-green-400 to-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="fas fa-check text-white text-4xl"></i>
                    </div>
                    
                    <h2 class="text-2xl font-black text-gray-800 mb-2">تم بنجاح! ✨</h2>
                    <p class="text-gray-600 mb-6">تم إنشاء البطاقة التعريفية</p>
                    
                    <div class="bg-gray-50 rounded-2xl p-4 mb-6">
                        <p class="text-sm text-gray-600 mb-2">رابط البطاقة:</p>
                        <a id="cardUrl" href="#" target="_blank" class="text-purple-600 font-bold break-all hover:underline text-sm"></a>
                    </div>
                    
                    <div id="qrCode" class="mb-6"></div>
                    
                    <div class="space-y-3">
                        <button onclick="writeNFC()" id="nfcBtn"
                                class="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold py-4 rounded-xl hover:shadow-xl transition-all">
                            <i class="fas fa-wifi mr-2"></i> كتابة على NFC
                        </button>
                        
                        <div class="flex gap-3">
                            <button onclick="copyUrl()" class="flex-1 bg-gray-200 text-gray-800 font-bold py-3 rounded-xl hover:bg-gray-300 transition-all">
                                <i class="fas fa-copy mr-2"></i> نسخ
                            </button>
                            <button onclick="closeModal()" class="flex-1 gradient-bg text-white font-bold py-3 rounded-xl hover:shadow-xl transition-all">
                                <i class="fas fa-plus mr-2"></i> جديد
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="text-center mt-8">
            <p class="text-gray-500 text-sm">
                آخر 5 بطاقات:
                <a href="/list" class="text-purple-600 font-bold hover:underline">عرض الكل</a>
            </p>
        </div>
        
    </div>
    
    <script>
        const photoInput = document.getElementById('photoInput');
        const photoPreview = document.getElementById('photoPreview');
        const previewImg = document.getElementById('previewImg');
        
        photoInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewImg.src = e.target.result;
                    photoPreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
        
        const form = document.getElementById('cardForm');
        const modal = document.getElementById('resultModal');
        const submitBtn = document.getElementById('submitBtn');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> جاري الإنشاء...';
            
            const formData = new FormData(form);
            
            try {
                const response = await fetch('/api/create', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('cardUrl').href = result.url;
                    document.getElementById('cardUrl').textContent = result.url;
                    
                    document.getElementById('qrCode').innerHTML = `
                        <img src="/api/qr?url=${encodeURIComponent(result.url)}" 
                             class="w-48 h-48 mx-auto rounded-xl border-4 border-gray-200">
                    `;
                    
                    modal.classList.remove('hidden');
                    form.reset();
                    photoPreview.style.display = 'none';
                } else {
                    alert('خطأ: ' + result.error);
                }
                
            } catch (error) {
                alert('حدث خطأ: ' + error.message);
            }
            
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-magic mr-2"></i> إنشاء البطاقة';
        });
        
        async function writeNFC() {
            const url = document.getElementById('cardUrl').textContent;
            const btn = document.getElementById('nfcBtn');
            
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> جاري الكتابة... قرّب البطاقة';
            
            try {
                const response = await fetch('/api/write_nfc', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    btn.innerHTML = '<i class="fas fa-check mr-2"></i> تمت الكتابة بنجاح!';
                    btn.className = 'w-full bg-gradient-to-r from-green-600 to-emerald-700 text-white font-bold py-4 rounded-xl';
                    
                    setTimeout(() => {
                        btn.disabled = false;
                        btn.innerHTML = '<i class="fas fa-wifi mr-2"></i> كتابة على NFC';
                        btn.className = 'w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold py-4 rounded-xl hover:shadow-xl transition-all';
                    }, 3000);
                } else {
                    alert('❌ خطأ: ' + result.error);
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-wifi mr-2"></i> كتابة على NFC';
                }
            } catch (error) {
                alert('❌ حدث خطأ: ' + error.message);
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-wifi mr-2"></i> كتابة على NFC';
            }
        }
        
        function closeModal() {
            modal.classList.add('hidden');
        }
        
        function copyUrl() {
            const url = document.getElementById('cardUrl').textContent;
            navigator.clipboard.writeText(url);
            alert('تم نسخ الرابط!');
        }
    </script>
    
</body>
</html>
"""

LIST_TEMPLATE = """[نفس القالب السابق]"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/create', methods=['POST'])
def api_create():
    """API endpoint to create new card with photo"""
    try:
        # Handle photo upload
        photo_filename = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename:
                # Will be saved by CardGenerator
                photo_filename = photo.filename
        
        name = request.form.get('name', '')
        username = CardGenerator().sanitize_username(name)
        
        # Save photo if exists
        if photo_filename:
            client_dir = CLIENTS_PATH / username
            client_dir.mkdir(parents=True, exist_ok=True)
            
            ext = Path(photo_filename).suffix
            photo_path = client_dir / f'photo{ext}'
            request.files['photo'].save(str(photo_path))
            
            photo_url = f'https://maroof-id.github.io/maroof-cards/{username}/photo{ext}'
        else:
            photo_url = ''
        
        generator = CardGenerator()
        result = generator.create_card(
            name=name,
            phone=request.form.get('phone', ''),
            email=request.form.get('email', ''),
            instagram=request.form.get('instagram', ''),
            linkedin=request.form.get('linkedin', ''),
            twitter=request.form.get('twitter', ''),
            bio=request.form.get('bio', ''),
            template=request.form.get('template', 'modern'),
            photo=photo_url
        )
        
        return jsonify({
            'success': True,
            'username': result['username'],
            'url': result['url'],
            'path': result['path']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/vcard/<username>')
def api_vcard(username):
    """Generate vCard file"""
    try:
        client_dir = CLIENTS_PATH / username
        data_file = client_dir / 'data.json'
        
        if not data_file.exists():
            return "Card not found", 404
        
        import json
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create vCard
        vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{data.get('NAME', '')}
TEL;TYPE=CELL:+{data.get('PHONE_INTL', data.get('PHONE', ''))}
EMAIL:{data.get('EMAIL', '')}
URL:https://maroof-id.github.io/maroof-cards/{username}
NOTE:{data.get('BIO', '')}
"""
        if data.get('PHOTO'):
            vcard += f"PHOTO;VALUE=URL:{data['PHOTO']}\n"
        
        vcard += "END:VCARD"
        
        # Return as downloadable file
        return vcard, 200, {
            'Content-Type': 'text/vcard',
            'Content-Disposition': f'attachment; filename="{username}.vcf"'
        }
        
    except Exception as e:
        return str(e), 500

@app.route('/api/write_nfc', methods=['POST'])
def api_write_nfc():
    """Write to NFC card"""
    try:
        data = request.json
        url = data.get('url', '')
        
        from nfc_writer import NFCWriter
        
        writer = NFCWriter()
        
        if not writer.connect():
            return jsonify({
                'success': False,
                'error': 'NFC reader not connected!'
            }), 400
        
        success = writer.write_url(url)
        writer.close()
        
        if success:
            try:
                import subprocess
                subprocess.run(['aplay', '/usr/share/sounds/alsa/Front_Center.wav'], 
                             check=False, capture_output=True, timeout=2)
            except:
                pass
            
            return jsonify({
                'success': True,
                'message': 'Card written successfully!'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to write card!'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/qr')
def api_qr():
    """Generate QR Code"""
    url = request.args.get('url', '')
    
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🎴 Maroof - Digital Business Cards")
    print("="*50)
    print("\n📱 Open from mobile:")
    print("   http://192.168.1.103:5000")
    print("\n💻 Or from Pi:")
    print("   http://localhost:5000")
    print("\n" + "="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
