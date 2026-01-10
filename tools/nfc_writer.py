#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maroof - NFC Writer using nfcpy ONLY
"""

import nfc
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
        
        transports = [
            ('tty:USB1:pn532', 'PN532 on USB1'),
            ('tty:USB0:pn532', 'PN532 on USB0'),
            ('tty:/dev/ttyUSB1:pn532', 'PN532 ttyUSB1'),
            ('tty:/dev/ttyUSB0:pn532', 'PN532 ttyUSB0'),
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
        
        print("Connection failed!")
        return False
    
    def is_connected(self) -> bool:
        return self.clf is not None
    
    def write_url(self, url: str, timeout: int = 10) -> Tuple[bool, str]:
        """Write URL to NFC card"""
        if not self.clf:
            return False, "NFC reader not connected"
        
        print(f"\nReady to write: {url}")
        print("Place card on reader...")
        
        try:
            import ndef
            record = ndef.UriRecord(url)
            
            start_time = time.time()
            tag = None
            
            while time.time() - start_time < timeout:
                try:
                    tag = self.clf.connect(rdwr={'on-connect': lambda t: False})
                    if tag:
                        break
                except:
                    time.sleep(0.1)
            
            if not tag:
                return False, f"No card detected within {timeout} seconds"
            
            print(f"Card: {tag}")
            
            if tag.ndef:
                tag.ndef.records = [record]
                print("Success!")
                return True, "Successfully written to NFC"
            else:
                return False, "Card doesn't support NDEF"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def read_card(self, timeout: int = 10) -> Tuple[Optional[Dict], str]:
        """Read NFC card"""
        if not self.clf:
            return None, "NFC reader not connected"
        
        print("\nPlace card to read...")
        
        try:
            start_time = time.time()
            tag = None
            
            while time.time() - start_time < timeout:
                try:
                    tag = self.clf.connect(rdwr={'on-connect': lambda t: False})
                    if tag:
                        break
                except:
                    time.sleep(0.1)
            
            if not tag:
                return None, f"No card detected"
            
            print(f"Card: {tag}")
            result = {'uid': tag.identifier.hex()}
            
            if tag.ndef:
                for record in tag.ndef.records:
                    if hasattr(record, 'uri'):
                        result['url'] = record.uri
                        print(f"URL: {record.uri}")
                
                if 'url' in result:
                    return result, "Successfully read"
                return result, "No URL data"
            return result, "No NDEF data"
                
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def close(self):
        if self.clf:
            try:
                self.clf.close()
            except:
                pass
            finally:
                self.clf = None


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Maroof NFC Writer')
    parser.add_argument('--url', '-u', help='URL to write')
    parser.add_argument('--read', '-r', action='store_true', help='Read card')
    parser.add_argument('--timeout', '-t', type=int, default=10)
    
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
            print(f"\n{msg}")
            if not success:
                sys.exit(1)
        else:
            url = input("\nEnter URL: ").strip()
            if url:
                success, msg = writer.write_url(url, timeout=args.timeout)
                print(f"\n{msg}")
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        writer.close()

if __name__ == '__main__':
    main()
