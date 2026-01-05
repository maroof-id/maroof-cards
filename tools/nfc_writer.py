#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFC Writer - Handles NFC card reading and writing
"""

import threading
import time

try:
    import nfc
    import ndef
except Exception:
    # Import errors will surface when attempting to use NFC on systems without nfcpy
    nfc = None
    ndef = None

class NFCWriter:
    """NFC card reader/writer using PN532"""
    
    def __init__(self):
        self.clf = None
    
    def connect(self):
        """Connect to NFC reader"""
        if nfc is None:
            return False

        try:
            self.clf = nfc.ContactlessFrontend(self.transport)
            return True
        except Exception as e:
            print(f"❌ Failed to connect to NFC reader: {e}")
            self.clf = None
            return False
    
    def write_url(self, url: str, timeout: int = 5):
        """Write URL to NFC card with timeout (seconds).

        Returns: (success: bool, message: str)
        """
        if nfc is None or ndef is None:
            return False, 'nfc library not available'

        if not self.clf:
            if not self.connect():
                return False, 'Could not connect to NFC reader'

        record = ndef.UriRecord(url)
        result = {'ok': False, 'msg': ''}

        def on_connect(tag):
            try:
                if getattr(tag, 'ndef', None):
                    try:
                        tag.ndef.records = [record]
                        result['ok'] = True
                        result['msg'] = 'Written'
                        return True
                    except Exception as e:
                        result['msg'] = f'Failed writing to tag: {e}'
                        return False
                else:
                    result['msg'] = 'Tag does not support NDEF'
                    return False
            except Exception as e:
                result['msg'] = f'Exception in on_connect: {e}'
                return False

        def _target():
            try:
                self.clf.connect(rdwr={'on-connect': on_connect})
            except Exception as e:
                result['msg'] = f'Connect failed: {e}'

        thread = threading.Thread(target=_target, daemon=True)
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            return False, 'Timeout waiting for card'

        return bool(result.get('ok', False)), result.get('msg', '')
    
    def read_card(self, timeout: int = 5):
        """Read NFC card with timeout.

        Returns: (data: dict or None, message: str)
        """
        if nfc is None or ndef is None:
            return None, 'nfc library not available'

        if not self.clf:
            if not self.connect():
                return None, 'Could not connect to NFC reader'

        data = {'url': None, 'raw_records': []}

        def on_connect(tag):
            try:
                if getattr(tag, 'ndef', None):
                    for record in tag.ndef.records:
                        data['raw_records'].append(record)
                        if isinstance(record, ndef.UriRecord):
                            data['url'] = record.uri
                    # return True to stop polling after reading
                    return True
                else:
                    return False
            except Exception as e:
                return False

        def _target():
            try:
                self.clf.connect(rdwr={'on-connect': on_connect})
            except Exception as e:
                pass

        thread = threading.Thread(target=_target, daemon=True)
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            return None, 'Timeout waiting for card'

        if data.get('url'):
            return {'url': data['url']}, 'OK'
        elif data['raw_records']:
            return {'records': data['raw_records']}, 'No URI record found'
        else:
            return None, 'No data found on tag'
    
    def close(self):
        """Close NFC reader connection"""
        if self.clf:
            self.clf.close()