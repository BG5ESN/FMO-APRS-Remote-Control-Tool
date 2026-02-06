"""
Unit tests for APRS client module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from fmo_aprs import APRSClient


class TestAPRSClient(unittest.TestCase):
    """Test cases for APRSClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APRSClient("N0CALL", "12345")
    
    def test_initialization(self):
        """Test client initialization."""
        self.assertEqual(self.client.callsign, "N0CALL")
        self.assertEqual(self.client.passcode, "12345")
        self.assertEqual(self.client.server, APRSClient.DEFAULT_SERVER)
        self.assertEqual(self.client.port, APRSClient.DEFAULT_PORT)
        self.assertFalse(self.client.connected)
    
    def test_initialization_custom_server(self):
        """Test client initialization with custom server."""
        client = APRSClient("N0CALL", "12345", "custom.server.net", 14501)
        self.assertEqual(client.server, "custom.server.net")
        self.assertEqual(client.port, 14501)
    
    def test_callsign_uppercase(self):
        """Test that callsign is converted to uppercase."""
        client = APRSClient("n0call", "12345")
        self.assertEqual(client.callsign, "N0CALL")
    
    def test_parse_message_packet(self):
        """Test parsing APRS message packets."""
        packet = "N0CALL>APRS,TCPIP*::FMO-1    :test message"
        parsed = self.client._parse_packet(packet)
        
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['type'], 'message')
        self.assertEqual(parsed['from'], 'N0CALL')
        self.assertEqual(parsed['to'], 'FMO-1')
        self.assertEqual(parsed['message'], 'test message')
    
    def test_parse_non_message_packet(self):
        """Test parsing non-message APRS packets."""
        packet = "N0CALL>APRS,TCPIP*:!1234.56N/12345.67W-Test"
        parsed = self.client._parse_packet(packet)
        
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['type'], 'other')
        self.assertEqual(parsed['from'], 'N0CALL')
    
    def test_parse_invalid_packet(self):
        """Test parsing invalid packets."""
        # No '>' character
        self.assertIsNone(self.client._parse_packet("INVALID"))
        
        # No ':' character
        self.assertIsNone(self.client._parse_packet("N0CALL>APRS"))
    
    def test_disconnect(self):
        """Test disconnection."""
        self.client.socket = Mock()
        self.client.connected = True
        
        self.client.disconnect()
        
        self.assertFalse(self.client.connected)
        self.assertIsNone(self.client.socket)
    
    @patch('socket.socket')
    def test_send_message_format(self, mock_socket):
        """Test message formatting."""
        # Setup mock socket
        mock_sock = Mock()
        self.client.socket = mock_sock
        self.client.connected = True
        
        # Send message
        self.client.send_message("FMO-1", "test message")
        
        # Verify packet format
        mock_sock.sendall.assert_called_once()
        sent_data = mock_sock.sendall.call_args[0][0].decode('utf-8')
        
        # Should contain padded destination
        self.assertIn("FMO-1    ", sent_data)  # Padded to 9 chars
        self.assertIn("test message", sent_data)
        self.assertTrue(sent_data.startswith("N0CALL>APRS,TCPIP*::"))
        self.assertTrue(sent_data.endswith("\r\n"))
    
    def test_send_message_not_connected(self):
        """Test sending message when not connected."""
        result = self.client.send_message("FMO-1", "test")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
