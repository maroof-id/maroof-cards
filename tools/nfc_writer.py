#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maroof - NFC Writer for PN532
Uses Adafruit PN532 library
"""

import serial
import time
import sys
from pathlib import Path

class NFCWriter:
    """NFC Card Writer"""
    
    def __init__(self):
        self.pn532 = None
        self.uart = None
        
    def connect(self):
        """Connect to NFC reader"""
        try:
            print("🔍 Searching for NFC reader...")
            from adafruit_pn532.uart import PN532_UART
            
            self.uart = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
            self.pn532 = PN532_UART(self.uart, debug=False)
            
            ic, ver, rev, support = self.pn532.firmware_version
            print(f"✅ Connected: PN532 v{ver}.{rev}")
            
            # Configure PN532 to communicate with MiFare cards
            self.pn532.SAM_configuration()
            
            return True
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("\n💡 Make sure:")
            print("  - NFC reader is connected to /dev/ttyUSB0")
            print("  - Reader is in HSU/UART mode (SEL0=OFF, SEL1=ON)")
            return False
    
    def write_url(self, url: str):
        """Write URL to NFC card"""
        if not self.pn532:
            print("❌ Not connected!")
            return False
        
        print(f"\n📝 Ready to write: {url}")
        print("💳 Place card on reader...")
        
        try:
            # Wait for card (timeout 5 seconds)
            uid = self.pn532.read_passive_target(timeout=5)
            
            if not uid:
                print("❌ No card detected")
                return False
            
            print(f"✅ Card detected: {uid.hex()}")
            
            # Create NDEF URL record
            ndef_url = self._create_ndef_url(url)
            
            # Write to card (blocks 4-7 on MiFare Classic)
            # For MiFare Ultralight, use different blocks
            success = self._write_ndef_message(ndef_url)
            
            if success:
                print("✅ Card written successfully!")
                print(f"📱 Card ready: {url}")
                
                # Success sound
                self.beep_success()
                
                return True
            else:
                print("❌ Failed to write card")
                return False
                
        except Exception as e:
            print(f"❌ Write error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_ndef_url(self, url: str):
        """Create NDEF URL message"""
        # NDEF URL Record format
        # See: https://learn.adafruit.com/adafruit-pn532-rfid-nfc/ndef
        
        # Remove http:// or https:// prefix
        if url.startswith('https://'):
            prefix = 0x04  # https://
            url_data = url[8:]
        elif url.startswith('http://'):
            prefix = 0x03  # http://
            url_data = url[7:]
        else:
            prefix = 0x00  # No prefix
            url_data = url
        
        url_bytes = url_data.encode('utf-8')
        payload_len = len(url_bytes) + 1  # +1 for prefix
        
        # NDEF message structure
        message = bytearray([
            0x03,  # NDEF message
            payload_len + 5,  # Message length
            0xD1,  # Record header (MB=1, ME=1, SR=1, TNF=0x01)
            0x01,  # Type length
            payload_len,  # Payload length
            0x55,  # Type: 'U' (URI)
            prefix,  # URI prefix
        ])
        message.extend(url_bytes)
        message.append(0xFE)  # NDEF message terminator
        
        return bytes(message)
    
    def _write_ndef_message(self, ndef_data):
        """Write NDEF message to card"""
        try:
            # Try MiFare Ultralight first
            print("📝 Trying MiFare Ultralight...")
            page = 4
            
            for i in range(0, len(ndef_data), 4):
                chunk = ndef_data[i:i+4]
                
                if len(chunk) < 4:
                    chunk = chunk + b'\x00' * (4 - len(chunk))
                
                success = self.pn532.ntag2xx_write_block(page, chunk)
                
                if not success:
                    print(f"⚠️ Ultralight failed at page {page}")
                    break
                
                page += 1
            else:
                return True  # Success if loop completed
            
            # Try MiFare Classic with multiple keys
            print("📝 Trying MiFare Classic...")
            
            # Common keys to try
            keys = [
                b'\xFF\xFF\xFF\xFF\xFF\xFF',  # Factory default
                b'\xA0\xA1\xA2\xA3\xA4\xA5',  # MAD key
                b'\xD3\xF7\xD3\xF7\xD3\xF7',  # NDEF key
                b'\x00\x00\x00\x00\x00\x00',  # Null key
                b'\xB0\xB1\xB2\xB3\xB4\xB5',  # Alternative
            ]
            
            authenticated = False
            key_used = None
            
            for key in keys:
                try:
                    # Get fresh UID
                    uid = self.pn532.read_passive_target(timeout=1)
                    if not uid:
                        continue
                    
                    # Try to authenticate block 4
                    if self.pn532.mifare_classic_authenticate_block(
                        uid=uid,
                        block_number=4,
                        key_number=0x60,  # KEY_A
                        key=key
                    ):
                        authenticated = True
                        key_used = key
                        print(f"✅ Authenticated with key: {key.hex()}")
                        break
                except:
                    continue
            
            if not authenticated:
                print("❌ Authentication failed with all keys")
                print("💡 Try a different card or format this one")
                return False
            
            # Write data in 16-byte blocks
            block = 4
            for i in range(0, len(ndef_data), 16):
                chunk = ndef_data[i:i+16]
                
                if len(chunk) < 16:
                    chunk = chunk + b'\x00' * (16 - len(chunk))
                
                success = self.pn532.mifare_classic_write_block(block, chunk)
                
                if not success:
                    print(f"❌ Failed to write block {block}")
                    return False
                
                block += 1
                
                # Re-authenticate every 4 blocks (new sector)
                if block % 4 == 0:
                    uid = self.pn532.read_passive_target(timeout=1)
                    if not self.pn532.mifare_classic_authenticate_block(
                        uid=uid,
                        block_number=block,
                        key_number=0x60,
                        key=key_used
                    ):
                        print(f"❌ Authentication failed at block {block}")
                        return False
            
            return True
            
        except Exception as e:
            print(f"❌ Write error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def read_card(self):
        """Read NFC card"""
        if not self.pn532:
            print("❌ Not connected!")
            return None
        
        print("\n📖 Place card to read...")
        
        try:
            # Wait for card
            uid = self.pn532.read_passive_target(timeout=5)
            
            if not uid:
                print("❌ No card detected")
                return None
            
            print(f"✅ Card detected: {uid.hex()}")
            
            # Try MiFare Classic with multiple keys
            data = bytearray()
            
            # Common keys to try
            keys = [
                b'\xFF\xFF\xFF\xFF\xFF\xFF',  # Factory default
                b'\xA0\xA1\xA2\xA3\xA4\xA5',  # MAD key
                b'\xD3\xF7\xD3\xF7\xD3\xF7',  # NDEF key
                b'\x00\x00\x00\x00\x00\x00',  # Null key
                b'\xB0\xB1\xB2\xB3\xB4\xB5',  # Alternative
            ]
            
            print("📝 Trying to read MiFare Classic...")
            
            authenticated_key = None
            
            try:
                # Try to authenticate with each key
                for key in keys:
                    if self.pn532.mifare_classic_authenticate_block(
                        uid=uid,
                        block_number=4,
                        key_number=0x60,
                        key=key
                    ):
                        authenticated_key = key
                        print(f"✅ Authenticated with key: {key.hex()}")
                        break
                
                if not authenticated_key:
                    print("⚠️ Authentication failed with all keys")
                    return uid
                
                # Read blocks 4-7 (sector 1)
                for block in range(4, 8):
                    # Re-authenticate if needed
                    if block > 4:
                        self.pn532.mifare_classic_authenticate_block(
                            uid=uid,
                            block_number=block,
                            key_number=0x60,
                            key=authenticated_key
                        )
                    
                    # Read block
                    block_data = self.pn532.mifare_classic_read_block(block)
                    if block_data:
                        data.extend(block_data)
                
                if data:
                    print(f"\n📄 Raw data ({len(data)} bytes): {data.hex()}")
                    
                    # Try to parse NDEF
                    if len(data) > 0 and data[0] == 0x03:
                        msg_len = data[1]
                        print(f"📱 NDEF message detected! Length: {msg_len}")
                        
                        # Try to extract URL
                        if len(data) > 6 and data[2] == 0xD1 and data[5] == 0x55:
                            prefix_code = data[6]
                            
                            prefixes = {
                                0x00: '',
                                0x01: 'http://www.',
                                0x02: 'https://www.',
                                0x03: 'http://',
                                0x04: 'https://',
                            }
                            
                            prefix = prefixes.get(prefix_code, '')
                            url_data = data[7:7+msg_len-5]
                            url = prefix + url_data.decode('utf-8', errors='ignore')
                            
                            print(f"🔗 URL: {url}")
                    
                    return data
                else:
                    print("⚠️ No data read")
                    
            except Exception as e:
                print(f"⚠️ MiFare Classic read failed: {e}")
            
            return uid
                
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
    
    def close(self):
        """Close connection"""
        if self.uart:
            self.uart.close()
            print("👋 Connection closed")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Maroof - NFC Writer')
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
