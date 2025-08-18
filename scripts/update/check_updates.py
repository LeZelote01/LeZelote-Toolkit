#!/usr/bin/env python3
# =============================================================================
# LeZelote-Toolkit - Update Checker
# =============================================================================
# Description: Check for available updates without applying them
# Author: LeZelote Team
# Version: 1.0.0
# License: MIT
# =============================================================================

import os
import sys
import json
import yaml
import requests
import subprocess
import logging
import argparse
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
import packaging.version

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/update_check.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class UpdateChecker:
    """Check for available updates across all components"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.check_config_file = self.config_dir / "update_check_config.yaml"
        self.system_info = self.get_system_info()
        
    def get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        return {
            'system': platform.system().lower(),
            'machine': platform.machine(),
            'python_version': platform.python_version(),
            'platform': platform.platform()
        }
    
    def print_banner(self):
        """Print update checker banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     LeZelote-Toolkit Update Checker                          ║
║                              Version 1.0.0                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def load_check_config(self) -> Dict[str, Any]:
        """Load update check configuration"""
        default_config = {
            'update_sources': {
                'lezelote_toolkit': {
                    'type': 'github_release',
                    'repo': 'LeZelote01/LeZelote-Toolkit',
                    'current_version_file': 'VERSION',
                    'check_prereleases': False
                },
                'tools': {
                    'nmap': {
                        'type': 'system_package',
                        'check_method': 'package_manager'
                    },
                    'nuclei': {
                        'type': 'github_release',
                        'repo': 'projectdiscovery/nuclei',
                        'check_prereleases': False
                    },
                    'subfinder': {
                        'type': 'github_release',
                        'repo': 'projectdiscovery/subfinder',
                        'check_prereleases': False
                    },
                    'httpx': {
                        'type': 'github_release',
                        'repo': 'projectdiscovery/httpx',
                        'check_prereleases': False
                    },
                    'gobuster': {
                        'type': 'github_release',
                        'repo': 'OJ/gobuster',
                        'check_prereleases': False
                    },
                    'ffuf': {
                        'type': 'github_release',
                        'repo': 'ffuf/ffuf',
                        'check_prereleases': False
                    }
                },
                'databases': {
                    'nuclei_templates': {
                        'type': 'git_repo',
                        'repo': 'https://github.com/projectdiscovery/nuclei-templates.git',
                        'local_path': 'data/vulnerability_databases/nuclei-templates'
                    },
                    'seclists': {
                        'type': 'git_repo',
                        'repo': 'https://github.com/danielmiessler/SecLists.git',
                        'local_path': 'data/wordlists/SecLists'
                    },
                    'payloads_all_the_things': {
                        'type': 'git_repo',
                        'repo': 'https://github.com/swisskyrepo/PayloadsAllTheThings.git',
                        'local_path': 'data/vulnerability_databases/PayloadsAllTheThings'
                    }
                },
                'python_packages': {
                    'requirements_file': 'requirements.txt',
                    'check_outdated': True
                }
            },
            'notification': {
                'enabled': True,
                'methods': ['console', 'file'],
                'file_path': 'logs/update_notifications.log'
            },
            'cache': {
                'enabled': True,
                'cache_duration': 3600,  # 1 hour
                'cache_file': 'cache/update_check_cache.json'
            }
        }
        
        if self.check_config_file.exists():
            try:
                with open(self.check_config_file, 'r') as f:
                    config = yaml.safe_load(f)
                # Merge with defaults
                default_config.update(config)
                return default_config
            except Exception as e:
                logger.warning(f"Failed to load check config, using defaults: {e}")
        
        # Create default config file
        self.create_check_config(default_config)
        return default_config
    
    def create_check_config(self, config: Dict[str, Any]) -> None:
        """Create update check configuration file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.check_config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        logger.info(f"Created update check configuration: {self.check_config_file}")
    
    def load_cache(self) -> Dict[str, Any]:
        """Load cached update check results"""
        config = self.load_check_config()
        cache_config = config.get('cache', {})
        
        if not cache_config.get('enabled', True):
            return {}
        
        cache_file = self.project_root / cache_config.get('cache_file', 'cache/update_check_cache.json')
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                # Check if cache is still valid
                cache_time = datetime.fromisoformat(cache_data.get('cached_at', ''))
                cache_duration = cache_config.get('cache_duration', 3600)
                
                if (datetime.now(timezone.utc) - cache_time).total_seconds() < cache_duration:
                    return cache_data
            except Exception as e:
                logger.debug(f"Failed to load cache: {e}")
        
        return {}
    
    def save_cache(self, cache_data: Dict[str, Any]) -> None:
        """Save update check results to cache"""
        config = self.load_check_config()
        cache_config = config.get('cache', {})
        
        if not cache_config.get('enabled', True):
            return
        
        cache_file = self.project_root / cache_config.get('cache_file', 'cache/update_check_cache.json')
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        cache_data['cached_at'] = datetime.now(timezone.utc).isoformat()
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def get_current_toolkit_version(self) -> Optional[str]:
        """Get current toolkit version"""
        version_file = self.project_root / "VERSION"
        
        if version_file.exists():
            try:
                return version_file.read_text().strip()
            except Exception as e:
                logger.warning(f"Failed to read VERSION file: {e}")
        
        # Fallback to default version
        return "1.0.0"
    
    def check_github_releases(self, repo: str, include_prereleases: bool = False) -> List[Dict[str, Any]]:
        """Check GitHub releases for a repository"""
        url = f"https://api.github.com/repos/{repo}/releases"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            releases = response.json()
            
            if not include_prereleases:
                releases = [r for r in releases if not r.get('prerelease', False)]
            
            return releases[:5]  # Get latest 5 releases
            
        except requests.RequestException as e:
            logger.error(f"Failed to check releases for {repo}: {e}")
            return []
    
    def get_latest_git_commit(self, repo_url: str, local_path: Optional[Path] = None) -> Optional[Dict[str, str]]:
        """Get latest commit information from Git repository"""
        try:
            if local_path and local_path.exists() and (local_path / '.git').exists():
                # Check local repository
                result = subprocess.run(['git', 'log', '-1', '--format=%H|%ad|%s'], 
                                      cwd=local_path, capture_output=True, text=True, check=True)
                
                commit_info = result.stdout.strip().split('|', 2)
                if len(commit_info) == 3:
                    return {
                        'hash': commit_info[0],
                        'date': commit_info[1],
                        'message': commit_info[2],
                        'source': 'local'
                    }
            
            # Check remote repository (GitHub API for public repos)
            if 'github.com' in repo_url:
                repo_path = repo_url.replace('https://github.com/', '').replace('.git', '')
                api_url = f"https://api.github.com/repos/{repo_path}/commits"
                
                response = requests.get(api_url, timeout=30)
                response.raise_for_status()
                
                commits = response.json()
                if commits:
                    latest_commit = commits[0]
                    return {
                        'hash': latest_commit['sha'],
                        'date': latest_commit['commit']['committer']['date'],
                        'message': latest_commit['commit']['message'],
                        'source': 'remote'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get git commit info for {repo_url}: {e}")
            return None
    
    def check_system_package_updates(self, package_name: str) -> Dict[str, Any]:
        """Check if system package has updates available"""
        try:
            if self.system_info['system'] == 'linux':
                # Try different package managers
                if os.path.exists('/usr/bin/apt'):
                    # Debian/Ubuntu
                    result = subprocess.run(['apt', 'list', '--upgradable', package_name], 
                                          capture_output=True, text=True)
                    
                    if package_name in result.stdout and 'upgradable' in result.stdout:
                        # Parse version information
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if package_name in line and 'upgradable' in line:
                                parts = line.split()
                                if len(parts) >= 3:
                                    return {
                                        'update_available': True,
                                        'current_version': parts[1],
                                        'latest_version': parts[2] if len(parts) > 2 else 'unknown',
                                        'package_manager': 'apt'
                                    }
                
                elif os.path.exists('/usr/bin/yum'):
                    # CentOS/RHEL
                    result = subprocess.run(['yum', 'check-update', package_name], 
                                          capture_output=True, text=True)
                    
                    if result.returncode == 100:  # Updates available
                        return {
                            'update_available': True,
                            'package_manager': 'yum'
                        }
                
                elif os.path.exists('/usr/bin/pacman'):
                    # Arch Linux
                    result = subprocess.run(['pacman', '-Qu', package_name], 
                                          capture_output=True, text=True)
                    
                    if package_name in result.stdout:
                        return {
                            'update_available': True,
                            'package_manager': 'pacman'
                        }
            
            elif self.system_info['system'] == 'darwin':
                # macOS with Homebrew
                if os.path.exists('/usr/local/bin/brew') or os.path.exists('/opt/homebrew/bin/brew'):
                    result = subprocess.run(['brew', 'outdated', package_name], 
                                          capture_output=True, text=True)
                    
                    if package_name in result.stdout:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if package_name in line:
                                parts = line.split()
                                if len(parts) >= 3:
                                    return {
                                        'update_available': True,
                                        'current_version': parts[1],
                                        'latest_version': parts[2],
                                        'package_manager': 'brew'
                                    }
            
            return {'update_available': False}
            
        except Exception as e:
            logger.warning(f"Failed to check system package {package_name}: {e}")
            return {'update_available': False, 'error': str(e)}
    
    def check_python_package_updates(self) -> Dict[str, Any]:
        """Check for Python package updates"""
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            return {'error': 'requirements.txt not found'}
        
        try:
            # Get list of outdated packages
            result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--outdated', '--format=json'], 
                                  capture_output=True, text=True, check=True)
            
            outdated_packages = json.loads(result.stdout)
            
            # Read requirements.txt
            with open(requirements_file, 'r') as f:
                requirements = f.read()
            
            # Filter outdated packages that are in requirements
            relevant_outdated = []
            for package in outdated_packages:
                if package['name'].lower() in requirements.lower():
                    relevant_outdated.append(package)
            
            return {
                'outdated_count': len(relevant_outdated),
                'outdated_packages': relevant_outdated,
                'total_outdated': len(outdated_packages)
            }
            
        except Exception as e:
            logger.error(f"Failed to check Python package updates: {e}")
            return {'error': str(e)}
    
    def check_toolkit_updates(self) -> Dict[str, Any]:
        """Check for LeZelote-Toolkit updates"""
        config = self.load_check_config()
        toolkit_config = config['update_sources']['lezelote_toolkit']
        
        current_version = self.get_current_toolkit_version()
        
        if toolkit_config['type'] == 'github_release':
            releases = self.check_github_releases(
                toolkit_config['repo'], 
                toolkit_config.get('check_prereleases', False)
            )
            
            if not releases:
                return {'error': 'Could not fetch release information'}
            
            latest_release = releases[0]
            latest_version = latest_release['tag_name'].lstrip('v')
            
            try:
                if packaging.version.parse(latest_version) > packaging.version.parse(current_version):
                    return {
                        'update_available': True,
                        'current_version': current_version,
                        'latest_version': latest_version,
                        'release_url': latest_release['html_url'],
                        'published_at': latest_release['published_at']
                    }
                else:
                    return {
                        'update_available': False,
                        'current_version': current_version,
                        'latest_version': latest_version
                    }
            except Exception as e:
                logger.warning(f"Failed to compare versions: {e}")
                return {
                    'update_available': current_version != latest_version,
                    'current_version': current_version,
                    'latest_version': latest_version
                }
        
        return {'error': 'Unsupported update source type'}
    
    def check_tool_updates(self) -> Dict[str, Dict[str, Any]]:
        """Check for updates of security tools"""
        config = self.load_check_config()
        tools_config = config['update_sources']['tools']
        
        results = {}
        
        for tool_name, tool_config in tools_config.items():
            logger.info(f"Checking updates for {tool_name}...")
            
            try:
                if tool_config['type'] == 'github_release':
                    releases = self.check_github_releases(
                        tool_config['repo'], 
                        tool_config.get('check_prereleases', False)
                    )
                    
                    if releases:
                        latest_release = releases[0]
                        results[tool_name] = {
                            'type': 'github_release',
                            'latest_version': latest_release['tag_name'],
                            'published_at': latest_release['published_at'],
                            'release_url': latest_release['html_url'],
                            'prerelease': latest_release.get('prerelease', False)
                        }
                    else:
                        results[tool_name] = {'error': 'Could not fetch release information'}
                
                elif tool_config['type'] == 'system_package':
                    package_info = self.check_system_package_updates(tool_name)
                    results[tool_name] = package_info
                
            except Exception as e:
                logger.error(f"Failed to check updates for {tool_name}: {e}")
                results[tool_name] = {'error': str(e)}
        
        return results
    
    def check_database_updates(self) -> Dict[str, Dict[str, Any]]:
        """Check for database updates"""
        config = self.load_check_config()
        databases_config = config['update_sources']['databases']
        
        results = {}
        
        for db_name, db_config in databases_config.items():
            logger.info(f"Checking updates for {db_name}...")
            
            try:
                if db_config['type'] == 'git_repo':
                    local_path = self.project_root / db_config['local_path']
                    
                    local_commit = self.get_latest_git_commit(db_config['repo'], local_path)
                    remote_commit = self.get_latest_git_commit(db_config['repo'])
                    
                    if local_commit and remote_commit:
                        if local_commit['hash'] != remote_commit['hash']:
                            results[db_name] = {
                                'update_available': True,
                                'local_commit': local_commit,
                                'remote_commit': remote_commit
                            }
                        else:
                            results[db_name] = {
                                'update_available': False,
                                'current_commit': local_commit
                            }
                    elif remote_commit:
                        results[db_name] = {
                            'update_available': True,
                            'status': 'not_installed',
                            'remote_commit': remote_commit
                        }
                    else:
                        results[db_name] = {'error': 'Could not fetch repository information'}
            
            except Exception as e:
                logger.error(f"Failed to check updates for {db_name}: {e}")
                results[db_name] = {'error': str(e)}
        
        return results
    
    def check_all_updates(self) -> Dict[str, Any]:
        """Check all available updates"""
        logger.info("Checking for updates across all components...")
        
        # Load cache first
        cache = self.load_cache()
        if cache and 'results' in cache:
            logger.info("Using cached results (use --no-cache to force refresh)")
            return cache['results']
        
        results = {
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'toolkit': self.check_toolkit_updates(),
            'tools': self.check_tool_updates(),
            'databases': self.check_database_updates(),
            'python_packages': self.check_python_package_updates()
        }
        
        # Save to cache
        self.save_cache({'results': results})
        
        return results
    
    def print_update_summary(self, results: Dict[str, Any]) -> None:
        """Print update summary to console"""
        print("\n" + "="*80)
        print("UPDATE CHECK SUMMARY")
        print("="*80)
        print(f"Checked at: {results['checked_at']}")
        print()
        
        # Toolkit updates
        toolkit_result = results.get('toolkit', {})
        print("🛠️  LEZELOTE-TOOLKIT:")
        if toolkit_result.get('update_available'):
            print(f"   ⚠️  Update available: {toolkit_result['current_version']} -> {toolkit_result['latest_version']}")
            print(f"   📅 Published: {toolkit_result.get('published_at', 'Unknown')}")
        elif 'error' in toolkit_result:
            print(f"   ❌ Error: {toolkit_result['error']}")
        else:
            print(f"   ✅ Up to date: v{toolkit_result.get('current_version', 'Unknown')}")
        print()
        
        # Tools updates
        tools_results = results.get('tools', {})
        print("🔧 SECURITY TOOLS:")
        updates_available = 0
        for tool_name, tool_result in tools_results.items():
            if tool_result.get('update_available'):
                print(f"   ⚠️  {tool_name}: Update available")
                updates_available += 1
            elif 'error' in tool_result:
                print(f"   ❌ {tool_name}: {tool_result['error']}")
            else:
                print(f"   ✅ {tool_name}: Up to date")
        
        if updates_available == 0:
            print("   ✅ All tools are up to date")
        print()
        
        # Database updates
        db_results = results.get('databases', {})
        print("💾 DATABASES:")
        db_updates_available = 0
        for db_name, db_result in db_results.items():
            if db_result.get('update_available'):
                if db_result.get('status') == 'not_installed':
                    print(f"   📥 {db_name}: Not installed")
                else:
                    print(f"   ⚠️  {db_name}: Updates available")
                db_updates_available += 1
            elif 'error' in db_result:
                print(f"   ❌ {db_name}: {db_result['error']}")
            else:
                print(f"   ✅ {db_name}: Up to date")
        
        if db_updates_available == 0:
            print("   ✅ All databases are up to date")
        print()
        
        # Python packages updates
        py_result = results.get('python_packages', {})
        print("🐍 PYTHON PACKAGES:")
        if 'error' in py_result:
            print(f"   ❌ Error: {py_result['error']}")
        else:
            outdated_count = py_result.get('outdated_count', 0)
            if outdated_count > 0:
                print(f"   ⚠️  {outdated_count} packages have updates available")
                for package in py_result.get('outdated_packages', [])[:5]:  # Show first 5
                    print(f"      - {package['name']}: {package['version']} -> {package['latest_version']}")
                if len(py_result.get('outdated_packages', [])) > 5:
                    print(f"      ... and {len(py_result.get('outdated_packages', [])) - 5} more")
            else:
                print("   ✅ All packages are up to date")
        
        print("\n" + "="*80)
    
    def save_results_to_file(self, results: Dict[str, Any]) -> None:
        """Save update check results to file"""
        config = self.load_check_config()
        notification_config = config.get('notification', {})
        
        if 'file' in notification_config.get('methods', []):
            file_path = self.project_root / notification_config.get('file_path', 'logs/update_notifications.log')
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                with open(file_path, 'a') as f:
                    f.write(f"\n{'='*50}\n")
                    f.write(f"Update Check - {results['checked_at']}\n")
                    f.write(f"{'='*50}\n")
                    
                    # Write summary
                    toolkit = results.get('toolkit', {})
                    if toolkit.get('update_available'):
                        f.write(f"TOOLKIT UPDATE: {toolkit['current_version']} -> {toolkit['latest_version']}\n")
                    
                    tools = results.get('tools', {})
                    tool_updates = sum(1 for t in tools.values() if t.get('update_available'))
                    if tool_updates > 0:
                        f.write(f"TOOL UPDATES: {tool_updates} tools have updates\n")
                    
                    databases = results.get('databases', {})
                    db_updates = sum(1 for d in databases.values() if d.get('update_available'))
                    if db_updates > 0:
                        f.write(f"DATABASE UPDATES: {db_updates} databases have updates\n")
                    
                    py_packages = results.get('python_packages', {})
                    py_updates = py_packages.get('outdated_count', 0)
                    if py_updates > 0:
                        f.write(f"PYTHON UPDATES: {py_updates} packages have updates\n")
                    
                    f.write(f"\n")
                
                logger.info(f"Update check results saved to: {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to save results to file: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="LeZelote-Toolkit Update Checker")
    parser.add_argument('--project-root', default=os.getcwd(), 
                       help='Project root directory')
    parser.add_argument('--component', choices=['toolkit', 'tools', 'databases', 'python', 'all'],
                       default='all', help='Component to check for updates')
    parser.add_argument('--no-cache', action='store_true', help='Ignore cached results')
    parser.add_argument('--quiet', action='store_true', help='Quiet output (errors only)')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    # Create update checker
    checker = UpdateChecker(args.project_root)
    
    if not args.quiet:
        checker.print_banner()
    
    try:
        # Clear cache if requested
        if args.no_cache:
            cache_file = checker.project_root / "cache" / "update_check_cache.json"
            if cache_file.exists():
                cache_file.unlink()
        
        # Check updates based on component selection
        if args.component == 'all':
            results = checker.check_all_updates()
        elif args.component == 'toolkit':
            results = {'toolkit': checker.check_toolkit_updates()}
        elif args.component == 'tools':
            results = {'tools': checker.check_tool_updates()}
        elif args.component == 'databases':
            results = {'databases': checker.check_database_updates()}
        elif args.component == 'python':
            results = {'python_packages': checker.check_python_package_updates()}
        
        # Add timestamp if not present
        if 'checked_at' not in results:
            results['checked_at'] = datetime.now(timezone.utc).isoformat()
        
        # Output results
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            checker.print_update_summary(results)
            checker.save_results_to_file(results)
        
        # Exit with appropriate code
        has_updates = (
            results.get('toolkit', {}).get('update_available', False) or
            any(t.get('update_available', False) for t in results.get('tools', {}).values()) or
            any(d.get('update_available', False) for d in results.get('databases', {}).values()) or
            results.get('python_packages', {}).get('outdated_count', 0) > 0
        )
        
        sys.exit(2 if has_updates else 0)  # Exit code 2 = updates available
        
    except KeyboardInterrupt:
        logger.info("Update check interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()