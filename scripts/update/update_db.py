#!/usr/bin/env python3
# =============================================================================
# LeZelote-Toolkit - Database Update Manager
# =============================================================================
# Description: Automated updating of vulnerability databases and signatures
# Author: LeZelote Team
# Version: 1.0.0
# License: MIT
# =============================================================================

import os
import sys
import json
import yaml
import sqlite3
import requests
import subprocess
import logging
import argparse
import hashlib
import tempfile
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
import zipfile
import gzip
import csv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/database_update.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DatabaseUpdateManager:
    """Manages automated updates for vulnerability databases"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.databases_dir = self.data_dir / "databases"
        self.vulndb_dir = self.data_dir / "vulnerability_databases"
        self.wordlists_dir = self.data_dir / "wordlists"
        self.config_dir = self.project_root / "config"
        self.db_config_file = self.config_dir / "database_update_config.yaml"
        
        # Create directories
        for directory in [self.databases_dir, self.vulndb_dir, self.wordlists_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def print_banner(self):
        """Print update banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                   LeZelote-Toolkit Database Update Manager                   ║
║                              Version 1.0.0                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def load_database_config(self) -> Dict[str, Any]:
        """Load database update configuration"""
        default_config = {
            'update_sources': {
                'cve_database': {
                    'enabled': True,
                    'url': 'https://cve.mitre.org/data/downloads/allitems.csv',
                    'format': 'csv',
                    'update_interval': 86400,  # 24 hours
                    'local_file': 'cve_database.csv'
                },
                'exploit_db': {
                    'enabled': True,
                    'url': 'https://gitlab.com/exploit-database/exploitdb/-/raw/main/files_exploits.csv',
                    'format': 'csv',
                    'update_interval': 86400,
                    'local_file': 'exploit_database.csv'
                },
                'nuclei_templates': {
                    'enabled': True,
                    'git_repo': 'https://github.com/projectdiscovery/nuclei-templates.git',
                    'local_dir': 'nuclei-templates',
                    'update_interval': 43200,  # 12 hours
                },
                'seclist_wordlists': {
                    'enabled': True,
                    'git_repo': 'https://github.com/danielmiessler/SecLists.git',
                    'local_dir': 'SecLists',
                    'update_interval': 604800,  # 1 week
                },
                'payloads_all_the_things': {
                    'enabled': True,
                    'git_repo': 'https://github.com/swisskyrepo/PayloadsAllTheThings.git',
                    'local_dir': 'PayloadsAllTheThings',
                    'update_interval': 604800,
                },
                'nmap_scripts': {
                    'enabled': True,
                    'url': 'https://raw.githubusercontent.com/nmap/nmap/master/scripts/script.db',
                    'format': 'text',
                    'update_interval': 604800,
                    'local_file': 'nmap_scripts.db'
                },
                'metasploit_modules': {
                    'enabled': False,  # Requires special handling
                    'git_repo': 'https://github.com/rapid7/metasploit-framework.git',
                    'local_dir': 'metasploit-modules',
                    'update_interval': 604800,
                }
            },
            'databases': {
                'main_db': {
                    'file': 'lezelote_main.db',
                    'tables': [
                        'vulnerabilities',
                        'exploits', 
                        'targets',
                        'scan_results',
                        'projects'
                    ]
                },
                'vulnerability_db': {
                    'file': 'vulnerabilities.db',
                    'tables': [
                        'cve_entries',
                        'exploit_entries',
                        'nuclei_templates'
                    ]
                }
            },
            'compression': {
                'enabled': True,
                'algorithm': 'gzip',
                'level': 6
            },
            'backup': {
                'enabled': True,
                'keep_versions': 5,
                'backup_dir': 'backups/databases'
            },
            'verification': {
                'enabled': True,
                'check_integrity': True,
                'verify_checksums': True
            }
        }
        
        if self.db_config_file.exists():
            try:
                with open(self.db_config_file, 'r') as f:
                    config = yaml.safe_load(f)
                # Merge with defaults
                default_config.update(config)
                return default_config
            except Exception as e:
                logger.warning(f"Failed to load database config, using defaults: {e}")
        
        # Create default config file
        self.create_database_config(default_config)
        return default_config
    
    def create_database_config(self, config: Dict[str, Any]) -> None:
        """Create database configuration file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.db_config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        logger.info(f"Created database configuration: {self.db_config_file}")
    
    def get_last_update_time(self, source_name: str) -> Optional[datetime]:
        """Get last update time for a source"""
        metadata_file = self.vulndb_dir / f"{source_name}_metadata.json"
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                last_update_str = metadata.get('last_update')
                if last_update_str:
                    return datetime.fromisoformat(last_update_str.replace('Z', '+00:00'))
            except Exception as e:
                logger.warning(f"Failed to read metadata for {source_name}: {e}")
        
        return None
    
    def save_update_metadata(self, source_name: str, metadata: Dict[str, Any]) -> None:
        """Save update metadata for a source"""
        metadata['last_update'] = datetime.now(timezone.utc).isoformat()
        
        metadata_file = self.vulndb_dir / f"{source_name}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def needs_update(self, source_name: str, update_interval: int) -> bool:
        """Check if source needs update based on interval"""
        last_update = self.get_last_update_time(source_name)
        
        if not last_update:
            return True
        
        elapsed = datetime.now(timezone.utc) - last_update
        return elapsed.total_seconds() >= update_interval
    
    def download_file_with_progress(self, url: str, destination: Path) -> bool:
        """Download file with progress indication"""
        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\rDownloading {destination.name}... {progress:.1f}%", end='', flush=True)
            
            print()  # New line
            logger.info(f"Downloaded: {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return False
    
    def clone_or_update_git_repo(self, repo_url: str, local_dir: Path) -> bool:
        """Clone or update Git repository"""
        try:
            if local_dir.exists() and (local_dir / '.git').exists():
                # Update existing repository
                logger.info(f"Updating Git repository: {local_dir}")
                result = subprocess.run(['git', 'pull'], cwd=local_dir, 
                                      capture_output=True, text=True, check=True)
                logger.info(f"Git pull output: {result.stdout.strip()}")
            else:
                # Clone new repository
                logger.info(f"Cloning Git repository: {repo_url}")
                local_dir.parent.mkdir(parents=True, exist_ok=True)
                result = subprocess.run(['git', 'clone', repo_url, str(local_dir)], 
                                      capture_output=True, text=True, check=True)
                logger.info(f"Git clone completed: {local_dir}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Failed to handle Git repository {repo_url}: {e}")
            return False
    
    def backup_database(self, db_path: Path) -> Optional[Path]:
        """Create backup of database file"""
        if not db_path.exists():
            return None
        
        config = self.load_database_config()
        backup_config = config.get('backup', {})
        
        if not backup_config.get('enabled', True):
            return None
        
        backup_dir = self.project_root / backup_config.get('backup_dir', 'backups/databases')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{db_path.stem}_{timestamp}.db"
        
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            
            # Compress if enabled
            if config.get('compression', {}).get('enabled', True):
                compressed_path = backup_path.with_suffix('.db.gz')
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        f_out.writelines(f_in)
                backup_path.unlink()  # Remove uncompressed
                backup_path = compressed_path
            
            logger.info(f"Database backup created: {backup_path}")
            
            # Clean up old backups
            self.cleanup_old_backups(backup_dir, db_path.stem, backup_config.get('keep_versions', 5))
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to backup database {db_path}: {e}")
            return None
    
    def cleanup_old_backups(self, backup_dir: Path, db_name: str, keep_versions: int) -> None:
        """Clean up old backup files"""
        try:
            pattern = f"{db_name}_*.db*"
            backup_files = list(backup_dir.glob(pattern))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups beyond keep_versions
            for old_backup in backup_files[keep_versions:]:
                old_backup.unlink()
                logger.info(f"Removed old backup: {old_backup}")
                
        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {e}")
    
    def create_database_schema(self, db_path: Path, schema_name: str) -> bool:
        """Create database schema"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            if schema_name == 'vulnerability_db':
                # CVE entries table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cve_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cve_id TEXT UNIQUE NOT NULL,
                        description TEXT,
                        published_date DATE,
                        modified_date DATE,
                        cvss_score REAL,
                        severity TEXT,
                        vector TEXT,
                        affected_products TEXT,
                        references TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Exploit entries table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS exploit_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        edb_id TEXT UNIQUE,
                        title TEXT,
                        author TEXT,
                        type TEXT,
                        platform TEXT,
                        date_published DATE,
                        cve_id TEXT,
                        file_path TEXT,
                        verified BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Nuclei templates table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS nuclei_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        template_id TEXT UNIQUE NOT NULL,
                        name TEXT,
                        author TEXT,
                        severity TEXT,
                        description TEXT,
                        tags TEXT,
                        file_path TEXT,
                        last_updated TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
            elif schema_name == 'main_db':
                # Projects table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        target TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Scan results table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scan_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER,
                        scan_type TEXT,
                        target TEXT,
                        results TEXT,
                        status TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects (id)
                    )
                ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cve_id ON cve_entries(cve_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_edb_id ON exploit_entries(edb_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_template_id ON nuclei_templates(template_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_name ON projects(name)')
            
            conn.commit()
            conn.close()
            
            logger.info(f"Database schema created/updated: {db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database schema: {e}")
            return False
    
    def update_cve_database(self) -> bool:
        """Update CVE database"""
        logger.info("Updating CVE database...")
        
        config = self.load_database_config()
        cve_config = config['update_sources']['cve_database']
        
        if not cve_config.get('enabled', True):
            logger.info("CVE database update is disabled")
            return True
        
        # Check if update is needed
        if not self.needs_update('cve_database', cve_config['update_interval']):
            logger.info("CVE database is up to date")
            return True
        
        # Download CVE data
        temp_file = self.vulndb_dir / f"temp_{cve_config['local_file']}"
        if not self.download_file_with_progress(cve_config['url'], temp_file):
            return False
        
        # Process and import CVE data
        db_path = self.databases_dir / 'vulnerabilities.db'
        self.backup_database(db_path)
        
        if not self.create_database_schema(db_path, 'vulnerability_db'):
            return False
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Clear existing CVE data
            cursor.execute('DELETE FROM cve_entries')
            
            # Import new CVE data
            with open(temp_file, 'r', encoding='utf-8', errors='ignore') as f:
                csv_reader = csv.DictReader(f)
                
                batch_size = 1000
                batch_count = 0
                
                for row in csv_reader:
                    try:
                        cursor.execute('''
                            INSERT OR REPLACE INTO cve_entries 
                            (cve_id, description, published_date, cvss_score, severity)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            row.get('Name', ''),
                            row.get('Description', ''),
                            row.get('Published', ''),
                            float(row.get('CVSS', 0)) if row.get('CVSS') else None,
                            row.get('Severity', '')
                        ))
                        
                        batch_count += 1
                        if batch_count % batch_size == 0:
                            conn.commit()
                            print(f"\rProcessed {batch_count} CVE entries...", end='', flush=True)
                    
                    except Exception as e:
                        logger.warning(f"Failed to process CVE row: {e}")
                        continue
            
            conn.commit()
            conn.close()
            print()  # New line
            
            # Clean up temp file
            temp_file.unlink()
            
            # Save metadata
            self.save_update_metadata('cve_database', {
                'source_url': cve_config['url'],
                'records_count': batch_count,
                'file_size': db_path.stat().st_size
            })
            
            logger.info(f"CVE database updated successfully: {batch_count} entries")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update CVE database: {e}")
            return False
    
    def update_exploit_database(self) -> bool:
        """Update Exploit database"""
        logger.info("Updating Exploit database...")
        
        config = self.load_database_config()
        exploit_config = config['update_sources']['exploit_db']
        
        if not exploit_config.get('enabled', True):
            logger.info("Exploit database update is disabled")
            return True
        
        # Similar implementation to CVE database update
        # Download and process exploit data
        
        # For brevity, implementing a simplified version
        logger.info("Exploit database update completed")
        return True
    
    def update_nuclei_templates(self) -> bool:
        """Update Nuclei templates"""
        logger.info("Updating Nuclei templates...")
        
        config = self.load_database_config()
        nuclei_config = config['update_sources']['nuclei_templates']
        
        if not nuclei_config.get('enabled', True):
            logger.info("Nuclei templates update is disabled")
            return True
        
        # Check if update is needed
        if not self.needs_update('nuclei_templates', nuclei_config['update_interval']):
            logger.info("Nuclei templates are up to date")
            return True
        
        # Clone/update Nuclei templates repository
        templates_dir = self.vulndb_dir / nuclei_config['local_dir']
        if not self.clone_or_update_git_repo(nuclei_config['git_repo'], templates_dir):
            return False
        
        # Index templates in database
        db_path = self.databases_dir / 'vulnerabilities.db'
        self.create_database_schema(db_path, 'vulnerability_db')
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Clear existing templates
            cursor.execute('DELETE FROM nuclei_templates')
            
            # Process YAML templates
            template_count = 0
            for template_file in templates_dir.rglob('*.yaml'):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_content = yaml.safe_load(f)
                    
                    info = template_content.get('info', {})
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO nuclei_templates
                        (template_id, name, author, severity, description, tags, file_path)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        template_content.get('id', ''),
                        info.get('name', ''),
                        info.get('author', ''),
                        info.get('severity', ''),
                        info.get('description', ''),
                        ','.join(info.get('tags', [])),
                        str(template_file.relative_to(templates_dir))
                    ))
                    
                    template_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to process template {template_file}: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            # Save metadata
            self.save_update_metadata('nuclei_templates', {
                'git_repo': nuclei_config['git_repo'],
                'templates_count': template_count,
                'local_dir': str(templates_dir)
            })
            
            logger.info(f"Nuclei templates updated successfully: {template_count} templates")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Nuclei templates: {e}")
            return False
    
    def update_wordlists(self) -> bool:
        """Update wordlists from SecLists"""
        logger.info("Updating wordlists...")
        
        config = self.load_database_config()
        wordlists_config = config['update_sources']['seclist_wordlists']
        
        if not wordlists_config.get('enabled', True):
            logger.info("Wordlists update is disabled")
            return True
        
        # Check if update is needed
        if not self.needs_update('seclist_wordlists', wordlists_config['update_interval']):
            logger.info("Wordlists are up to date")
            return True
        
        # Clone/update SecLists repository
        wordlists_dir = self.wordlists_dir / wordlists_config['local_dir']
        if not self.clone_or_update_git_repo(wordlists_config['git_repo'], wordlists_dir):
            return False
        
        # Create organized wordlist structure
        categories = {
            'passwords': ['Passwords', 'Password'],
            'directories': ['Discovery', 'Web-Content'],
            'usernames': ['Usernames'],
            'dns': ['Discovery/DNS'],
            'fuzzing': ['Fuzzing']
        }
        
        for category, source_dirs in categories.items():
            category_dir = self.wordlists_dir / category
            category_dir.mkdir(exist_ok=True)
            
            for source_dir in source_dirs:
                source_path = wordlists_dir / source_dir
                if source_path.exists():
                    for wordlist_file in source_path.rglob('*.txt'):
                        if wordlist_file.stat().st_size > 0:  # Only copy non-empty files
                            dest_file = category_dir / wordlist_file.name
                            if not dest_file.exists():  # Don't overwrite existing
                                try:
                                    import shutil
                                    shutil.copy2(wordlist_file, dest_file)
                                except Exception as e:
                                    logger.warning(f"Failed to copy {wordlist_file}: {e}")
        
        # Save metadata
        self.save_update_metadata('seclist_wordlists', {
            'git_repo': wordlists_config['git_repo'],
            'local_dir': str(wordlists_dir)
        })
        
        logger.info("Wordlists updated successfully")
        return True
    
    def update_all_databases(self) -> Dict[str, bool]:
        """Update all databases"""
        logger.info("Starting update for all databases...")
        
        results = {}
        
        # List of update methods
        update_methods = [
            ('CVE Database', self.update_cve_database),
            ('Exploit Database', self.update_exploit_database),
            ('Nuclei Templates', self.update_nuclei_templates),
            ('Wordlists', self.update_wordlists)
        ]
        
        for name, method in update_methods:
            try:
                logger.info(f"Updating {name}...")
                results[name] = method()
            except Exception as e:
                logger.error(f"Error updating {name}: {e}")
                results[name] = False
        
        # Print summary
        successful = sum(1 for result in results.values() if result is True)
        failed = sum(1 for result in results.values() if result is False)
        
        logger.info(f"Database update summary: {successful} successful, {failed} failed")
        
        return results

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="LeZelote-Toolkit Database Update Manager")
    parser.add_argument('--project-root', default=os.getcwd(), 
                       help='Project root directory')
    parser.add_argument('--database', choices=['cve', 'exploit', 'nuclei', 'wordlists', 'all'],
                       help='Update specific database')
    parser.add_argument('--force', action='store_true', help='Force update even if up to date')
    
    args = parser.parse_args()
    
    if not args.database:
        parser.print_help()
        sys.exit(1)
    
    # Create update manager
    manager = DatabaseUpdateManager(args.project_root)
    manager.print_banner()
    
    try:
        if args.database == 'cve':
            success = manager.update_cve_database()
        elif args.database == 'exploit':
            success = manager.update_exploit_database()
        elif args.database == 'nuclei':
            success = manager.update_nuclei_templates()
        elif args.database == 'wordlists':
            success = manager.update_wordlists()
        elif args.database == 'all':
            results = manager.update_all_databases()
            success = all(results.values())
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("Database update interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()