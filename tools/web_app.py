#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معروف - واجهة الويب لإنشاء البطاقات
Maroof Web Interface for Card Creation
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import os
import sys
import qrcode
from io import BytesIO
from pathlib import Path

# إضافة مسار tools للـ imports
sys.path.insert(0, str(Path(__file__).parent))
from create_card import CardGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'maroof-secret-key-2025'

# HTML Template للواجهة
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
    </style>
</head>
<body class="bg-gradient-to-br from-purple-50 to-pink-50 min-h-screen p-4">
    
    <div class="max-w-lg mx-auto">
        
        <!-- Header -->
        <div class="gradient-bg rounded-t-3xl p-6 text-center shadow-xl">
            <h1 class="text-3xl font-black text-white mb-2">🎴 معروف</h1>
            <p class="text-white/90">إنشاء بطاقة تعريفية جديدة</p>
        </div>
        
        <!-- Form -->
        <div class="bg-white rounded-b-3xl shadow-2xl p-6">
            
            <form id="cardForm" class="space-y-4">
                
                <!-- الاسم -->
                <div>
                    <label class="block text-gray-700 font-bold mb-2">
                        <i class="fas fa-user text-purple-600"></i> الاسم الكامل *
                    </label>
                    <input type="text" name="name" required
                           class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none text-lg"
                           placeholder="محمد أحمد">
                </div>
                
                <!-- رقم الجوال -->
                <div>
                    <label class="block text-gray-700 font-bold mb-2">
                        <i class="fas fa-phone text-green-600"></i> رقم الجوال
                    </label>
                    <input type="tel" name="phone" dir="ltr"
                           class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none text-lg"
                           placeholder="0501234567">
                </div>
                
                <!-- البريد الإلكتروني -->
                <div>
                    <label class="block text-gray-700 font-bold mb-2">
                        <i class="fas fa-envelope text-red-600"></i> البريد الإلكتروني
                    </label>
                    <input type="email" name="email" dir="ltr"
                           class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none text-lg"
                           placeholder="email@example.com">
                </div>
                
                <!-- Instagram -->
                <div>
                    <label class="block text-gray-700 font-bold mb-2">
                        <i class="fab fa-instagram text-pink-600"></i> Instagram
                    </label>
                    <input type="text" name="instagram" dir="ltr"
                           class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none text-lg"
                           placeholder="@username">
                </div>
                
                <!-- LinkedIn -->
                <div>
                    <label class="block text-gray-700 font-bold mb-2">
                        <i class="fab fa-linkedin text-blue-600"></i> LinkedIn
                    </label>
                    <input type="text" name="linkedin" dir="ltr"
                           class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none text-lg"
                           placeholder="username">
                </div>
                
                <!-- Twitter -->
                <div>
                    <label class="block text-gray-700 font-bold mb-2">
                        <i class="fab fa-x-twitter text-gray-700"></i> X (Twitter)
                    </label>
                    <input type="text" name="twitter" dir="ltr"
                           class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none text-lg"
                           placeholder="@username">
                </div>
                
                <!-- نبذة تعريفية -->
                <div>
                    <label class="block text-gray-700 font-bold mb-2">
                        <i class="fas fa-info-circle text-indigo-600"></i> نبذة تعريفية
                    </label>
                    <textarea name="bio" rows="3"
                              class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none text-lg resize-none"
                              placeholder="مطور برمجيات، مهتم بالتقنية..."></textarea>
                </div>
                
                <!-- اختيار القالب -->
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
                
                <!-- زر الإنشاء -->
                <button type="submit" id="submitBtn"
                        class="w-full gradient-bg text-white font-black py-4 rounded-2xl hover:shadow-2xl transition-all text-lg mt-6">
                    <i class="fas fa-magic mr-2"></i>
                    <span>إنشاء البطاقة</span>
                </button>
                
            </form>
            
        </div>
        
        <!-- Result Modal -->
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
                        <a id="cardUrl" href="#" target="_blank" class="text-purple-600 font-bold break-all hover:underline"></a>
                    </div>
                    
                    <div id="qrCode" class="mb-6"></div>
                    
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
        
        <!-- Footer -->
        <div class="text-center mt-8">
            <p class="text-gray-500 text-sm">
                آخر 5 بطاقات:
                <a href="/list" class="text-purple-600 font-bold hover:underline">عرض الكل</a>
            </p>
        </div>
        
    </div>
    
    <script>
        const form = document.getElementById('cardForm');
        const modal = document.getElementById('resultModal');
        const submitBtn = document.getElementById('submitBtn');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // تعطيل الزر
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> جاري الإنشاء...';
            
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // عرض النتيجة
                    document.getElementById('cardUrl').href = result.url;
                    document.getElementById('cardUrl').textContent = result.url;
                    
                    // عرض QR Code
                    document.getElementById('qrCode').innerHTML = `
                        <img src="/api/qr?url=${encodeURIComponent(result.url)}" 
                             class="w-48 h-48 mx-auto rounded-xl border-4 border-gray-200">
                    `;
                    
                    modal.classList.remove('hidden');
                    form.reset();
                } else {
                    alert('خطأ: ' + result.error);
                }
                
            } catch (error) {
                alert('حدث خطأ: ' + error.message);
            }
            
            // إعادة تفعيل الزر
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-magic mr-2"></i> إنشاء البطاقة';
        });
        
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

