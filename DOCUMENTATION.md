# FMO-APRS-Remote-Control-Tool

An open-source library for remote control of FMO (Field Mobile Operation) devices via APRS-IS network relay. This tool uses HMAC-based authentication to ensure command authenticity and integrity without encryption.

## Overview

This tool uses APRS-IS as a network relay to control FMO devices. There is no command encryption; only the method of signing with `hmac(secret, context)` is used to ensure the reliability and validity of commands. This open-source library fully discloses the authentication method to facilitate quick remote control of FMOs via APRS.

## Features

- **APRS-IS Network Relay**: Leverages the APRS-IS infrastructure for global command delivery
- **HMAC Authentication**: Uses HMAC-SHA256 for command signing and verification
- **No Encryption**: Commands are authenticated but not encrypted, per APRS best practices
- **Replay Protection**: Timestamp-based validation prevents replay attacks
- **Open Source**: Fully disclosed authentication method for transparency
- **Easy Integration**: Simple Python API for quick implementation

## Authentication Method

### Overview

Commands are authenticated using HMAC-SHA256 with the following method:

1. **Context Construction**: 
   ```
   context = f"{timestamp}:{command}:{parameters}"
   ```

2. **Signature Generation**:
   ```
   signature = HMAC-SHA256(secret, context)
   ```

3. **Message Format**:
   ```
   {timestamp}:{command}:{parameters}:{signature}
   ```

4. **Verification**:
   - Timestamp must be recent (default: within 5 minutes)
   - HMAC signature must match expected value
   - Uses constant-time comparison to prevent timing attacks

### Security Properties

This authentication method provides:

- **Authenticity**: Verifies the command came from someone with the shared secret
- **Integrity**: Ensures the command was not modified in transit
- **Replay Protection**: Timestamp validation prevents old commands from being replayed
- **Non-repudiation**: Signed commands cannot be denied by the sender

### What It Does NOT Provide

- **Confidentiality**: Commands are visible to anyone monitoring APRS-IS
- **Forward Secrecy**: Compromise of the secret allows verification of past commands
- **Multi-party Authentication**: Single shared secret between sender and receiver

## Installation

### From Source

```bash
git clone https://github.com/BG5ESN/FMO-APRS-Remote-Control-Tool.git
cd FMO-APRS-Remote-Control-Tool
pip install -e .
```

### Requirements

- Python 3.7+
- No external dependencies (uses standard library only)

## Quick Start

### Sending Commands

```python
from fmo_aprs import APRSClient, HMACAuth

# Initialize
auth = HMACAuth("your-shared-secret")
client = APRSClient("N0CALL", "12345")

# Connect
client.connect()

# Sign and send command
signed = auth.sign_command("SET_FREQ", "144.390")
client.send_message("FMO-1", signed)

# Disconnect
client.disconnect()
```

### Receiving Commands

```python
from fmo_aprs import APRSClient, HMACAuth, Command, CommandHandler

# Initialize
auth = HMACAuth("your-shared-secret")
handler = CommandHandler()
client = APRSClient("FMO-1", "12345")

# Register command handlers
def handle_status(cmd: Command) -> bool:
    print(f"Status requested by {cmd.source}")
    return True

handler.register("STATUS", handle_status)

# Connect and receive
client.connect()

def on_message(packet):
    if packet['type'] == 'message':
        verified = auth.verify_command(packet['message'])
        if verified:
            cmd = Command(
                command=verified['command'],
                parameters=verified['parameters'],
                timestamp=verified['timestamp'],
                age=verified['age'],
                source=packet['from']
            )
            handler.handle(cmd)

client.receive_messages(on_message)
```

## Examples

The `examples/` directory contains complete working examples:

- **send_command.py**: Demonstrates sending authenticated commands
- **receive_command.py**: Shows how to receive and process commands
- **test_auth.py**: Fully demonstrates the HMAC authentication method

Run examples:

```bash
python examples/test_auth.py
python examples/send_command.py
python examples/receive_command.py
```

## API Documentation

### APRSClient

```python
APRSClient(callsign: str, passcode: str, server: str, port: int)
```

Main client for APRS-IS communication.

**Methods:**
- `connect() -> bool`: Connect to APRS-IS
- `disconnect()`: Disconnect from APRS-IS
- `send_message(destination: str, message: str) -> bool`: Send a message
- `receive_messages(callback, timeout)`: Receive messages with callback

### HMACAuth

```python
HMACAuth(secret: str, time_window: int = 300)
```

HMAC authentication for commands.

**Methods:**
- `sign_command(command: str, parameters: str = "") -> str`: Sign a command
- `verify_command(signed_message: str) -> Optional[dict]`: Verify a signed command
- `sign_json_command(command: str, params_dict: dict) -> str`: Sign with JSON params
- `verify_json_command(signed_message: str) -> Optional[dict]`: Verify with JSON params

### CommandHandler

```python
CommandHandler()
```

Command dispatcher and handler registry.

**Methods:**
- `register(command_name: str, handler: Callable)`: Register a command handler
- `set_default_handler(handler: Callable)`: Set default handler for unknown commands
- `handle(command: Command) -> bool`: Dispatch command to handler
- `list_commands() -> list`: Get list of registered commands

## Configuration

### APRS-IS Passcode

To connect to APRS-IS, you need a valid passcode for your callsign. Generate one at:
- https://apps.magicbug.co.uk/passcode/

**Note**: For receive-only operation, use passcode `-1`.

### Shared Secret

Both the command sender and FMO receiver must use the same shared secret. This should be:
- At least 16 characters long
- Randomly generated
- Kept confidential
- Unique per FMO installation

Example generation:
```python
import secrets
secret = secrets.token_urlsafe(32)
print(secret)
```

## Security Considerations

### Best Practices

1. **Use Strong Secrets**: Generate cryptographically random shared secrets
2. **Rotate Secrets**: Periodically change shared secrets
3. **Monitor Commands**: Log all received commands for audit
4. **Validate Parameters**: Always validate command parameters before execution
5. **Rate Limiting**: Implement rate limiting to prevent abuse
6. **Command Whitelist**: Only accept known, expected commands

### Known Limitations

1. **No Encryption**: Commands are visible to anyone monitoring APRS-IS
2. **Shared Secret**: Single secret shared between sender and receiver
3. **Time Synchronization**: Requires reasonably synchronized clocks
4. **Network Dependency**: Relies on APRS-IS infrastructure availability

### Why No Encryption?

This tool follows APRS best practices and regulations:

1. **Amateur Radio Regulations**: In many jurisdictions, amateur radio transmissions must not be encrypted
2. **APRS Philosophy**: APRS is designed for open, shared information
3. **Transparency**: Open authentication allows community verification and improvement
4. **Performance**: HMAC is lightweight and suitable for resource-constrained devices

Authentication (HMAC) provides integrity and authenticity without encryption, which is appropriate for this use case.

## Contributing

Contributions are welcome! This is an open-source project that fully discloses its methods.

### Areas for Contribution

- Additional command handlers
- Enhanced error handling
- More examples
- Documentation improvements
- Testing framework

## License

This project is open source. Please check the LICENSE file for details.

## Acknowledgments

- APRS-IS network and infrastructure
- Amateur radio community
- Contributors to APRS standards

## Contact

- **Author**: BG5ESN
- **Repository**: https://github.com/BG5ESN/FMO-APRS-Remote-Control-Tool

## Disclaimer

This tool is provided for educational and legitimate amateur radio use only. Users are responsible for ensuring compliance with local regulations regarding amateur radio communications and remote control systems.
