"""
Pentest-USB Toolkit - Database Models
====================================

Data models and schema definitions for the
Pentest-USB Toolkit database.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any, Optional


@dataclass
class Project:
    """Project data model"""
    id: str
    name: str
    target: str
    profile: str
    created_at: datetime
    status: str = 'active'


@dataclass
class ScanResult:
    """Scan result data model"""
    id: str
    project_id: str
    module: str
    target: str
    result_data: Dict[str, Any]
    created_at: datetime


class DatabaseModels:
    """Database models manager"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize models"""
        self.db_path = db_path
    
    def create_all_tables(self) -> bool:
        """Create all required tables"""
        # Mock implementation for testing
        return True
    
    def get_table_schema(self) -> Dict[str, List[str]]:
        """Get table schema information"""
        return {
            'projects': ['id', 'name', 'target', 'created_at'],
            'scans': ['id', 'project_id', 'scan_type', 'results'],
            'vulnerabilities': ['id', 'scan_id', 'severity', 'description'],
            'reports': ['id', 'project_id', 'format', 'path']
        }
    
    def create_project(self, name: str, target: str, profile: str) -> Project:
        """Create new project"""
        return Project(
            id=f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=name,
            target=target,
            profile=profile,
            created_at=datetime.now()
        )
    
    def create_scan_result(self, project_id: str, module: str, 
                          target: str, result_data: Dict[str, Any]) -> ScanResult:
        """Create new scan result"""
        return ScanResult(
            id=f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            project_id=project_id,
            module=module,
            target=target,
            result_data=result_data,
            created_at=datetime.now()
        )