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
    
    def __init__(self, repo_path: str = "/home/Xmoha4/maroof-id.github.io"):
        self.repo_path = Path(repo_path)
        self.templates_path = self.repo_path / "templates"
        self.clients_path = self.repo_path / "clients"
        
        # التأكد من وجود المجلدات
        self.clients_path.mkdir(exist_ok=True)
        
    def sanitize_username(self, name: str) -> str:
        """
        تحويل الاسم لـ username صالح
        محمد أحمد → mohammed-ahmed
        """
        # إزالة المسافات الزائدة
        name = name.strip()
        
        # تحويل العربي للإنجليزي (transliteration بسيط)
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
        
        # تنظيف النتيجة
        username = ''.join(result)
        username = re.sub(r'-+', '-', username)  # إزالة الشرطات المتكررة
        username = username.strip('-')
        
        return username or 'user'
    
    def format_phone_international(self, phone: str) -> str:
        """
        تحويل رقم الجوال لصيغة دولية
        0501234567 → 966501234567
        """
        phone = re.sub(r'\D', '', phone)  # إزالة كل شيء ماعدا الأرقام
        
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
        
        # إضافة رقم دولي
        if 'PHONE' in data and data['PHONE']:
            data['PHONE_INTL'] = self.format_phone_international(data['PHONE'])
        
        # استبدال المتغيرات العادية {{VAR}}
        for key, value in data.items():
            if value:
                html = html.replace(f'{{{{{key}}}}}', str(value))
        
        # معالجة الشروط {{#if VAR}}...{{/if}}
        for key, value in data.items():
            if value:
                # إذا كان القيمة موجودة، احذف علامات الشرط واترك المحتوى
                pattern = f'{{{{#if {key}}}}}(.*?){{{{/if}}}}'
                html = re.sub(pattern, r'\1', html, flags=re.DOTALL)
            else:
                # إذا كانت القيمة فارغة، احذف كل المحتوى
                pattern = f'{{{{#if {key}}}}}.*?{{{{/if}}}}'
                html = re.sub(pattern, '', html, flags=re.DOTALL)
        
        # استبدال المتغيرات المتبقية بفراغ
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
        """
        إنشاء بطاقة جديدة
        
        Returns:
            dict: معلومات البطاقة المنشأة (username, url, path)
        """
        
        # توليد username إذا لم يُحدد
        if not username:
            username = self.sanitize_username(name)
        
        # إنشاء مجلد العميل
        client_dir = self.clients_path / username
        client_dir.mkdir(exist_ok=True)
        
        # تحضير البيانات
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
        
        # تحميل القالب
        html = self.load_template(template)
        
        # استبدال المتغيرات
        html = self.replace_variables(html, data)
        
        # حفظ الملف
        output_file = client_dir / 'index.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # حفظ البيانات كـ JSON (للتعديل لاحقاً)
        data_file = client_dir / 'data.json'
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {
            'username': username,
            'url': f'https://maroof-id.github.io/{username}',
            'path': str(output_file),
            'template': template
        }
    
    def git_push(self, message: str = 'تحديث البطاقات'):
        """رفع التعديلات لـ GitHub"""
        try:
            os.chdir(self.repo_path)
            
            # إضافة كل الملفات
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Commit
            subprocess.run(['git', 'commit', '-m', message], check=True)
            
            # Push
            subprocess.run(['git', 'push'], check=True)
            
            print("✅ تم رفع التحديثات لـ GitHub بنجاح!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ خطأ في رفع الملفات: {e}")
            return False
    
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
                            'url': f'https://maroof-id.github.io/{client_dir.name}'
                        })
        
        return cards


def main():
    """الدالة الرئيسية"""
    parser = argparse.ArgumentParser(
        description='معروف - نظام إنشاء البطاقات التعريفية',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--name', '-n', required=True, help='الاسم الكامل')
    parser.add_argument('--phone', '-p', default='', help='رقم الجوال')
    parser.add_argument('--email', '-e', default='', help='البريد الإلكتروني')
    parser.add_argument('--instagram', '-i', default='', help='Instagram username')
    parser.add_argument('--linkedin', '-l', default='', help='LinkedIn username')
    parser.add_argument('--twitter', '-t', default='', help='Twitter/X username')
    parser.add_argument('--bio', '-b', default='', help='نبذة تعريفية')
    parser.add_argument('--template', '-T', default='modern', 
                       choices=['modern', 'classic', 'minimal'],
                       help='القالب المستخدم')
    parser.add_argument('--username', '-u', default='',
                       help='اسم المستخدم (اختياري، يُولّد تلقائياً)')
    parser.add_argument('--photo', default='', help='رابط الصورة الشخصية')
    parser.add_argument('--push', action='store_true', 
                       help='رفع لـ GitHub تلقائياً')
    parser.add_argument('--list', action='store_true',
                       help='عرض قائمة البطاقات الموجودة')
    
    args = parser.parse_args()
    
    generator = CardGenerator()
    
    # عرض القائمة
    if args.list:
        cards = generator.list_cards()
        print(f"\n📋 البطاقات الموجودة ({len(cards)}):\n")
        for card in cards:
            print(f"  • {card['name']}")
            print(f"    🔗 {card['url']}\n")
        return
    
    # إنشاء بطاقة جديدة
    print(f"\n🎴 جاري إنشاء بطاقة لـ {args.name}...\n")
    
    result = generator.create_card(
        name=args.name,
        phone=args.phone,
        email=args.email,
        instagram=args.instagram,
        linkedin=args.linkedin,
        twitter=args.twitter,
        bio=args.bio,
        template=args.template,
        username=args.username or None,
        photo=args.photo
    )
    
    print(f"✅ تم إنشاء البطاقة بنجاح!")
    print(f"\n📊 معلومات البطاقة:")
    print(f"  👤 الاسم: {args.name}")
    print(f"  🆔 Username: {result['username']}")
    print(f"  🎨 القالب: {result['template']}")
    print(f"  🔗 الرابط: {result['url']}")
    print(f"  📁 المسار: {result['path']}")
    
    # رفع لـ GitHub
    if args.push:
        print(f"\n📤 جاري رفع البطاقة لـ GitHub...")
        generator.git_push(f"إضافة بطاقة: {args.name}")
    else:
        print(f"\n💡 لرفع البطاقة لـ GitHub، استخدم: --push")
    
    print(f"\n🎉 انتهى!")


if __name__ == '__main__':
    main()