# قائمة البطاقات
LIST_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>معروف - قائمة البطاقات</title>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        body { font-family: 'Cairo', sans-serif; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen p-4">
    
    <div class="max-w-4xl mx-auto">
        
        <!-- Header -->
        <div class="bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl p-8 text-center shadow-xl mb-6">
            <h1 class="text-3xl font-black text-white mb-2">📋 البطاقات المنشأة</h1>
            <p class="text-white/90">المجموع: {{ cards|length }} بطاقة</p>
        </div>
        
        <!-- Cards List -->
        <div class="space-y-4">
            {% for card in cards %}
            <div class="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all">
                <div class="flex items-center justify-between">
                    <div class="flex-1">
                        <h3 class="text-xl font-bold text-gray-800 mb-1">{{ card.name }}</h3>
                        <p class="text-gray-500 text-sm mb-2">@{{ card.username }}</p>
                        <a href="{{ card.url }}" target="_blank" 
                           class="text-purple-600 font-semibold hover:underline break-all text-sm">
                            {{ card.url }}
                        </a>
                    </div>
                    <a href="{{ card.url }}" target="_blank"
                       class="bg-purple-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-purple-700 transition-all">
                        <i class="fas fa-external-link-alt"></i>
                    </a>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <!-- Back Button -->
        <div class="text-center mt-8">
            <a href="/" class="inline-block bg-gray-800 text-white px-8 py-4 rounded-2xl font-bold hover:bg-gray-900 transition-all">
                <i class="fas fa-arrow-right mr-2"></i> رجوع
            </a>
        </div>
        
    </div>
    
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/list')
def list_cards():
    """قائمة البطاقات"""
    generator = CardGenerator()
    cards = generator.list_cards()
    return render_template_string(LIST_TEMPLATE, cards=cards)

@app.route('/api/create', methods=['POST'])
def api_create():
    """API لإنشاء بطاقة جديدة"""
    try:
        data = request.json
        
        generator = CardGenerator()
        result = generator.create_card(
            name=data.get('name', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            instagram=data.get('instagram', ''),
            linkedin=data.get('linkedin', ''),
            twitter=data.get('twitter', ''),
            bio=data.get('bio', ''),
            template=data.get('template', 'modern')
        )
        
        # رفع لـ GitHub (اختياري - يمكن تعطيله للسرعة)
        # generator.git_push(f"إضافة بطاقة: {data.get('name')}")
        
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

@app.route('/api/qr')
def api_qr():
    """توليد QR Code"""
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
    print("🎴 معروف - واجهة إنشاء البطاقات")
    print("="*50)
    print("\n📱 افتح من جوالك:")
    print("   http://192.168.1.108:5000")
    print("\n💻 أو من Pi:")
    print("   http://localhost:5000")
    print("\n" + "="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)