#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append('./tools')

try:
    from nfc_writer import NFCWriter
    print("✅ استيراد nfc_writer نجح")
    
    writer = NFCWriter()
    print("✅ إنشاء NFCWriter نجح")
    
    if writer.connect():
        print("✅ الاتصال بالقارئ نجح!")
        print(f"📡 القارئ: {writer.device}")
        writer.close()
        print("✅ اختبار كامل ناجح!")
        sys.exit(0)
    else:
        print("❌ فشل الاتصال بالقارئ")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ خطأ: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
