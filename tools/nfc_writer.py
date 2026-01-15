#!/usr/bin/env python3
import nfc
import time
import sys
import subprocess
import threading
from typing import Tuple, Optional, Dict

class NFCWriter:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.clf = None
                    cls._instance.device_path = None
                    cls._instance.last_connected = 0
        return cls._instance
    
    def reset_usb(self):
        """Reset USB port"""
        try:
            subprocess.run(['sudo', '/usr/local/bin/reset_usb_nfc.sh'], 
                         timeout=3, capture_output=True)
            time.sleep(1)
            return True
        except:
            return False
    
    def connect(self) -> bool:
        """Connect to NFC reader (compatibility wrapper)"""
        return self.ensure_connected()
    
    def ensure_connected(self) -> bool:
        """Ensure connection is alive"""
        # Recently connected? Assume OK
        if self.clf and (time.time() - self.last_connected) < 2:
            return True
        
        # Try connect
        if self._try_connect():
            self.last_connected = time.time()
            return True
        
        # Failed - reset and retry
        print("⚠️ Resetting USB...")
        self.close()
        self.reset_usb()
        
        if self._try_connect():
            self.last_connected = time.time()
            return True
        
        return False
    
    def _try_connect(self) -> bool:
        """Internal connection"""
        if self.clf:
            return True
        
        methods = ['tty:USB0:pn532', 'tty:USB1:pn532', 'usb', 'tty:AMA0:pn532']
        
        for method in methods:
            try:
                self.clf = nfc.ContactlessFrontend(method)
                self.device_path = method
                print(f"✅ Connected via: {method}")
                return True
            except:
                continue
        
        return False
    
    def close(self):
        """Close connection"""
        if self.clf:
            try:
                self.clf.close()
            except:
                pass
            self.clf = None
    
    def write_url(self, url: str, timeout: int = 15) -> Tuple[bool, str]:
        """Write URL to NFC card"""
        try:
            if not self.ensure_connected():
                return False, "Cannot connect to NFC reader"
            
            print(f"📝 Writing: {url}")
            
            import ndef
            record = ndef.UriRecord(url)
            
            print("⏳ Place card on reader...")
            start = time.time()
            
            while time.time() - start < timeout:
                try:
                    tag = self.clf.connect(rdwr={'on-connect': lambda t: False})
                    if tag:
                        print("✅ Card detected!")
                        if tag.ndef:
                            tag.ndef.records = [record]
                            print("✅ Write successful!")
                            return True, "Successfully written"
                        return False, "Card doesn't support NDEF"
                except:
                    time.sleep(0.2)
            
            return False, "No card detected - timeout"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def read_card(self, timeout: int = 15) -> Tuple[Optional[Dict], str]:
        """Read NFC card"""
        try:
            if not self.ensure_connected():
                return None, "Cannot connect to NFC reader"
            
            print(f"📖 Reading...")
            print("⏳ Place card on reader...")
            
            start = time.time()
            
            while time.time() - start < timeout:
                try:
                    tag = self.clf.connect(rdwr={'on-connect': lambda t: False})
                    if tag:
                        print("✅ Card detected!")
                        result = {
                            'uid': tag.identifier.hex(),
                            'type': str(tag.type) if hasattr(tag, 'type') else 'Unknown'
                        }
                        
                        if tag.ndef:
                            result['ndef'] = True
                            for record in tag.ndef.records:
                                if hasattr(record, 'uri'):
                                    result['url'] = record.uri
                                    print(f"📌 URL: {result['url']}")
                                if hasattr(record, 'text'):
                                    result['text'] = record.text
                            return result, "Read successfully"
                        else:
                            result['ndef'] = False
                            return result, "No NDEF"
                except:
                    time.sleep(0.2)
            
            return None, "No card detected - timeout"
                
        except Exception as e:
            return None, f"Error: {str(e)}"

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Maroof NFC Writer')
    parser.add_argument('--url', '-u', help='URL to write')
    parser.add_argument('--read', '-r', action='store_true', help='Read card')
    parser.add_argument('--test', '-t', action='store_true', help='Test')
    parser.add_argument('--timeout', type=int, default=15)
    
    args = parser.parse_args()
    writer = NFCWriter()
    
    try:
        if args.test:
            print("🔍 Testing...")
            if writer.connect():
                print(f"✅ Connected: {writer.device_path}")
            else:
                print("❌ Failed")
                sys.exit(1)
                
        elif args.read:
            data, msg = writer.read_card(args.timeout)
            print(f"\n📋 {msg}")
            if data:
                print(f"📊 {data}")
                
        elif args.url:
            ok, msg = writer.write_url(args.url, args.timeout)
            print(f"\n📋 {msg}")
            if not ok:
                sys.exit(1)
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n⚠️ Stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        writer.close()

if __name__ == '__main__':
    main()
