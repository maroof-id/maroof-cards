#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template
import sys
from pathlib import Path
from datetime import datetime

current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from create_card import CardGenerator
from nfc_writer import NFCWriter

app = Flask(__name__, template_folder='../templates/pages', static_folder='../static')
app.config['JSON_AS_ASCII'] = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

generator = CardGenerator()

# ==================== PAGES ====================

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/edit/<username>')
def edit(username):
    return render_template('edit.html')

# ==================== API ENDPOINTS ====================

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get list of available templates"""
    try:
        templates = generator.get_available_templates()
        return jsonify({'success': True, 'templates': templates})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/create', methods=['POST'])
def create_card():
    """Create new card (admin interface)"""
    try:
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400

        result = generator.create_card(
            name=name,
            job_title=data.get('job_title', ''),  # 🆕
            company=data.get('company', ''),  # 🆕
            phone=data.get('phone', ''),
            phone2=data.get('phone2', ''),  # 🆕
            email=data.get('email', ''),
            instagram=data.get('instagram', ''),
            linkedin=data.get('linkedin', ''),
            twitter=data.get('twitter', ''),
            youtube=data.get('youtube', ''),  # 🆕
            tiktok=data.get('tiktok', ''),  # 🆕
            snapchat=data.get('snapchat', ''),  # 🆕
            github=data.get('github', ''),  # 🆕
            website=data.get('website', ''),
            custom_link=data.get('custom_link', ''),  # 🆕
            bio=data.get('bio', ''),
            template=data.get('template', 'professional'),
            photo=data.get('photo', ''),
            cv=data.get('cv', ''),  # 🆕
            source='admin'
        )
        
        generator.git_push_background(f"Add card: {name}")
        
        return jsonify({
            'success': True,
            'url': result['url'],
            'username': result['username'],
            'template': result['template']
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500

@app.route('/api/register', methods=['POST'])
def register_card():
    """Register new card (client self-registration)"""
    try:
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400

        result = generator.create_card(
            name=name,
            job_title=data.get('job_title', ''),  # 🆕
            company=data.get('company', ''),  # 🆕
            phone=data.get('phone', ''),
            phone2=data.get('phone2', ''),  # 🆕
            email=data.get('email', ''),
            instagram=data.get('instagram', ''),
            linkedin=data.get('linkedin', ''),
            twitter=data.get('twitter', ''),
            youtube=data.get('youtube', ''),  # 🆕
            tiktok=data.get('tiktok', ''),  # 🆕
            snapchat=data.get('snapchat', ''),  # 🆕
            github=data.get('github', ''),  # 🆕
            website=data.get('website', ''),
            custom_link=data.get('custom_link', ''),  # 🆕
            bio=data.get('bio', ''),
            template=data.get('template', 'professional'),
            photo=data.get('photo', ''),
            cv=data.get('cv', ''),  # 🆕
            source='client'
        )
        
        generator.git_push_background(f"Client registration: {name}")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'username': result['username']
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500

@app.route('/api/cards', methods=['GET'])
def list_cards():
    """Get all cards with statistics"""
    try:
        cards = generator.list_cards()
        stats = {
            'pending': len([c for c in cards if c.get('status') == 'pending']),
            'printed': len([c for c in cards if c.get('status') == 'printed']),
            'modified': len([c for c in cards if c.get('status') == 'modified']),
            'total': len(cards)
        }
        return jsonify({'success': True, 'cards': cards, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cards/<username>', methods=['GET'])
def get_card(username):
    """Get card data by username"""
    try:
        data = generator.get_card_data(username)
        if data:
            return jsonify({'success': True, 'data': data})
        return jsonify({'success': False, 'error': 'Card not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cards/<username>', methods=['PUT'])
def update_card(username):
    """Update existing card"""
    try:
        data = request.get_json() or {}
        
        result = generator.update_card(
            username=username,
            name=data.get('name'),
            job_title=data.get('job_title'),  # 🆕
            company=data.get('company'),  # 🆕
            phone=data.get('phone'),
            phone2=data.get('phone2'),  # 🆕
            email=data.get('email'),
            instagram=data.get('instagram'),
            linkedin=data.get('linkedin'),
            twitter=data.get('twitter'),
            youtube=data.get('youtube'),  # 🆕
            tiktok=data.get('tiktok'),  # 🆕
            snapchat=data.get('snapchat'),  # 🆕
            github=data.get('github'),  # 🆕
            website=data.get('website'),
            custom_link=data.get('custom_link'),  # 🆕
            bio=data.get('bio'),
            template=data.get('template'),
            photo=data.get('photo'),
            cv=data.get('cv')  # 🆕
        )
        
        generator.git_push_background(f"Update card: {username}")
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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

# ==================== NFC ENDPOINTS ====================

@app.route('/api/nfc/test', methods=['GET'])
def nfc_test():
    """Test NFC reader connection"""
    try:
        writer = NFCWriter()
        if writer.ensure_connected():
            writer.close()
            return jsonify({'success': True, 'message': 'NFC reader connected'})
        return jsonify({'success': False, 'message': 'Failed to connect'}), 503
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
            return jsonify({'success': False, 'message': 'URL required'}), 400

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
    """Get count of pending cards"""
    try:
        count = len(generator.list_cards(status_filter='pending'))
        return jsonify({'count': count})
    except:
        return jsonify({'count': 0})

# ==================== SERVER START ====================
# Server IP endpoint
@app.route('/api/server-info', methods=['GET'])
def server_info():
    """Get server IP"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"
    
    return jsonify({
        'success': True,
        'ip': local_ip,
        'hostname': 'raspberrypi.local',
        'port': 7070
    })
    
if __name__ == '__main__':
    print("="*60)
    print("🚀 Maroof NFC System - Digital Business Cards")
    print("="*60)
    print("🌐 Admin Panel:    http://0.0.0.0:7070")
    print("📱 Registration:   http://0.0.0.0:7070/register")
    print("📊 Dashboard:      http://0.0.0.0:7070/dashboard")
    print("="*60)
    
    # Show available templates
    templates = generator.get_available_templates()
    print(f"📋 Available Templates ({len(templates)}):")
    for i, t in enumerate(templates, 1):
        print(f"   {i}. {t}")
    
    print("="*60)
    print("✨ Ready to create digital business cards!")
    print("="*60)
    
    app.run(host='0.0.0.0', port=7070, debug=False)