#!/usr/bin/env python3
"""
Setup test consent data for LeZelote-Toolkit testing
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.security.consent_manager import ConsentManager

def setup_test_consents():
    """Setup test consent data for testing"""
    print("Setting up test consent data...")
    
    consent_manager = ConsentManager()
    
    # Add test consents for common test targets
    test_targets = [
        "192.168.1.100",
        "example.com", 
        "testsite.local",
        "integration-test.local",
        "*.local",  # Wildcard for all .local domains
        "192.168.1.0/24"  # Network range
    ]
    
    for target in test_targets:
        consent_id = consent_manager.add_consent(
            target=target,
            scope=["reconnaissance", "vulnerability", "web_scan", "network_scan", "reporting"],
            authorization_doc="/app/test_authorization.txt",
            contact_info={
                "name": "Test Administrator",
                "email": "test@example.com",
                "phone": "+1-555-0123"
            },
            valid_until=datetime.now() + timedelta(days=365),  # Valid for 1 year
            restrictions=[]
        )
        print(f"✅ Added consent for {target} (ID: {consent_id})")
    
    print("✅ Test consent data setup complete!")
    return True

if __name__ == "__main__":
    setup_test_consents()