"""
Unit tests for HMAC authentication module.
"""

import unittest
import time
from fmo_aprs import HMACAuth


class TestHMACAuth(unittest.TestCase):
    """Test cases for HMACAuth class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.secret = "test-secret-key"
        self.auth = HMACAuth(self.secret, time_window=300)
    
    def test_sign_command(self):
        """Test command signing."""
        signed = self.auth.sign_command("TEST", "param1")
        
        # Should have 4 parts separated by colons
        parts = signed.split(':')
        self.assertEqual(len(parts), 4)
        
        # First part should be a timestamp
        timestamp = int(parts[0])
        self.assertIsInstance(timestamp, int)
        self.assertLessEqual(abs(time.time() - timestamp), 2)
        
        # Second part should be command
        self.assertEqual(parts[1], "TEST")
        
        # Third part should be parameters
        self.assertEqual(parts[2], "param1")
        
        # Fourth part should be signature (64 hex chars for SHA256)
        self.assertEqual(len(parts[3]), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in parts[3]))
    
    def test_verify_valid_command(self):
        """Test verification of valid command."""
        signed = self.auth.sign_command("STATUS", "")
        verified = self.auth.verify_command(signed)
        
        self.assertIsNotNone(verified)
        self.assertEqual(verified['command'], "STATUS")
        self.assertEqual(verified['parameters'], "")
        self.assertIn('timestamp', verified)
        self.assertIn('signature', verified)
        self.assertIn('age', verified)
    
    def test_verify_invalid_signature(self):
        """Test verification rejects invalid signature."""
        signed = self.auth.sign_command("TEST", "param")
        
        # Tamper with signature
        tampered = signed[:-4] + "XXXX"
        verified = self.auth.verify_command(tampered)
        
        self.assertIsNone(verified)
    
    def test_verify_expired_command(self):
        """Test verification rejects expired commands."""
        # Create a command with old timestamp
        old_timestamp = int(time.time()) - 400  # 400 seconds ago
        context = f"{old_timestamp}:TEST:param"
        
        import hmac
        import hashlib
        signature = hmac.new(
            self.secret.encode('utf-8'),
            context.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        old_signed = f"{context}:{signature}"
        verified = self.auth.verify_command(old_signed)
        
        self.assertIsNone(verified)
    
    def test_verify_future_command(self):
        """Test verification rejects commands with future timestamps."""
        # Create command with timestamp far in future
        future_timestamp = int(time.time()) + 120  # 2 minutes in future
        context = f"{future_timestamp}:TEST:param"
        
        import hmac
        import hashlib
        signature = hmac.new(
            self.secret.encode('utf-8'),
            context.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        future_signed = f"{context}:{signature}"
        verified = self.auth.verify_command(future_signed)
        
        self.assertIsNone(verified)
    
    def test_sign_with_empty_parameters(self):
        """Test signing command with empty parameters."""
        signed = self.auth.sign_command("PING", "")
        verified = self.auth.verify_command(signed)
        
        self.assertIsNotNone(verified)
        self.assertEqual(verified['command'], "PING")
        self.assertEqual(verified['parameters'], "")
    
    def test_sign_json_command(self):
        """Test signing command with JSON parameters."""
        params = {"freq": 144.390, "mode": "FM"}
        signed = self.auth.sign_json_command("CONFIG", params)
        
        verified = self.auth.verify_json_command(signed)
        self.assertIsNotNone(verified)
        self.assertEqual(verified['command'], "CONFIG")
        self.assertIn('params_dict', verified)
        self.assertEqual(verified['params_dict']['freq'], 144.390)
        self.assertEqual(verified['params_dict']['mode'], "FM")
    
    def test_different_secrets_fail_verification(self):
        """Test that different secrets cannot verify each other's commands."""
        auth1 = HMACAuth("secret1")
        auth2 = HMACAuth("secret2")
        
        signed = auth1.sign_command("TEST", "param")
        verified = auth2.verify_command(signed)
        
        self.assertIsNone(verified)
    
    def test_malformed_message(self):
        """Test verification of malformed messages."""
        # Too few parts
        self.assertIsNone(self.auth.verify_command("invalid:message"))
        
        # Non-numeric timestamp
        self.assertIsNone(self.auth.verify_command("abc:cmd:param:sig"))
        
        # Empty message
        self.assertIsNone(self.auth.verify_command(""))


if __name__ == '__main__':
    unittest.main()
