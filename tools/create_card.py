#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معروف - نظام إنشاء البطاقات التعريفية الرقمية
Maroof Digital Business Cards Generator
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, Optional
import subprocess

class CardGenerator:
    """مولّد البطاقات التعريفية"""
    
    def __init__(self, repo_path: str = None):
        if repo_path is None:
            # تحديد المسار تلقائياً
            current_file = Path(__file__).resolve()
            self.repo_path = current_file.parent.parent
        else:
            self.repo_path = Path(repo_path)
            
        self.templates_path = self.repo_path / "templates"
        self.clients_path = self.repo_path / "clients"
        
        # التأكد من وجود المجلدات
        self.clients_path.mkdir(exist_ok=True)
        
    def sanitize_username(self, name: str) -> str:
        """تحويل الاسم لـ username صالح"""
        name = name.strip()
        
        # تحويل العربي للإنجليزي
        arabic_to_english = {
            'ا': 'a', 'أ': 'a', 'إ': 'i', 'آ': 'a',
            'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j',
            'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'th',
            'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh',
            'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'z',
            'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ق': 'q',
            'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n',
            'ه': 'h', 'و': 'w', 'ي': 'y', 'ى': 'a',
            'ة': 'h', 'ء': 'a'
        }
        
        result = []
        for char in name.lower():
            if char in arabic_to_english:
                result.append(arabic_to_english[char])
            elif char.isalnum() or char == '-':
                result.append(char)
            elif char == ' ':
                result.append('-')
        
        username = ''.join(result)
        username = re.sub(r'-+', '-', username)
        username = username.strip('-')
        
        return username or 'user'
    
    def format_phone_international(self, phone: str) -> str:
        """تحويل رقم الجوال لصيغة دولية"""
        phone = re.sub(r'\D', '', phone)
        
        if phone.startswith('00966'):
            return phone[2:]
        elif phone.startswith('966'):
            return phone
        elif phone.startswith('0'):
            return '966' + phone[1:]
        else:
            return '966' + phone
    
    def load_template(self, template_name: str) -> str:
        """تحميل قالب HTML"""
        template_file = self.templates_path / f"{template_name}.html"
        
        if not template_file.exists():
            raise FileNotFoundError(f"القالب غير موجود: {template_name}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def replace_variables(self, html: str, data: Dict[str, str]) -> str:
        """استبدال المتغيرات في HTML"""
        
        if 'PHONE' in data and data['PHONE']:
            data['PHONE_INTL'] = self.format_phone_international(data['PHONE'])
        
        for key, value in data.items():
            if value:
                html = html.replace(f'{{{{{key}}}}}', str(value))
        
        for key, value in data.items():
            if value:
                pattern = f'{{{{#if {key}}}}}(.*?){{{{/if}}}}'
                html = re.sub(pattern, r'\1', html, flags=re.DOTALL)
            else:
                pattern = f'{{{{#if {key}}}}}.*?{{{{/if}}}}'
                html = re.sub(pattern, '', html, flags=re.DOTALL)
        
        html = re.sub(r'\{\{[^}]+\}\}', '', html)
        
        return html
    
    def create_card(
        self,
        name: str,
        phone: str = '',
        email: str = '',
        instagram: str = '',
        linkedin: str = '',
        twitter: str = '',
        bio: str = '',
        template: str = 'modern',
        username: Optional[str] = None,
        photo: str = ''
    ) -> Dict[str, str]:
        """إنشاء بطاقة جديدة"""
        
        if not username:
            username = self.sanitize_username(name)
        
        client_dir = self.clients_path / username
        client_dir.mkdir(exist_ok=True)
        
        data = {
            'NAME': name,
            'PHONE': phone,
            'EMAIL': email,
            'INSTAGRAM': instagram.lstrip('@'),
            'LINKEDIN': linkedin,
            'TWITTER': twitter.lstrip('@'),
            'BIO': bio or f'{name}',
            'PHOTO': photo
        }
        
        html = self.load_template(template)
        html = self.replace_variables(html, data)
        
        output_file = client_dir / 'index.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        data_file = client_dir / 'data.json'
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {
            'username': username,
            'url': f'https://maroof-id.github.io/maroof-cards/{username}',
            'path': str(output_file),
            'template': template
        }
    
    def list_cards(self) -> list:
        """عرض قائمة البطاقات الموجودة"""
        cards = []
        
        for client_dir in self.clients_path.iterdir():
            if client_dir.is_dir():
                data_file = client_dir / 'data.json'
                if data_file.exists():
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        cards.append({
                            'username': client_dir.name,
                            'name': data.get('NAME', ''),
                            'url': f'https://maroof-id.github.io/maroof-cards/{client_dir.name}'
                        })
        
        return cards


if __name__ == '__main__':
    print("CardGenerator module loaded!")
