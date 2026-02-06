"""
APRS-IS Client Implementation

Handles connection and communication with APRS-IS servers.
"""

import socket
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class APRSClient:
    """APRS-IS client for sending and receiving messages."""
    
    DEFAULT_SERVER = "rotate.aprs2.net"
    DEFAULT_PORT = 14580
    
    def __init__(self, callsign: str, passcode: str, 
                 server: str = DEFAULT_SERVER, port: int = DEFAULT_PORT):
        """
        Initialize APRS-IS client.
        
        Args:
            callsign: Your amateur radio callsign
            passcode: APRS-IS passcode for your callsign
            server: APRS-IS server hostname
            port: APRS-IS server port
        """
        self.callsign = callsign.upper()
        self.passcode = passcode
        self.server = server
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        
    def connect(self) -> bool:
        """
        Connect to APRS-IS server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((self.server, self.port))
            
            # Read server banner
            banner = self.socket.recv(1024).decode('utf-8', errors='ignore')
            logger.info(f"Server banner: {banner.strip()}")
            
            # Send login
            login_string = f"user {self.callsign} pass {self.passcode} vers FMO-APRS 0.1.0\r\n"
            self.socket.sendall(login_string.encode('utf-8'))
            
            # Read login response
            response = self.socket.recv(1024).decode('utf-8', errors='ignore')
            logger.info(f"Login response: {response.strip()}")
            
            if "verified" in response.lower():
                self.connected = True
                logger.info(f"Successfully connected as {self.callsign}")
                return True
            else:
                logger.warning(f"Login not verified: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from APRS-IS server."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.connected = False
        logger.info("Disconnected from APRS-IS")
    
    def send_message(self, destination: str, message: str) -> bool:
        """
        Send a message to a destination callsign.
        
        Args:
            destination: Destination callsign
            message: Message content
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.connected or not self.socket:
            logger.error("Not connected to APRS-IS")
            return False
        
        try:
            # Format APRS message packet
            # Format: SOURCE>APRS,TCPIP*::DESTINATION:message
            destination_padded = destination.ljust(9)
            packet = f"{self.callsign}>APRS,TCPIP*::{destination_padded}:{message}\r\n"
            
            self.socket.sendall(packet.encode('utf-8'))
            logger.info(f"Sent message to {destination}: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def receive_messages(self, callback: Callable[[dict], None], timeout: int = 300):
        """
        Receive messages from APRS-IS.
        
        Args:
            callback: Function to call for each received message
            timeout: Timeout in seconds (0 for infinite)
        """
        if not self.connected or not self.socket:
            logger.error("Not connected to APRS-IS")
            return
        
        self.socket.settimeout(timeout if timeout > 0 else None)
        buffer = ""
        
        try:
            while True:
                try:
                    data = self.socket.recv(4096).decode('utf-8', errors='ignore')
                    if not data:
                        logger.warning("Connection closed by server")
                        break
                    
                    buffer += data
                    
                    # Process complete lines
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        
                        if not line or line.startswith('#'):
                            continue
                        
                        # Parse APRS packet
                        parsed = self._parse_packet(line)
                        if parsed:
                            callback(parsed)
                            
                except socket.timeout:
                    logger.debug("Receive timeout")
                    continue
                    
        except KeyboardInterrupt:
            logger.info("Receive interrupted by user")
        except Exception as e:
            logger.error(f"Receive error: {e}")
        finally:
            self.disconnect()
    
    def _parse_packet(self, packet: str) -> Optional[dict]:
        """
        Parse APRS packet.
        
        Args:
            packet: Raw APRS packet string
            
        Returns:
            Dictionary with parsed packet data or None
        """
        try:
            # Basic packet format: SOURCE>DEST,PATH:DATA
            if '>' not in packet or ':' not in packet:
                return None
            
            header, data = packet.split(':', 1)
            source = header.split('>')[0]
            
            # Check if it's a message (:CALLSIGN :message)
            if data.startswith(':'):
                parts = data[1:].split(':', 1)
                if len(parts) == 2:
                    destination = parts[0].strip()
                    message = parts[1]
                    
                    return {
                        'type': 'message',
                        'from': source,
                        'to': destination,
                        'message': message,
                        'raw': packet
                    }
            
            return {
                'type': 'other',
                'from': source,
                'data': data,
                'raw': packet
            }
            
        except Exception as e:
            logger.debug(f"Failed to parse packet: {e}")
            return None
