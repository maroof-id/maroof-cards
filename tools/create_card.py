#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maroof - Digital Business Cards Generator
Creates professional digital business cards with NFC support
"""

import re
import json
import subprocess
import base64
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from datetime import datetime

class CardGenerator:
    """Generates digital business cards"""

    def __init__(self, repo_path: str = None):
        if repo_path is None:
            current_file = Path(__file__).resolve()
            self.repo_path = current_file.parent.parent
        else:
            self.repo_path = Path(repo_path)

        self.templates_path = self.repo_path / "templates"
        self.clients_path = self.repo_path / "clients"

        self.clients_path.mkdir(parents=True, exist_ok=True)
        self.templates_path.mkdir(parents=True, exist_ok=True)

    def get_available_templates(self) -> List[str]:
        """Get list of available templates from templates/cards/"""
        templates_dir = self.templates_path / "cards"
        if not templates_dir.exists():
            return ['professional']
        
        templates = []
        for file in templates_dir.glob("*.html"):
            template_name = file.stem
            templates.append(template_name)
        
        return sorted(templates) if templates else ['professional']

    def sanitize_username(self, name: str) -> str:
        """Convert Arabic/English name to safe username"""
        name = name.strip()

        arabic_map = {
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
            if char in arabic_map:
                result.append(arabic_map[char])
            elif char.isalnum() or char == '-':
                result.append(char)
            elif char == ' ':
                result.append('-')

        username = ''.join(result)
        username = re.sub(r'-+', '-', username)
        username = username.strip('-')

        return username or 'user'

    def get_unique_username(self, base_username: str) -> str:
        """Ensure username is unique"""
        username = base_username
        counter = 1

        while (self.clients_path / username).exists():
            username = f"{base_username}-{counter}"
            counter += 1

        return username

    def format_phone_international(self, phone: str) -> str:
        """Convert phone to international format"""
        phone = re.sub(r'\D', '', phone)

        if phone.startswith('00966'):
            return phone[2:]
        elif phone.startswith('966'):
            return phone
        elif phone.startswith('0'):
            return '966' + phone[1:]
        else:
            return '966' + phone

    def compress_image(self, image_bytes: bytes, image_format: str) -> bytes:
        """Compress image to reduce size"""
        try:
            from PIL import Image
            from io import BytesIO
            
            img = Image.open(BytesIO(image_bytes))
            
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            max_size = (800, 800)
            if img.width > max_size[0] or img.height > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
            
        except ImportError:
            print("⚠️ Pillow not installed")
            return image_bytes
        except Exception as e:
            print(f"⚠️ Compression failed: {e}")
            return image_bytes

    def load_template(self, template_name: str) -> str:
        """Load HTML template"""
        template_file = self.templates_path / "cards" / f"{template_name}.html"

        if not template_file.exists():
            print(f"⚠️ Template not found: {template_name}, using professional")
            template_file = self.templates_path / "cards" / "professional.html"
            
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")

        with open(template_file, 'r', encoding='utf-8') as f:
            return f.read()

    def replace_variables(self, html: str, data: Dict[str, str]) -> str:
        """Replace variables in HTML template"""

        if 'PHONE' in data and data['PHONE']:
            data['PHONE_INTL'] = self.format_phone_international(data['PHONE'])

        if 'NAME' in data and data['NAME']:
            data['NAME_INITIAL'] = data['NAME'][0].upper()

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

        for key, value in data.items():
            if not value:
                pattern = f'{{{{#if !{key}}}}}(.*?){{{{/if}}}}'
                html = re.sub(pattern, r'\1', html, flags=re.DOTALL)
            else:
                pattern = f'{{{{#if !{key}}}}}.*?{{{{/if}}}}'
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
        website: str = '',  # ← NEW: Website field
        bio: str = '',
        template: str = 'professional',
        username: Optional[str] = None,
        photo: str = '',
        source: str = 'admin'
    ) -> Dict[str, str]:
        """Create new business card"""

        if not name or not name.strip():
            raise ValueError('Name is required')

        if not username:
            base_username = self.sanitize_username(name)
            username = self.get_unique_username(base_username)

        client_dir = self.clients_path / username
        client_dir.mkdir(exist_ok=True)

        photo_path = ''
        if photo and photo.startswith('data:image'):
            try:
                match = re.match(r'data:image/(\w+);base64,(.+)', photo)
                if match:
                    image_format = match.group(1).lower()
                    image_data = match.group(2)
                    
                    image_bytes = base64.b64decode(image_data)
                    compressed_bytes = self.compress_image(image_bytes, image_format)
                    
                    photo_filename = 'photo.jpg'
                    photo_file_path = client_dir / photo_filename
                    
                    with open(photo_file_path, 'wb') as f:
                        f.write(compressed_bytes)
                    
                    photo_path = f'./{photo_filename}'
                    
                    original_size = len(image_bytes) / 1024
                    compressed_size = len(compressed_bytes) / 1024
                    print(f"✅ Photo: {original_size:.1f}KB → {compressed_size:.1f}KB")
            except Exception as e:
                print(f"⚠️ Photo failed: {e}")
                photo_path = ''

        # ✅ FIX: Add template to data.json
        data = {
            'NAME': name,
            'PHONE': phone,
            'EMAIL': email,
            'INSTAGRAM': instagram.lstrip('@'),
            'LINKEDIN': linkedin,
            'TWITTER': twitter.lstrip('@'),
            'WEBSITE': website,  # ← NEW
            'BIO': bio or '',
            'PHOTO': photo_path,
            'template': template,  # ← FIX: Save template name
            'created_at': datetime.now().isoformat(),
            'source': source,
            'status': 'pending',
            'print_count': 0,
            'print_history': []
        }

        if data.get('PHONE'):
            data['PHONE_INTL'] = self.format_phone_international(data['PHONE'])

        try:
            html = self.load_template(template)
            html = self.replace_variables(html, data)
        except Exception as e:
            print(f"⚠️ Template error: {e}")
            html = self.load_template('professional')
            html = self.replace_variables(html, data)

        output_file = client_dir / 'index.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        # ✅ FIX: Always save data.json
        data_file = client_dir / 'data.json'
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self._create_vcard(data, username, client_dir)

        return {
            'username': username,
            'url': f'https://maroof-id.github.io/maroof-cards/clients/{username}/',
            'path': str(output_file),
            'template': template,
            'source': source
        }

    def update_card(
        self,
        username: str,
        name: str = None,
        phone: str = None,
        email: str = None,
        instagram: str = None,
        linkedin: str = None,
        twitter: str = None,
        website: str = None,  # ← NEW
        bio: str = None,
        template: str = None,
        photo: str = None
    ) -> Dict[str, str]:
        """Update existing card"""
        
        data_file = self.clients_path / username / 'data.json'
        if not data_file.exists():
            raise ValueError(f'Card not found: {username}')
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update fields
        if name: data['NAME'] = name
        if phone: data['PHONE'] = phone
        if email: data['EMAIL'] = email
        if instagram: data['INSTAGRAM'] = instagram.lstrip('@')
        if linkedin: data['LINKEDIN'] = linkedin
        if twitter: data['TWITTER'] = twitter.lstrip('@')
        if website is not None: data['WEBSITE'] = website  # ← NEW
        if bio is not None: data['BIO'] = bio
        
        # ✅ FIX: Update template
        if template:
            data['template'] = template
        
        if photo and photo.startswith('data:image'):
            client_dir = self.clients_path / username
            try:
                match = re.match(r'data:image/(\w+);base64,(.+)', photo)
                if match:
                    image_data = match.group(2)
                    image_bytes = base64.b64decode(image_data)
                    compressed_bytes = self.compress_image(image_bytes, 'jpg')
                    
                    photo_filename = 'photo.jpg'
                    photo_file_path = client_dir / photo_filename
                    
                    with open(photo_file_path, 'wb') as f:
                        f.write(compressed_bytes)
                    
                    data['PHOTO'] = f'./{photo_filename}'
            except Exception as e:
                print(f"⚠️ Photo update failed: {e}")
        
        if data.get('print_count', 0) > 0:
            data['status'] = 'modified'
        
        if data.get('PHONE'):
            data['PHONE_INTL'] = self.format_phone_international(data['PHONE'])
        
        # ✅ FIX: Use template from data
        template_name = data.get('template', 'professional')
        
        try:
            html = self.load_template(template_name)
            html = self.replace_variables(html, data)
        except Exception as e:
            print(f"⚠️ Template error: {e}")
            html = self.load_template('professional')
            html = self.replace_variables(html, data)
        
        output_file = self.clients_path / username / 'index.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # ✅ FIX: Save updated data.json
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self._create_vcard(data, username, self.clients_path / username)
        
        return {
            'username': username,
            'url': f'https://maroof-id.github.io/maroof-cards/clients/{username}/',
            'status': data.get('status'),
            'template': template_name
        }

    def mark_as_printed(self, username: str) -> bool:
        """Mark card as printed"""
        data_file = self.clients_path / username / 'data.json'
        if not data_file.exists():
            return False
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['print_count'] = data.get('print_count', 0) + 1
        data['status'] = 'printed'
        
        if 'print_history' not in data:
            data['print_history'] = []
        
        data['print_history'].append({
            'date': datetime.now().isoformat(),
            'count': data['print_count']
        })
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True

    def _create_vcard(self, data: Dict[str, str], username: str, client_dir: Path):
        """Create vCard file"""
        vcard_lines = [
            'BEGIN:VCARD',
            'VERSION:3.0',
            f'FN:{data.get("NAME", "")}',
            f'N:{data.get("NAME", "")};;;;',
        ]
        
        if data.get('PHOTO') and data['PHOTO'].startswith('./'):
            photo_url = f'https://maroof-id.github.io/maroof-cards/clients/{username}/{data["PHOTO"][2:]}'
            vcard_lines.append(f'PHOTO;VALUE=URL;TYPE=JPEG:{photo_url}')
        
        if data.get('PHONE_INTL'):
            vcard_lines.append(f'TEL;TYPE=CELL:+{data["PHONE_INTL"]}')
        elif data.get('PHONE'):
            vcard_lines.append(f'TEL;TYPE=CELL:{data["PHONE"]}')
        
        if data.get('EMAIL'):
            vcard_lines.append(f'EMAIL;TYPE=INTERNET:{data["EMAIL"]}')
        
        if data.get('WEBSITE'):
            vcard_lines.append(f'URL;TYPE=Website:{data["WEBSITE"]}')
        
        if data.get('INSTAGRAM'):
            vcard_lines.append(f'URL;TYPE=Instagram:https://instagram.com/{data["INSTAGRAM"]}')
        
        if data.get('LINKEDIN'):
            vcard_lines.append(f'URL;TYPE=LinkedIn:https://linkedin.com/in/{data["LINKEDIN"]}')
        
        if data.get('TWITTER'):
            vcard_lines.append(f'URL;TYPE=Twitter:https://twitter.com/{data["TWITTER"]}')
        
        vcard_lines.append(f'URL:https://maroof-id.github.io/maroof-cards/clients/{username}/')
        
        if data.get('BIO'):
            vcard_lines.append(f'NOTE:{data["BIO"]}')
        
        vcard_lines.append('END:VCARD')
        
        vcard_path = client_dir / 'contact.vcf'
        with open(vcard_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(vcard_lines))
        
        return vcard_path

    def git_push(self, message: str = 'Update cards', timeout: int = 30) -> Tuple[bool, str]:
        """Push to GitHub"""
        try:
            subprocess.run(['git', 'add', '.'], cwd=self.repo_path, check=True, timeout=timeout, capture_output=True)
            
            status = subprocess.run(['git', 'status', '--porcelain'], cwd=self.repo_path, capture_output=True, text=True, check=True, timeout=timeout)
            
            if not status.stdout.strip():
                return True, "No changes"
            
            subprocess.run(['git', 'commit', '-m', message], cwd=self.repo_path, capture_output=True, text=True, timeout=timeout)
            subprocess.run(['git', 'push'], cwd=self.repo_path, check=True, timeout=timeout, capture_output=True)
            
            return True, "Success"
        except:
            return False, "Failed"

    def git_push_background(self, message: str = 'Update cards', callback=None):
        """Push in background"""
        from threading import Thread
        def task():
            success, msg = self.git_push(message)
            if callback:
                try:
                    callback(success, msg)
                except:
                    pass
        Thread(target=task, daemon=True).start()

    def get_card_data(self, username: str) -> Optional[Dict]:
        """Load card data"""
        data_file = self.clients_path / username / 'data.json'
        if not data_file.exists():
            return None
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_cards(self, status_filter: str = None) -> list:
        """List all cards"""
        cards = []
        for client_dir in self.clients_path.iterdir():
            if client_dir.is_dir():
                data_file = client_dir / 'data.json'
                if data_file.exists():
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        card_status = data.get('status', 'pending')
                        
                        if status_filter is None or card_status == status_filter:
                            cards.append({
                                'username': client_dir.name,
                                'name': data.get('NAME', ''),
                                'phone': data.get('PHONE', ''),
                                'status': card_status,
                                'source': data.get('source', 'admin'),
                                'template': data.get('template', 'professional'),
                                'print_count': data.get('print_count', 0),
                                'created_at': data.get('created_at', ''),
                                'url': f'https://maroof-id.github.io/maroof-cards/clients/{client_dir.name}/'
                            })
        
        cards.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return cards

    def delete_card(self, username: str) -> bool:
        """Delete card"""
        import shutil
        client_dir = self.clients_path / username
        if not client_dir.exists():
            return False
        shutil.rmtree(client_dir)
        return True