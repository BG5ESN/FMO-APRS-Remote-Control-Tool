#!/usr/bin/env python3
"""
Example: Sending Commands via APRS-IS

This example demonstrates how to send authenticated commands to an FMO
via the APRS-IS network.
"""

import sys
import logging
from fmo_aprs import APRSClient, HMACAuth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Configuration
    YOUR_CALLSIGN = "N0CALL"  # Your callsign
    YOUR_PASSCODE = "-1"      # Your APRS-IS passcode
    TARGET_CALLSIGN = "FMO-1"  # Target FMO callsign
    SHARED_SECRET = "your-secret-key-here"  # Shared secret with FMO
    
    # Initialize HMAC authenticator
    auth = HMACAuth(SHARED_SECRET)
    
    # Initialize APRS client
    client = APRSClient(YOUR_CALLSIGN, YOUR_PASSCODE)
    
    # Connect to APRS-IS
    print(f"Connecting to APRS-IS as {YOUR_CALLSIGN}...")
    if not client.connect():
        print("Failed to connect to APRS-IS")
        return 1
    
    print("Connected successfully!")
    
    # Example commands
    commands = [
        ("STATUS", ""),           # Get status
        ("SET_FREQ", "144.390"),  # Set frequency
        ("POWER", "HIGH"),        # Set power level
    ]
    
    # Send commands
    for command, parameters in commands:
        # Sign the command
        signed_message = auth.sign_command(command, parameters)
        
        print(f"\nSending command: {command} {parameters}")
        print(f"Signed message: {signed_message}")
        
        # Send via APRS-IS
        if client.send_message(TARGET_CALLSIGN, signed_message):
            print("Command sent successfully!")
        else:
            print("Failed to send command")
    
    # Disconnect
    client.disconnect()
    print("\nDisconnected from APRS-IS")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
