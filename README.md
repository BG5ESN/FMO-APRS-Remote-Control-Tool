# FMO-APRS-Remote-Control-Tool

An open-source library for remote control of FMO (Field Mobile Operation) devices via APRS-IS network relay.

## Overview

This tool uses APRS-IS as a network relay to control FMO. There is no command encryption; only the method of signing with `hmac(secret, context)` is used to ensure the reliability and validity of commands. This open-source library fully discloses the authentication method to facilitate quick remote control of FMOs via APRS.

## Features

- **APRS-IS Network Relay**: Global command delivery via APRS infrastructure
- **HMAC Authentication**: HMAC-SHA256 signing for command verification
- **Open Source**: Fully disclosed authentication method
- **Easy Integration**: Simple Python API
- **No Dependencies**: Uses Python standard library only

## Authentication Method

Commands are authenticated using HMAC-SHA256:

1. **Context**: `{timestamp}:{command}:{parameters}`
2. **Signature**: `HMAC-SHA256(secret, context)`
3. **Message**: `{context}:{signature}`

This provides:
- Command authenticity
- Message integrity
- Replay protection (via timestamp)

## Quick Start

### Installation

```bash
git clone https://github.com/BG5ESN/FMO-APRS-Remote-Control-Tool.git
cd FMO-APRS-Remote-Control-Tool
pip install -e .
```

### Send a Command

```python
from fmo_aprs import APRSClient, HMACAuth

auth = HMACAuth("shared-secret")
client = APRSClient("N0CALL", "12345")
client.connect()

signed = auth.sign_command("STATUS", "")
client.send_message("FMO-1", signed)
client.disconnect()
```

### Receive Commands

```python
from fmo_aprs import APRSClient, HMACAuth

auth = HMACAuth("shared-secret")
client = APRSClient("FMO-1", "12345")
client.connect()

def on_message(packet):
    if packet['type'] == 'message':
        verified = auth.verify_command(packet['message'])
        if verified:
            print(f"Valid command: {verified['command']}")

client.receive_messages(on_message)
```

## Documentation

See [DOCUMENTATION.md](DOCUMENTATION.md) for complete API documentation, examples, and security considerations.

## Examples

- `examples/test_auth.py` - Demonstrates HMAC authentication method
- `examples/send_command.py` - Send authenticated commands
- `examples/receive_command.py` - Receive and process commands

## Security

This tool uses **authentication without encryption**:
- ✓ Ensures commands come from authorized sources (HMAC)
- ✓ Prevents command tampering (integrity check)
- ✓ Prevents replay attacks (timestamp validation)
- ✗ Does NOT hide command content (no encryption)

This approach is appropriate for amateur radio use and complies with regulations requiring non-encrypted transmissions.

## License

MIT License - See LICENSE file for details

## Author

**BG5ESN**

Repository: https://github.com/BG5ESN/FMO-APRS-Remote-Control-Tool
