"""
FMO-APRS-Remote-Control-Tool

An open-source library for remote control of FMO via APRS-IS network relay.
Uses HMAC signing for command authentication and validation.
"""

__version__ = "0.1.0"
__author__ = "BG5ESN"

from .client import APRSClient
from .auth import HMACAuth
from .commands import Command, CommandHandler

__all__ = ["APRSClient", "HMACAuth", "Command", "CommandHandler"]
