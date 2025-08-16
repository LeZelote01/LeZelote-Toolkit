"""
Pentest-USB Toolkit - Consent Manager
====================================

Manages authorization, consent verification, and ethical
compliance for penetration testing operations.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..utils.logging_handler import get_logger
from ..utils.error_handler import PentestError
from ..utils.file_ops import FileOperations


class ConsentManager:
    """
    Consent and authorization management system
    """
    
    def __init__(self, consent_db_path: str = "/app/data/databases/consent.db"):
        """
        Initialize consent manager
        
        Args:
            consent_db_path: Path to consent database
        """
        self.consent_db_path = Path(consent_db_path)
        self.logger = get_logger(__name__)
        self.file_ops = FileOperations()
        
        # Ensure consent database directory exists
        self.file_ops.ensure_directory(self.consent_db_path.parent)
        
        # Load existing consents
        self.consents = self._load_consents()
        
        self.logger.info("ConsentManager initialized")
    
    def _load_consents(self) -> Dict[str, Any]:
        """Load existing consent records from database"""
        try:
            if self.consent_db_path.exists():
                return self.file_ops.load_json(self.consent_db_path)
            else:
                return {
                    'consents': {},
                    'audit_log': [],
                    'created': datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.warning(f"Failed to load consent database: {str(e)}")
            return {
                'consents': {},
                'audit_log': [],
                'created': datetime.now().isoformat()
            }
    
    def _save_consents(self):
        """Save consent records to database"""
        try:
            self.file_ops.save_json(self.consent_db_path, self.consents)
        except Exception as e:
            self.logger.error(f"Failed to save consent database: {str(e)}")
            raise PentestError(f"Failed to save consent database: {str(e)}")
    
    def add_consent(self, target: str, scope: List[str], 
                   authorization_doc: str, contact_info: Dict[str, str],
                   valid_until: Optional[datetime] = None,
                   restrictions: Optional[List[str]] = None) -> str:
        """
        Add consent record for a target
        
        Args:
            target: Target identifier (IP, domain, etc.)
            scope: List of authorized test scopes
            authorization_doc: Path to authorization document
            contact_info: Emergency contact information
            valid_until: Consent expiration date
            restrictions: List of restrictions/limitations
            
        Returns:
            Consent ID
        """
        # Generate consent ID
        consent_data = f"{target}{datetime.now().isoformat()}{authorization_doc}"
        consent_id = hashlib.sha256(consent_data.encode()).hexdigest()[:16]
        
        # Default expiration (30 days)
        if valid_until is None:
            valid_until = datetime.now() + timedelta(days=30)
        
        consent_record = {
            'consent_id': consent_id,
            'target': target,
            'scope': scope,
            'authorization_doc': authorization_doc,
            'contact_info': contact_info,
            'created': datetime.now().isoformat(),
            'valid_until': valid_until.isoformat() if isinstance(valid_until, datetime) else valid_until,
            'restrictions': restrictions or [],
            'status': 'active',
            'usage_count': 0,
            'last_used': None
        }
        
        # Store consent
        self.consents['consents'][consent_id] = consent_record
        
        # Add to audit log
        self._log_audit('consent_added', {
            'consent_id': consent_id,
            'target': target,
            'scope': scope
        })
        
        # Save to database
        self._save_consents()
        
        self.logger.info(f"Consent added for target {target} (ID: {consent_id})")
        return consent_id
    
    def verify_consent(self, target: str, test_scope: Optional[str] = None) -> bool:
        """
        Verify if consent exists for target and scope
        
        Args:
            target: Target to verify consent for
            test_scope: Specific test scope to verify
            
        Returns:
            bool: True if consent is valid
        """
        try:
            # Find matching consent
            matching_consents = []
            
            for consent_record in self.consents['consents'].values():
                if self._target_matches(consent_record['target'], target):
                    if consent_record['status'] == 'active':
                        if self._is_consent_valid(consent_record):
                            if test_scope is None or test_scope in consent_record['scope']:
                                matching_consents.append(consent_record)
            
            if not matching_consents:
                self.logger.warning(f"No valid consent found for target: {target}")
                self._log_audit('consent_verification_failed', {
                    'target': target,
                    'test_scope': test_scope,
                    'reason': 'no_valid_consent'
                })
                return False
            
            # Use the most recent valid consent
            latest_consent = max(matching_consents, key=lambda x: x['created'])
            
            # Update usage statistics
            latest_consent['usage_count'] += 1
            latest_consent['last_used'] = datetime.now().isoformat()
            
            # Log successful verification
            self._log_audit('consent_verified', {
                'consent_id': latest_consent['consent_id'],
                'target': target,
                'test_scope': test_scope
            })
            
            # Save updated statistics
            self._save_consents()
            
            self.logger.info(f"Consent verified for target {target} (ID: {latest_consent['consent_id']})")
            return True
            
        except Exception as e:
            self.logger.error(f"Consent verification failed: {str(e)}")
            self._log_audit('consent_verification_error', {
                'target': target,
                'error': str(e)
            })
            return False
    
    def _target_matches(self, consent_target: str, actual_target: str) -> bool:
        """Check if actual target matches consent target pattern"""
        # Exact match
        if consent_target == actual_target:
            return True
        
        # Wildcard domain matching (*.example.com)
        if consent_target.startswith('*.'):
            domain_pattern = consent_target[2:]  # Remove *.
            if actual_target.endswith(domain_pattern):
                return True
        
        # CIDR network matching would require additional logic
        # For now, implement exact matching
        
        return False
    
    def _is_consent_valid(self, consent_record: Dict[str, Any]) -> bool:
        """Check if consent record is still valid"""
        # Check expiration
        valid_until = datetime.fromisoformat(consent_record['valid_until'])
        if datetime.now() > valid_until:
            return False
        
        # Check status
        if consent_record['status'] != 'active':
            return False
        
        return True
    
    def revoke_consent(self, consent_id: str, reason: str = "manual_revocation") -> bool:
        """
        Revoke an existing consent
        
        Args:
            consent_id: ID of consent to revoke
            reason: Reason for revocation
            
        Returns:
            bool: True if successfully revoked
        """
        try:
            if consent_id not in self.consents['consents']:
                return False
            
            consent_record = self.consents['consents'][consent_id]
            consent_record['status'] = 'revoked'
            consent_record['revoked_at'] = datetime.now().isoformat()
            consent_record['revocation_reason'] = reason
            
            # Log revocation
            self._log_audit('consent_revoked', {
                'consent_id': consent_id,
                'target': consent_record['target'],
                'reason': reason
            })
            
            # Save changes
            self._save_consents()
            
            self.logger.info(f"Consent revoked: {consent_id} (reason: {reason})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke consent {consent_id}: {str(e)}")
            return False
    
    def list_consents(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        List all consent records
        
        Args:
            active_only: Whether to return only active consents
            
        Returns:
            List of consent records
        """
        consents = list(self.consents['consents'].values())
        
        if active_only:
            consents = [c for c in consents if c['status'] == 'active' and self._is_consent_valid(c)]
        
        # Sort by creation date (newest first)
        consents.sort(key=lambda x: x['created'], reverse=True)
        
        return consents
    
    def get_consent_details(self, consent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific consent
        
        Args:
            consent_id: Consent ID to look up
            
        Returns:
            Consent record or None if not found
        """
        return self.consents['consents'].get(consent_id)
    
    def check_restrictions(self, consent_id: str, proposed_action: str) -> bool:
        """
        Check if proposed action violates consent restrictions
        
        Args:
            consent_id: Consent ID to check
            proposed_action: Action to validate
            
        Returns:
            bool: True if action is allowed
        """
        consent_record = self.get_consent_details(consent_id)
        if not consent_record:
            return False
        
        restrictions = consent_record.get('restrictions', [])
        
        # Check against restrictions
        for restriction in restrictions:
            if restriction.lower() in proposed_action.lower():
                self.logger.warning(f"Action '{proposed_action}' violates restriction: {restriction}")
                return False
        
        return True
    
    def _log_audit(self, action: str, details: Dict[str, Any]):
        """Add entry to audit log"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details,
            'user': os.getenv('USER', 'unknown'),
            'hostname': os.getenv('HOSTNAME', 'unknown')
        }
        
        self.consents['audit_log'].append(audit_entry)
        
        # Keep only last 1000 audit entries
        if len(self.consents['audit_log']) > 1000:
            self.consents['audit_log'] = self.consents['audit_log'][-1000:]
    
    def get_audit_log(self, limit: Optional[int] = 100) -> List[Dict[str, Any]]:
        """
        Get audit log entries
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of audit log entries
        """
        audit_log = self.consents.get('audit_log', [])
        
        if limit:
            return audit_log[-limit:]
        
        return audit_log
    
    def export_consent_report(self, output_path: str) -> bool:
        """
        Export consent report for compliance
        
        Args:
            output_path: Path to save report
            
        Returns:
            bool: True if successful
        """
        try:
            report = {
                'generated': datetime.now().isoformat(),
                'active_consents': len([c for c in self.consents['consents'].values() 
                                      if c['status'] == 'active' and self._is_consent_valid(c)]),
                'total_consents': len(self.consents['consents']),
                'audit_entries': len(self.consents['audit_log']),
                'consents': self.list_consents(active_only=False),
                'recent_audit_log': self.get_audit_log(50)
            }
            
            self.file_ops.save_json(output_path, report)
            
            self.logger.info(f"Consent report exported to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export consent report: {str(e)}")
            return False
    
    def validate_engagement_scope(self, targets: List[str], test_types: List[str]) -> Dict[str, bool]:
        """
        Validate entire engagement scope against consents
        
        Args:
            targets: List of target identifiers
            test_types: List of test types to perform
            
        Returns:
            Dict mapping targets to validation results
        """
        results = {}
        
        for target in targets:
            target_valid = True
            
            # Check if consent exists for target
            if not self.verify_consent(target):
                target_valid = False
            
            # Check each test type
            for test_type in test_types:
                if not self.verify_consent(target, test_type):
                    target_valid = False
                    break
            
            results[target] = target_valid
        
        # Log validation results
        self._log_audit('engagement_scope_validated', {
            'targets': targets,
            'test_types': test_types,
            'results': results
        })
        
        return results