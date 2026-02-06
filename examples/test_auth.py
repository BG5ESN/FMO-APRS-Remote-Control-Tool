#!/usr/bin/env python3
"""
Example: Testing HMAC Authentication

This example demonstrates the HMAC authentication system and 
fully discloses the encryption method.
"""

import time
from fmo_aprs import HMACAuth

def main():
    print("=" * 70)
    print("FMO-APRS HMAC Authentication Method Demonstration")
    print("=" * 70)
    print()
    
    # Initialize authenticator with a secret
    secret = "my-secret-key"
    auth = HMACAuth(secret, time_window=300)
    
    print("1. AUTHENTICATION METHOD")
    print("-" * 70)
    print("Commands are signed using HMAC-SHA256:")
    print()
    print("   Context format: {timestamp}:{command}:{parameters}")
    print("   Signature: HMAC-SHA256(secret, context)")
    print("   Message format: {context}:{signature}")
    print()
    
    print("2. SIGNING A COMMAND")
    print("-" * 70)
    command = "SET_FREQ"
    parameters = "144.390"
    
    print(f"Command: {command}")
    print(f"Parameters: {parameters}")
    print(f"Secret: {secret}")
    print()
    
    signed = auth.sign_command(command, parameters)
    print(f"Signed message:\n{signed}")
    print()
    
    # Parse the signed message
    parts = signed.split(':')
    print("Message components:")
    print(f"  Timestamp: {parts[0]}")
    print(f"  Command: {parts[1]}")
    print(f"  Parameters: {parts[2]}")
    print(f"  Signature: {parts[3]}")
    print()
    
    print("3. VERIFYING A COMMAND")
    print("-" * 70)
    print(f"Verifying: {signed}")
    print()
    
    verified = auth.verify_command(signed)
    if verified:
        print("✓ Verification SUCCESS")
        print(f"  Command: {verified['command']}")
        print(f"  Parameters: {verified['parameters']}")
        print(f"  Timestamp: {verified['timestamp']}")
        print(f"  Age: {verified['age']} seconds")
    else:
        print("✗ Verification FAILED")
    print()
    
    print("4. TESTING INVALID SIGNATURE")
    print("-" * 70)
    tampered = signed[:-4] + "XXXX"  # Tamper with signature
    print(f"Tampered message: {tampered}")
    print()
    
    verified = auth.verify_command(tampered)
    if verified:
        print("✗ SECURITY ISSUE: Tampered message verified!")
    else:
        print("✓ Tampered message correctly rejected")
    print()
    
    print("5. TESTING EXPIRED COMMAND")
    print("-" * 70)
    # Create an old timestamp
    old_timestamp = int(time.time()) - 400  # 400 seconds ago
    context = f"{old_timestamp}:{command}:{parameters}"
    
    import hmac
    import hashlib
    signature = hmac.new(
        secret.encode('utf-8'),
        context.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    old_signed = f"{context}:{signature}"
    print(f"Old message (400s ago): {old_signed}")
    print()
    
    verified = auth.verify_command(old_signed)
    if verified:
        print("✗ SECURITY ISSUE: Expired message verified!")
    else:
        print("✓ Expired message correctly rejected")
    print()
    
    print("6. JSON PARAMETERS")
    print("-" * 70)
    params_dict = {
        "frequency": 144.390,
        "mode": "FM",
        "power": "HIGH"
    }
    
    signed_json = auth.sign_json_command("CONFIGURE", params_dict)
    print(f"Command with JSON params:\n{signed_json}")
    print()
    
    verified_json = auth.verify_json_command(signed_json)
    if verified_json and 'params_dict' in verified_json:
        print("✓ JSON parameters parsed:")
        for key, value in verified_json['params_dict'].items():
            print(f"  {key}: {value}")
    print()
    
    print("=" * 70)
    print("Authentication method fully disclosed for open-source transparency")
    print("=" * 70)

if __name__ == "__main__":
    main()
