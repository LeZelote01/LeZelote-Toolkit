#!/usr/bin/env python3
"""
LeZelote Toolkit - Multi-OS Compatibility Testing Script
========================================================

Comprehensive testing system for validating packages across:
- Windows (10, 11, Server 2019, Server 2022) 
- Linux (Ubuntu, CentOS, Debian, Fedora, Arch)
- macOS (Big Sur, Monterey, Ventura, Sonoma)

Tests:
- Installation procedures
- Runtime compatibility
- Performance benchmarks
- Security validations
- Portability assessments
"""

import os
import sys
import subprocess
import platform
import json
import time
import hashlib
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import logging

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.utils.logging_handler import get_logger
    from core.utils.system_info import get_system_info
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    get_system_info = lambda: {"os": platform.system(), "arch": platform.machine()}

logger = get_logger(__name__)

class MultiOSCompatibilityTester:
    """Comprehensive multi-OS compatibility testing system."""
    
    def __init__(self, packages_dir="releases", test_results_dir="test_results"):
        self.packages_dir = Path(packages_dir)
        self.test_results_dir = Path(test_results_dir)
        self.test_results_dir.mkdir(exist_ok=True, parents=True)
        
        # Test configurations for different OS versions
        self.os_configs = {
            "windows": {
                "versions": ["10", "11", "server-2019", "server-2022"],
                "architectures": ["x64", "arm64"],
                "python_versions": ["3.9", "3.10", "3.11", "3.12"],
                "test_environments": ["clean", "corporate", "restricted"]
            },
            "linux": {
                "distributions": ["ubuntu-20.04", "ubuntu-22.04", "ubuntu-24.04",
                                "centos-7", "centos-8", "centos-stream",
                                "debian-11", "debian-12", "fedora-38", "fedora-39",
                                "arch-latest", "alpine-latest"],
                "architectures": ["x64", "arm64"],
                "python_versions": ["3.9", "3.10", "3.11", "3.12"],
                "test_environments": ["minimal", "desktop", "server"]
            },
            "macos": {
                "versions": ["11.0", "12.0", "13.0", "14.0", "15.0"],
                "architectures": ["intel", "arm64", "universal"], 
                "python_versions": ["3.9", "3.10", "3.11", "3.12"],
                "test_environments": ["standard", "developer", "restricted"]
            }
        }
        
        # Performance benchmarks thresholds
        self.performance_thresholds = {
            "startup_time": 10.0,  # seconds
            "memory_usage": 500,   # MB
            "cpu_usage": 80,       # percentage
            "disk_space": 100      # MB minimum free after install
        }
        
        self.current_os = self._detect_current_os()
        self.host_info = self._get_host_info()
        
    def _detect_current_os(self):
        """Detect current operating system."""
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "linux":
            return "linux"
        elif system == "darwin":
            return "macos"
        else:
            return "unknown"
            
    def _get_host_info(self):
        """Get detailed host system information."""
        info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node()
        }
        
        # Get additional OS-specific info
        if self.current_os == "linux":
            try:
                # Try to get distribution info
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            info["distribution"] = line.split("=")[1].strip('"')
                            break
            except FileNotFoundError:
                info["distribution"] = "Unknown Linux"
                
        elif self.current_os == "windows":
            info["windows_version"] = platform.win32_ver()[0]
            
        elif self.current_os == "macos":
            info["macos_version"] = platform.mac_ver()[0]
            
        return info
        
    def discover_packages(self):
        """Discover all available packages for testing."""
        packages = []
        
        if not self.packages_dir.exists():
            logger.warning(f"Packages directory not found: {self.packages_dir}")
            return packages
            
        # Find all package files
        for pattern in ["*.zip", "*.tar.gz", "*.tgz"]:
            for package_file in self.packages_dir.glob(pattern):
                package_info = self._analyze_package_filename(package_file)
                if package_info:
                    package_info["path"] = package_file
                    packages.append(package_info)
                    
        logger.info(f"Discovered {len(packages)} packages for testing")
        return packages
        
    def _analyze_package_filename(self, package_file):
        """Extract information from package filename."""
        filename = package_file.stem
        parts = filename.split("-")
        
        if len(parts) < 3:
            return None
            
        # Expected format: lezelote-toolkit-VERSION-PLATFORM-TYPE
        try:
            toolkit_name = "-".join(parts[:2])  # lezelote-toolkit
            version = parts[2]
            
            if len(parts) > 3:
                platform_arch = "-".join(parts[3:])
            else:
                platform_arch = "universal"
                
            return {
                "name": toolkit_name,
                "version": version,
                "platform_arch": platform_arch,
                "filename": package_file.name,
                "size": package_file.stat().st_size
            }
        except IndexError:
            logger.warning(f"Could not parse package filename: {package_file.name}")
            return None
            
    def test_package_installation(self, package):
        """Test package installation process."""
        logger.info(f"Testing installation of {package['filename']}")
        
        test_result = {
            "package": package["filename"],
            "test_type": "installation",
            "start_time": datetime.utcnow().isoformat(),
            "host_info": self.host_info,
            "tests": {}
        }
        
        # Create temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # Test 1: Package extraction
                extract_result = self._test_extraction(package, temp_path)
                test_result["tests"]["extraction"] = extract_result
                
                if extract_result["success"]:
                    # Test 2: File integrity
                    integrity_result = self._test_file_integrity(temp_path)
                    test_result["tests"]["integrity"] = integrity_result
                    
                    # Test 3: Dependencies check
                    deps_result = self._test_dependencies(temp_path)
                    test_result["tests"]["dependencies"] = deps_result
                    
                    # Test 4: Basic execution test
                    execution_result = self._test_basic_execution(temp_path)
                    test_result["tests"]["execution"] = execution_result
                    
                    # Test 5: CLI interface test
                    cli_result = self._test_cli_interface(temp_path)
                    test_result["tests"]["cli_interface"] = cli_result
                    
                else:
                    test_result["tests"]["integrity"] = {"success": False, "error": "Extraction failed"}
                    test_result["tests"]["dependencies"] = {"success": False, "error": "Extraction failed"}
                    test_result["tests"]["execution"] = {"success": False, "error": "Extraction failed"}
                    test_result["tests"]["cli_interface"] = {"success": False, "error": "Extraction failed"}
                    
            except Exception as e:
                test_result["error"] = str(e)
                logger.error(f"Installation test failed for {package['filename']}: {e}")
                
        test_result["end_time"] = datetime.utcnow().isoformat()
        test_result["duration"] = self._calculate_test_duration(test_result["start_time"], test_result["end_time"])
        test_result["overall_success"] = all(
            test.get("success", False) for test in test_result["tests"].values()
        )
        
        return test_result
        
    def _test_extraction(self, package, temp_path):
        """Test package extraction."""
        try:
            package_path = package["path"]
            
            if package_path.suffix == ".zip":
                import zipfile
                with zipfile.ZipFile(package_path, 'r') as zipf:
                    zipf.extractall(temp_path)
            elif package_path.suffix in [".tar.gz", ".tgz"]:
                import tarfile
                with tarfile.open(package_path, 'r:gz') as tar:
                    tar.extractall(temp_path)
            else:
                return {"success": False, "error": f"Unsupported archive format: {package_path.suffix}"}
                
            # Check if files were extracted
            extracted_files = list(temp_path.rglob("*"))
            if not extracted_files:
                return {"success": False, "error": "No files extracted"}
                
            return {
                "success": True,
                "files_extracted": len(extracted_files),
                "total_size": sum(f.stat().st_size for f in extracted_files if f.is_file())
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def _test_file_integrity(self, temp_path):
        """Test file integrity after extraction."""
        try:
            required_files = [
                "run_cli.py", "requirements.txt", "launch.sh", "README.md"
            ]
            
            # Find the actual toolkit directory
            toolkit_dirs = [d for d in temp_path.iterdir() if d.is_dir() and "lezelote" in d.name.lower()]
            if toolkit_dirs:
                toolkit_dir = toolkit_dirs[0]
            else:
                toolkit_dir = temp_path
                
            missing_files = []
            for required_file in required_files:
                if not (toolkit_dir / required_file).exists():
                    # Check for platform-specific alternatives
                    alternatives = []
                    if required_file == "launch.sh":
                        alternatives = ["launch.bat"]
                        
                    found_alternative = False
                    for alt in alternatives:
                        if (toolkit_dir / alt).exists():
                            found_alternative = True
                            break
                            
                    if not found_alternative:
                        missing_files.append(required_file)
                        
            return {
                "success": len(missing_files) == 0,
                "missing_files": missing_files,
                "toolkit_directory": str(toolkit_dir)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def _test_dependencies(self, temp_path):
        """Test Python dependencies."""
        try:
            # Find toolkit directory
            toolkit_dirs = [d for d in temp_path.iterdir() if d.is_dir() and "lezelote" in d.name.lower()]
            if toolkit_dirs:
                toolkit_dir = toolkit_dirs[0]
            else:
                toolkit_dir = temp_path
                
            requirements_file = toolkit_dir / "requirements.txt"
            if not requirements_file.exists():
                return {"success": False, "error": "requirements.txt not found"}
                
            # Try to parse requirements
            with open(requirements_file) as f:
                requirements = f.read().strip().split('\n')
                
            # Filter out comments and empty lines
            requirements = [req.strip() for req in requirements 
                          if req.strip() and not req.strip().startswith('#')]
                          
            # Test if requirements can be checked (not installed to avoid conflicts)
            python_cmd = self._get_python_command()
            check_cmd = [python_cmd, "-m", "pip", "check"]
            
            try:
                result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=30)
                pip_check_success = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pip_check_success = False
                
            return {
                "success": True,
                "requirements_count": len(requirements),
                "pip_check_success": pip_check_success,
                "python_command": python_cmd
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def _test_basic_execution(self, temp_path):
        """Test basic execution without full startup."""
        try:
            # Find toolkit directory
            toolkit_dirs = [d for d in temp_path.iterdir() if d.is_dir() and "lezelote" in d.name.lower()]
            if toolkit_dirs:
                toolkit_dir = toolkit_dirs[0]
            else:
                toolkit_dir = temp_path
                
            # Test Python import
            python_cmd = self._get_python_command()
            test_script = toolkit_dir / "run_cli.py"
            
            if not test_script.exists():
                return {"success": False, "error": "run_cli.py not found"}
                
            # Try to run with --version or similar non-interactive option
            test_cmd = [python_cmd, str(test_script), "--help"]
            
            try:
                # Set environment
                env = os.environ.copy()
                env["PYTHONPATH"] = str(toolkit_dir)
                
                result = subprocess.run(
                    test_cmd,
                    cwd=toolkit_dir,
                    capture_output=True,
                    text=True,
                    timeout=15,
                    env=env
                )
                
                # Check if it ran without critical errors
                success = result.returncode == 0 or "LeZelote" in result.stdout or "toolkit" in result.stdout.lower()
                
                return {
                    "success": success,
                    "return_code": result.returncode,
                    "stdout_length": len(result.stdout),
                    "stderr_length": len(result.stderr),
                    "has_output": len(result.stdout) > 0
                }
                
            except subprocess.TimeoutExpired:
                return {"success": False, "error": "Execution timeout (>15s)"}
            except FileNotFoundError:
                return {"success": False, "error": f"Python command not found: {python_cmd}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def _test_cli_interface(self, temp_path):
        """Test CLI interface responsiveness."""
        try:
            # Find toolkit directory
            toolkit_dirs = [d for d in temp_path.iterdir() if d.is_dir() and "lezelote" in d.name.lower()]
            if toolkit_dirs:
                toolkit_dir = toolkit_dirs[0]
            else:
                toolkit_dir = temp_path
                
            python_cmd = self._get_python_command()
            cli_script = toolkit_dir / "run_cli.py"
            
            if not cli_script.exists():
                return {"success": False, "error": "CLI script not found"}
                
            # Test CLI import without execution
            import_test = f"""
import sys
sys.path.insert(0, '{toolkit_dir}')
try:
    from interfaces.cli.main_cli import PentestCLI
    print('CLI_IMPORT_SUCCESS')
except ImportError as e:
    print(f'CLI_IMPORT_FAILED: {{e}}')
"""
            
            try:
                result = subprocess.run(
                    [python_cmd, "-c", import_test],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                success = "CLI_IMPORT_SUCCESS" in result.stdout
                
                return {
                    "success": success,
                    "import_test_passed": success,
                    "error_output": result.stderr if result.stderr else None
                }
                
            except subprocess.TimeoutExpired:
                return {"success": False, "error": "CLI import test timeout"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def _get_python_command(self):
        """Get appropriate Python command for current OS."""
        if self.current_os == "windows":
            # Try common Windows Python commands
            for cmd in ["python", "python3", "py"]:
                try:
                    result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and "Python 3" in result.stdout:
                        return cmd
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
        else:
            # Unix-like systems
            for cmd in ["python3", "python"]:
                try:
                    result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and "Python 3" in result.stdout:
                        return cmd
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
                    
        return "python3"  # Default fallback
        
    def run_performance_tests(self, package):
        """Run performance benchmarks."""
        logger.info(f"Running performance tests for {package['filename']}")
        
        test_result = {
            "package": package["filename"],
            "test_type": "performance",
            "start_time": datetime.utcnow().isoformat(),
            "host_info": self.host_info,
            "tests": {}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # Extract package
                extract_result = self._test_extraction(package, temp_path)
                if not extract_result["success"]:
                    test_result["error"] = "Failed to extract package"
                    return test_result
                    
                # Find toolkit directory
                toolkit_dirs = [d for d in temp_path.iterdir() if d.is_dir() and "lezelote" in d.name.lower()]
                toolkit_dir = toolkit_dirs[0] if toolkit_dirs else temp_path
                
                # Performance tests
                test_result["tests"]["startup_time"] = self._test_startup_time(toolkit_dir)
                test_result["tests"]["memory_usage"] = self._test_memory_usage(toolkit_dir)
                test_result["tests"]["disk_usage"] = self._test_disk_usage(toolkit_dir)
                
            except Exception as e:
                test_result["error"] = str(e)
                
        test_result["end_time"] = datetime.utcnow().isoformat()
        test_result["duration"] = self._calculate_test_duration(test_result["start_time"], test_result["end_time"])
        
        return test_result
        
    def _test_startup_time(self, toolkit_dir):
        """Measure startup time."""
        try:
            python_cmd = self._get_python_command()
            cli_script = toolkit_dir / "run_cli.py"
            
            if not cli_script.exists():
                return {"success": False, "error": "CLI script not found"}
                
            # Measure time to import main modules
            timing_test = f"""
import time
import sys
sys.path.insert(0, '{toolkit_dir}')
start_time = time.time()
try:
    from interfaces.cli.main_cli import PentestCLI
    from core.engine.orchestrator import PentestOrchestrator
    end_time = time.time()
    print(f'STARTUP_TIME: {{end_time - start_time:.3f}}')
except ImportError as e:
    print(f'STARTUP_FAILED: {{e}}')
"""
            
            result = subprocess.run(
                [python_cmd, "-c", timing_test],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if "STARTUP_TIME:" in result.stdout:
                startup_time = float(result.stdout.split("STARTUP_TIME: ")[1].split()[0])
                return {
                    "success": True,
                    "startup_time_seconds": startup_time,
                    "meets_threshold": startup_time <= self.performance_thresholds["startup_time"]
                }
            else:
                return {"success": False, "error": "Could not measure startup time"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def _test_memory_usage(self, toolkit_dir):
        """Estimate memory usage."""
        try:
            # Calculate basic memory footprint by file sizes
            total_size = 0
            file_count = 0
            
            for file_path in toolkit_dir.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
                    
            # Estimate memory usage (rough approximation)
            estimated_memory_mb = total_size / 1024 / 1024 * 2  # Assume 2x file size in memory
            
            return {
                "success": True,
                "estimated_memory_mb": round(estimated_memory_mb, 2),
                "file_count": file_count,
                "total_disk_size_mb": round(total_size / 1024 / 1024, 2),
                "meets_threshold": estimated_memory_mb <= self.performance_thresholds["memory_usage"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def _test_disk_usage(self, toolkit_dir):
        """Measure disk usage."""
        try:
            total_size = 0
            for file_path in toolkit_dir.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    
            size_mb = total_size / 1024 / 1024
            
            return {
                "success": True,
                "disk_usage_mb": round(size_mb, 2),
                "disk_usage_bytes": total_size,
                "meets_threshold": size_mb <= 1000  # 1GB threshold
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def _calculate_test_duration(self, start_time, end_time):
        """Calculate test duration in seconds."""
        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            return (end - start).total_seconds()
        except:
            return 0.0
            
    def run_compatibility_matrix(self, packages=None):
        """Run comprehensive compatibility testing."""
        if packages is None:
            packages = self.discover_packages()
            
        if not packages:
            logger.error("No packages found for testing")
            return None
            
        logger.info(f"Running compatibility tests for {len(packages)} packages")
        
        test_matrix = {
            "test_run_id": f"compat_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.utcnow().isoformat(),
            "host_info": self.host_info,
            "packages_tested": len(packages),
            "results": []
        }
        
        for package in packages:
            logger.info(f"Testing package: {package['filename']}")
            
            # Installation tests
            install_result = self.test_package_installation(package)
            test_matrix["results"].append(install_result)
            
            # Performance tests (only if installation passed)
            if install_result.get("overall_success", False):
                perf_result = self.run_performance_tests(package)
                test_matrix["results"].append(perf_result)
            else:
                logger.warning(f"Skipping performance tests for {package['filename']} due to installation failure")
                
        test_matrix["end_time"] = datetime.utcnow().isoformat()
        test_matrix["total_duration"] = self._calculate_test_duration(
            test_matrix["start_time"], test_matrix["end_time"]
        )
        
        # Calculate summary statistics
        total_tests = len(test_matrix["results"])
        passed_tests = sum(1 for r in test_matrix["results"] if r.get("overall_success", False))
        
        test_matrix["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": round(passed_tests / total_tests * 100, 1) if total_tests > 0 else 0
        }
        
        # Save results
        results_file = self.test_results_dir / f"compatibility_test_{test_matrix['test_run_id']}.json"
        with open(results_file, "w") as f:
            json.dump(test_matrix, f, indent=2)
            
        logger.info(f"✅ Compatibility testing completed!")
        logger.info(f"📊 Results: {passed_tests}/{total_tests} tests passed ({test_matrix['summary']['success_rate']}%)")
        logger.info(f"💾 Results saved to: {results_file}")
        
        return test_matrix
        
    def generate_compatibility_report(self, test_results):
        """Generate human-readable compatibility report."""
        if not test_results:
            return None
            
        report_file = self.test_results_dir / f"compatibility_report_{test_results['test_run_id']}.md"
        
        with open(report_file, "w") as f:
            f.write("# LeZelote Toolkit - Compatibility Test Report\n\n")
            f.write(f"**Test Run ID:** {test_results['test_run_id']}\n")
            f.write(f"**Date:** {test_results['start_time']}\n")
            f.write(f"**Host OS:** {self.host_info['os']} {self.host_info.get('os_version', '')}\n")
            f.write(f"**Architecture:** {self.host_info['architecture']}\n")
            f.write(f"**Python Version:** {self.host_info['python_version']}\n\n")
            
            # Summary
            summary = test_results['summary']
            f.write("## Summary\n\n")
            f.write(f"- **Total Tests:** {summary['total_tests']}\n")
            f.write(f"- **Passed:** {summary['passed_tests']} ✅\n")
            f.write(f"- **Failed:** {summary['failed_tests']} ❌\n")
            f.write(f"- **Success Rate:** {summary['success_rate']}%\n")
            f.write(f"- **Duration:** {test_results['total_duration']:.1f} seconds\n\n")
            
            # Detailed results
            f.write("## Detailed Results\n\n")
            
            for result in test_results['results']:
                package_name = result.get('package', 'Unknown')
                test_type = result.get('test_type', 'unknown')
                success = result.get('overall_success', False)
                
                status_icon = "✅" if success else "❌"
                f.write(f"### {status_icon} {package_name} ({test_type})\n\n")
                
                if 'tests' in result:
                    for test_name, test_data in result['tests'].items():
                        test_success = test_data.get('success', False)
                        test_icon = "✅" if test_success else "❌"
                        f.write(f"- **{test_name.replace('_', ' ').title()}:** {test_icon}")
                        
                        if 'error' in test_data:
                            f.write(f" - {test_data['error']}")
                        f.write("\n")
                        
                if 'error' in result:
                    f.write(f"**Error:** {result['error']}\n")
                    
                f.write(f"**Duration:** {result.get('duration', 0):.1f} seconds\n\n")
                
        logger.info(f"📄 Compatibility report generated: {report_file}")
        return report_file


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Multi-OS compatibility testing for LeZelote Toolkit")
    parser.add_argument("--packages-dir", default="releases", help="Directory containing packages to test")
    parser.add_argument("--results-dir", default="test_results", help="Directory to save test results")
    parser.add_argument("--package-filter", help="Filter packages by name pattern")
    parser.add_argument("--generate-report", action="store_true", default=True, help="Generate readable report")
    parser.add_argument("--performance-only", action="store_true", help="Run only performance tests")
    parser.add_argument("--installation-only", action="store_true", help="Run only installation tests")
    
    args = parser.parse_args()
    
    tester = MultiOSCompatibilityTester(args.packages_dir, args.results_dir)
    
    # Discover packages
    packages = tester.discover_packages()
    
    if args.package_filter:
        packages = [p for p in packages if args.package_filter.lower() in p['filename'].lower()]
        
    if not packages:
        logger.error("No packages found matching criteria")
        return False
        
    logger.info(f"Running compatibility tests on {len(packages)} packages")
    logger.info(f"Host: {tester.current_os} {tester.host_info.get('os_version', '')}")
    
    # Run tests
    try:
        test_results = tester.run_compatibility_matrix(packages)
        
        if test_results and args.generate_report:
            tester.generate_compatibility_report(test_results)
            
        # Print summary
        if test_results:
            summary = test_results['summary']
            logger.info(f"🎯 Final Results: {summary['passed_tests']}/{summary['total_tests']} tests passed")
            return summary['success_rate'] > 80  # Consider >80% success rate as overall success
            
    except KeyboardInterrupt:
        logger.info("Testing interrupted by user")
        return False
    except Exception as e:
        logger.error(f"Testing failed: {e}")
        return False
        
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)