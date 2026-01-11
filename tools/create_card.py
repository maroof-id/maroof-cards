#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maroof - Digital Business Cards Generator
Creates professional digital business cards with NFC support
"""
ش
import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple

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
        template: str = 'modern',
        username: Optional[str] = None,
        photo: str = ''
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

        # Prepare data
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

        # Add international phone format and persist it
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
            'url': f'https://maroof-id.github.io/maroof-cards/{username}',
            'path': str(output_file),
            'template': template
        }

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

        vcard += f"URL:https://maroof-id.github.io/maroof-cards/{username}\n"

        if data.get('BIO'):
            vcard += f"NOTE:{data['BIO']}\n"

        if data.get('PHOTO'):
            vcard += f"PHOTO;VALUE=URL:{data['PHOTO']}\n"

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
        """Push changes to GitHub with proper error handling.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Stage changes
            try:
                subprocess.run(
                    ['git', 'add', '.'],
                    cwd=self.repo_path,
                    check=True,
                    timeout=timeout,
                    capture_output=True
                )
            except subprocess.TimeoutExpired:
                error_msg = "❌ مهلة انتظار: git add تجاوز الوقت / Timeout: git add took too long"
                print(error_msg)
                return False, error_msg
            except subprocess.CalledProcessError as e:
                error_msg = f"❌ خطأ: فشل إضافة الملفات / Error: git add failed - {e.stderr.decode() if e.stderr else str(e)}"
                print(error_msg)
                return False, error_msg

            # Check if there is anything to commit
            try:
                status = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=timeout
                )
            except subprocess.TimeoutExpired:
                error_msg = "❌ مهلة انتظار: git status تجاوز الوقت / Timeout: git status took too long"
                print(error_msg)
                return False, error_msg
            except subprocess.CalledProcessError as e:
                error_msg = f"❌ خطأ: فشل التحقق من الحالة / Error: git status failed"
                print(error_msg)
                return False, error_msg

            if not status.stdout.strip():
                print("ℹ️ لا توجد تغييرات / No changes to commit")
                # Try to push anyway in case remote changed
                try:
                    subprocess.run(
                        ['git', 'push'],
                        cwd=self.repo_path,
                        check=True,
                        timeout=timeout,
                        capture_output=True
                    )
                    print("✅ تم دفع البيانات بنجاح / Successfully pushed to GitHub")
                    return True, "✅ تم دفع البيانات بنجاح / Successfully pushed to GitHub"
                except subprocess.TimeoutExpired:
                    error_msg = "❌ مهلة انتظار: git push تجاوز الوقت / Timeout: git push took too long"
                    print(error_msg)
                    return False, error_msg
                except subprocess.CalledProcessError as e:
                    error_msg = f"❌ خطأ: فشل دفع البيانات / Error: git push failed - GitHub may be offline"
                    print(error_msg)
                    return False, error_msg

            # Commit changes
            try:
                commit = subprocess.run(
                    ['git', 'commit', '-m', message],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                if commit.returncode != 0:
                    combined = (commit.stdout or '') + (commit.stderr or '')
                    if 'nothing to commit' in combined.lower():
                        print("ℹ️ لا توجد تغييرات / No changes to commit")
                    else:
                        error_msg = f"❌ خطأ: فشل الحفظ / Git commit failed: {combined}"
                        print(error_msg)
                        return False, error_msg
            except subprocess.TimeoutExpired:
                error_msg = "❌ مهلة انتظار: git commit تجاوز الوقت / Timeout: git commit took too long"
                print(error_msg)
                return False, error_msg

            # Push
            try:
                subprocess.run(
                    ['git', 'push'],
                    cwd=self.repo_path,
                    check=True,
                    timeout=timeout,
                    capture_output=True
                )
                success_msg = "✅ تم دفع البيانات بنجاح / Successfully pushed to GitHub"
                print(success_msg)
                return True, success_msg

            except subprocess.TimeoutExpired:
                error_msg = "❌ مهلة انتظار: git push تجاوز الوقت / Timeout: git push took too long"
                print(error_msg)
                return False, error_msg
            except subprocess.CalledProcessError as e:
                error_msg = "❌ خطأ: فشل دفع البيانات إلى GitHub / Error: git push failed - Check credentials or network"
                print(error_msg)
                return False, error_msg

        except Exception as e:
            error_msg = f"❌ خطأ غير متوقع / Unexpected error: {str(e)}"
            print(error_msg)
            return False, error_msg

    def git_push_background(self, message: str = 'Update cards', callback=None):
        """Run git_push in a background thread with proper error handling.

        Args:
            message: Commit message
            callback: Optional callback function that receives (success: bool, message: str)

        Returns:
            Thread object
        """
        def background_task():
            success, msg = self.git_push(message)
            if callback:
                try:
                    callback(success, msg)
                except Exception as e:
                    print(f"❌ خطأ في callback / Callback error: {e}")

        from threading import Thread
        t = Thread(target=background_task, daemon=True)
        t.start()
        return t

    def get_card_data(self, username: str) -> Optional[Dict]:
        """Load card data from username"""
        data_file = self.clients_path / username / 'data.json'

        if not data_file.exists():
            return None

        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def delete_card(self, username: str) -> bool:
        """Delete a card"""
        import shutil

        client_dir = self.clients_path / username

        if not client_dir.exists():
            return False

        shutil.rmtree(client_dir)
        return True

    def list_cards(self) -> list:
        """List all existing cards"""
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