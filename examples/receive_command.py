#!/usr/bin/env python3
"""
Example: Receiving and Processing Commands

This example demonstrates how to receive and verify commands from APRS-IS
for an FMO receiver.
"""

import sys
import logging
from fmo_aprs import APRSClient, HMACAuth, Command, CommandHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Configuration
    FMO_CALLSIGN = "FMO-1"     # FMO callsign
    FMO_PASSCODE = "-1"        # APRS-IS passcode
    SHARED_SECRET = "your-secret-key-here"  # Shared secret
    
    # Initialize HMAC authenticator
    auth = HMACAuth(SHARED_SECRET)
    
    # Initialize command handler
    cmd_handler = CommandHandler()
    
    # Register command handlers
    def handle_status(cmd: Command) -> bool:
        print(f"STATUS command received from {cmd.source}")
        # Implement status reporting here
        return True
    
    def handle_set_freq(cmd: Command) -> bool:
        print(f"SET_FREQ command: {cmd.parameters}")
        # Implement frequency setting here
        return True
    
    def handle_power(cmd: Command) -> bool:
        print(f"POWER command: {cmd.parameters}")
        # Implement power setting here
        return True
    
    cmd_handler.register("STATUS", handle_status)
    cmd_handler.register("SET_FREQ", handle_set_freq)
    cmd_handler.register("POWER", handle_power)
    
    # Initialize APRS client
    client = APRSClient(FMO_CALLSIGN, FMO_PASSCODE)
    
    # Connect to APRS-IS
    print(f"Connecting to APRS-IS as {FMO_CALLSIGN}...")
    if not client.connect():
        print("Failed to connect to APRS-IS")
        return 1
    
    print("Connected! Listening for commands...")
    print("Press Ctrl+C to stop")
    
    # Message callback
    def on_message(packet: dict):
        if packet['type'] != 'message':
            return
        
        if packet['to'].strip() != FMO_CALLSIGN:
            return
        
        message = packet['message']
        source = packet['from']
        
        print(f"\n--- Received message from {source} ---")
        print(f"Message: {message}")
        
        # Verify signature
        verified = auth.verify_command(message)
        
        if verified:
            print("✓ Signature verified!")
            print(f"  Command: {verified['command']}")
            print(f"  Parameters: {verified['parameters']}")
            print(f"  Age: {verified['age']} seconds")
            
            # Create command object
            cmd = Command(
                command=verified['command'],
                parameters=verified['parameters'],
                timestamp=verified['timestamp'],
                age=verified['age'],
                source=source
            )
            
            # Handle the command
            if cmd_handler.handle(cmd):
                print("✓ Command executed successfully")
            else:
                print("✗ Command execution failed")
        else:
            print("✗ Invalid signature or expired command")
    
    # Receive messages
    try:
        client.receive_messages(on_message, timeout=0)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    
    client.disconnect()
    return 0

if __name__ == "__main__":
    sys.exit(main())
