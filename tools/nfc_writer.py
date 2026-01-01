#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maroof - NFC Writer for PN532
Digital Business Cards System
"""

import nfc
import time
import sys
from pathlib import Path

class NFCWriter:
    """NFC Card Writer"""
    
    def __init__(self):
        self.clf = None
        
    def connect(self):
        """Connect to NFC reader"""
        try:
            print("🔍 Searching for NFC reader...")
            self.clf = nfc.ContactlessFrontend('usb')
            print(f"✅ Connected: {self.clf}")
            return True
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("\n💡 Make sure:")
            print("  - NFC reader is connected via USB")
            print("  - nfcpy is installed: pip3 install nfcpy --break-system-packages")
            return False
    
    def write_url(self, url: str):
        """Write URL to NFC card"""
        if not self.clf:
            print("❌ Not connected!")
            return False
        
        print(f"\n📝 Ready to write: {url}")
        print("💳 Place card on reader...")
        
        try:
            import ndeflib
            
            # Wait for card
            uri_record = ndeflib.UriRecord(url)
            
            if not tag:
                print("❌ No card detected")
                return False
            
            print(f"✅ Card detected: {tag}")
            
            # Create NDEF message
            uri_record = ndeflib.UriRecord(url)
            message = [uri_record]
            
            # Write to card
            if tag.ndef:
                tag.ndef.records = message
                print("✅ Card written successfully!")
                print(f"📱 Card ready: {url}")
                
                # Success sound
                self.beep_success()
                
                return True
            else:
                print("❌ Card doesn't support NDEF")
                return False
                
        except Exception as e:
            print(f"❌ Write error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def read_card(self):
        """Read NFC card"""
        if not self.clf:
            print("❌ Not connected!")
            return None
        
        print("\n📖 Place card to read...")
        
        try:
            tag = self.clf.connect(rdwr={'on-connect': lambda tag: False})
            
            if not tag:
                print("❌ No card detected")
                return None
            
            print(f"✅ Card detected: {tag}")
            
            if tag.ndef:
                for record in tag.ndef.records:
                    print(f"\n📄 Record: {record}")
                    if hasattr(record, 'uri'):
                        print(f"🔗 URL: {record.uri}")
                        return record.uri
                return True
            else:
                print("❌ Card has no NDEF data")
                return None
                
        except Exception as e:
            print(f"❌ Read error: {e}")
            return None
    
    def beep_success(self):
        """Play success sound"""
        try:
            import subprocess
            subprocess.run(['aplay', '/usr/share/sounds/alsa/Front_Center.wav'], 
                         check=False, capture_output=True, timeout=2)
        except:
            pass
    
    def wait_for_card(self, timeout=30):
        """Wait for card"""
        print(f"\n⏳ Waiting for card (timeout: {timeout}s)...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                tag = self.clf.connect(rdwr={'on-connect': lambda tag: False})
                if tag:
                    return tag
            except:
                pass
            
            time.sleep(0.1)
        
        print("⏱️ Timeout!")
        return None
    
    def close(self):
        """Close connection"""
        if self.clf:
            self.clf.close()
            print("👋 Connection closed")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Maroof - NFC Writer')
    parser.add_argument('--url', '-u', help='URL to write')
    parser.add_argument('--read', '-r', action='store_true', help='Read card')
    parser.add_argument('--wait', '-w', action='store_true', help='Continuous mode')
    
    args = parser.parse_args()
    
    writer = NFCWriter()
    
    if not writer.connect():
        sys.exit(1)
    
    try:
        if args.read:
            writer.read_card()
            
        elif args.url:
            writer.write_url(args.url)
            
        elif args.wait:
            print("\n🔄 Continuous mode...")
            print("💡 Press Ctrl+C to stop\n")
            
            while True:
                print("💳 Place new card...")
                tag = writer.wait_for_card(timeout=60)
                
                if tag:
                    url = input("\n🔗 Enter URL (or Enter to skip): ").strip()
                    
                    if url:
                        writer.write_url(url)
                    
                    time.sleep(2)
                    print("\n" + "="*50 + "\n")
                    
        else:
            print("\n📝 Interactive mode")
            url = input("🔗 Enter URL: ").strip()
            
            if url:
                writer.write_url(url)
            else:
                print("❌ No URL entered!")
                
    except KeyboardInterrupt:
        print("\n\n⛔ Stopped by user")
        
    finally:
        writer.close()


if __name__ == '__main__':
    main()
