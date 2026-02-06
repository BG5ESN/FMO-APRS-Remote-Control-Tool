"""
Command Handling Framework

Defines command structure and handling for FMO remote control.
"""

import logging
from typing import Optional, Callable, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Command:
    """Represents a parsed and verified command."""
    
    command: str
    parameters: str
    timestamp: int
    age: int
    source: Optional[str] = None
    
    def __str__(self):
        return f"Command({self.command}, params={self.parameters}, age={self.age}s)"


class CommandHandler:
    """
    Handler for processing verified commands.
    
    Allows registration of command handlers and dispatching commands
    to appropriate handlers.
    """
    
    def __init__(self):
        """Initialize command handler."""
        self.handlers: Dict[str, Callable[[Command], bool]] = {}
        self.default_handler: Optional[Callable[[Command], bool]] = None
    
    def register(self, command_name: str, handler: Callable[[Command], bool]):
        """
        Register a handler for a specific command.
        
        Args:
            command_name: Name of the command
            handler: Function to handle the command (returns True on success)
        """
        self.handlers[command_name] = handler
        logger.info(f"Registered handler for command: {command_name}")
    
    def set_default_handler(self, handler: Callable[[Command], bool]):
        """
        Set a default handler for unrecognized commands.
        
        Args:
            handler: Function to handle unknown commands
        """
        self.default_handler = handler
        logger.info("Set default command handler")
    
    def handle(self, command: Command) -> bool:
        """
        Dispatch a command to its handler.
        
        Args:
            command: Command to handle
            
        Returns:
            True if command was handled successfully, False otherwise
        """
        handler = self.handlers.get(command.command)
        
        if handler:
            try:
                logger.info(f"Handling command: {command}")
                return handler(command)
            except Exception as e:
                logger.error(f"Error handling command {command.command}: {e}")
                return False
        elif self.default_handler:
            try:
                logger.info(f"Handling command with default handler: {command}")
                return self.default_handler(command)
            except Exception as e:
                logger.error(f"Error in default handler for {command.command}: {e}")
                return False
        else:
            logger.warning(f"No handler for command: {command.command}")
            return False
    
    def list_commands(self) -> list:
        """
        Get list of registered command names.
        
        Returns:
            List of command names
        """
        return list(self.handlers.keys())
