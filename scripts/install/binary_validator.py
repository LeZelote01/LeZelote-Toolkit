#!/usr/bin/env python3
"""
LeZelote-Toolkit - Binary Validator
Validates installed binaries and tests functionality
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.utils.logging_handler import get_logger

class BinaryValidator:
    """Validates and tests installed security tool binaries"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.project_root = project_root
        self.binaries_dir = self.project_root / "tools" / "binaries"
        self.validation_results = {}
        
        # Test commands for each tool
        self.test_commands = {
            "nmap": {
                "windows": ["nmap.exe", "--version"],
                "linux": ["./nmap", "--version"],
                "macos": ["./nmap", "--version"],
                "expected_output": "Nmap version"
            },
            "sqlmap": {
                "windows": ["python", "sqlmap.py", "--version"],
                "linux": ["python3", "sqlmap.py", "--version"],
                "macos": ["python3", "sqlmap.py", "--version"],
                "expected_output": "sqlmap/"
            },
            "nikto": {
                "windows": ["perl", "nikto.pl", "-Version"],
                "linux": ["perl", "nikto.pl", "-Version"],
                "macos": ["perl", "nikto.pl", "-Version"],
                "expected_output": "Nikto"
            },
            "hydra": {
                "windows": ["hydra.exe", "-h"],
                "linux": ["./hydra", "-h"],
                "macos": ["./hydra", "-h"],
                "expected_output": "Hydra"
            },
            "hashcat": {
                "windows": ["hashcat.exe", "--version"],
                "linux": ["./hashcat", "--version"],
                "macos": ["./hashcat", "--version"],
                "expected_output": "hashcat"
            },
            "nuclei": {
                "windows": ["nuclei.exe", "-version"],
                "linux": ["./nuclei", "-version"],
                "macos": ["./nuclei", "-version"],
                "expected_output": "nuclei-version"
            }
        }
    
    def detect_platform(self) -> str:
        """Detect current platform"""
        import platform
        system = platform.system().lower()
        
        if system == 'windows':
            return 'windows'
        elif system == 'darwin':
            return 'macos'
        elif system == 'linux':
            return 'linux'
        else:
            raise ValueError(f"Unsupported platform: {system}")
    
    def check_binary_exists(self, tool_name: str, platform: str) -> Tuple[bool, Optional[Path]]:
        """Check if binary exists for given tool and platform"""
        platform_dir = self.binaries_dir / platform
        
        if not platform_dir.exists():
            return False, None
        
        # Common binary names to check
        possible_names = [
            f"{tool_name}",
            f"{tool_name}.exe",
            f"{tool_name}.py",
            f"{tool_name}.pl"
        ]
        
        for name in possible_names:
            binary_path = platform_dir / name
            if binary_path.exists():
                return True, binary_path
        
        return False, None
    
    def test_binary_execution(self, tool_name: str, platform: str) -> Dict:
        """Test if binary can execute and respond correctly"""
        result = {
            'tool': tool_name,
            'platform': platform,
            'exists': False,
            'executable': False,
            'functional': False,
            'version': None,
            'error': None,
            'path': None
        }
        
        # Check if binary exists
        exists, binary_path = self.check_binary_exists(tool_name, platform)
        if not exists or not binary_path:
            result['error'] = f"Binary not found for {tool_name} on {platform}"
            return result
        
        result['exists'] = True
        result['path'] = str(binary_path)
        
        # Check if file is executable
        if not os.access(binary_path, os.X_OK) and platform != 'windows':
            result['error'] = f"Binary not executable: {binary_path}"
            return result
        
        result['executable'] = True
        
        # Test execution with test command
        if tool_name not in self.test_commands:
            result['error'] = f"No test command configured for {tool_name}"
            return result
        
        test_config = self.test_commands[tool_name]
        if platform not in test_config:
            result['error'] = f"No test command for {tool_name} on {platform}"
            return result
        
        try:
            # Prepare command
            cmd = test_config[platform].copy()
            
            # Update paths for relative execution
            if cmd[0] in ['python', 'python3', 'perl']:
                # Script execution - update script path
                if len(cmd) > 1:
                    cmd[1] = str(binary_path.parent / cmd[1])
            else:
                # Direct binary execution
                cmd[0] = str(binary_path)
            
            # Execute test command
            process = subprocess.run(
                cmd,
                cwd=str(binary_path.parent),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check output
            output = process.stdout + process.stderr
            expected = test_config.get('expected_output', '')
            
            if expected and expected.lower() in output.lower():
                result['functional'] = True
                # Extract version if possible
                lines = output.split('\n')
                for line in lines:
                    if any(word in line.lower() for word in ['version', 'ver', 'v']):
                        result['version'] = line.strip()
                        break
                        
            else:
                result['error'] = f"Unexpected output: {output[:200]}"
                
        except subprocess.TimeoutExpired:
            result['error'] = f"Test command timeout for {tool_name}"
        except Exception as e:
            result['error'] = f"Test execution failed: {e}"
        
        return result
    
    def validate_platform(self, platform: str) -> Dict:
        """Validate all tools for a specific platform"""
        self.logger.info(f"Validating binaries for {platform}...")
        
        platform_results = {}
        platform_dir = self.binaries_dir / platform
        
        if not platform_dir.exists():
            self.logger.error(f"Platform directory not found: {platform_dir}")
            return platform_results
        
        # Test each configured tool
        for tool_name in self.test_commands.keys():
            self.logger.info(f"Testing {tool_name}...")
            result = self.test_binary_execution(tool_name, platform)
            platform_results[tool_name] = result
            
            # Log result
            if result['functional']:
                self.logger.info(f"✅ {tool_name}: Functional")
            elif result['exists']:
                self.logger.warning(f"⚠️  {tool_name}: Exists but not functional - {result['error']}")
            else:
                self.logger.error(f"❌ {tool_name}: Not found")
        
        return platform_results
    
    def validate_all_platforms(self) -> Dict:
        """Validate tools across all platforms"""
        all_results = {}
        
        for platform in ['windows', 'linux', 'macos']:
            platform_dir = self.binaries_dir / platform
            if platform_dir.exists():
                all_results[platform] = self.validate_platform(platform)
        
        self.validation_results = all_results
        return all_results
    
    def generate_report(self, results: Dict = None) -> str:
        """Generate validation report"""
        if results is None:
            results = self.validation_results
        
        report_lines = ["📋 BINARY VALIDATION REPORT", "=" * 50, ""]
        
        for platform, tools in results.items():
            report_lines.append(f"🖥️  Platform: {platform.upper()}")
            report_lines.append("-" * 30)
            
            total_tools = len(tools)
            functional_tools = sum(1 for tool in tools.values() if tool['functional'])
            existing_tools = sum(1 for tool in tools.values() if tool['exists'])
            
            # Platform summary
            report_lines.append(f"📊 Summary: {functional_tools}/{total_tools} functional, {existing_tools}/{total_tools} installed")
            report_lines.append("")
            
            # Individual tool status
            for tool_name, result in tools.items():
                if result['functional']:
                    status = "✅ FUNCTIONAL"
                    version = f" ({result['version']})" if result['version'] else ""
                elif result['exists']:
                    status = "⚠️  EXISTS (Not functional)"
                else:
                    status = "❌ NOT FOUND"
                
                report_lines.append(f"  {tool_name:12} | {status}{version}")
                if result['error']:
                    report_lines.append(f"               Error: {result['error']}")
            
            report_lines.append("")
        
        # Overall statistics
        all_tools = []
        for platform_tools in results.values():
            all_tools.extend(platform_tools.values())
        
        if all_tools:
            total_count = len(all_tools)
            functional_count = sum(1 for tool in all_tools if tool['functional'])
            existing_count = sum(1 for tool in all_tools if tool['exists'])
            
            report_lines.extend([
                "🎯 OVERALL STATISTICS",
                "=" * 20,
                f"Total binaries checked: {total_count}",
                f"Functional binaries: {functional_count} ({functional_count/total_count*100:.1f}%)",
                f"Installed binaries: {existing_count} ({existing_count/total_count*100:.1f}%)",
                f"Missing binaries: {total_count - existing_count}",
                ""
            ])
        
        return "\n".join(report_lines)
    
    def list_installed_binaries(self, platform: str = None) -> Dict:
        """List all installed binaries"""
        if platform is None:
            platform = self.detect_platform()
        
        platform_dir = self.binaries_dir / platform
        if not platform_dir.exists():
            return {}
        
        installed = {}
        
        for item in platform_dir.iterdir():
            if item.is_file() and not item.name.startswith('.') and item.name != 'README.md':
                file_info = {
                    'name': item.name,
                    'size': item.stat().st_size,
                    'executable': os.access(item, os.X_OK) if platform != 'windows' else True,
                    'path': str(item)
                }
                installed[item.stem] = file_info
        
        return installed

def main():
    """Main validation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LeZelote-Toolkit Binary Validator')
    parser.add_argument('--platform', choices=['windows', 'linux', 'macos'],
                       help='Validate specific platform (auto-detected if not specified)')
    parser.add_argument('--tool', help='Validate specific tool only')
    parser.add_argument('--list', action='store_true', help='List all installed binaries')
    parser.add_argument('--report', help='Save report to file')
    
    args = parser.parse_args()
    
    validator = BinaryValidator()
    
    print("🧪 LeZelote-Toolkit Binary Validator")
    print("=" * 40)
    
    try:
        if args.list:
            # List installed binaries
            platform = args.platform or validator.detect_platform()
            installed = validator.list_installed_binaries(platform)
            
            print(f"\n📦 Installed binaries for {platform}:")
            for name, info in installed.items():
                size_mb = info['size'] / (1024 * 1024)
                executable = "✅" if info['executable'] else "❌"
                print(f"  {name:15} | {size_mb:6.1f} MB | Executable: {executable}")
        
        elif args.tool and args.platform:
            # Validate specific tool
            result = validator.test_binary_execution(args.tool, args.platform)
            print(f"\n🔍 Validation result for {args.tool}:")
            print(f"  Exists: {'✅' if result['exists'] else '❌'}")
            print(f"  Executable: {'✅' if result['executable'] else '❌'}")
            print(f"  Functional: {'✅' if result['functional'] else '❌'}")
            if result['version']:
                print(f"  Version: {result['version']}")
            if result['error']:
                print(f"  Error: {result['error']}")
        
        elif args.platform:
            # Validate specific platform
            results = {args.platform: validator.validate_platform(args.platform)}
            report = validator.generate_report(results)
            print("\n" + report)
        
        else:
            # Validate all platforms
            results = validator.validate_all_platforms()
            report = validator.generate_report(results)
            print("\n" + report)
        
        # Save report if requested
        if args.report and 'report' in locals():
            with open(args.report, 'w') as f:
                f.write(report)
            print(f"\n💾 Report saved to: {args.report}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Validation interrupted by user")
    except Exception as e:
        print(f"\n❌ Validation error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())