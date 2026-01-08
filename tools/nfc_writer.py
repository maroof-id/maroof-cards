#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maroof - NFC Writer using nfcpy
"""

import nfc
import time
import sys

class NFCWriter:
    """NFC Card Writer using nfcpy"""
    
    def __init__(self):
        self.clf = None
        
    def connect(self):
        """Connect to NFC reader"""
        print("🔍 Searching for NFC reader...")
        
        transports = [
            ('tty:USB0:pn532', 'Serial USB0'),
            ('usb', 'USB Direct'),
            ('tty:AMA0:pn532', 'Serial AMA0'),
        ]
        
        for path, name in transports:
            try:
                print(f"⏳ Trying {name}...")
                self.clf = nfc.ContactlessFrontend(path)
                print(f"✅ Connected: {self.clf}")
                return True
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                continue
        
        print("\n❌ Connection failed!")
        return False
    
    def write_url(self, url: str):
        """Write URL to NFC card"""
        if not self.clf:
            return False
        
        print(f"\n📝 Ready: {url}")
        print("💳 Place card...")
        
        try:
            import ndef
            
            # Create NDEF message
            uri_record = ndef.UriRecord(url)
            message = [uri_record]
            
            # Wait for card
            tag = self.clf.connect(rdwr={'on-connect': lambda tag: False})
            
            if not tag:
                print("❌ No card")
                return False
            
            print(f"✅ Card: {tag}")
            
            # Write to card
            if tag.ndef:
                tag.ndef.records = message
                print("✅ Written!")
                self.beep_success()
                return True
            else:
                print("❌ Card doesn't support NDEF")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def read_card(self):
        """Read NFC card"""
        if not self.clf:
            return None
        
        print("\n📖 Place card...")
        
        try:
            tag = self.clf.connect(rdwr={'on-connect': lambda tag: False})
            
            if not tag:
                print("❌ No card")
                return None
            
            print(f"✅ Card: {tag}")
            
            if tag.ndef:
                for record in tag.ndef.records:
                    print(f"   Record: {record}")
                    if hasattr(record, 'uri'):
                        print(f"   URL: {record.uri}")
                        return record.uri
            
            return tag.identifier.hex()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def beep_success(self):
        """Play success sound"""
        try:
            import subprocess
            subprocess.run(['aplay', '/usr/share/sounds/alsa/Front_Center.wav'], 
                         check=False, capture_output=True, timeout=2)
        except:
            pass
    
    def close(self):
        """Close connection"""
        if self.clf:
            try:
                self.clf.close()
            except:
                pass


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Maroof NFC Writer')
    parser.add_argument('--url', '-u', help='URL to write')
    parser.add_argument('--read', '-r', action='store_true', help='Read card')
    
    args = parser.parse_args()
    
    writer = NFCWriter()
    
    if not writer.connect():
        sys.exit(1)
    
    try:
        if args.read:
            writer.read_card()
        elif args.url:
            writer.write_url(args.url)
        else:
            url = input("🔗 URL: ").strip()
            if url:
                writer.write_url(url)
    except KeyboardInterrupt:
        print("\n⛔ Stopped")
    finally:
        writer.close()


if __name__ == '__main__':
    main()
