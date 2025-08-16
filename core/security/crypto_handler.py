"""
Pentest-USB Toolkit - Crypto Handler
===================================

Cryptographic operations for secure data handling
and encrypted communications.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import hashlib
from cryptography.fernet import Fernet
from typing import Optional

from ..utils.logging_handler import get_logger
from ..utils.error_handler import PentestError


class CryptoHandler:
    """
    Cryptographic operations handler
    """
    
    def __init__(self, key: Optional[bytes] = None):
        """Initialize crypto handler"""
        self.logger = get_logger(__name__)
        
        if key:
            self.fernet = Fernet(key)
        else:
            self.fernet = Fernet(Fernet.generate_key())
        
        self.logger.info("CryptoHandler initialized")
    
    def encrypt_data(self, data: str) -> bytes:
        """Encrypt string data"""
        return self.fernet.encrypt(data.encode())
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt data to string"""
        return self.fernet.decrypt(encrypted_data).decode()
    
    def hash_data(self, data: str, algorithm: str = "sha256") -> str:
        """Hash data using specified algorithm"""
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(data.encode())
        return hash_obj.hexdigest()