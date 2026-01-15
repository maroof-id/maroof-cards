#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maroof Web App - Clean Version with Separated Templates
"""

from flask import Flask, request, jsonify, render_template
import os
import sys
from pathlib import Path
from datetime import datetime

current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from create_card import CardGenerator
from nfc_writer import NFCWriter

app = Flask(__name__, 
            template_folder='../templates/pages',
            static_folder='../static')
app.config['JSON_AS_ASCII'] = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

generator = CardGenerator()

# Notification counter
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

# =====================================================
# PAGE ROUTES
# =====================================================

@app.route('/')
def index():
    """Main page - Create card (Admin)"""
    response = app.response_class(
        response=render_template('home.html'),
        mimetype='text/html'
    )
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/dashboard')
def dashboard():
    """Dashboard - Manage cards (Admin)"""
    response = app.response_class(
        response=render_template('dashboard.html'),
        mimetype='text/html'
    )
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/settings')
def settings():
    """Settings - NFC reader (Admin)"""
    response = app.response_class(
        response=render_template('settings.html'),
        mimetype='text/html'
    )
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/register')
def register():
    """Register page - Client registration"""
    response = app.response_class(
        response=render_template('register.html'),
        mimetype='text/html'
    )
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/edit/<username>')
def edit(username):
    """Edit page - Edit existing card"""
    response = app.response_class(
        response=render_template('edit.html'),
        mimetype='text/html'
    )
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

# =====================================================
# API ROUTES
# =====================================================

@app.route('/api/create', methods=['POST'])
def create_card():
    """Create new card (Admin)"""
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
            template=data.get('template', 'professional'),
            photo=data.get('photo', ''),
            source='admin'
        )

        generator.git_push_background(f"Add card: {name}")

        return jsonify({
            'success': True,
            'url': result['url'],
            'username': result['username'],
            'message': 'Card created successfully'
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500

@app.route('/api/register', methods=['POST'])
def register_card():
    """Register card (Client)"""
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
            template=data.get('template', 'professional'),
            photo=data.get('photo', ''),
            source='client'
        )

        update_pending_count()
        
        generator.git_push_background(f"Client registration: {name}")

        return jsonify({
            'success': True,
            'message': 'Registration successful'
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500
@app.route('/api/cards/<username>', methods=['DELETE'])
def delete_card(username):
    """Delete card"""
    try:
        if generator.delete_card(username):
            generator.git_push_background(f"Delete card: {username}")
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Card not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================
# NFC API ROUTES
# =====================================================

@app.route('/api/nfc/test', methods=['GET'])
def nfc_test():
    """Test NFC reader connection"""
    try:
        writer = NFCWriter()
        if writer.connect():
            writer.close()
            return jsonify({'success': True, 'message': 'NFC reader connected and working'})
        return jsonify({'success': False, 'message': 'Failed to connect to NFC reader'}), 503
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/nfc/write', methods=['POST'])
def nfc_write():
    """Write URL to NFC card"""
    try:
        data = request.get_json() or {}
        url = data.get('url', '')
        username = data.get('username', '')

        if not url:
            return jsonify({'success': False, 'message': 'URL is required'}), 400

        writer = NFCWriter()
        ok, msg = writer.write_url(url, timeout=15)
        writer.close()

        if ok and username:
            generator.mark_as_printed(username)
            generator.git_push_background(f"Print card: {username}")

        return jsonify({'success': ok, 'message': msg})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/nfc/read', methods=['GET'])
def nfc_read():
    """Read NFC card"""
    try:
        writer = NFCWriter()
        data, msg = writer.read_card(timeout=15)
        writer.close()

        if data:
            return jsonify({'success': True, 'data': data, 'message': msg})
        return jsonify({'success': False, 'message': msg}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/pending-count', methods=['GET'])
def get_pending_count_api():
    """Get pending cards count"""
    try:
        count = len(generator.list_cards(status_filter='pending'))
        return jsonify({'count': count})
    except:
        return jsonify({'count': 0})

# =====================================================
# SERVER START
# =====================================================

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Maroof NFC System Starting...")
    print("=" * 50)
    print(f"📡 Server: http://0.0.0.0:7070")
    print(f"📱 Register: http://0.0.0.0:7070/register")
    print(f"📊 Dashboard: http://0.0.0.0:7070/dashboard")
    print(f"⚙️  Settings: http://0.0.0.0:7070/settings")
    print(f"🎨 Cache version: {CACHE_VERSION}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=7070, debug=False)
