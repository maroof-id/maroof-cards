#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maroof - NFC Writer using nfcpy
Fixed for AITRIP PN532 on Raspberry Pi
"""

import nfc
import ndeflib
import time
import sys
from typing import Tuple, Optional, Dict

class NFCWriter:
    """NFC Card Writer using nfcpy"""
    
    def __init__(self):
        self.clf = None
        
    def connect(self) -> bool:
        """Connect to NFC reader"""
        print("Searching for NFC reader...")
        
        # Working transport for your device
        transports = [
            ('tty:USB0:pn532', 'PN532 on USB0'),
            ('tty:/dev/ttyUSB0:pn532', 'PN532 on ttyUSB0'),
        ]
        
        for path, name in transports:
            try:
                print(f"Trying {name}...")
                self.clf = nfc.ContactlessFrontend(path)
                print(f"Connected: {self.clf}")
                return True
            except Exception as e:
                print(f"  Failed: {e}")
                continue
        
        print("\nConnection failed!")
        return False
    
    def is_connected(self) -> bool:
        """Check if reader is connected"""
        return self.clf is not None
    
    def write_url(self, url: str, timeout: int = 10) -> Tuple[bool, str]:
        """
        Write URL to NFC card
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.clf:
            return False, "❌ قارئ NFC غير متصل / NFC reader not connected"
        
        print(f"\nReady to write: {url}")
        print("Place card on reader...")
        
        try:
            # Create NDEF message with URL
            uri_record = ndeflib.Record('urn:nfc:wkt:U', data=url.encode())
            message = [uri_record]
            
            # Wait for card with timeout
            start_time = time.time()
            tag = None
            last_error = None
            
            while time.time() - start_time < timeout:
                try:
                    tag = self.clf.connect(rdwr={'on-connect': lambda t: False})
                    if tag:
                        break
                except Exception as e:
                    last_error = str(e)
                    time.sleep(0.1)
            
            if not tag:
                if last_error and 'timeout' in last_error.lower():
                    return False, "❌ انتهت مهلة انتظار قارئ NFC / NFC reader timeout"
                return False, f"❌ لم يتم اكتشاف بطاقة / No card detected within {timeout} seconds"
            
            print(f"Card detected: {tag}")
            
            # Write to card
            if tag.ndef is not None:
                try:
                    tag.ndef.records = message
                    tag.close()
                    print("Successfully written to NFC!")
                    return True, "✅ تمت الكتابة على البطاقة بنجاح / Successfully written to NFC"
                except Exception as write_err:
                    return False, f"❌ خطأ في الكتابة / Write error: {str(write_err)}"
            else:
                return False, "❌ البطاقة لا تدعم صيغة NDEF / Card doesn't support NDEF format"
                
        except ImportError:
            return False, "❌ مكتبة ndef غير مثبتة / ndef library not installed"
        except Exception as e:
            error_msg = f"❌ خطأ: {str(e)} / Error: {str(e)}"
            print(f"Error: {error_msg}")
            return False, error_msg
    
    def read_card(self, timeout: int = 10) -> Tuple[Optional[Dict], str]:
        """
        Read NFC card
        
        Returns:
            Tuple of (data: Optional[Dict], message: str)
        """
        if not self.clf:
            return None, "❌ قارئ NFC غير متصل / NFC reader not connected"
        
        print("\nPlace card on reader to read...")
        
        try:
            # Wait for card with timeout
            start_time = time.time()
            tag = None
            last_error = None
            
            while time.time() - start_time < timeout:
                try:
                    tag = self.clf.connect(rdwr={'on-connect': lambda t: False})
                    if tag:
                        break
                except Exception as e:
                    last_error = str(e)
                    time.sleep(0.1)
            
            if not tag:
                if last_error and 'timeout' in last_error.lower():
                    return None, "❌ انتهت مهلة انتظار قارئ NFC / NFC reader timeout"
                return None, f"❌ لم يتم اكتشاف بطاقة / No card detected within {timeout} seconds"
            
            print(f"Card detected: {tag}")
            
            result = {
                'uid': tag.identifier.hex()
            }
            
            # Try to read NDEF data
            if tag.ndef:
                try:
                    for record in tag.ndef.records:
                        print(f"  Record: {record}")
                        
                        # Handle URI records
                        if hasattr(record, 'uri'):
                            result['url'] = record.uri
                            print(f"  URL: {record.uri}")
                        
                        # Handle text records
                        elif hasattr(record, 'text'):
                            result['text'] = record.text
                            print(f"  Text: {record.text}")
                    
                    if 'url' in result:
                        return result, "✅ تم قراءة البطاقة بنجاح / Successfully read card"
                    else:
                        return result, "⚠️ البطاقة لا تحتوي بيانات رابط / Card has no URL data"
                finally:
                    tag.close()
            else:
                return result, "⚠️ البطاقة لا تحتوي بيانات NDEF / Card has no NDEF data"
                
        except Exception as e:
            error_msg = f"❌ خطأ في القراءة / Read error: {str(e)}"
            print(f"Error: {error_msg}")
            return None, error_msg
    
    def close(self):
        """Close connection"""
        if self.clf:
            try:
                self.clf.close()
                print("NFC reader disconnected")
            except:
                pass
            finally:
                self.clf = None


def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Maroof NFC Writer')
    parser.add_argument('--url', '-u', help='URL to write')
    parser.add_argument('--read', '-r', action='store_true', help='Read card')
    parser.add_argument('--timeout', '-t', type=int, default=10, help='Timeout in seconds')
    
    args = parser.parse_args()
    
    writer = NFCWriter()
    
    if not writer.connect():
        sys.exit(1)
    
    try:
        if args.read:
            data, msg = writer.read_card(timeout=args.timeout)
            if data:
                print(f"\nSuccess: {msg}")
                print(f"Data: {data}")
            else:
                print(f"\nFailed: {msg}")
                sys.exit(1)
                
        elif args.url:
            success, msg = writer.write_url(args.url, timeout=args.timeout)
            if success:
                print(f"\n{msg}")
            else:
                print(f"\n{msg}")
                sys.exit(1)
                
        else:
            url = input("\nEnter URL to write: ").strip()
            if url:
                success, msg = writer.write_url(url, timeout=args.timeout)
                if success:
                    print(f"\n{msg}")
                else:
                    print(f"\n{msg}")
                    sys.exit(1)
            else:
                print("No URL provided")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        writer.close()


if __name__ == '__main__':
    main()
