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
from typing import Dict, Optional, Tuple
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

    def sanitize_username(self, name: str) -> str:
        """Convert Arabic/English name to safe username"""
        name = name.strip()

        # Arabic to English transliteration
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
        """Ensure username is unique by adding sequential number if needed"""
        username = base_username
        counter = 1

        while (self.clients_path / username).exists():
            username = f"{base_username}-{counter}"
            counter += 1

        return username

    def format_phone_international(self, phone: str) -> str:
        """Convert phone to international format (966XXXXXXXXX)"""
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
            
            # Open image
            img = Image.open(BytesIO(image_bytes))
            
            # Convert RGBA to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if too large
            max_size = (800, 800)
            if img.width > max_size[0] or img.height > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save compressed
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
            
        except ImportError:
            # Pillow not installed, return original
            print("⚠️ Pillow not installed - image not compressed")
            return image_bytes
        except Exception as e:
            print(f"⚠️ Image compression failed: {e}")
            return image_bytes

    def load_template(self, template_name: str) -> str:
        """Load HTML template"""
        template_file = self.templates_path / f"{template_name}.html"

        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")

        with open(template_file, 'r', encoding='utf-8') as f:
            return f.read()

    def replace_variables(self, html: str, data: Dict[str, str]) -> str:
        """Replace variables in HTML template"""

        # Add international phone format
        if 'PHONE' in data and data['PHONE']:
            data['PHONE_INTL'] = self.format_phone_international(data['PHONE'])

        # Add name initial for avatar
        if 'NAME' in data and data['NAME']:
            data['NAME_INITIAL'] = data['NAME'][0].upper()

        # Replace simple variables
        for key, value in data.items():
            if value:
                html = html.replace(f'{{{{{key}}}}}', str(value))

        # Handle conditional blocks {{#if VAR}}...{{/if}}
        for key, value in data.items():
            if value:
                pattern = f'{{{{#if {key}}}}}(.*?){{{{/if}}}}'
                html = re.sub(pattern, r'\1', html, flags=re.DOTALL)
            else:
                pattern = f'{{{{#if {key}}}}}.*?{{{{/if}}}}'
                html = re.sub(pattern, '', html, flags=re.DOTALL)

        # Handle negation {{#if !VAR}}...{{/if}}
        for key, value in data.items():
            if not value:
                pattern = f'{{{{#if !{key}}}}}(.*?){{{{/if}}}}'
                html = re.sub(pattern, r'\1', html, flags=re.DOTALL)
            else:
                pattern = f'{{{{#if !{key}}}}}.*?{{{{/if}}}}'
                html = re.sub(pattern, '', html, flags=re.DOTALL)

        # Clean remaining variables
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
        template: str = 'professional',
        username: Optional[str] = None,
        photo: str = '',
        source: str = 'admin'
    ) -> Dict[str, str]:
        """Create new business card"""

        # Validate required fields
        if not name or not name.strip():
            raise ValueError('Name is required')

        # Generate username
        if not username:
            base_username = self.sanitize_username(name)
            username = self.get_unique_username(base_username)

        # Create client directory
        client_dir = self.clients_path / username
        client_dir.mkdir(exist_ok=True)

        # Save photo if provided (Base64 format)
        photo_path = ''
        if photo and photo.startswith('data:image'):
            try:
                # Parse data URL
                match = re.match(r'data:image/(\w+);base64,(.+)', photo)
                if match:
                    image_format = match.group(1).lower()
                    image_data = match.group(2)
                    
                    # Decode base64
                    image_bytes = base64.b64decode(image_data)
                    
                    # Compress image
                    compressed_bytes = self.compress_image(image_bytes, image_format)
                    
                    # Save to file (always as .jpg after compression)
                    photo_filename = 'photo.jpg'
                    photo_file_path = client_dir / photo_filename
                    
                    with open(photo_file_path, 'wb') as f:
                        f.write(compressed_bytes)
                    
                    photo_path = f'./{photo_filename}'
                    
                    # Calculate sizes
                    original_size = len(image_bytes) / 1024  # KB
                    compressed_size = len(compressed_bytes) / 1024  # KB
                    print(f"✅ Photo saved: {original_size:.1f}KB → {compressed_size:.1f}KB")
            except Exception as e:
                print(f"⚠️ Warning: Could not save photo - {e}")
                photo_path = ''

        # Prepare data
        data = {
            'NAME': name,
            'PHONE': phone,
            'EMAIL': email,
            'INSTAGRAM': instagram.lstrip('@'),
            'LINKEDIN': linkedin,
            'TWITTER': twitter.lstrip('@'),
            'BIO': bio or f'{name}',
            'PHOTO': photo_path,
            'created_at': datetime.now().isoformat(),
            'source': source,  # 'admin' or 'client'
            'status': 'pending',  # 'pending', 'printed', 'modified'
            'print_count': 0,
            'print_history': []
        }

        # Add international phone format
        if data.get('PHONE'):
            data['PHONE_INTL'] = self.format_phone_international(data['PHONE'])

        # Load and process template
        html = self.load_template(template)
        html = self.replace_variables(html, data)

        # Save HTML
        output_file = client_dir / 'index.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        # Save data.json
        data_file = client_dir / 'data.json'
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Create vCard
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
        bio: str = None,
        template: str = None,
        photo: str = None
    ) -> Dict[str, str]:
        """Update existing card"""
        
        # Load existing data
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
        if bio: data['BIO'] = bio
        
        # Update photo if provided
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
        
        # Mark as modified after print
        if data.get('print_count', 0) > 0:
            data['status'] = 'modified'
        
        # Update international phone
        if data.get('PHONE'):
            data['PHONE_INTL'] = self.format_phone_international(data['PHONE'])
        
        # Get template name
        template_name = template if template else data.get('template', 'professional')
        
        # Load and process template
        html = self.load_template(template_name)
        html = self.replace_variables(html, data)
        
        # Save HTML
        output_file = self.clients_path / username / 'index.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Save updated data
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Update vCard
        self._create_vcard(data, username, self.clients_path / username)
        
        return {
            'username': username,
            'url': f'https://maroof-id.github.io/maroof-cards/clients/{username}/',
            'status': data.get('status')
        }

    def mark_as_printed(self, username: str) -> bool:
        """Mark card as printed"""
        data_file = self.clients_path / username / 'data.json'
        if not data_file.exists():
            return False
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update print info
        data['print_count'] = data.get('print_count', 0) + 1
        data['status'] = 'printed'
        
        if 'print_history' not in data:
            data['print_history'] = []
        
        data['print_history'].append({
            'date': datetime.now().isoformat(),
            'count': data['print_count']
        })
        
        # Save
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True

    def _create_vcard(self, data: Dict[str, str], username: str, client_dir: Path):
        """Create vCard file for contact saving"""
        vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{data.get('NAME', '')}
