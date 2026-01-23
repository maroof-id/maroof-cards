#!/usr/bin/env python3
"""
Maroof NFC Writer - Supports NTAG & MIFARE Classic
"""

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
        """Connect to NFC reader"""
        return self.ensure_connected()
    
    def ensure_connected(self) -> bool:
        """Ensure connection is alive"""
        if self.clf and (time.time() - self.last_connected) < 2:
            return True
        
        if self._try_connect():
            self.last_connected = time.time()
            return True
        
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
    
    def _write_ntag(self, tag, url: str) -> Tuple[bool, str]:
        """Write to NTAG card (NDEF supported)"""
        try:
            import ndef
            
            # Check if tag has NDEF
            if not hasattr(tag, 'ndef'):
                return False, "Card doesn't support NDEF"
            
            # If NDEF is None, try raw write
            if tag.ndef is None:
                print("⚠️ No NDEF, trying raw write...")
                try:
                    # Create NDEF message manually
                    record = ndef.UriRecord(url)
                    message = ndef.message_encoder([record])
                    
                    # Write raw bytes starting at block 4
                    block_num = 4
                    
                    # Write NDEF header (TLV)
                    header = bytes([0x03, len(message)]) + message + bytes([0xFE])
                    
                    # Pad to 16-byte blocks
                    while len(header) % 16 != 0:
                        header += b'\x00'
                    
                    # Write blocks
                    for i in range(0, len(header), 16):
                        chunk = header[i:i+16]
                        tag.write(block_num, chunk)
                        print(f"   ✅ Written block {block_num}")
                        block_num += 1
                    
                    return True, "Written (raw mode)"
                    
                except Exception as e:
                    return False, f"Raw write failed: {e}"
            
            # Normal NDEF write
            if not tag.ndef.is_writeable:
                return False, "Card is write-protected"
            
            record = ndef.UriRecord(url)
            tag.ndef.records = [record]
            
            return True, "Written successfully (NTAG/NDEF)"
            
        except Exception as e:
            return False, f"NTAG write error: {e}"
    
    def _write_mifare_classic(self, tag, url: str) -> Tuple[bool, str]:
        """Write URL to MIFARE Classic 1K"""
        try:
            # Check if this is actually NTAG (not MIFARE Classic)
            product = str(tag.product).upper()
            
            if 'NTAG' in product or 'TYPE2TAG' in str(tag.type).upper():
                print("   ⚠️ This is NTAG, redirecting to NDEF write...")
                return self._write_ntag(tag, url)
            
            # Real MIFARE Classic only from here
            if not hasattr(tag, 'authenticate'):
                return False, "Card doesn't support authentication"
            
            # MIFARE Classic default key
            key_a = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
            
            # Prepare URL data
            url_bytes = url.encode('utf-8')
            blocks_to_write = [4, 5, 6]
            
            # Split into chunks
            chunks = []
            for i in range(0, len(url_bytes), 16):
                chunk = url_bytes[i:i+16]
                chunk = chunk + b'\x00' * (16 - len(chunk))
                chunks.append(chunk)
            chunks = chunks[:3]
            
            # Write blocks
            for i, block_num in enumerate(blocks_to_write):
                if i >= len(chunks):
                    break
                
                try:
                    # MIFARE Classic auth: (block, key, use_key_a)
                    if not tag.authenticate(block_num, key_a, True):
                        return False, f"Auth failed at block {block_num}"
                    
                    tag.write(block_num, chunks[i])
                    print(f"✅ Written to block {block_num}")
                    
                except Exception as e:
                    return False, f"Write error at block {block_num}: {e}"
            
            return True, "Written successfully (MIFARE Classic)"
            
        except Exception as e:
            return False, f"MIFARE error: {e}"
    
    def write_url(self, url: str, timeout: int = 15) -> Tuple[bool, str]:
        """Write URL to NFC card (auto-detect type)"""
        try:
            if not self.ensure_connected():
                return False, "Cannot connect to NFC reader"
            
            print(f"📝 Writing: {url}")
            print("⏳ Place card on reader...")
            
            start = time.time()
            result = [False, "Timeout"]
            
            def on_connect(tag):
                print(f"✅ Card detected: {tag.type}")
                print(f"   ID: {tag.identifier.hex()}")
                print(f"   Product: {tag.product}")
                
                # IMPROVED: Detect by product name
                product = str(tag.product).upper()
                card_type = str(tag.type).upper()
                
                # NTAG cards (including NTAG215)
                if 'NTAG' in product or 'TYPE2TAG' in card_type:
                    print("   Type: NTAG (NDEF)")
                    result[0], result[1] = self._write_ntag(tag, url)
                
                # Real MIFARE Classic (rare case)
                elif 'MIFARE CLASSIC' in product or ('TYPE1TAG' in card_type and hasattr(tag, 'authenticate')):
                    print("   Type: MIFARE Classic")
                    result[0], result[1] = self._write_mifare_classic(tag, url)
                
                else:
                    print(f"   ⚠️ Unknown: {product}")
                    # Default to NDEF
                    if hasattr(tag, 'ndef'):
                        print("   Trying NDEF write...")
                        result[0], result[1] = self._write_ntag(tag, url)
                    else:
                        result[0], result[1] = False, f"Unsupported: {product}"
                
                return False
            
            self.clf.connect(rdwr={'on-connect': on_connect}, terminate=lambda: time.time() - start > timeout)
            
            return result[0], result[1]
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _read_ntag(self, tag) -> Dict:
        """Read NTAG card"""
        result = {
            'uid': tag.identifier.hex(),
            'type': 'NTAG',
            'ndef': False
        }
        
        if tag.ndef:
            result['ndef'] = True
            for record in tag.ndef.records:
                if hasattr(record, 'uri'):
                    result['url'] = record.uri
                if hasattr(record, 'text'):
                    result['text'] = record.text
        
        return result
    
    def _read_mifare_classic(self, tag) -> Dict:
        """Read MIFARE Classic card"""
        result = {
            'uid': tag.identifier.hex(),
            'type': 'MIFARE Classic',
            'ndef': False
        }
        
        try:
            key_a = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
            
            # Read blocks 4-6
            url_bytes = b''
            for block_num in [4, 5, 6]:
                try:
                    if tag.authenticate(block_num, key_a, True):
                        data = tag.read(block_num)
                        url_bytes += data
                except:
                    break
            
            # Remove null bytes and decode
            url = url_bytes.rstrip(b'\x00').decode('utf-8', errors='ignore')
            
            if url and url.startswith('http'):
                result['url'] = url
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def read_card(self, timeout: int = 15) -> Tuple[Optional[Dict], str]:
        """Read NFC card (auto-detect type)"""
        try:
            if not self.ensure_connected():
                return None, "Cannot connect to NFC reader"
            
            print(f"📖 Reading...")
            print("⏳ Place card on reader...")
            
            start = time.time()
            result = [None, "Timeout"]
            
            def on_connect(tag):
                print(f"✅ Card detected: {tag.type}")
                
                card_type = str(tag.type)
                
                if 'Type2Tag' in card_type or hasattr(tag, 'ndef'):
                    data = self._read_ntag(tag)
                    result[0], result[1] = data, "Read successfully"
                    
                elif 'Type1Tag' in card_type or hasattr(tag, 'authenticate'):
                    data = self._read_mifare_classic(tag)
                    result[0], result[1] = data, "Read successfully"
                    
                else:
                    result[0], result[1] = None, f"Unsupported: {card_type}"
                
                return False
            
            self.clf.connect(rdwr={'on-connect': on_connect}, terminate=lambda: time.time() - start > timeout)
            
            return result[0], result[1]
                
        except Exception as e:
            return None, f"Error: {str(e)}"

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Maroof NFC Writer - Supports NTAG & MIFARE')
    parser.add_argument('--url', '-u', help='URL to write')
    parser.add_argument('--read', '-r', action='store_true', help='Read card')
    parser.add_argument('--test', '-t', action='store_true', help='Test connection')
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
                print(f"📊 Type: {data.get('type')}")
                print(f"📊 UID: {data.get('uid')}")
                if 'url' in data:
                    print(f"📊 URL: {data['url']}")
                
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
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        writer.close()

if __name__ == '__main__':
    main()
