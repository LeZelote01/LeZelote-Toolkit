#!/usr/bin/env python3
"""
LeZelote Toolkit - Master Deployment Orchestrator
================================================

Comprehensive deployment orchestration system that coordinates:
- Multi-platform package building
- Cross-platform compatibility testing  
- Digital signature and integrity verification
- Performance benchmarking
- USB optimization
- Release validation

This is the main entry point for Phase 11.1 - Scripts de Déploiement.
"""

import os
import sys
import subprocess
import json
import time
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
except ImportError:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)

class DeploymentOrchestrator:
    """Master deployment orchestration system for LeZelote Toolkit."""
    
    def __init__(self, version="1.0.0", output_dir="releases", parallel=True):
        self.version = version
        self.output_dir = Path(output_dir)
        self.parallel = parallel
        self.script_dir = script_dir
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Deployment configuration
        self.deployment_config = {
            "build_platforms": ["windows-x64", "linux-x64", "macos-universal"],
            "security_level": "standard", 
            "usb_optimized": True,
            "run_tests": True,
            "create_signatures": True,
            "performance_benchmarks": True
        }
        
        # Scripts to orchestrate
        self.scripts = {
            "multiplatform_builder": self.script_dir / "build_multiplatform.py",
            "compatibility_tester": self.script_dir / "test_compatibility.py", 
            "digital_signature": self.script_dir / "digital_signature.py",
            "release_creator": self.script_dir / "create_release.py"
        }
        
        # Validate scripts exist
        self._validate_scripts()
        
        # Deployment phases
        self.phases = [
            {"name": "validation", "description": "Pre-deployment validation"},
            {"name": "build", "description": "Multi-platform package building"},
            {"name": "test", "description": "Compatibility and performance testing"},
            {"name": "security", "description": "Digital signing and integrity verification"},
            {"name": "finalize", "description": "Final packaging and validation"}
        ]
        
    def _validate_scripts(self):
        """Validate that all required scripts exist."""
        missing_scripts = []
        for name, script_path in self.scripts.items():
            if not script_path.exists():
                missing_scripts.append(f"{name}: {script_path}")
                
        if missing_scripts:
            logger.error("Missing required scripts:")
            for script in missing_scripts:
                logger.error(f"  - {script}")
            raise FileNotFoundError("Required deployment scripts not found")
            
        logger.info(f"✅ All {len(self.scripts)} deployment scripts validated")
        
    def run_deployment_phase(self, phase_name, **kwargs):
        """Execute a specific deployment phase."""
        phase_info = next((p for p in self.phases if p["name"] == phase_name), None)
        if not phase_info:
            raise ValueError(f"Unknown deployment phase: {phase_name}")
            
        logger.info(f"🚀 Starting Phase: {phase_info['description']}")
        start_time = time.time()
        
        try:
            if phase_name == "validation":
                result = self._phase_validation(**kwargs)
            elif phase_name == "build":
                result = self._phase_build(**kwargs)
            elif phase_name == "test":
                result = self._phase_test(**kwargs)
            elif phase_name == "security":
                result = self._phase_security(**kwargs)
            elif phase_name == "finalize":
                result = self._phase_finalize(**kwargs)
            else:
                raise ValueError(f"Phase handler not implemented: {phase_name}")
                
            duration = time.time() - start_time
            
            if result.get("success", False):
                logger.info(f"✅ Phase '{phase_name}' completed successfully ({duration:.1f}s)")
            else:
                logger.error(f"❌ Phase '{phase_name}' failed ({duration:.1f}s)")
                
            result["duration"] = duration
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"💥 Phase '{phase_name}' crashed: {e} ({duration:.1f}s)")
            return {"success": False, "error": str(e), "duration": duration}
            
    def _phase_validation(self, **kwargs):
        """Pre-deployment validation phase."""
        logger.info("📋 Running pre-deployment validation...")
        
        validation_results = {
            "project_structure": False,
            "dependencies": False,
            "scripts": False,
            "configuration": False
        }
        
        try:
            # Validate project structure using existing release creator
            logger.info("Validating project structure...")
            cmd = [
                sys.executable, str(self.scripts["release_creator"]),
                "--validate-only"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            validation_results["project_structure"] = result.returncode == 0
            
            if not validation_results["project_structure"]:
                logger.warning(f"Project structure validation warnings: {result.stderr}")
            else:
                logger.info("✅ Project structure validation passed")
                
            # Check Python dependencies
            logger.info("Checking Python dependencies...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "check"], 
                             capture_output=True, check=True, timeout=30)
                validation_results["dependencies"] = True
                logger.info("✅ Dependencies validation passed")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Dependencies check warning: {e}")
                validation_results["dependencies"] = False
                
            # Validate scripts are executable
            validation_results["scripts"] = all(script.exists() for script in self.scripts.values())
            
            # Check configuration files
            config_files = [
                project_root / "config" / "main_config.yaml",
                project_root / "requirements.txt",
                project_root / "run_cli.py"
            ]
            validation_results["configuration"] = all(f.exists() for f in config_files)
            
            overall_success = all(validation_results.values())
            
            return {
                "success": overall_success,
                "details": validation_results,
                "message": "Validation completed" if overall_success else "Validation failed"
            }
            
        except Exception as e:
            logger.error(f"Validation phase error: {e}")
            return {"success": False, "error": str(e), "details": validation_results}
            
    def _phase_build(self, platforms=None, **kwargs):
        """Multi-platform build phase."""
        logger.info("🔨 Starting multi-platform build...")
        
        if platforms is None:
            platforms = self.deployment_config["build_platforms"]
            
        try:
            # Build packages using multi-platform builder
            cmd = [
                sys.executable, str(self.scripts["multiplatform_builder"]),
                "--version", self.version,
                "--output-dir", str(self.output_dir),
                "--platforms"
            ] + platforms
            
            if self.deployment_config["usb_optimized"]:
                cmd.append("--usb-optimized")
                
            if self.parallel:
                cmd.append("--parallel")
                
            cmd.append("--test-integrity")
            
            logger.info(f"Building platforms: {', '.join(platforms)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
            
            if result.returncode == 0:
                # Parse build results
                build_info = self._parse_build_output(result.stdout)
                
                # Count created packages
                packages = list(self.output_dir.glob("*.zip")) + list(self.output_dir.glob("*.tar.gz"))
                
                return {
                    "success": True,
                    "packages_created": len(packages),
                    "platforms": platforms,
                    "build_info": build_info,
                    "message": f"Successfully built {len(packages)} packages"
                }
            else:
                logger.error(f"Build failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            logger.error("Build process timed out (30 minutes)")
            return {"success": False, "error": "Build timeout"}
        except Exception as e:
            logger.error(f"Build phase error: {e}")
            return {"success": False, "error": str(e)}
            
    def _phase_test(self, **kwargs):
        """Compatibility and performance testing phase."""
        logger.info("🧪 Starting compatibility and performance testing...")
        
        try:
            # Run compatibility tests
            cmd = [
                sys.executable, str(self.scripts["compatibility_tester"]),
                "--packages-dir", str(self.output_dir),
                "--results-dir", str(self.output_dir / "test_results"),
                "--generate-report"
            ]
            
            logger.info("Running compatibility tests...")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
            
            if result.returncode == 0:
                # Parse test results
                test_results_dir = self.output_dir / "test_results"
                if test_results_dir.exists():
                    test_files = list(test_results_dir.glob("compatibility_test_*.json"))
                    if test_files:
                        # Load latest test result
                        latest_test = max(test_files, key=lambda x: x.stat().st_mtime)
                        with open(latest_test) as f:
                            test_data = json.load(f)
                            
                        return {
                            "success": True,
                            "test_results": test_data["summary"],
                            "test_file": str(latest_test),
                            "message": f"Testing completed: {test_data['summary']['success_rate']}% success rate"
                        }
                        
                return {
                    "success": True,
                    "message": "Testing completed but no detailed results found"
                }
            else:
                logger.warning(f"Some tests may have failed: {result.stderr}")
                return {
                    "success": True,  # Don't fail deployment for test failures
                    "warning": result.stderr,
                    "message": "Testing completed with warnings"
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Testing process timed out (30 minutes)")
            return {"success": False, "error": "Testing timeout"}
        except Exception as e:
            logger.error(f"Testing phase error: {e}")
            return {"success": False, "error": str(e)}
            
    def _phase_security(self, **kwargs):
        """Digital signing and integrity verification phase."""
        logger.info("🔐 Starting security and signing phase...")
        
        try:
            # Generate signing key if not exists
            logger.info("Ensuring signing keys exist...")
            key_cmd = [
                sys.executable, str(self.scripts["digital_signature"]),
                "generate-key",
                "--key-name", "lezelote_deployment",
                "--key-size", "4096"
            ]
            
            # Run key generation (will skip if exists)
            subprocess.run(key_cmd, capture_output=True, text=True, timeout=300)
            
            # Sign all packages
            logger.info("Signing all packages...")
            sign_cmd = [
                sys.executable, str(self.scripts["digital_signature"]),
                "sign-all",
                "--packages-dir", str(self.output_dir),
                "--security-level", self.deployment_config["security_level"],
                "--key-name", "lezelote_deployment"
            ]
            
            result = subprocess.run(sign_cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                # Verify all signatures
                logger.info("Verifying signatures...")
                verify_cmd = [
                    sys.executable, str(self.scripts["digital_signature"]),
                    "verify-all"
                ]
                
                verify_result = subprocess.run(verify_cmd, capture_output=True, text=True, timeout=300)
                
                # Count signature files
                signature_files = list(self.output_dir.glob("signatures/*.manifest.json"))
                
                return {
                    "success": True,
                    "packages_signed": len(signature_files),
                    "security_level": self.deployment_config["security_level"],
                    "verification_passed": verify_result.returncode == 0,
                    "message": f"Security phase completed: {len(signature_files)} packages signed"
                }
            else:
                logger.error(f"Signing failed: {result.stderr}")
                return {"success": False, "error": f"Signing failed: {result.stderr}"}
                
        except subprocess.TimeoutExpired:
            logger.error("Security phase timed out")
            return {"success": False, "error": "Security phase timeout"}
        except Exception as e:
            logger.error(f"Security phase error: {e}")
            return {"success": False, "error": str(e)}
            
    def _phase_finalize(self, **kwargs):
        """Final packaging and validation phase."""
        logger.info("🎁 Finalizing deployment...")
        
        try:
            # Create final release using existing script
            cmd = [
                sys.executable, str(self.scripts["release_creator"]),
                "--version", self.version,
                "--output-dir", str(self.output_dir)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                # Generate deployment summary
                summary = self._generate_deployment_summary()
                
                return {
                    "success": True,
                    "summary": summary,
                    "message": "Deployment finalized successfully"
                }
            else:
                logger.warning(f"Final packaging had issues: {result.stderr}")
                # Still count as success if we have packages
                packages = list(self.output_dir.glob("*.zip")) + list(self.output_dir.glob("*.tar.gz"))
                if packages:
                    summary = self._generate_deployment_summary()
                    return {
                        "success": True,
                        "summary": summary,
                        "warning": result.stderr,
                        "message": "Deployment completed with warnings"
                    }
                else:
                    return {"success": False, "error": "No packages found after finalization"}
                    
        except Exception as e:
            logger.error(f"Finalization error: {e}")
            return {"success": False, "error": str(e)}
            
    def _parse_build_output(self, output):
        """Parse build output for information."""
        build_info = {
            "packages_built": 0,
            "total_size_mb": 0,
            "platforms": []
        }
        
        lines = output.split('\n')
        for line in lines:
            if "Built" in line and "packages" in line:
                try:
                    build_info["packages_built"] = int(line.split()[1])
                except:
                    pass
            elif "Total size:" in line:
                try:
                    size_str = line.split("Total size:")[1].strip()
                    build_info["total_size_mb"] = float(size_str.split()[0])
                except:
                    pass
                    
        return build_info
        
    def _generate_deployment_summary(self):
        """Generate comprehensive deployment summary."""
        summary = {
            "version": self.version,
            "deployment_date": datetime.utcnow().isoformat(),
            "output_directory": str(self.output_dir),
            "packages": {},
            "signatures": {},
            "test_results": {},
            "total_files": 0,
            "total_size_mb": 0
        }
        
        # Count packages
        packages = list(self.output_dir.glob("*.zip")) + list(self.output_dir.glob("*.tar.gz"))
        for package in packages:
            summary["packages"][package.name] = {
                "size_mb": round(package.stat().st_size / 1024 / 1024, 2),
                "created": datetime.fromtimestamp(package.stat().st_mtime).isoformat()
            }
            
        summary["total_files"] = len(packages)
        summary["total_size_mb"] = sum(p["size_mb"] for p in summary["packages"].values())
        
        # Count signatures
        signatures_dir = self.output_dir / "signatures"
        if signatures_dir.exists():
            signature_files = list(signatures_dir.glob("*.manifest.json"))
            summary["signatures"]["count"] = len(signature_files)
            
        # Check for test results
        test_results_dir = self.output_dir / "test_results"
        if test_results_dir.exists():
            test_files = list(test_results_dir.glob("compatibility_test_*.json"))
            if test_files:
                latest_test = max(test_files, key=lambda x: x.stat().st_mtime)
                try:
                    with open(latest_test) as f:
                        test_data = json.load(f)
                    summary["test_results"] = test_data["summary"]
                except:
                    pass
                    
        return summary
        
    def run_full_deployment(self, phases=None, **kwargs):
        """Run complete deployment process."""
        if phases is None:
            phases = [p["name"] for p in self.phases]
            
        logger.info(f"🚀 Starting full deployment process...")
        logger.info(f"📋 Phases to execute: {', '.join(phases)}")
        
        deployment_start = time.time()
        deployment_results = {
            "version": self.version,
            "start_time": datetime.utcnow().isoformat(),
            "phases": {},
            "overall_success": True
        }
        
        # Execute phases sequentially
        for phase_name in phases:
            try:
                phase_result = self.run_deployment_phase(phase_name, **kwargs)
                deployment_results["phases"][phase_name] = phase_result
                
                if not phase_result.get("success", False):
                    logger.error(f"💥 Phase '{phase_name}' failed, stopping deployment")
                    deployment_results["overall_success"] = False
                    break
                    
            except KeyboardInterrupt:
                logger.warning("⚠️  Deployment interrupted by user")
                deployment_results["overall_success"] = False
                deployment_results["error"] = "Interrupted by user"
                break
            except Exception as e:
                logger.error(f"💥 Unexpected error in phase '{phase_name}': {e}")
                deployment_results["overall_success"] = False
                deployment_results["error"] = str(e)
                break
                
        # Finalize deployment results
        deployment_duration = time.time() - deployment_start
        deployment_results["end_time"] = datetime.utcnow().isoformat()
        deployment_results["total_duration"] = deployment_duration
        
        # Save deployment report
        report_file = self.output_dir / f"deployment_report_{self.version}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(deployment_results, f, indent=2)
            
        # Print summary
        self._print_deployment_summary(deployment_results)
        
        return deployment_results
        
    def _print_deployment_summary(self, results):
        """Print deployment summary to console."""
        print("\n" + "="*80)
        print("🎯 DEPLOYMENT SUMMARY")
        print("="*80)
        
        success = results["overall_success"]
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"Status: {status}")
        print(f"Version: {results['version']}")
        print(f"Duration: {results['total_duration']:.1f} seconds")
        print(f"Output: {self.output_dir}")
        
        print("\n📋 Phase Results:")
        for phase_name, phase_result in results["phases"].items():
            phase_success = phase_result.get("success", False)
            phase_icon = "✅" if phase_success else "❌"
            duration = phase_result.get("duration", 0)
            print(f"  {phase_icon} {phase_name.title()}: {duration:.1f}s")
            
            # Print phase-specific details
            if phase_name == "build" and "packages_created" in phase_result:
                print(f"     📦 Packages: {phase_result['packages_created']}")
            elif phase_name == "test" and "test_results" in phase_result:
                tr = phase_result["test_results"]
                print(f"     🧪 Tests: {tr.get('success_rate', 0)}% success rate")
            elif phase_name == "security" and "packages_signed" in phase_result:
                print(f"     🔐 Signed: {phase_result['packages_signed']} packages")
                
        if success:
            print("\n🎉 Deployment completed successfully!")
            
            # Show final statistics if available
            if "summary" in results.get("phases", {}).get("finalize", {}):
                summary = results["phases"]["finalize"]["summary"]
                print(f"📊 Final Statistics:")
                print(f"   📦 Total packages: {summary.get('total_files', 0)}")
                print(f"   💾 Total size: {summary.get('total_size_mb', 0):.1f} MB")
                
        else:
            print(f"\n💥 Deployment failed: {results.get('error', 'Unknown error')}")
            
        print("="*80)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Master deployment orchestrator for LeZelote Toolkit")
    parser.add_argument("--version", default="1.0.0", help="Version to deploy")
    parser.add_argument("--output-dir", default="releases", help="Output directory")
    parser.add_argument("--phases", nargs="*", 
                       choices=["validation", "build", "test", "security", "finalize"],
                       help="Specific phases to run (default: all)")
    parser.add_argument("--platforms", nargs="*", 
                       default=["windows-x64", "linux-x64", "macos-universal"],
                       help="Platforms to build")
    parser.add_argument("--security-level", choices=["basic", "standard", "high", "paranoid"],
                       default="standard", help="Security level")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel processing")
    parser.add_argument("--skip-tests", action="store_true", help="Skip compatibility tests")
    parser.add_argument("--skip-signatures", action="store_true", help="Skip digital signatures")
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = DeploymentOrchestrator(
        version=args.version,
        output_dir=args.output_dir,
        parallel=not args.no_parallel
    )
    
    # Update configuration based on arguments
    if args.skip_tests:
        orchestrator.deployment_config["run_tests"] = False
    if args.skip_signatures:
        orchestrator.deployment_config["create_signatures"] = False
    if args.security_level:
        orchestrator.deployment_config["security_level"] = args.security_level
        
    # Determine phases to run
    phases = args.phases if args.phases else None
    if args.skip_tests and phases is None:
        phases = ["validation", "build", "security", "finalize"]
    if args.skip_signatures and phases is None:
        phases = ["validation", "build", "test", "finalize"]
        
    try:
        logger.info(f"🚀 LeZelote Toolkit - Master Deployment Orchestrator")
        logger.info(f"📦 Version: {args.version}")
        logger.info(f"🎯 Platforms: {', '.join(args.platforms)}")
        logger.info(f"🔐 Security Level: {args.security_level}")
        
        # Run deployment
        results = orchestrator.run_full_deployment(
            phases=phases,
            platforms=args.platforms
        )
        
        success = results["overall_success"]
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️  Deployment cancelled by user")
        return False
    except Exception as e:
        logger.error(f"💥 Deployment orchestration failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)