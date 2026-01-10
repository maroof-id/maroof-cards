#!/usr/bin/env python3
import nfc
import time
import sys
from typing import Tuple, Optional, Dict

class NFCWriter:
    def __init__(self):
        self.clf = None
        
    def connect(self) -> bool:
        """Connect to NFC reader"""
        if self.clf:
            return True
            
        try:
            self.clf = nfc.ContactlessFrontend('tty:USB0:pn532')
            return True
        except:
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
    
    def write_url(self, url: str, timeout: int = 10) -> Tuple[bool, str]:
        """Write URL and close connection"""
        try:
            # اتصال جديد
            if not self.connect():
                return False, "Cannot connect to NFC reader"
            
            print(f"Writing: {url}")
            
            import ndef
            record = ndef.UriRecord(url)
            
            start = time.time()
            tag = None
            
            while time.time() - start < timeout:
                try:
                    tag = self.clf.connect(rdwr={'on-connect': lambda t: False})
                    if tag:
                        break
                except:
                    time.sleep(0.1)
            
            if not tag:
                return False, "No card detected"
            
            if tag.ndef:
                tag.ndef.records = [record]
                return True, "Written successfully!"
            return False, "Card doesn't support NDEF"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            # إغلاق الاتصال بعد كل عملية
            self.close()
    
    def read_card(self, timeout: int = 10) -> Tuple[Optional[Dict], str]:
        """Read card and close connection"""
        try:
            if not self.connect():
                return None, "Cannot connect to NFC reader"
            
            start = time.time()
            tag = None
            
            while time.time() - start < timeout:
                try:
                    tag = self.clf.connect(rdwr={'on-connect': lambda t: False})
                    if tag:
                        break
                except:
                    time.sleep(0.1)
            
            if not tag:
                return None, "No card"
            
            result = {'uid': tag.identifier.hex()}
            
            if tag.ndef:
                for record in tag.ndef.records:
                    if hasattr(record, 'uri'):
                        result['url'] = record.uri
                
                if 'url' in result:
                    return result, "Read successfully"
                return result, "No URL"
            return result, "No NDEF"
                
        except Exception as e:
            return None, f"Error: {str(e)}"
        finally:
            # إغلاق الاتصال بعد كل عملية
            self.close()

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', '-u')
    parser.add_argument('--read', '-r', action='store_true')
    parser.add_argument('--timeout', '-t', type=int, default=10)
    
    args = parser.parse_args()
    writer = NFCWriter()
    
    try:
        if args.read:
            data, msg = writer.read_card(args.timeout)
            print(f"\n{msg}")
            if data:
                print(f"Data: {data}")
        elif args.url:
            ok, msg = writer.write_url(args.url, args.timeout)
            print(f"\n{msg}")
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        writer.close()

if __name__ == '__main__':
    main()
