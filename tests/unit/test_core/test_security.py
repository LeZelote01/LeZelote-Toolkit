"""
Unit Tests for Security Modules
==============================

Tests for security-related components including
consent management and cryptographic operations.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import os
import sys
import unittest
import tempfile
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.security.consent_manager import ConsentManager
from core.utils.error_handler import PentestError


class TestConsentManager(unittest.TestCase):
    """Test cases for ConsentManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test database
        self.temp_dir = tempfile.mkdtemp()
        self.consent_db_path = os.path.join(self.temp_dir, "test_consent.db")
        
        # Mock dependencies
        self.mock_file_ops = Mock()
        self.mock_logger = Mock()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('core.security.consent_manager.FileOperations')
    @patch('core.security.consent_manager.get_logger')
    def test_consent_manager_initialization(self, mock_get_logger, mock_file_ops_class):
        """Test consent manager initialization"""
        # Arrange
        mock_get_logger.return_value = self.mock_logger
        mock_file_ops_class.return_value = self.mock_file_ops
        
        # Mock file operations
        self.mock_file_ops.load_json.return_value = {
            'consents': {},
            'audit_log': [],
            'created': datetime.now().isoformat()
        }
        
        # Act
        consent_manager = ConsentManager(self.consent_db_path)
        
        # Assert
        self.assertEqual(str(consent_manager.consent_db_path), self.consent_db_path)
        self.mock_file_ops.ensure_directory.assert_called_once()
        mock_get_logger.assert_called_once()
    
    @patch('core.security.consent_manager.FileOperations')
    @patch('core.security.consent_manager.get_logger')
    def test_add_consent_success(self, mock_get_logger, mock_file_ops_class):
        """Test successful consent addition"""
        # Arrange
        mock_get_logger.return_value = self.mock_logger
        mock_file_ops_class.return_value = self.mock_file_ops
        
        # Mock empty consent database
        self.mock_file_ops.load_json.return_value = {
            'consents': {},
            'audit_log': [],
            'created': datetime.now().isoformat()
        }
        
        consent_manager = ConsentManager(self.consent_db_path)
        
        # Test data
        target = "192.168.1.0/24"
        scope = ["reconnaissance", "vulnerability_scanning"]
        authorization_doc = "/path/to/authorization.pdf"
        contact_info = {"name": "John Doe", "email": "john@example.com"}
        
        # Act
        consent_id = consent_manager.add_consent(
            target=target,
            scope=scope,
            authorization_doc=authorization_doc,
            contact_info=contact_info
        )
        
        # Assert
        self.assertIsInstance(consent_id, str)
        self.assertEqual(len(consent_id), 16)  # SHA256 hash truncated to 16 chars
        
        # Verify consent was added
        self.assertIn(consent_id, consent_manager.consents['consents'])
        consent_record = consent_manager.consents['consents'][consent_id]
        
        self.assertEqual(consent_record['target'], target)
        self.assertEqual(consent_record['scope'], scope)
        self.assertEqual(consent_record['authorization_doc'], authorization_doc)
        self.assertEqual(consent_record['contact_info'], contact_info)
        self.assertEqual(consent_record['status'], 'active')
        
        # Verify save was called
        self.mock_file_ops.save_json.assert_called()
    
    @patch('core.security.consent_manager.FileOperations')
    @patch('core.security.consent_manager.get_logger')
    def test_verify_consent_valid(self, mock_get_logger, mock_file_ops_class):
        """Test consent verification with valid consent"""
        # Arrange
        mock_get_logger.return_value = self.mock_logger
        mock_file_ops_class.return_value = self.mock_file_ops
        
        # Mock consent database with valid consent
        target = "example.com"
        consent_record = {
            'consent_id': 'test123',
            'target': target,
            'scope': ['reconnaissance', 'vulnerability_scanning'],
            'authorization_doc': '/path/to/doc.pdf',
            'contact_info': {'name': 'Test User'},
            'created': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=30)).isoformat(),
            'restrictions': [],
            'status': 'active',
            'usage_count': 0,
            'last_used': None
        }
        
        self.mock_file_ops.load_json.return_value = {
            'consents': {'test123': consent_record},
            'audit_log': [],
            'created': datetime.now().isoformat()
        }
        
        consent_manager = ConsentManager(self.consent_db_path)
        
        # Act
        is_valid = consent_manager.verify_consent(target, 'reconnaissance')
        
        # Assert
        self.assertTrue(is_valid)
        
        # Verify usage count was incremented
        updated_record = consent_manager.consents['consents']['test123']
        self.assertEqual(updated_record['usage_count'], 1)
        self.assertIsNotNone(updated_record['last_used'])
    
    @patch('core.security.consent_manager.FileOperations')
    @patch('core.security.consent_manager.get_logger')
    def test_verify_consent_expired(self, mock_get_logger, mock_file_ops_class):
        """Test consent verification with expired consent"""
        # Arrange
        mock_get_logger.return_value = self.mock_logger
        mock_file_ops_class.return_value = self.mock_file_ops
        
        # Mock consent database with expired consent
        target = "example.com"
        consent_record = {
            'consent_id': 'expired123',
            'target': target,
            'scope': ['reconnaissance'],
            'authorization_doc': '/path/to/doc.pdf',
            'contact_info': {'name': 'Test User'},
            'created': (datetime.now() - timedelta(days=60)).isoformat(),
            'valid_until': (datetime.now() - timedelta(days=30)).isoformat(),  # Expired
            'restrictions': [],
            'status': 'active',
            'usage_count': 0,
            'last_used': None
        }
        
        self.mock_file_ops.load_json.return_value = {
            'consents': {'expired123': consent_record},
            'audit_log': [],
            'created': datetime.now().isoformat()
        }
        
        consent_manager = ConsentManager(self.consent_db_path)
        
        # Act
        is_valid = consent_manager.verify_consent(target, 'reconnaissance')
        
        # Assert
        self.assertFalse(is_valid)
    
    @patch('core.security.consent_manager.FileOperations')
    @patch('core.security.consent_manager.get_logger')
    def test_verify_consent_no_match(self, mock_get_logger, mock_file_ops_class):
        """Test consent verification with no matching consent"""
        # Arrange
        mock_get_logger.return_value = self.mock_logger
        mock_file_ops_class.return_value = self.mock_file_ops
        
        # Mock empty consent database
        self.mock_file_ops.load_json.return_value = {
            'consents': {},
            'audit_log': [],
            'created': datetime.now().isoformat()
        }
        
        consent_manager = ConsentManager(self.consent_db_path)
        
        # Act
        is_valid = consent_manager.verify_consent("nonexistent.com", 'reconnaissance')
        
        # Assert
        self.assertFalse(is_valid)
    
    @patch('core.security.consent_manager.FileOperations')
    @patch('core.security.consent_manager.get_logger')
    def test_revoke_consent_success(self, mock_get_logger, mock_file_ops_class):
        """Test successful consent revocation"""
        # Arrange
        mock_get_logger.return_value = self.mock_logger
        mock_file_ops_class.return_value = self.mock_file_ops
        
        consent_record = {
            'consent_id': 'revoke123',
            'target': 'example.com',
            'scope': ['reconnaissance'],
            'authorization_doc': '/path/to/doc.pdf',
            'contact_info': {'name': 'Test User'},
            'created': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=30)).isoformat(),
            'restrictions': [],
            'status': 'active',
            'usage_count': 0,
            'last_used': None
        }
        
        self.mock_file_ops.load_json.return_value = {
            'consents': {'revoke123': consent_record},
            'audit_log': [],
            'created': datetime.now().isoformat()
        }
        
        consent_manager = ConsentManager(self.consent_db_path)
        
        # Act
        result = consent_manager.revoke_consent('revoke123', 'test_revocation')
        
        # Assert
        self.assertTrue(result)
        
        # Verify consent was revoked
        revoked_record = consent_manager.consents['consents']['revoke123']
        self.assertEqual(revoked_record['status'], 'revoked')
        self.assertEqual(revoked_record['revocation_reason'], 'test_revocation')
        self.assertIn('revoked_at', revoked_record)
    
    @patch('core.security.consent_manager.FileOperations')
    @patch('core.security.consent_manager.get_logger')
    def test_target_matching_exact(self, mock_get_logger, mock_file_ops_class):
        """Test exact target matching"""
        # Arrange
        mock_get_logger.return_value = self.mock_logger
        mock_file_ops_class.return_value = self.mock_file_ops
        
        self.mock_file_ops.load_json.return_value = {
            'consents': {},
            'audit_log': [],
            'created': datetime.now().isoformat()
        }
        
        consent_manager = ConsentManager(self.consent_db_path)
        
        # Act & Assert
        self.assertTrue(consent_manager._target_matches('example.com', 'example.com'))
        self.assertFalse(consent_manager._target_matches('example.com', 'other.com'))
    
    @patch('core.security.consent_manager.FileOperations')
    @patch('core.security.consent_manager.get_logger')
    def test_target_matching_wildcard(self, mock_get_logger, mock_file_ops_class):
        """Test wildcard target matching"""
        # Arrange
        mock_get_logger.return_value = self.mock_logger
        mock_file_ops_class.return_value = self.mock_file_ops
        
        self.mock_file_ops.load_json.return_value = {
            'consents': {},
            'audit_log': [],
            'created': datetime.now().isoformat()
        }
        
        consent_manager = ConsentManager(self.consent_db_path)
        
        # Act & Assert
        self.assertTrue(consent_manager._target_matches('*.example.com', 'api.example.com'))
        self.assertTrue(consent_manager._target_matches('*.example.com', 'www.example.com'))
        self.assertFalse(consent_manager._target_matches('*.example.com', 'other.com'))
    
    @patch('core.security.consent_manager.FileOperations')
    @patch('core.security.consent_manager.get_logger')
    def test_list_consents_active_only(self, mock_get_logger, mock_file_ops_class):
        """Test listing only active consents"""
        # Arrange
        mock_get_logger.return_value = self.mock_logger
        mock_file_ops_class.return_value = self.mock_file_ops
        
        active_consent = {
            'consent_id': 'active123',
            'target': 'example.com',
            'scope': ['reconnaissance'],
            'created': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=30)).isoformat(),
            'status': 'active',
            'restrictions': []
        }
        
        revoked_consent = {
            'consent_id': 'revoked123',
            'target': 'other.com',
            'scope': ['reconnaissance'],
            'created': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=30)).isoformat(),
            'status': 'revoked',
            'restrictions': []
        }
        
        self.mock_file_ops.load_json.return_value = {
            'consents': {
                'active123': active_consent,
                'revoked123': revoked_consent
            },
            'audit_log': [],
            'created': datetime.now().isoformat()
        }
        
        consent_manager = ConsentManager(self.consent_db_path)
        
        # Act
        active_consents = consent_manager.list_consents(active_only=True)
        all_consents = consent_manager.list_consents(active_only=False)
        
        # Assert
        self.assertEqual(len(active_consents), 1)
        self.assertEqual(active_consents[0]['consent_id'], 'active123')
        
        self.assertEqual(len(all_consents), 2)
    
    @patch('core.security.consent_manager.FileOperations')
    @patch('core.security.consent_manager.get_logger')
    def test_audit_log_functionality(self, mock_get_logger, mock_file_ops_class):
        """Test audit logging functionality"""
        # Arrange
        mock_get_logger.return_value = self.mock_logger
        mock_file_ops_class.return_value = self.mock_file_ops
        
        self.mock_file_ops.load_json.return_value = {
            'consents': {},
            'audit_log': [],
            'created': datetime.now().isoformat()
        }
        
        consent_manager = ConsentManager(self.consent_db_path)
        
        # Act - Add audit entry indirectly through consent addition
        consent_manager.add_consent(
            target="test.com",
            scope=["reconnaissance"],
            authorization_doc="/path/to/doc.pdf",
            contact_info={"name": "Test User"}
        )
        
        # Get audit log
        audit_log = consent_manager.get_audit_log(limit=10)
        
        # Assert
        self.assertGreater(len(audit_log), 0)
        self.assertIn('consent_added', [entry['action'] for entry in audit_log])


if __name__ == '__main__':
    unittest.main()