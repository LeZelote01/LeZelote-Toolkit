"""
Pentest-USB Toolkit - Security Module
====================================

Security and stealth components for covert operations,
evasion tactics, consent management and cryptography.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

__version__ = "1.0.0"

from .stealth_engine import StealthEngine
from .evasion_tactics import EvasionTactics
from .consent_manager import ConsentManager
from .crypto_handler import CryptoHandler

__all__ = [
    'StealthEngine',
    'EvasionTactics',
    'ConsentManager',
    'CryptoHandler'
]