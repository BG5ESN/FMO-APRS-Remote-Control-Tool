# Examples

This directory contains example scripts demonstrating the FMO-APRS-Remote-Control-Tool functionality.

## Files

### test_auth.py

Demonstrates the HMAC authentication method with detailed output showing:
- How commands are signed
- How signatures are verified
- Detection of tampered messages
- Detection of expired commands
- JSON parameter support

This script fully discloses the authentication method used by the library.

**Run:**
```bash
python3 test_auth.py
```

### send_command.py

Example of sending authenticated commands to an FMO via APRS-IS.

**Before running:**
1. Edit the script to set your callsign and passcode
2. Set the target FMO callsign
3. Set the shared secret (must match the FMO's secret)

**Run:**
```bash
python3 send_command.py
```

### receive_command.py

Example of receiving and processing authenticated commands from APRS-IS.

**Before running:**
1. Edit the script to set your FMO callsign and passcode
2. Set the shared secret (must match the sender's secret)
3. Implement your command handlers

**Run:**
```bash
python3 receive_command.py
```

Press Ctrl+C to stop.

## Configuration

All examples require:
- A valid amateur radio callsign
- APRS-IS passcode (get from https://apps.magicbug.co.uk/passcode/)
- Shared secret for HMAC authentication

For testing without network access, use `test_auth.py` which demonstrates the authentication method without connecting to APRS-IS.
