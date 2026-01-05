#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maroof - NFC Writer for PN532
Auto-detects baudrate and handles multiple card types
"""

import serial
import time
import sys

class NFCWriter:
    """NFC Card Writer with auto-detect"""
    
    def __init__(self):
        self.pn532 = None
        self.uart = None
        self.baudrate = None
        
    def connect(self):
        """Connect to NFC reader with auto-detect baudrate"""
        print("🔍 Searching for NFC reader...")
        
        baudrates = [115200, 9600, 19200, 38400, 57600]
        
        for baud in baudrates:
            try:
                print(f"⏳ Trying {baud} baud...")
                
                from adafruit_pn532.uart import PN532_UART
                
                self.uart = serial.Serial('/dev/ttyUSB0', baudrate=baud, timeout=1)
                time.sleep(0.1)
                
                self.pn532 = PN532_UART(self.uart, debug=False)
                
                ic, ver, rev, support = self.pn532.firmware_version
                
                print(f"✅ Connected: PN532 v{ver}.{rev} @ {baud} baud")
                self.baudrate = baud
                
                self.pn532.SAM_configuration()
                return True
                
            except Exception as e:
                if self.uart:
                    try:
                        self.uart.close()
                    except:
                        pass
                    self.uart = None
                print(f"   ❌ Failed: {e}")
                continue
        
        print("\n❌ Connection failed!")
        print("💡 Check: ls -la /dev/ttyUSB0")
        return False
    
    def write_url(self, url: str):
        """Write URL to NFC card"""
        if not self.pn532:
            return False
        
        print(f"\n📝 Ready: {url}")
        print("💳 Place card...")
        
        try:
            uid = self.pn532.read_passive_target(timeout=10)
            
            if not uid:
                print("❌ No card")
                return False
            
            print(f"✅ Card: {uid.hex()}")
            
            ndef_url = self._create_ndef_url(url)
            success = self._write_ndef_message(ndef_url)
            
            if success:
                print("✅ Written!")
                self.beep_success()
                return True
            else:
                print("❌ Failed")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def _create_ndef_url(self, url: str):
        """Create NDEF URL message"""
        if url.startswith('https://'):
            prefix = 0x04
            url_data = url[8:]
        elif url.startswith('http://'):
            prefix = 0x03
            url_data = url[7:]
        else:
            prefix = 0x00
            url_data = url
        
        url_bytes = url_data.encode('utf-8')
        payload_len = len(url_bytes) + 1
        
        message = bytearray([
            0x03, payload_len + 5, 0xD1, 0x01, 
            payload_len, 0x55, prefix
        ])
        message.extend(url_bytes)
        message.append(0xFE)
        
        return bytes(message)
    
    def _write_ndef_message(self, ndef_data):
        """Write NDEF message to card"""
        try:
            # Try MiFare Ultralight
            print("📝 Ultralight...")
            page = 4
            
            for i in range(0, len(ndef_data), 4):
                chunk = ndef_data[i:i+4]
                if len(chunk) < 4:
                    chunk = chunk + b'\x00' * (4 - len(chunk))
                
                success = self.pn532.ntag2xx_write_block(page, chunk)
                if not success:
                    break
                page += 1
            else:
                return True
            
            # Try MiFare Classic
            print("📝 Classic...")
            
            keys = [
                b'\xFF\xFF\xFF\xFF\xFF\xFF',
                b'\xA0\xA1\xA2\xA3\xA4\xA5',
                b'\xD3\xF7\xD3\xF7\xD3\xF7',
            ]
            
            key_used = None
            for key in keys:
                try:
                    uid = self.pn532.read_passive_target(timeout=1)
                    if not uid:
                        continue
                    
                    if self.pn532.mifare_classic_authenticate_block(
                        uid=uid, block_number=4, key_number=0x60, key=key
                    ):
                        key_used = key
                        print(f"✅ Auth: {key.hex()}")
                        break
                except:
                    continue
            
            if not key_used:
                return False
            
            block = 4
            for i in range(0, len(ndef_data), 16):
                chunk = ndef_data[i:i+16]
                if len(chunk) < 16:
                    chunk = chunk + b'\x00' * (16 - len(chunk))
                
                if not self.pn532.mifare_classic_write_block(block, chunk):
                    return False
                block += 1
            
            return True
            
        except Exception as e:
            print(f"❌ Write error: {e}")
            return False
    
    def read_card(self):
        """Read NFC card"""
        if not self.pn532:
            return None
        
        print("\n📖 Place card...")
        
        try:
            uid = self.pn532.read_passive_target(timeout=10)
            if uid:
                print(f"✅ Card: {uid.hex()}")
                return uid.hex()
            else:
                print("❌ No card")
                return None
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
        if self.uart:
            try:
                self.uart.close()
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