"""

        if data.get('PHONE_INTL'):
            vcard += f"TEL;TYPE=CELL:+{data['PHONE_INTL']}\n"
        elif data.get('PHONE'):
            vcard += f"TEL;TYPE=CELL:{data['PHONE']}\n"

        if data.get('EMAIL'):
            vcard += f"EMAIL:{data['EMAIL']}\n"

        vcard += f"URL:https://maroof-id.github.io/maroof-cards/clients/{username}/\n"

        if data.get('BIO'):
            vcard += f"NOTE:{data['BIO']}\n"

        if data.get('PHOTO') and data['PHOTO'].startswith('./'):
            photo_url = f"https://maroof-id.github.io/maroof-cards/clients/{username}/{data['PHOTO'][2:]}"
            vcard += f"PHOTO;VALUE=URL:{photo_url}\n"

        social = []
        if data.get('INSTAGRAM'):
            social.append(f"Instagram: @{data['INSTAGRAM']}")
        if data.get('LINKEDIN'):
            social.append(f"LinkedIn: {data['LINKEDIN']}")
        if data.get('TWITTER'):
            social.append(f"Twitter: @{data['TWITTER']}")

        if social:
            vcard += f"X-SOCIALPROFILE:{' | '.join(social)}\n"

        vcard += "END:VCARD"

        vcard_path = client_dir / 'contact.vcf'
        with open(vcard_path, 'w', encoding='utf-8') as f:
            f.write(vcard)

        return vcard_path

    def git_push(self, message: str = 'Update cards', timeout: int = 30) -> Tuple[bool, str]:
        """Push changes to GitHub"""
        try:
            subprocess.run(['git', 'add', '.'], cwd=self.repo_path, check=True, timeout=timeout, capture_output=True)
            
            status = subprocess.run(['git', 'status', '--porcelain'], cwd=self.repo_path, capture_output=True, text=True, check=True, timeout=timeout)
            
            if not status.stdout.strip():
                return True, "No changes"
            
            subprocess.run(['git', 'commit', '-m', message], cwd=self.repo_path, capture_output=True, text=True, timeout=timeout)
            subprocess.run(['git', 'push'], cwd=self.repo_path, check=True, timeout=timeout, capture_output=True)
            
            return True, "Successfully pushed"
        except:
            return False, "Push failed"

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
        """List all cards with optional status filter"""
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
                                'print_count': data.get('print_count', 0),
                                'created_at': data.get('created_at', ''),
                                'url': f'https://maroof-id.github.io/maroof-cards/clients/{client_dir.name}/'
                            })
        
        # Sort by creation date (newest first)
        cards.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return cards

    def delete_card(self, username: str) -> bool:
        """Delete a card"""
        import shutil
        client_dir = self.clients_path / username
        if not client_dir.exists():
            return False
        shutil.rmtree(client_dir)
        return True