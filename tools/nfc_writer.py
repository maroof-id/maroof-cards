#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معروف - كتابة بطاقات NFC
Maroof NFC Writer for PN532
"""

import nfc
import time
import sys
from pathlib import Path

class NFCWriter:
    """كاتب بطاقات NFC"""
    
    def __init__(self):
        self.clf = None
        
    def connect(self):
        """الاتصال بقارئ NFC"""
        try:
            print("🔍 جاري البحث عن قارئ NFC...")
            self.clf = nfc.ContactlessFrontend('usb')
            print(f"✅ تم الاتصال بالقارئ: {self.clf}")
            return True
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
            print("\n💡 تأكد من:")
            print("  - توصيل القارئ بـ USB")
            print("  - تثبيت nfcpy: pip3 install nfcpy --break-system-packages")
            return False
    
    def write_url(self, url: str):
        """
        كتابة رابط URL على بطاقة NFC
        
        Args:
            url: الرابط المراد كتابته
        """
        if not self.clf:
            print("❌ غير متصل بالقارئ!")
            return False
        
        print(f"\n📝 جاهز للكتابة: {url}")
        print("💳 قرّب البطاقة من القارئ...")
        
        try:
            # انتظار البطاقة
            tag = self.clf.connect(rdwr={'on-connect': lambda tag: False})
            
            if not tag:
                print("❌ لم يتم اكتشاف بطاقة")
                return False
            
            print(f"✅ تم اكتشاف البطاقة: {tag}")
            
            # إنشاء NDEF Record لـ URL
            import ndef
            
            # إنشاء رسالة NDEF
            uri_record = ndef.UriRecord(url)
            message = ndef.Message(uri_record)
            
            # كتابة على البطاقة
            if tag.ndef:
                tag.ndef.records = message
                print("✅ تم كتابة الرابط بنجاح!")
                print(f"📱 البطاقة جاهزة: {url}")
                
                # صوت تأكيد (اختياري)
                self.beep_success()
                
                return True
            else:
                print("❌ البطاقة لا تدعم NDEF")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في الكتابة: {e}")
            return False
    
    def read_card(self):
        """قراءة محتوى بطاقة NFC"""
        if not self.clf:
            print("❌ غير متصل بالقارئ!")
            return None
        
        print("\n📖 قرّب البطاقة للقراءة...")
        
        try:
            tag = self.clf.connect(rdwr={'on-connect': lambda tag: False})
            
            if not tag:
                print("❌ لم يتم اكتشاف بطاقة")
                return None
            
            print(f"✅ تم اكتشاف البطاقة: {tag}")
            
            if tag.ndef:
                for record in tag.ndef.records:
                    print(f"\n📄 السجل: {record}")
                    if hasattr(record, 'uri'):
                        print(f"🔗 الرابط: {record.uri}")
                        return record.uri
                return True
            else:
                print("❌ البطاقة لا تحتوي على بيانات NDEF")
                return None
                
        except Exception as e:
            print(f"❌ خطأ في القراءة: {e}")
            return None
    
    def beep_success(self):
        """صوت تأكيد (باستخدام GPIO buzzer إن وُجد)"""
        try:
            # محاولة تشغيل صوت باستخدام pygame
            import pygame
            pygame.mixer.init()
            # يمكن إضافة ملف صوت هنا
        except:
            # إذا لم ينجح، استخدم beep النظام
            try:
                import os
                os.system('beep -f 1000 -l 200')
            except:
                pass
    
    def wait_for_card(self, timeout=30):
        """
        انتظار تقريب بطاقة
        
        Args:
            timeout: المدة القصوى للانتظار (ثانية)
        """
        print(f"\n⏳ انتظار البطاقة (timeout: {timeout}s)...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                tag = self.clf.connect(rdwr={'on-connect': lambda tag: False})
                if tag:
                    return tag
            except:
                pass
            
            time.sleep(0.1)
        
        print("⏱️ انتهى الوقت!")
        return None
    
    def close(self):
        """إغلاق الاتصال"""
        if self.clf:
            self.clf.close()
            print("👋 تم إغلاق الاتصال")


def main():
    """الدالة الرئيسية"""
    import argparse
    
    parser = argparse.ArgumentParser(description='معروف - كتابة بطاقات NFC')
    parser.add_argument('--url', '-u', help='الرابط المراد كتابته')
    parser.add_argument('--read', '-r', action='store_true', help='قراءة البطاقة')
    parser.add_argument('--wait', '-w', action='store_true', 
                       help='وضع الانتظار المستمر')
    
    args = parser.parse_args()
    
    # إنشاء الكاتب
    writer = NFCWriter()
    
    # الاتصال بالقارئ
    if not writer.connect():
        sys.exit(1)
    
    try:
        if args.read:
            # قراءة البطاقة
            writer.read_card()
            
        elif args.url:
            # كتابة رابط محدد
            writer.write_url(args.url)
            
        elif args.wait:
            # وضع الانتظار المستمر
            print("\n🔄 وضع الانتظار المستمر...")
            print("💡 اضغط Ctrl+C للإيقاف\n")
            
            while True:
                print("💳 قرّب بطاقة جديدة...")
                tag = writer.wait_for_card(timeout=60)
                
                if tag:
                    # اطلب الرابط
                    url = input("\n🔗 أدخل الرابط (أو Enter للتخطي): ").strip()
                    
                    if url:
                        writer.write_url(url)
                    
                    time.sleep(2)
                    print("\n" + "="*50 + "\n")
                    
        else:
            # وضع تفاعلي
            print("\n📝 وضع الكتابة التفاعلي")
            url = input("🔗 أدخل الرابط: ").strip()
            
            if url:
                writer.write_url(url)
            else:
                print("❌ لم تدخل رابط!")
                
    except KeyboardInterrupt:
        print("\n\n⛔ تم الإيقاف بواسطة المستخدم")
        
    finally:
        writer.close()


if __name__ == '__main__':
    main()