#!/usr/bin/env python3
import nfc
import time

print("?? AITRIP PN532 Connection Test")
print("=" * 50)

# ??????? ?????? ?? ??????
attempts = [
    ('usb', 2),
    ('usb:072f:2200', 2),  # ???? ???? ?? AITRIP
    ('tty:/dev/ttyUSB0:pn532', 1),
    ('tty:/dev/ttyACM0:pn532', 1),
]

for transport, wait_time in attempts:
    try:
        print(f"\n? {transport}...")
        time.sleep(wait_time)  # ????? ??????
        
        clf = nfc.ContactlessFrontend(transport)
        print(f"??? SUCCESS!")
        print(f"Device: {clf}")
        print(f"\n?? Use this in your code: '{transport}'")
        
        # ?????? ????
        print("\n?? Test: Place NFC card (5 seconds)...")
        tag = clf.connect(rdwr={'on-connect': lambda t: False})
        if tag:
            print(f"? Card detected: {tag}")
        else:
            print("?? No card (timeout)")
        
        clf.close()
        break
        
    except Exception as e:
        print(f"? {str(e)[:60]}")

print("\n" + "=" * 50)
