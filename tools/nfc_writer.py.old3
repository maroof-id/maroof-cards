#!/usr/bin/env python3
import nfc
import time
import sys
from typing import Tuple, Optional, Dict

class NFCWriter:
    def __init__(self):
        self.clf = None
        self.device_path = None
        
    def connect(self) -> bool:
        """Connect to NFC reader with auto-detection"""
        if self.clf:
            return True
            
        connection_methods = [
            'tty:USB0:pn532',
            'tty:USB1:pn532',
            'usb',
            'tty:AMA0:pn532',
        ]
        
        for method in connection_methods:
            try:
                self.clf = nfc.ContactlessFrontend(method)
                self.device_path = method
                print(f"✅ Connected via: {method}")
                return True
            except:
                continue
        
        print("❌ Failed to connect to NFC reader")
        return False
    
    def close(self):
        """Close and free the reader"""
        if self.clf:
            try:
                self.clf.close()
            except:
                pass
            finally:
                self.clf = None
    
    def write_url(self, url: str, timeout: int = 15) -> Tuple[bool, str]:
        """Write URL to NFC card"""
        try:
            self.close()
            if not self.connect():
                return False, "Cannot connect to NFC reader"
            
            print(f"📝 Writing: {url}")
            print(f"📟 Using: {self.device_path}")
            
            import ndef
            record = ndef.UriRecord(url)
            
            print("⏳ Place card on reader...")
            start = time.time()
            tag = None
            
            while time.time() - start < timeout:
                try:
                    tag = self.clf.connect(rdwr={'on-connect': lambda t: False})
                    if tag:
                        print("✅ Card detected!")
                        break
                except:
                    time.sleep(0.2)
            
            if not tag:
                return False, "No card detected - timeout"
            
            if not tag.ndef:
                return False, "Card doesn't support NDEF"
            
            try:
                tag.ndef.records = [record]
                print("✅ Write successful!")
                return True, f"Successfully written: {url}"
            except Exception as e:
                return False, f"Write failed: {str(e)}"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            self.close()
    
    def read_card(self, timeout: int = 15) -> Tuple[Optional[Dict], str]:
        """Read NFC card"""
        try:
            self.close()
            if not self.connect():
                return None, "Cannot connect to NFC reader"
            
            print(f"📖 Reading card...")
            print(f"📟 Using: {self.device_path}")
            print("⏳ Place card on reader...")
            
            start = time.time()
            tag = None
            
            while time.time() - start < timeout:
                try:
                    tag = self.clf.connect(rdwr={'on-connect': lambda t: False})
                    if tag:
                        print("✅ Card detected!")
                        break
                except:
                    time.sleep(0.2)
            
            if not tag:
                return None, "No card detected - timeout"
            
            result = {
                'uid': tag.identifier.hex(),
                'type': str(tag.type) if hasattr(tag, 'type') else 'Unknown'
            }
            
            if tag.ndef:
                result['ndef'] = True
                for record in tag.ndef.records:
                    if hasattr(record, 'uri'):
                        result['url'] = record.uri
                    if hasattr(record, 'text'):
                        result['text'] = record.text
                
                if 'url' in result:
                    print(f"📌 URL found: {result['url']}")
                    return result, "Read successfully"
                return result, "Card has NDEF but no URL"
            else:
                result['ndef'] = False
                return result, "Card doesn't support NDEF"
                
        except Exception as e:
            return None, f"Error: {str(e)}"
        finally:
            self.close()

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Maroof NFC Writer')
    parser.add_argument('--url', '-u', help='URL to write')
    parser.add_argument('--read', '-r', action='store_true', help='Read card')
    parser.add_argument('--test', '-t', action='store_true', help='Test reader')
    parser.add_argument('--timeout', type=int, default=15, help='Timeout in seconds')
    
    args = parser.parse_args()
    writer = NFCWriter()
    
    try:
        if args.test:
            print("🔍 Testing NFC reader...")
            if writer.connect():
                print(f"✅ Reader connected: {writer.device_path}")
                writer.close()
            else:
                print("❌ Reader not found")
                sys.exit(1)
                
        elif args.read:
            data, msg = writer.read_card(args.timeout)
            print(f"\n📋 Result: {msg}")
            if data:
                print(f"📊 Data: {data}")
                
        elif args.url:
            ok, msg = writer.write_url(args.url, args.timeout)
            print(f"\n📋 Result: {msg}")
            if not ok:
                sys.exit(1)
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n⚠️ Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        writer.close()

if __name__ == '__main__':
    main()