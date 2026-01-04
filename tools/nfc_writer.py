#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFC Writer - Handles NFC card reading and writing
"""

import nfc
import ndef

class NFCWriter:
    """NFC card reader/writer using PN532"""
    
    def __init__(self):
        self.clf = None
    
    def connect(self):
        """Connect to NFC reader"""
        try:
            self.clf = nfc.ContactlessFrontend('usb')
            print("✅ Connected to NFC reader")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to NFC reader: {e}")
            return False
    
    def write_url(self, url):
        """Write URL to NFC card"""
        if not self.clf:
            if not self.connect():
                return False
        
        print(f"\n📝 Writing: {url}")
        print("⏳ Place card on reader...")
        
        record = ndef.UriRecord(url)
        
        def on_connect(tag):
            if tag.ndef:
                tag.ndef.records = [record]
                print("✅ Successfully written!")
                return True
            else:
                print("❌ Card does not support NDEF")
                return False
        
        try:
            self.clf.connect(rdwr={'on-connect': on_connect})
            return True
        except Exception as e:
            print(f"❌ Write error: {e}")
            return False
    
    def read_card(self):
        """Read NFC card"""
        if not self.clf:
            if not self.connect():
                return None
        
        print("\n📖 Reading card...")
        print("⏳ Place card on reader...")
        
        data = {}
        
        def on_connect(tag):
            if tag.ndef:
                for record in tag.ndef.records:
                    if isinstance(record, ndef.UriRecord):
                        data['url'] = record.uri
                        print(f"✅ URL: {record.uri}")
                return True
            else:
                print("❌ Card is empty")
                return False
        
        try:
            self.clf.connect(rdwr={'on-connect': on_connect})
            return data
        except Exception as e:
            print(f"❌ Read error: {e}")
            return None
    
    def close(self):
        """Close NFC reader connection"""
        if self.clf:
            self.clf.close()