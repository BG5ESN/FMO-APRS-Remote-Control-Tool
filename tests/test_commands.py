"""
Unit tests for command handling module.
"""

import unittest
from fmo_aprs import Command, CommandHandler


class TestCommand(unittest.TestCase):
    """Test cases for Command dataclass."""
    
    def test_command_creation(self):
        """Test creating a Command instance."""
        cmd = Command(
            command="TEST",
            parameters="param1",
            timestamp=1234567890,
            age=10,
            source="N0CALL"
        )
        
        self.assertEqual(cmd.command, "TEST")
        self.assertEqual(cmd.parameters, "param1")
        self.assertEqual(cmd.timestamp, 1234567890)
        self.assertEqual(cmd.age, 10)
        self.assertEqual(cmd.source, "N0CALL")
    
    def test_command_str(self):
        """Test string representation of Command."""
        cmd = Command(
            command="STATUS",
            parameters="",
            timestamp=1234567890,
            age=5
        )
        
        str_repr = str(cmd)
        self.assertIn("STATUS", str_repr)
        self.assertIn("5", str_repr)


class TestCommandHandler(unittest.TestCase):
    """Test cases for CommandHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = CommandHandler()
        self.handled_commands = []
    
    def test_register_handler(self):
        """Test registering a command handler."""
        def test_handler(cmd: Command) -> bool:
            return True
        
        self.handler.register("TEST", test_handler)
        commands = self.handler.list_commands()
        
        self.assertIn("TEST", commands)
    
    def test_handle_registered_command(self):
        """Test handling a registered command."""
        def status_handler(cmd: Command) -> bool:
            self.handled_commands.append(cmd)
            return True
        
        self.handler.register("STATUS", status_handler)
        
        cmd = Command(
            command="STATUS",
            parameters="",
            timestamp=1234567890,
            age=5
        )
        
        result = self.handler.handle(cmd)
        
        self.assertTrue(result)
        self.assertEqual(len(self.handled_commands), 1)
        self.assertEqual(self.handled_commands[0].command, "STATUS")
    
    def test_handle_unregistered_command(self):
        """Test handling an unregistered command returns False."""
        cmd = Command(
            command="UNKNOWN",
            parameters="",
            timestamp=1234567890,
            age=5
        )
        
        result = self.handler.handle(cmd)
        self.assertFalse(result)
    
    def test_default_handler(self):
        """Test default handler for unregistered commands."""
        handled = []
        
        def default_handler(cmd: Command) -> bool:
            handled.append(cmd)
            return True
        
        self.handler.set_default_handler(default_handler)
        
        cmd = Command(
            command="ANYTHING",
            parameters="test",
            timestamp=1234567890,
            age=5
        )
        
        result = self.handler.handle(cmd)
        
        self.assertTrue(result)
        self.assertEqual(len(handled), 1)
        self.assertEqual(handled[0].command, "ANYTHING")
    
    def test_handler_exception(self):
        """Test that exceptions in handlers are caught."""
        def failing_handler(cmd: Command) -> bool:
            raise Exception("Handler error")
        
        self.handler.register("FAIL", failing_handler)
        
        cmd = Command(
            command="FAIL",
            parameters="",
            timestamp=1234567890,
            age=5
        )
        
        result = self.handler.handle(cmd)
        self.assertFalse(result)
    
    def test_multiple_handlers(self):
        """Test registering and using multiple handlers."""
        results = {}
        
        def handler1(cmd: Command) -> bool:
            results['cmd1'] = cmd
            return True
        
        def handler2(cmd: Command) -> bool:
            results['cmd2'] = cmd
            return True
        
        self.handler.register("CMD1", handler1)
        self.handler.register("CMD2", handler2)
        
        cmd1 = Command("CMD1", "", 1234567890, 5)
        cmd2 = Command("CMD2", "", 1234567890, 5)
        
        self.handler.handle(cmd1)
        self.handler.handle(cmd2)
        
        self.assertIn('cmd1', results)
        self.assertIn('cmd2', results)
        self.assertEqual(results['cmd1'].command, "CMD1")
        self.assertEqual(results['cmd2'].command, "CMD2")
    
    def test_list_commands(self):
        """Test listing registered commands."""
        def handler1(cmd): return True
        def handler2(cmd): return True
        def handler3(cmd): return True
        
        self.handler.register("CMD1", handler1)
        self.handler.register("CMD2", handler2)
        self.handler.register("CMD3", handler3)
        
        commands = self.handler.list_commands()
        
        self.assertEqual(len(commands), 3)
        self.assertIn("CMD1", commands)
        self.assertIn("CMD2", commands)
        self.assertIn("CMD3", commands)


if __name__ == '__main__':
    unittest.main()
