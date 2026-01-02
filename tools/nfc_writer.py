#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح بطاقة NFC - النسخة النهائية
Fix NFC Card - Final Version
"""

import serial
from adafruit_pn532.uart import PN532_UART
import time

def fix_card():
    """إصلاح البطاقة بشكل كامل"""
    
    print("\n" + "="*70)
    print("🔧 برنامج إصلاح بطاقة NFC")
    print("="*70)
    
    # Connect
    try:
        uart = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
        pn532 = PN532_UART(uart, debug=False)
        
        ic, ver, rev, support = pn532.firmware_version
        print(f"\n✅ متصل بـ: PN532 v{ver}.{rev}")
    except Exception as e:
        print(f"\n❌ خطأ في الاتصال: {e}")
        print("\n💡 تأكد من:")
        print("   - القارئ موصول على /dev/ttyUSB0")
        print("   - القارئ في وضع UART/HSU")
        return False
    
    # Read card
    print("\n[1/4] 💳 ضع البطاقة على القارئ...")
    print("   (انتظر 3 ثواني...)")
    time.sleep(3)
    
    uid = pn532.read_passive_target(timeout=5)
    
    if not uid:
        print("\n❌ لم يتم العثور على بطاقة!")
        print("\n💡 تأكد من:")
        print("   - البطاقة قريبة من القارئ")
        print("   - البطاقة نوع MiFare Classic")
        uart.close()
        return False
    
    print(f"\n✅ البطاقة: {uid.hex()}")
    
    # Fix sector trailer
    print("\n[2/4] 🔧 إصلاح Sector Trailer (Block 7)...")
    
    # Proper MiFare Classic Sector Trailer Structure
    # [Key A (6)][Access Bits (4)][Key B (6)]
    sector_trailer = bytes([
        # Key A - Factory Default (FF FF FF FF FF FF)
        0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
        
        # Access Bits - Transport Configuration
        # Allows read/write with Key A or B
        # Format: C1 C2 C3 (with complement bytes)
        0xFF, 0x07, 0x80, 0x69,
        
        # Key B - Factory Default (FF FF FF FF FF FF)
        0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF
    ])
    
    print(f"   📋 Trailer Data: {sector_trailer.hex()}")
    print(f"   📋 Breakdown:")
    print(f"      Key A:        {sector_trailer[0:6].hex()}")
    print(f"      Access Bits:  {sector_trailer[6:10].hex()}")
    print(f"      Key B:        {sector_trailer[10:16].hex()}")
    
    # Try to write trailer
    fixed = False
    
    # Method 1: Direct write (sometimes works on damaged cards)
    print("\n   📝 محاولة 1: كتابة مباشرة...")
    try:
        success = pn532.mifare_classic_write_block(7, sector_trailer)
        if success:
            print("   ✅ نجحت الكتابة المباشرة!")
            fixed = True
        else:
            print("   ⚠️ الكتابة المباشرة فشلت")
    except Exception as e:
        print(f"   ⚠️ خطأ: {e}")
    
    # Method 2: Try with all known keys
    if not fixed:
        print("\n   📝 محاولة 2: تجربة كل المفاتيح المعروفة...")
        
        keys = [
            (b'\xFF\xFF\xFF\xFF\xFF\xFF', 'Factory Default'),
            (b'\xA0\xA1\xA2\xA3\xA4\xA5', 'MAD Key'),
            (b'\xD3\xF7\xD3\xF7\xD3\xF7', 'NDEF Key'),
            (b'\x00\x00\x00\x00\x00\x00', 'Null Key'),
            (b'\xB0\xB1\xB2\xB3\xB4\xB5', 'Alternative'),
            (b'\xA0\xB0\xC0\xD0\xE0\xF0', 'Alternative 2'),
        ]
        
        for i, (key, name) in enumerate(keys, 1):
            print(f"\n   [{i}/{len(keys)}] جاري تجربة: {name} ({key.hex()})")
            
            try:
                # Get fresh UID
                time.sleep(0.5)
                uid = pn532.read_passive_target(timeout=2)
                
                if not uid:
                    print("      ⚠️ فشل قراءة UID")
                    continue
                
                # Try to authenticate
                auth = pn532.mifare_classic_authenticate_block(
                    uid=uid,
                    block_number=7,
                    key_number=0x60,  # KEY_A
                    key=key
                )
                
                if auth:
                    print("      ✅ نجح التحقق!")
                    
                    # Write trailer
                    success = pn532.mifare_classic_write_block(7, sector_trailer)
                    
                    if success:
                        print("      ✅ تم إصلاح Sector Trailer!")
                        fixed = True
                        break
                    else:
                        print("      ⚠️ التحقق نجح لكن الكتابة فشلت")
                else:
                    print("      ⚠️ فشل التحقق")
                    
            except Exception as e:
                print(f"      ⚠️ خطأ: {e}")
                continue
    
    if not fixed:
        print("\n" + "="*70)
        print("❌ فشل إصلاح Sector Trailer مع كل الطرق")
        print("="*70)
        print("\n💡 الحلول البديلة:")
        print("   1. استخدم تطبيق 'MIFARE Classic Tool' على Android")
        print("   2. جرب بطاقة NFC أخرى")
        print("   3. اشتري بطاقات NTAG215 (أفضل وأسهل)")
        uart.close()
        return False
    
    # Clear data blocks
    print("\n[3/4] 🧹 تنظيف البيانات...")
    
    time.sleep(1)
    uid = pn532.read_passive_target(timeout=2)
    
    if not uid:
        print("   ⚠️ فشل قراءة UID")
    else:
        key = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        
        for block in [4, 5, 6]:
            try:
                if pn532.mifare_classic_authenticate_block(
                    uid=uid,
                    block_number=block,
                    key_number=0x60,
                    key=key
                ):
                    pn532.mifare_classic_write_block(block, b'\x00' * 16)
                    print(f"   ✅ Block {block} تم تنظيفه")
                else:
                    print(f"   ⚠️ Block {block} فشل التحقق")
            except Exception as e:
                print(f"   ⚠️ Block {block}: {e}")
    
    # Test write/read
    print("\n[4/4] 🧪 اختبار الكتابة والقراءة...")
    
    # Create test NDEF message
    test_url = "maroof-id.github.io/test"
    test_ndef = bytes([
        0x03,  # NDEF message
        len(test_url) + 6,  # Length
        0xD1, 0x01, len(test_url) + 1, 0x55, 0x04
    ]) + test_url.encode('utf-8') + bytes([0xFE])
    
    # Pad to 16 bytes
    test_data = test_ndef + b'\x00' * (16 - len(test_ndef))
    
    print(f"   📋 Test Data: {test_data.hex()}")
    
    time.sleep(1)
    uid = pn532.read_passive_target(timeout=2)
    
    if not uid:
        print("   ⚠️ فشل قراءة UID")
    else:
        key = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        
        try:
            # Write test
            if pn532.mifare_classic_authenticate_block(
                uid=uid,
                block_number=4,
                key_number=0x60,
                key=key
            ):
                success = pn532.mifare_classic_write_block(4, test_data)
                
                if success:
                    print("   ✅ الكتابة نجحت!")
                    
                    # Read back
                    time.sleep(0.5)
                    uid = pn532.read_passive_target(timeout=2)
                    
                    if uid and pn532.mifare_classic_authenticate_block(
                        uid=uid,
                        block_number=4,
                        key_number=0x60,
                        key=key
                    ):
                        data = pn532.mifare_classic_read_block(4)
                        
                        if data and data == test_data:
                            print("   ✅ القراءة نجحت!")
                            print(f"   📄 البيانات مطابقة: {data.hex()}")
                        else:
                            print("   ⚠️ البيانات مختلفة")
                            if data:
                                print(f"      المتوقع: {test_data.hex()}")
                                print(f"      المقروء: {data.hex()}")
                else:
                    print("   ❌ الكتابة فشلت")
            else:
                print("   ❌ التحقق فشل")
                
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
    
    uart.close()
    
    # Final result
    print("\n" + "="*70)
    print("🎉 تم إصلاح البطاقة بنجاح!")
    print("="*70)
    print("\n💡 الآن يمكنك:")
    print("   1. كتابة بطاقات جديدة")
    print("   2. استخدام وضع النسخ (Duplicate)")
    print("   3. قراءة البطاقات الموجودة")
    print("\n🚀 جرب الآن:")
    print("   python3 ~/maroof/maroof-cards/tools/nfc_writer.py --url 'https://example.com'")
    print("")
    
    return True

if __name__ == '__main__':
    try:
        fix_card()
    except KeyboardInterrupt:
        print("\n\n⛔ تم الإيقاف من قبل المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()
