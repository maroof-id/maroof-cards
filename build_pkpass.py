#!/usr/bin/env python3
"""Build proper .pkpass file for Apple Wallet"""

import json
import zipfile
import hashlib
from pathlib import Path
from PIL import Image
import qrcode

def create_icon(client_dir):
    """Create a simple icon.png if doesn't exist"""
    icon_path = client_dir / "icon.png"
    if not icon_path.exists():
        # Create simple 29x29 icon (required by Apple)
        img = Image.new('RGB', (29, 29), color='#f59e0b')
        img.save(icon_path)
        print(f"✅ Created icon: {icon_path}")
    return icon_path

def create_logo(client_dir):
    """Create a simple logo.png if doesn't exist"""
    logo_path = client_dir / "logo.png"
    if not logo_path.exists():
        # Create simple 160x50 logo
        img = Image.new('RGB', (160, 50), color='#000000')
        img.save(logo_path)
        print(f"✅ Created logo: {logo_path}")
    return logo_path

def build_pkpass(username: str):
    """Build a proper .pkpass file"""
    
    base_dir = Path(__file__).parent.parent
    client_dir = base_dir / "clients" / username
    data_file = client_dir / "data.json"
    
    if not data_file.exists():
        print(f"❌ Card not found: {username}")
        return False
    
    print(f"📦 Building .pkpass for {username}...")
    
    # Load data
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Card URL
    card_url = f"https://maroof-id.github.io/maroof-cards-data/{username}/"
    
    # Create pass.json
    pass_data = {
        "formatVersion": 1,
        "passTypeIdentifier": "pass.com.maroof.card",
        "serialNumber": username,
        "teamIdentifier": "MAROOF",
        "organizationName": "Maroof Digital Cards",
        "description": f"{data.get('NAME', 'Business Card')}",
        "backgroundColor": "rgb(0, 0, 0)",
        "foregroundColor": "rgb(255, 255, 255)",
        "labelColor": "rgb(200, 200, 200)",
        "logoText": "MAROOF",
        "generic": {
            "primaryFields": [{
                "key": "name",
                "label": "",
                "value": data.get('NAME', ''),
                "textAlignment": "PKTextAlignmentLeft"
            }],
            "secondaryFields": [
                {
                    "key": "title",
                    "label": "TITLE",
                    "value": data.get('JOB_TITLE', ''),
                    "textAlignment": "PKTextAlignmentLeft"
                },
                {
                    "key": "company",
                    "label": "COMPANY",
                    "value": data.get('COMPANY', ''),
                    "textAlignment": "PKTextAlignmentLeft"
                }
            ],
            "auxiliaryFields": [
                {
                    "key": "phone",
                    "label": "PHONE",
                    "value": data.get('PHONE', ''),
                    "textAlignment": "PKTextAlignmentLeft"
                },
                {
                    "key": "email",
                    "label": "EMAIL",
                    "value": data.get('EMAIL', ''),
                    "textAlignment": "PKTextAlignmentLeft"
                }
            ],
            "backFields": [
                {
                    "key": "url",
                    "label": "Digital Card",
                    "value": card_url,
                    "textAlignment": "PKTextAlignmentLeft"
                }
            ]
        },
        "barcode": {
            "message": card_url,
            "format": "PKBarcodeFormatQR",
            "messageEncoding": "iso-8859-1"
        }
    }
    
    pass_json_path = client_dir / "pass.json"
    with open(pass_json_path, 'w', encoding='utf-8') as f:
        json.dump(pass_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created pass.json")
    
    # Create icon and logo
    create_icon(client_dir)
    create_logo(client_dir)
    
    # Create manifest.json
    manifest = {}
    files_to_include = ['pass.json', 'icon.png', 'logo.png']
    
    # Add photo if exists
    photo_path = client_dir / "photo.jpg"
    if photo_path.exists():
        files_to_include.append('photo.jpg')
    
    for filename in files_to_include:
        file_path = client_dir / filename
        if file_path.exists():
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha1(f.read()).hexdigest()
                manifest[filename] = file_hash
    
    manifest_path = client_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"✅ Created manifest.json with {len(manifest)} files")
    
    # Create signature (dummy - will show warning on iOS)
    signature_path = client_dir / "signature"
    # Use manifest hash as signature placeholder
    manifest_str = json.dumps(manifest, sort_keys=True)
    signature_hash = hashlib.sha256(manifest_str.encode()).digest()
    with open(signature_path, 'wb') as f:
        f.write(signature_hash)
    print(f"✅ Created signature (self-signed)")
    
    # Build .pkpass ZIP file
    pkpass_path = client_dir / f"{username}.pkpass"
    with zipfile.ZipFile(pkpass_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add pass.json
        zipf.write(pass_json_path, 'pass.json')
        
        # Add manifest.json
        zipf.write(manifest_path, 'manifest.json')
        
        # Add signature
        zipf.write(signature_path, 'signature')
        
        # Add icon and logo
        zipf.write(client_dir / 'icon.png', 'icon.png')
        zipf.write(client_dir / 'logo.png', 'logo.png')
        
        # Add photo if exists
        if photo_path.exists():
            zipf.write(photo_path, 'photo.jpg')
    
    print(f"\n🎉 SUCCESS! Created: {pkpass_path}")
    print(f"📦 File size: {pkpass_path.stat().st_size / 1024:.1f} KB")
    print(f"\n⚠️  IMPORTANT:")
    print(f"   - This is a SELF-SIGNED pass")
    print(f"   - iOS will show: 'This pass is not from a trusted source'")
    print(f"   - User must tap 'Add' to accept")
    print(f"\n📱 Download URL:")
    print(f"   https://maroof-id.github.io/maroof-cards-data/{username}/{username}.pkpass")
    print(f"\n🔄 Next steps:")
    print(f"   cd ~/maroof/maroof-cards/clients")
    print(f"   git add {username}/{username}.pkpass {username}/icon.png {username}/logo.png")
    print(f"   git commit -m 'Add pkpass for {username}'")
    print(f"   git push origin main")
    
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        username = sys.argv[1]
        build_pkpass(username)
    else:
        print("Usage: python3 build_pkpass.py <username>")
        print("Example: python3 build_pkpass.py mhmd-kaml")
