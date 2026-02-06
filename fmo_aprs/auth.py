"""
HMAC Authentication Module

Implements HMAC-based authentication for command signing and verification.
This module fully discloses the authentication method used in FMO-APRS.
"""

import hmac
import hashlib
import time
import json
from typing import Optional

class HMACAuth:
    """
    HMAC-based authentication for FMO commands.
    
    Authentication Method:
    ----------------------
    Commands are signed using HMAC-SHA256 with the following format:
    
    1. Context is constructed from command data:
       context = f"{timestamp}:{command}:{parameters}"
       
    2. Signature is computed as:
       signature = hmac(secret, context, sha256)
       
    3. The complete message format is:
       {timestamp}:{command}:{parameters}:{signature}
       
    4. Signature verification checks:
       - Timestamp is recent (within time window)
       - HMAC signature matches expected value
    
    This method ensures:
    - Command authenticity (came from holder of secret)
    - Command integrity (not modified in transit)
    - Replay protection (via timestamp validation)
    """
    
    def __init__(self, secret: str, time_window: int = 300):
        """
        Initialize HMAC authenticator.
        
        Args:
            secret: Shared secret key for HMAC
            time_window: Maximum age of commands in seconds (default: 300)
        """
        self.secret = secret.encode('utf-8')
        self.time_window = time_window
    
    def sign_command(self, command: str, parameters: str = "") -> str:
        """
        Sign a command with HMAC.
        
        Args:
            command: Command name
            parameters: Command parameters (optional)
            
        Returns:
            Signed command string in format: {timestamp}:{command}:{parameters}:{signature}
        """
        timestamp = int(time.time())
        
        # Build context for HMAC
        context = f"{timestamp}:{command}:{parameters}"
        
        # Compute HMAC signature
        signature = hmac.new(
            self.secret,
            context.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Return complete signed message
        return f"{context}:{signature}"
    
    def verify_command(self, signed_message: str) -> Optional[dict]:
        """
        Verify a signed command.
        
        Args:
            signed_message: Signed command string
            
        Returns:
            Dictionary with command details if valid, None if invalid
            {
                'timestamp': int,
                'command': str,
                'parameters': str,
                'signature': str
            }
        """
        try:
            # Parse signed message
            # Signature is last 64 hex chars + 1 colon = 65 chars
            if len(signed_message) < 65 or signed_message[-65] != ':':
                return None
            
            signature = signed_message[-64:]
            context_with_sep = signed_message[:-65]
            
            # Split context: timestamp:command:parameters
            parts = context_with_sep.split(':', 2)
            if len(parts) != 3:
                return None
            
            timestamp_str, command, parameters = parts
            timestamp = int(timestamp_str)
            
            # Check timestamp freshness
            current_time = int(time.time())
            age = current_time - timestamp
            
            if age > self.time_window:
                return None  # Command too old
            
            if age < -60:  # Allow 60 seconds clock skew into future
                return None  # Timestamp in future
            
            # Reconstruct context and verify signature
            context = f"{timestamp}:{command}:{parameters}"
            expected_signature = hmac.new(
                self.secret,
                context.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Use constant-time comparison to prevent timing attacks
            if not hmac.compare_digest(signature, expected_signature):
                return None  # Invalid signature
            
            # Command is valid
            return {
                'timestamp': timestamp,
                'command': command,
                'parameters': parameters,
                'signature': signature,
                'age': age
            }
            
        except Exception:
            return None
    
    def sign_json_command(self, command: str, params_dict: dict) -> str:
        """
        Sign a command with JSON parameters.
        
        Args:
            command: Command name
            params_dict: Parameters as dictionary
            
        Returns:
            Signed command string
        """
        parameters = json.dumps(params_dict, separators=(',', ':'), sort_keys=True)
        return self.sign_command(command, parameters)
    
    def verify_json_command(self, signed_message: str) -> Optional[dict]:
        """
        Verify a command with JSON parameters.
        
        Args:
            signed_message: Signed command string
            
        Returns:
            Dictionary with command and parsed parameters if valid, None if invalid
        """
        result = self.verify_command(signed_message)
        if result and result['parameters']:
            try:
                result['params_dict'] = json.loads(result['parameters'])
            except:
                pass
        return result
