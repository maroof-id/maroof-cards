#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maroof Web App - Enhanced System
"""

from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import os
import sys
from pathlib import Path
from datetime import datetime

current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from create_card import CardGenerator
from nfc_writer import NFCWriter

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

generator = CardGenerator()

# Notification counter (in-memory, resets on restart)
pending_count = 0

def get_pending_count():
    """Get count of pending cards"""
    cards = generator.list_cards(status_filter='pending')
    return len(cards)

def update_pending_count():
    """Update pending count"""
    global pending_count
    pending_count = get_pending_count()

# Cache-busting version
CACHE_VERSION = datetime.now().strftime('%Y%m%d%H%M%S')

# HTML Templates with modern design
BASE_STYLE = f"""
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    
    :root {{
        --white: #FFFFFF;
        --light-gray: #F5F5F5;
        --gray: #E0E0E0;
        --dark-gray: #757575;
        --black: #212121;
        --success: #4CAF50;
        --warning: #FF9800;
        --error: #F44336;
        --pending: #2196F3;
    }}
    
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'SF Pro Display', sans-serif;
        background: var(--light-gray);
        min-height: 100vh;
        color: var(--black);
        line-height: 1.6;
    }}
    
    .container {{
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }}
    
    .nav {{
        background: var(--white);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 30px;
        position: sticky;
        top: 0;
        z-index: 100;
    }}
    
    .nav-inner {{
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        padding: 15px 20px;
        gap: 15px;
    }}
    
    .nav-btn {{
        padding: 10px 20px;
        background: var(--white);
        color: var(--black);
        border: 2px solid var(--gray);
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        transition: all 0.2s;
    }}
    
    .nav-btn:hover {{
        background: var(--light-gray);
        border-color: var(--dark-gray);
        transform: translateY(-1px);
    }}
    
    .nav-btn.active {{
        background: var(--black);
        color: var(--white);
        border-color: var(--black);
    }}
    
    .notification-badge {{
        background: var(--error);
        color: white;
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 5px;
    }}
    
    .card {{
        background: var(--white);
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }}
    
    h1 {{
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 25px;
        color: var(--black);
    }}
    
    h2 {{
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 15px;
        color: var(--black);
    }}
    
    .form-group {{
        margin-bottom: 20px;
    }}
    
    label {{
        display: block;
        margin-bottom: 8px;
        color: var(--black);
        font-weight: 500;
        font-size: 14px;
    }}
    
    input, textarea, select {{
        width: 100%;
        padding: 12px 15px;
        border: 2px solid var(--gray);
        border-radius: 8px;
        font-size: 15px;
        font-family: inherit;
        transition: border-color 0.2s;
        background: var(--white);
    }}
    
    input:focus, textarea:focus, select:focus {{
        outline: none;
        border-color: var(--black);
    }}
    
    textarea {{
        resize: vertical;
        min-height: 100px;
    }}
    
    input[type="file"] {{
        padding: 10px;
        border: 2px dashed var(--gray);
        background: var(--light-gray);
        cursor: pointer;
    }}
    
    input[type="file"]:hover {{
        border-color: var(--dark-gray);
    }}
    
    .btn {{
        padding: 12px 24px;
        background: var(--black);
        color: var(--white);
        border: none;
        border-radius: 8px;
        font-size: 15px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }}
    
    .btn:hover {{
        background: #000;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }}
    
    .btn:disabled {{
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
    }}
    
    .btn-success {{ background: var(--success); }}
    .btn-warning {{ background: var(--warning); }}
    .btn-error {{ background: var(--error); }}
    .btn-secondary {{ background: var(--dark-gray); }}
    
    .btn-outline {{
        background: var(--white);
        color: var(--black);
        border: 2px solid var(--gray);
    }}
    
    .btn-outline:hover {{
        background: var(--light-gray);
        border-color: var(--black);
    }}
    
    .status-indicator {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 500;
    }}
    
    .status-success {{
        background: #e8f5e9;
        color: var(--success);
    }}
    
    .status-warning {{
        background: #fff3e0;
        color: var(--warning);
    }}
    
    .status-error {{
        background: #ffebee;
        color: var(--error);
    }}
    
    .status-pending {{
        background: #e3f2fd;
        color: var(--pending);
    }}
    
    .stats {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-bottom: 30px;
    }}
    
    .stat-card {{
        background: var(--white);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    
    .stat-value {{
        font-size: 32px;
        font-weight: 700;
        color: var(--black);
        margin-bottom: 5px;
    }}
    
    .stat-label {{
        font-size: 14px;
        color: var(--dark-gray);
        font-weight: 500;
    }}
    
    table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
    }}
    
    th {{
        background: var(--light-gray);
        padding: 12px;
        text-align: left;
        font-weight: 600;
        font-size: 13px;
        color: var(--black);
        border-bottom: 2px solid var(--gray);
    }}
    
    td {{
        padding: 15px 12px;
        border-bottom: 1px solid var(--gray);
        font-size: 14px;
    }}
    
    tr:hover {{
        background: var(--light-gray);
    }}
    
    .photo-preview {{
        margin-top: 15px;
        text-align: center;
    }}
    
    .photo-preview img {{
        width: 120px;
        height: 120px;
        object-fit: cover;
        border-radius: 50%;
        border: 3px solid var(--gray);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    
    .alert {{
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        display: none;
    }}
    
    .alert.show {{ display: block; }}
    
    .alert-success {{
        background: #e8f5e9;
        color: var(--success);
        border-left: 4px solid var(--success);
    }}
    
    .alert-error {{
        background: #ffebee;
        color: var(--error);
        border-left: 4px solid var(--error);
    }}
    
    .loading {{
        display: none;
        text-align: center;
        padding: 20px;
    }}
    
    .spinner {{
        display: inline-block;
        width: 24px;
        height: 24px;
        border: 3px solid var(--gray);
        border-top: 3px solid var(--black);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }}
    
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    
    .reader-status {{
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 500;
    }}
    
    .reader-status.online {{
        background: #e8f5e9;
        color: var(--success);
    }}
    
    .reader-status.offline {{
        background: #ffebee;
        color: var(--error);
    }}
    
    .status-dot {{
        width: 12px;
        height: 12px;
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
    }}
    
    .status-dot.green {{ background: var(--success); }}
    .status-dot.red {{ background: var(--error); }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    
    @media (max-width: 768px) {{
        .container {{ padding: 10px; }}
        .nav-inner {{ flex-wrap: wrap; }}
        .stats {{ grid-template-columns: 1fr; }}
        table {{ font-size: 12px; }}
        th, td {{ padding: 8px; }}
    }}
</style>
"""

DASHBOARD_PAGE = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maroof - لوحة التحكم</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    {BASE_STYLE}
</head>
<body>
    <div class="nav">
        <div class="nav-inner">
            <a href="/" class="nav-btn">
                <i class="fas fa-plus-circle"></i> إنشاء بطاقة
            </a>
            <a href="/dashboard" class="nav-btn active">
                <i class="fas fa-th-large"></i> لوحة التحكم
                <span class="notification-badge" id="pendingBadge" style="display:none;">0</span>
            </a>
            <a href="/settings" class="nav-btn">
                <i class="fas fa-cog"></i> الإعدادات
            </a>
        </div>
    </div>

    <div class="container">
        <h1>📊 لوحة التحكم</h1>

        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="stat-value" id="pendingCount">0</div>
                <div class="stat-label">⏳ قيد الانتظار</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="printedCount">0</div>
                <div class="stat-label">✅ مطبوعة</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="modifiedCount">0</div>
                <div class="stat-label">📝 معدّلة</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalCount">0</div>
                <div class="stat-label">📇 الإجمالي</div>
            </div>
        </div>

        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;">
                <h2>📋 البطاقات</h2>
                <div style="display: flex; gap: 10px;">
                    <input type="text" id="searchInput" placeholder="🔍 بحث بالاسم أو الجوال" 
                           style="width: 250px;" onkeyup="filterCards()">
                    <select id="statusFilter" onchange="filterCards()" style="width: 150px;">
                        <option value="all">كل الحالات</option>
                        <option value="pending">⏳ قيد الانتظار</option>
                        <option value="printed">✅ مطبوعة</option>
                        <option value="modified">📝 معدّلة</option>
                    </select>
                </div>
            </div>

            <div id="loading" class="loading" style="display: block;">
                <div class="spinner"></div>
                <p style="margin-top: 10px;">جاري التحميل...</p>
            </div>

            <div id="tableContainer" style="display: none; overflow-x: auto;">
                <table id="cardsTable">
                    <thead>
                        <tr>
                            <th>الاسم</th>
                            <th>الجوال</th>
                            <th>الحالة</th>
                            <th>المصدر</th>
                            <th>عدد الطباعة</th>
                            <th>التاريخ</th>
                            <th>إجراءات</th>
                        </tr>
                    </thead>
                    <tbody id="cardsBody">
                    </tbody>
                </table>
            </div>

            <div id="emptyState" style="display: none; text-align: center; padding: 40px; color: var(--dark-gray);">
                <i class="fas fa-inbox" style="font-size: 48px; margin-bottom: 15px; opacity: 0.3;"></i>
                <p>لا توجد بطاقات</p>
            </div>
        </div>
    </div>

    <script>
        let allCards = [];

        async function loadCards() {{
            try {{
                const response = await fetch('/api/cards');
                const data = await response.json();
                
                if (data.success) {{
                    allCards = data.cards;
                    updateStats(data.stats);
                    renderCards(allCards);
                    document.getElementById('loading').style.display = 'none';
                    
                    if (allCards.length > 0) {{
                        document.getElementById('tableContainer').style.display = 'block';
                        document.getElementById('emptyState').style.display = 'none';
                    }} else {{
                        document.getElementById('tableContainer').style.display = 'none';
                        document.getElementById('emptyState').style.display = 'block';
                    }}
                }}
            }} catch (error) {{
                console.error('Failed to load cards:', error);
                document.getElementById('loading').style.display = 'none';
            }}
        }}

        function updateStats(stats) {{
            document.getElementById('pendingCount').textContent = stats.pending;
            document.getElementById('printedCount').textContent = stats.printed;
            document.getElementById('modifiedCount').textContent = stats.modified;
            document.getElementById('totalCount').textContent = stats.total;
            
            const badge = document.getElementById('pendingBadge');
            if (stats.pending > 0) {{
                badge.textContent = stats.pending;
                badge.style.display = 'inline-block';
            }} else {{
                badge.style.display = 'none';
            }}
        }}

        function renderCards(cards) {{
            const tbody = document.getElementById('cardsBody');
            tbody.innerHTML = '';
            
            cards.forEach(card => {{
                const tr = document.createElement('tr');
                
                let statusBadge = '';
                if (card.status === 'pending') {{
                    statusBadge = '<span class="status-indicator status-pending">⏳ قيد الانتظار</span>';
                }} else if (card.status === 'printed') {{
                    statusBadge = '<span class="status-indicator status-success">✅ مطبوعة</span>';
                }} else if (card.status === 'modified') {{
                    statusBadge = '<span class="status-indicator status-warning">📝 معدّلة</span>';
                }}
                
                const source = card.source === 'client' ? '👤 عميل' : '⚙️ إدارة';
                const date = card.created_at ? new Date(card.created_at).toLocaleDateString('ar-SA') : '-';
                
                tr.innerHTML = `
                    <td><strong>${{card.name}}</strong></td>
                    <td>${{card.phone || '-'}}</td>
                    <td>${{statusBadge}}</td>
                    <td>${{source}}</td>
                    <td>${{card.print_count}}x</td>
                    <td>${{date}}</td>
                    <td>
                        <div style="display: flex; gap: 5px;">
                            <button class="btn btn-outline" style="padding: 6px 12px; font-size: 13px;" 
                                    onclick="viewCard('${{card.url}}')">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-outline" style="padding: 6px 12px; font-size: 13px;" 
                                    onclick="editCard('${{card.username}}')">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-success" style="padding: 6px 12px; font-size: 13px;" 
                                    onclick="printCard('${{card.username}}', '${{card.url}}')">
                                <i class="fas fa-print"></i>
                            </button>
                            <button class="btn btn-error" style="padding: 6px 12px; font-size: 13px;" 
                                    onclick="deleteCard('${{card.username}}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                `;
                
                tbody.appendChild(tr);
            }});
        }}

        function filterCards() {{
            const search = document.getElementById('searchInput').value.toLowerCase();
            const status = document.getElementById('statusFilter').value;
            
            let filtered = allCards;
            
            if (status !== 'all') {{
                filtered = filtered.filter(card => card.status === status);
            }}
            
            if (search) {{
                filtered = filtered.filter(card => 
                    card.name.toLowerCase().includes(search) || 
                    (card.phone && card.phone.includes(search))
                );
            }}
            
            renderCards(filtered);
        }}

        function viewCard(url) {{
            window.open(url, '_blank');
        }}

        function editCard(username) {{
            window.location.href = `/edit/${{username}}`;
        }}

        async function printCard(username, url) {{
            if (!confirm('هل تريد كتابة هذه البطاقة على NFC؟')) return;
            
            try {{
                const response = await fetch('/api/nfc/write', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{url: url, username: username}})
                }});

                const result = await response.json();

                if (result.success) {{
                    alert('✅ تمت الكتابة بنجاح!');
                    loadCards(); // Reload to update print count
                }} else {{
                    alert('❌ فشلت الكتابة: ' + result.message);
                }}
            }} catch (error) {{
                alert('خطأ في الاتصال بالقارئ');
            }}
        }}

        async function deleteCard(username) {{
            if (!confirm('هل أنت متأكد من حذف هذه البطاقة؟')) return;
            
            try {{
                const response = await fetch(`/api/cards/${{username}}`, {{
                    method: 'DELETE'
                }});

                const result = await response.json();

                if (result.success) {{
                    alert('✅ تم الحذف بنجاح');
                    loadCards();
                }} else {{
                    alert('❌ فشل الحذف');
                }}
            }} catch (error) {{
                alert('خطأ في الحذف');
            }}
        }}

        // Auto-refresh every 30 seconds
        setInterval(loadCards, 30000);
        
        // Load on page load
        loadCards();
    </script>
</body>
</html>
"""

SETTINGS_PAGE = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maroof - الإعدادات</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    {BASE_STYLE}
</head>
<body>
    <div class="nav">
        <div class="nav-inner">
            <a href="/" class="nav-btn">
                <i class="fas fa-plus-circle"></i> إنشاء بطاقة
            </a>
            <a href="/dashboard" class="nav-btn" id="dashboardBtn">
                <i class="fas fa-th-large"></i> لوحة التحكم
                <span class="notification-badge" id="pendingBadge" style="display:none;">0</span>
            </a>
            <a href="/settings" class="nav-btn active">
                <i class="fas fa-cog"></i> الإعدادات
            </a>
        </div>
    </div>

    <div class="container">
        <h1>⚙️ إعدادات القارئ</h1>

        <div class="card">
            <h2>حالة القارئ</h2>
            <div id="readerStatus" class="reader-status offline" style="margin: 20px 0;">
                <span class="status-dot red"></span>
                <span>جاري الفحص...</span>
            </div>
            
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <button class="btn btn-warning" onclick="testReader()" id="testBtn">
                    <i class="fas fa-stethoscope"></i> اختبار القارئ
                </button>
                <button class="btn btn-secondary" onclick="resetReader()" id="resetBtn">
                    <i class="fas fa-redo"></i> إعادة ضبط القارئ
                </button>
                <button class="btn btn-outline" onclick="readCard()" id="readBtn">
                    <i class="fas fa-book"></i> قراءة بطاقة
                </button>
            </div>

            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p id="loadingText" style="margin-top: 10px;">جاري المعالجة...</p>
            </div>

            <div id="result" style="margin-top: 20px; display: none;">
                <h3 id="resultTitle" style="margin-bottom: 10px;"></h3>
                <pre id="resultContent" style="background: var(--light-gray); padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 13px;"></pre>
            </div>
        </div>

        <div class="card" id="readResultCard" style="display: none;">
            <h2>📖 بيانات البطاقة المقروءة</h2>
            <div id="readResult"></div>
            <button class="btn" onclick="useReadData()" style="margin-top: 15px;">
                <i class="fas fa-copy"></i> استخدام هذه البيانات لإنشاء بطاقة
            </button>
        </div>

        <div class="card" style="background: #fff3cd; border-left: 4px solid var(--warning);">
            <h3 style="color: var(--warning); margin-bottom: 10px;">💡 نصائح</h3>
            <ul style="margin-right: 20px; line-height: 1.8;">
                <li>إذا فشل الاتصال بالقارئ، افصله من USB وأعد توصيله</li>
                <li>استخدم بطاقات NTAG213/215/216 للحصول على أفضل النتائج</li>
                <li>تأكد من وضع البطاقة بشكل صحيح على القارئ</li>
                <li>انتظر حتى تظهر رسالة النجاح قبل رفع البطاقة</li>
            </ul>
        </div>
    </div>

    <script>
        let readData = null;

        async function checkReaderStatus() {{
            try {{
                const response = await fetch('/api/nfc/test');
                const result = await response.json();
                
                const statusDiv = document.getElementById('readerStatus');
                if (result.success) {{
                    statusDiv.className = 'reader-status online';
                    statusDiv.innerHTML = '<span class="status-dot green"></span><span>🟢 القارئ متصل وجاهز</span>';
                }} else {{
                    statusDiv.className = 'reader-status offline';
                    statusDiv.innerHTML = '<span class="status-dot red"></span><span>🔴 القارئ غير متصل</span>';
                }}
            }} catch (error) {{
                const statusDiv = document.getElementById('readerStatus');
                statusDiv.className = 'reader-status offline';
                statusDiv.innerHTML = '<span class="status-dot red"></span><span>🔴 خطأ في الاتصال</span>';
            }}
        }}

        async function testReader() {{
            const testBtn = document.getElementById('testBtn');
            testBtn.disabled = true;
            document.getElementById('loading').style.display = 'block';
            document.getElementById('loadingText').textContent = 'جاري الاختبار...';
            document.getElementById('result').style.display = 'none';

            try {{
                const response = await fetch('/api/nfc/test');
                const result = await response.json();

                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
                testBtn.disabled = false;

                if (result.success) {{
                    document.getElementById('resultTitle').textContent = '✅ القارئ يعمل بشكل صحيح';
                    document.getElementById('resultTitle').style.color = 'var(--success)';
                    document.getElementById('resultContent').textContent = result.message;
                    checkReaderStatus();
                }} else {{
                    document.getElementById('resultTitle').textContent = '❌ فشل الاتصال بالقارئ';
                    document.getElementById('resultTitle').style.color = 'var(--error)';
                    document.getElementById('resultContent').textContent = result.message + '\\n\\nافصل القارئ من USB وأعد توصيله';
                    checkReaderStatus();
                }}
            }} catch (error) {{
                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
                document.getElementById('resultTitle').textContent = '❌ خطأ في الاتصال';
                document.getElementById('resultTitle').style.color = 'var(--error)';
                document.getElementById('resultContent').textContent = error.toString();
                testBtn.disabled = false;
            }}
        }}

        async function resetReader() {{
            if (!confirm('هل تريد إعادة ضبط القارئ؟\\n\\nافصل القارئ من USB ثم اضغط موافق')) return;
            
            alert('الآن أعد توصيل القارئ بـ USB');
            
            setTimeout(() => {{
                testReader();
            }}, 3000);
        }}

        async function readCard() {{
            const readBtn = document.getElementById('readBtn');
            readBtn.disabled = true;
            document.getElementById('loading').style.display = 'block';
            document.getElementById('loadingText').textContent = 'ضع البطاقة على القارئ...';
            document.getElementById('result').style.display = 'none';
            document.getElementById('readResultCard').style.display = 'none';

            try {{
                const response = await fetch('/api/nfc/read');
                const result = await response.json();

                document.getElementById('loading').style.display = 'none';
                readBtn.disabled = false;

                if (result.success && result.data) {{
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('resultTitle').textContent = '✅ تمت القراءة بنجاح';
                    document.getElementById('resultTitle').style.color = 'var(--success)';
                    document.getElementById('resultContent').textContent = JSON.stringify(result.data, null, 2);
                    
                    readData = result.data;
                    displayReadData(result.data);
                }} else {{
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('resultTitle').textContent = '❌ فشلت القراءة';
                    document.getElementById('resultTitle').style.color = 'var(--error)';
                    document.getElementById('resultContent').textContent = result.message || 'خطأ غير معروف';
                }}
            }} catch (error) {{
                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
                document.getElementById('resultTitle').textContent = '❌ خطأ في الاتصال';
                document.getElementById('resultTitle').style.color = 'var(--error)';
                document.getElementById('resultContent').textContent = error.toString();
                readBtn.disabled = false;
            }}
        }}

        function displayReadData(data) {{
            let html = '<div style="background: var(--light-gray); padding: 15px; border-radius: 8px;">';
            html += `<p><strong>UID:</strong> ${{data.uid}}</p>`;
            if (data.url) {{
                html += `<p><strong>الرابط:</strong> <a href="${{data.url}}" target="_blank">${{data.url}}</a></p>`;
            }}
            if (data.type) {{
                html += `<p><strong>النوع:</strong> ${{data.type}}</p>`;
            }}
            html += '</div>';
            
            document.getElementById('readResult').innerHTML = html;
            document.getElementById('readResultCard').style.display = 'block';
        }}

        function useReadData() {{
            if (!readData || !readData.url) {{
                alert('لا توجد بيانات للاستخدام');
                return;
            }}
            
            // Extract username from URL
            const match = readData.url.match(/clients\\/([^\\/]+)\\/?$/);
            if (match) {{
                const username = match[1];
                window.location.href = `/edit/${{username}}`;
            }} else {{
                alert('لم يتم العثور على البطاقة');
            }}
        }}

        // Check status on load
        checkReaderStatus();
        
        // Auto-check every 30 seconds
        setInterval(checkReaderStatus, 30000);
    </script>
</body>
</html>
"""

REGISTER_PAGE = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maroof - تسجيل بطاقة</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    {BASE_STYLE}
</head>
<body style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <div class="container" style="max-width: 600px; padding-top: 40px;">
        <div class="card" style="text-align: center;">
            <div style="font-size: 48px; margin-bottom: 20px;">👋</div>
            <h1 style="margin-bottom: 10px;">مرحباً بك!</h1>
            <p style="color: var(--dark-gray); margin-bottom: 30px;">سجل بياناتك للحصول على بطاقتك الرقمية</p>

            <div id="alert" class="alert"></div>

            <form id="registerForm" style="text-align: right;">
                <div class="form-group">
                    <label>الاسم الكامل *</label>
                    <input type="text" name="name" required placeholder="أدخل اسمك الكامل">
                </div>

                <div class="form-group">
                    <label>الصورة الشخصية</label>
                    <input type="file" name="photo" id="photoInput" accept="image/jpeg,image/png,image/gif,image/webp">
                    <small style="color: var(--dark-gray); display: block; margin-top: 5px;">
                        اختياري - JPG, PNG (الحد الأقصى 5MB)
                    </small>
                    <div class="photo-preview" id="photoPreview" style="display: none;">
                        <img id="previewImage" src="" alt="معاينة">
                    </div>
                </div>

                <div class="form-group">
                    <label>رقم الجوال *</label>
                    <input type="tel" name="phone" required placeholder="05xxxxxxxx">
                </div>

                <div class="form-group">
                    <label>البريد الإلكتروني</label>
                    <input type="email" name="email" placeholder="example@email.com">
                </div>

                <div class="form-group">
                    <label>نبذة تعريفية</label>
                    <textarea name="bio" placeholder="اكتب نبذة مختصرة عنك" rows="3"></textarea>
                </div>

                <button type="submit" class="btn" id="submitBtn" style="width: 100%; margin-top: 10px;">
                    <i class="fas fa-paper-plane"></i> إرسال البيانات
                </button>
            </form>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="margin-top: 10px;">جاري الإرسال...</p>
            </div>
        </div>

        <div class="card" id="successCard" style="display: none; text-align: center; background: #e8f5e9;">
            <div style="font-size: 64px; margin-bottom: 15px;">✅</div>
            <h2 style="color: var(--success); margin-bottom: 10px;">تم إرسال بياناتك بنجاح!</h2>
            <p style="color: var(--dark-gray);">سنتواصل معك قريباً لاستلام بطاقتك</p>
        </div>
    </div>

    <script>
        // Photo preview
        document.getElementById('photoInput').addEventListener('change', function(e) {{
            const file = e.target.files[0];
            if (file) {{
                if (file.size > 5 * 1024 * 1024) {{
                    showAlert('الصورة كبيرة جداً! الحد الأقصى 5MB', 'error');
                    e.target.value = '';
                    document.getElementById('photoPreview').style.display = 'none';
                    return;
                }}
                
                const reader = new FileReader();
                reader.onload = function(event) {{
                    document.getElementById('previewImage').src = event.target.result;
                    document.getElementById('photoPreview').style.display = 'block';
                }};
                reader.readAsDataURL(file);
            }} else {{
                document.getElementById('photoPreview').style.display = 'none';
            }}
        }});

        // Form submission
        document.getElementById('registerForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const photoFile = document.getElementById('photoInput').files[0];
            let photoBase64 = '';
            
            if (photoFile) {{
                if (photoFile.size > 5 * 1024 * 1024) {{
                    showAlert('الصورة كبيرة جداً! الحد الأقصى 5MB', 'error');
                    return;
                }}
                
                try {{
                    photoBase64 = await new Promise((resolve, reject) => {{
                        const reader = new FileReader();
                        reader.onload = () => resolve(reader.result);
                        reader.onerror = reject;
                        reader.readAsDataURL(photoFile);
                    }});
                }} catch (error) {{
                    showAlert('فشل قراءة الصورة', 'error');
                    return;
                }}
            }}
            
            const data = Object.fromEntries(formData);
            delete data.photo;
            if (photoBase64) {{
                data.photo = photoBase64;
            }}
            data.source = 'client';
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('submitBtn').disabled = true;

            try {{
                const response = await fetch('/api/register', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(data)
                }});

                const result = await response.json();
                
                document.getElementById('loading').style.display = 'none';
                document.getElementById('submitBtn').disabled = false;

                if (result.success) {{
                    document.getElementById('registerForm').style.display = 'none';
                    document.getElementById('successCard').style.display = 'block';
                }} else {{
                    showAlert(result.error || 'حدث خطأ غير معروف', 'error');
                }}
            }} catch (error) {{
                document.getElementById('loading').style.display = 'none';
                document.getElementById('submitBtn').disabled = false;
                showAlert('خطأ في الاتصال بالخادم', 'error');
            }}
        }});

        function showAlert(message, type) {{
            const alert = document.getElementById('alert');
            alert.textContent = message;
            alert.className = `alert alert-${{type}} show`;
            setTimeout(() => {{
                alert.classList.remove('show');
            }}, 5000);
        }}
    </script>
</body>
</html>
"""

EDIT_PAGE = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maroof - تعديل بطاقة</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    {BASE_STYLE}
</head>
<body>
    <div class="nav">
        <div class="nav-inner">
            <a href="/" class="nav-btn">
                <i class="fas fa-plus-circle"></i> إنشاء بطاقة
            </a>
            <a href="/dashboard" class="nav-btn">
                <i class="fas fa-th-large"></i> لوحة التحكم
            </a>
            <a href="/settings" class="nav-btn">
                <i class="fas fa-cog"></i> الإعدادات
            </a>
        </div>
    </div>

    <div class="container">
        <div class="card">
            <h1>✏️ تعديل البطاقة</h1>

            <div id="alert" class="alert"></div>

            <div id="loading" class="loading" style="display: block;">
                <div class="spinner"></div>
                <p style="margin-top: 10px;">جاري التحميل...</p>
            </div>

            <form id="editForm" style="display: none;">
                <input type="hidden" id="username" value="">
                
                <div class="form-group">
                    <label>الاسم الكامل *</label>
                    <input type="text" name="name" id="name" required>
                </div>

                <div class="form-group">
                    <label>الصورة الشخصية</label>
                    <input type="file" name="photo" id="photoInput" accept="image/jpeg,image/png,image/gif,image/webp">
                    <small style="color: var(--dark-gray); display: block; margin-top: 5px;">
                        اختياري - اترك فارغاً للإبقاء على الصورة الحالية
                    </small>
                    <div class="photo-preview" id="currentPhoto" style="display: none; margin-top: 10px;">
                        <p style="font-size: 13px; color: var(--dark-gray); margin-bottom: 5px;">الصورة الحالية:</p>
                        <img id="currentPhotoImg" src="" alt="الصورة الحالية">
                    </div>
                    <div class="photo-preview" id="photoPreview" style="display: none;">
                        <p style="font-size: 13px; color: var(--dark-gray); margin-bottom: 5px;">الصورة الجديدة:</p>
                        <img id="previewImage" src="" alt="معاينة">
                    </div>
                </div>

                <div class="form-group">
                    <label>رقم الجوال</label>
                    <input type="tel" name="phone" id="phone">
                </div>

                <div class="form-group">
                    <label>البريد الإلكتروني</label>
                    <input type="email" name="email" id="email">
                </div>

                <div class="form-group">
                    <label>Instagram</label>
                    <input type="text" name="instagram" id="instagram">
                </div>

                <div class="form-group">
                    <label>LinkedIn</label>
                    <input type="text" name="linkedin" id="linkedin">
                </div>

                <div class="form-group">
                    <label>Twitter/X</label>
                    <input type="text" name="twitter" id="twitter">
                </div>

                <div class="form-group">
                    <label>نبذة تعريفية</label>
                    <textarea name="bio" id="bio"></textarea>
                </div>

                <div class="form-group">
                    <label>التصميم</label>
                    <select name="template" id="template">
                        <option value="professional">Professional</option>
                        <option value="luxury">Luxury</option>
                        <option value="friendly">Friendly</option>
                        <option value="modern">Modern</option>
                        <option value="classic">Classic</option>
                        <option value="minimal">Minimal</option>
                    </select>
                </div>

                <div style="display: flex; gap: 10px;">
                    <button type="submit" class="btn" id="submitBtn">
                        <i class="fas fa-save"></i> حفظ التعديلات
                    </button>
                    <a href="/dashboard" class="btn btn-outline">
                        <i class="fas fa-times"></i> إلغاء
                    </a>
                </div>
            </form>
        </div>
    </div>

    <script>
        const username = window.location.pathname.split('/').pop();

        async function loadCard() {{
            try {{
                const response = await fetch(`/api/cards/${{username}}`);
                const result = await response.json();

                if (result.success) {{
                    const data = result.data;
                    document.getElementById('username').value = username;
                    document.getElementById('name').value = data.NAME || '';
                    document.getElementById('phone').value = data.PHONE || '';
                    document.getElementById('email').value = data.EMAIL || '';
                    document.getElementById('instagram').value = data.INSTAGRAM || '';
                    document.getElementById('linkedin').value = data.LINKEDIN || '';
                    document.getElementById('twitter').value = data.TWITTER || '';
                    document.getElementById('bio').value = data.BIO || '';
                    
                    if (data.PHOTO) {{
                        const photoUrl = `https://maroof-id.github.io/maroof-cards/clients/${{username}}/${{data.PHOTO.replace('./', '')}}`;
                        document.getElementById('currentPhotoImg').src = photoUrl;
                        document.getElementById('currentPhoto').style.display = 'block';
                    }}
                    
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('editForm').style.display = 'block';
                }} else {{
                    showAlert('فشل تحميل البيانات', 'error');
                }}
            }} catch (error) {{
                showAlert('خطأ في الاتصال', 'error');
            }}
        }}

        // Photo preview
        document.getElementById('photoInput').addEventListener('change', function(e) {{
            const file = e.target.files[0];
            if (file) {{
                if (file.size > 5 * 1024 * 1024) {{
                    showAlert('الصورة كبيرة جداً! الحد الأقصى 5MB', 'error');
                    e.target.value = '';
                    document.getElementById('photoPreview').style.display = 'none';
                    return;
                }}
                
                const reader = new FileReader();
                reader.onload = function(event) {{
                    document.getElementById('previewImage').src = event.target.result;
                    document.getElementById('photoPreview').style.display = 'block';
                }};
                reader.readAsDataURL(file);
            }} else {{
                document.getElementById('photoPreview').style.display = 'none';
            }}
        }});

        // Form submission
        document.getElementById('editForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const photoFile = document.getElementById('photoInput').files[0];
            let photoBase64 = '';
            
            if (photoFile) {{
                try {{
                    photoBase64 = await new Promise((resolve, reject) => {{
                        const reader = new FileReader();
                        reader.onload = () => resolve(reader.result);
                        reader.onerror = reject;
                        reader.readAsDataURL(photoFile);
                    }});
                }} catch (error) {{
                    showAlert('فشل قراءة الصورة', 'error');
                    return;
                }}
            }}
            
            const data = Object.fromEntries(formData);
            delete data.photo;
            if (photoBase64) {{
                data.photo = photoBase64;
            }}
            
            document.getElementById('submitBtn').disabled = true;

            try {{
                const response = await fetch(`/api/cards/${{username}}`, {{
                    method: 'PUT',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(data)
                }});

                const result = await response.json();
                
                document.getElementById('submitBtn').disabled = false;

                if (result.success) {{
                    showAlert('✅ تم حفظ التعديلات بنجاح! سيتم تحديث البطاقة على GitHub...', 'success');
                    setTimeout(() => {{
                        window.location.href = '/dashboard';
                    }}, 2000);
                }} else {{
                    showAlert(result.error || 'حدث خطأ', 'error');
                }}
            }} catch (error) {{
                document.getElementById('submitBtn').disabled = false;
                showAlert('خطأ في الاتصال', 'error');
            }}
        }});

        function showAlert(message, type) {{
            const alert = document.getElementById('alert');
            alert.textContent = message;
            alert.className = `alert alert-${{type}} show`;
        }}

        // Load card data
        loadCard();
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    response = app.response_class(
        response=HOME_PAGE,
        mimetype='text/html'
    )
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/dashboard')
def dashboard():
    response = app.response_class(
        response=DASHBOARD_PAGE,
        mimetype='text/html'
    )
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/settings')
def settings():
    response = app.response_class(
        response=SETTINGS_PAGE,
        mimetype='text/html'
    )
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/register')
def register():
    response = app.response_class(
        response=REGISTER_PAGE,
        mimetype='text/html'
    )
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/edit/<username>')
def edit(username):
    response = app.response_class(
        response=EDIT_PAGE,
        mimetype='text/html'
    )
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

# API Routes
@app.route('/api/create', methods=['POST'])
def create_card():
    try:
        data = request.get_json() or {{}}
        name = (data.get('name') or '').strip()

        if not name:
            return jsonify({{'success': False, 'error': 'Name is required'}}), 400

        result = generator.create_card(
            name=name,
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            instagram=data.get('instagram', ''),
            linkedin=data.get('linkedin', ''),
            twitter=data.get('twitter', ''),
            bio=data.get('bio', ''),
            template=data.get('template', 'professional'),
            photo=data.get('photo', ''),
            source='admin'
        )

        generator.git_push_background(f"Add card: {{name}}")

        return jsonify({{
            'success': True,
            'url': result['url'],
            'username': result['username'],
            'message': 'Card created successfully'
        }}), 201

    except Exception as e:
        return jsonify({{'success': False, 'error': f'Error: {{str(e)}}'}}) , 500

@app.route('/api/register', methods=['POST'])
def register_card():
    try:
        data = request.get_json() or {{}}
        name = (data.get('name') or '').strip()

        if not name:
            return jsonify({{'success': False, 'error': 'Name is required'}}), 400

        result = generator.create_card(
            name=name,
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            bio=data.get('bio', ''),
            template='professional',
            photo=data.get('photo', ''),
            source='client'
        )

        update_pending_count()
        
        generator.git_push_background(f"Client registration: {{name}}")

        return jsonify({{
            'success': True,
            'message': 'Registration successful'
        }}), 201

    except Exception as e:
        return jsonify({{'success': False, 'error': f'Error: {{str(e)}}'}}) 500

@app.route('/api/cards', methods=['GET'])
def list_cards():
    try:
        cards = generator.list_cards()
        
        stats = {{
            'pending': len([c for c in cards if c.get('status') == 'pending']),
            'printed': len([c for c in cards if c.get('status') == 'printed']),
            'modified': len([c for c in cards if c.get('status') == 'modified']),
            'total': len(cards)
        }}
        
        return jsonify({{'success': True, 'cards': cards, 'stats': stats}})
    except Exception as e:
        return jsonify({{'success': False, 'error': str(e)}}), 500

@app.route('/api/cards/<username>', methods=['GET'])
def get_card(username):
    try:
        data = generator.get_card_data(username)
        if data:
            return jsonify({{'success': True, 'data': data}})
        return jsonify({{'success': False, 'error': 'Card not found'}}), 404
    except Exception as e:
        return jsonify({{'success': False, 'error': str(e)}}), 500

@app.route('/api/cards/<username>', methods=['PUT'])
def update_card(username):
    try:
        data = request.get_json() or {{}}
        
        result = generator.update_card(
            username=username,
            name=data.get('name'),
            phone=data.get('phone'),
            email=data.get('email'),
            instagram=data.get('instagram'),
            linkedin=data.get('linkedin'),
            twitter=data.get('twitter'),
            bio=data.get('bio'),
            template=data.get('template'),
            photo=data.get('photo')
        )

        generator.git_push_background(f"Update card: {{username}}")

        return jsonify({{'success': True, 'message': 'Card updated'}})
    except Exception as e:
        return jsonify({{'success': False, 'error': str(e)}}), 500

@app.route('/api/cards/<username>', methods=['DELETE'])
def delete_card(username):
    try:
        if generator.delete_card(username):
            generator.git_push_background(f"Delete card: {{username}}")
            return jsonify({{'success': True}})
        return jsonify({{'success': False, 'error': 'Card not found'}}), 404
    except Exception as e:
        return jsonify({{'success': False, 'error': str(e)}}), 500

@app.route('/api/nfc/test', methods=['GET'])
def nfc_test():
    try:
        writer = NFCWriter()
        if writer.connect():
            writer.close()
            return jsonify({{'success': True, 'message': 'NFC reader connected and working'}})
        return jsonify({{'success': False, 'message': 'Failed to connect to NFC reader'}}), 503
    except Exception as e:
        return jsonify({{'success': False, 'message': f'Error: {{str(e)}}'}}) 500

@app.route('/api/nfc/write', methods=['POST'])
def nfc_write():
    try:
        data = request.get_json() or {{}}
        url = data.get('url', '')
        username = data.get('username', '')

        if not url:
            return jsonify({{'success': False, 'message': 'URL is required'}}), 400

        writer = NFCWriter()
        ok, msg = writer.write_url(url, timeout=15)
        writer.close()

        if ok and username:
            generator.mark_as_printed(username)
            generator.git_push_background(f"Print card: {{username}}")

        return jsonify({{'success': ok, 'message': msg}})
    except Exception as e:
        return jsonify({{'success': False, 'message': f'Error: {{str(e)}}'}}) 500

@app.route('/api/nfc/read', methods=['GET'])
def nfc_read():
    try:
        writer = NFCWriter()
        data, msg = writer.read_card(timeout=15)
        writer.close()

        if data:
            return jsonify({{'success': True, 'data': data, 'message': msg}})
        return jsonify({{'success': False, 'message': msg}}), 404
    except Exception as e:
        return jsonify({{'success': False, 'message': f'Error: {{str(e)}}'}}) 500

@app.route('/api/pending-count', methods=['GET'])
def get_pending_count():
    try:
        count = len(generator.list_cards(status_filter='pending'))
        return jsonify({{'count': count}})
    except:
        return jsonify({{'count': 0}})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Maroof NFC System Starting...")
    print("=" * 50)
    print(f"📡 Server: http://0.0.0.0:7070")
    print(f"📱 Register: http://0.0.0.0:7070/register")
    print(f"📊 Dashboard: http://0.0.0.0:7070/dashboard")
    print(f"⚙️  Settings: http://0.0.0.0:7070/settings")
    print(f"🎨 Cache version: {{CACHE_VERSION}}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=7070, debug=False)