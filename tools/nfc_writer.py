#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maroof - NFC Writer using nfcpy
Fixed version with proper error handling and return values
"""

import nfc
import time
import sys
from typing import Tuple, Optional, Dict

class NFCWriter:
    """NFC Card Writer using nfcpy - Fixed Version"""
    
    def __init__(self):
        self.clf = None
        
    def connect(self) -> bool:
        """Connect to NFC reader"""
        print("🔍 Searching for NFC reader...")
        
        # AITRIP PN532 connection methods in order of preference
        transports = [
            ('usb', 'USB Direct'),
            ('usb:054c:0268', 'USB with ID'),
            ('tty:/dev/ttyUSB0:pn532', 'Serial USB0'),
            ('tty:/dev/ttyS0:pn532', 'Serial UART'),
            ('tty:/dev/ttyAMA0:pn532', 'Serial AMA0'),
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
        
        print("\n❌ Connection failed! Please check:")
        print("   1. NFC reader is connected via USB")
        print("   2. Run: lsusb | grep -i nfc")
        print("   3. Check permissions: sudo usermod -a -G dialout $USER")
        return False
    
    def is_connected(self) -> bool:
        """Check if reader is connected"""
        return self.clf is not None
    
    def write_url(self, url: str, timeout: int = 10) -> Tuple[bool, str]:
        """
        Write URL to NFC card
        
        Args:
            url: The URL to write
            timeout: Maximum wait time in seconds
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.clf:
            return False, "NFC reader not connected"
        
        print(f"\n📝 Ready to write: {url}")
        print("💳 Place card on reader...")
        
        try:
            import ndef
            
            # Create NDEF message with URL
            uri_record = ndef.UriRecord(url)
            message = [uri_record]
            
            # Wait for card with timeout
            start_time = time.time()
            tag = None
            
            def on_connect(tag):
                return False  # Disconnect immediately after detection
            
            while time.time() - start_time < timeout:
                try:
                    tag = self.clf.connect(rdwr={'on-connect': on_connect})
                    if tag:
                        break
                except Exception as e:
                    if time.time() - start_time >= timeout:
                        break
                    time.sleep(0.1)
            
            if not tag:
                return False, f"No card detected within {timeout} seconds"
            
            print(f"✅ Card detected: {tag}")
            
            # Write to card
            if tag.ndef:
                tag.ndef.records = message
                print("✅ Successfully written to NFC!")
                self.beep_success()
                return True, "Successfully written to NFC"
            else:
                return False, "Card doesn't support NDEF format"
                
        except Exception as e:
            error_msg = f"Write error: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return False, error_msg
    
    def read_card(self, timeout: int = 10) -> Tuple[Optional[Dict], str]:
        """
        Read NFC card
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            Tuple of (data: Optional[Dict], message: str)
            data format: {'url': 'https://...', 'uid': 'hex_string'}
        """
        if not self.clf:
            return None, "NFC reader not connected"
        
        print("\n📖 Place card on reader to read...")
        
        try:
            # Wait for card with timeout
            start_time = time.time()
            tag = None
            
            def on_connect(tag):
                return False  # Disconnect immediately after detection
            
            while time.time() - start_time < timeout:
                try:
                    tag = self.clf.connect(rdwr={'on-connect': on_connect})
                    if tag:
                        break
                except Exception as e:
                    if time.time() - start_time >= timeout:
                        break
                    time.sleep(0.1)
            
            if not tag:
                return None, f"No card detected within {timeout} seconds"
            
            print(f"✅ Card detected: {tag}")
            
            result = {
                'uid': tag.identifier.hex()
            }
            
            # Try to read NDEF data
            if tag.ndef:
                for record in tag.ndef.records:
                    print(f"   Record type: {type(record).__name__}")
                    
                    # Handle URI records
                    if hasattr(record, 'uri'):
                        result['url'] = record.uri
                        print(f"   URL: {record.uri}")
                    
                    # Handle text records
                    elif hasattr(record, 'text'):
                        result['text'] = record.text
                        print(f"   Text: {record.text}")
                
                if 'url' in result:
                    return result, "Successfully read card"
                else:
                    return result, "Card has no URL data"
            else:
                return result, "Card has no NDEF data"
                
        except Exception as e:
            error_msg = f"Read error: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return None, error_msg
    
    def beep_success(self):
        """Play success sound (if available)"""
        try:
            import subprocess
            subprocess.run(
                ['aplay', '-q', '/usr/share/sounds/alsa/Front_Center.wav'], 
                check=False, 
                capture_output=True, 
                timeout=2
            )
        except:
            pass  # Silently fail if sound not available
    
    def close(self):
        """Close connection and release resources"""
        if self.clf:
            try:
                self.clf.close()
                print("🔌 NFC reader disconnected")
            except Exception as e:
                print(f"Warning: Error closing NFC reader: {e}")
            finally:
                self.clf = None


def main():
    """Command-line interface for NFC operations"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Maroof NFC Writer - Fixed Version',
        epilog='Examples:\n'
               '  Read card:  python3 nfc_writer.py --read\n'
               '  Write URL:  python3 nfc_writer.py --url https://example.com\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--url', '-u', help='URL to write to NFC card')
    parser.add_argument('--read', '-r', action='store_true', help='Read NFC card')
    parser.add_argument('--timeout', '-t', type=int, default=10, 
                       help='Timeout in seconds (default: 10)')
    
    args = parser.parse_args()
    
    # Create writer and connect
    writer = NFCWriter()
    
    if not writer.connect():
        sys.exit(1)
    
    try:
        if args.read:
            # Read mode
            data, msg = writer.read_card(timeout=args.timeout)
            if data:
                print(f"\n✅ Success: {msg}")
                print(f"📊 Data: {data}")
            else:
                print(f"\n❌ Failed: {msg}")
                sys.exit(1)
                
        elif args.url:
            # Write mode
            success, msg = writer.write_url(args.url, timeout=args.timeout)
            if success:
                print(f"\n✅ {msg}")
            else:
                print(f"\n❌ {msg}")
                sys.exit(1)
                
        else:
            # Interactive mode
            url = input("\n🔗 Enter URL to write: ").strip()
            if url:
                success, msg = writer.write_url(url, timeout=args.timeout)
                if success:
                    print(f"\n✅ {msg}")
                else:
                    print(f"\n❌ {msg}")
                    sys.exit(1)
            else:
                print("❌ No URL provided")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n⛔ Stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        writer.close()


if __name__ == '__main__':
    main()