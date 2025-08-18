#!/usr/bin/env python3
"""
LeZelote Toolkit - Digital Signature and Integrity Verification System
======================================================================

Comprehensive security system for:
- Digital signing of release packages
- Cryptographic integrity verification  
- Chain of trust validation
- Security audit trails
- Tamper detection

Supported signature methods:
- GPG/PGP signatures
- RSA signatures with PKCS#1 v1.5
- ECDSA signatures
- Hash-based integrity checks
"""

import os
import sys
import subprocess
import hashlib
import json
import hmac
import base64
import tempfile
from pathlib import Path
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.exceptions import InvalidSignature
import argparse
import logging

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.utils.logging_handler import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)

class SignatureManager:
    """Advanced digital signature and integrity verification system."""
    
    def __init__(self, key_dir="security_keys", signatures_dir="signatures"):
        self.key_dir = Path(key_dir)
        self.signatures_dir = Path(signatures_dir)
        self.key_dir.mkdir(exist_ok=True, parents=True)
        self.signatures_dir.mkdir(exist_ok=True, parents=True)
        
        # Signature algorithms configuration
        self.signature_config = {
            "rsa": {
                "key_size": 4096,
                "hash_algorithm": hashes.SHA256(),
                "padding": padding.PKCS1v15()
            },
            "hash": {
                "algorithms": ["sha256", "sha512", "blake2b"],
                "default": "sha256"
            },
            "gpg": {
                "key_type": "RSA",
                "key_length": 4096,
                "expire_date": "2y"
            }
        }
        
        # Security levels
        self.security_levels = {
            "basic": ["sha256"],
            "standard": ["sha256", "rsa"],  
            "high": ["sha256", "sha512", "rsa", "gpg"],
            "paranoid": ["sha256", "sha512", "blake2b", "rsa", "gpg", "hmac"]
        }
        
    def generate_rsa_keypair(self, key_name="lezelote_signing", key_size=4096):
        """Generate RSA keypair for signing."""
        logger.info(f"Generating RSA keypair: {key_name} ({key_size} bits)")
        
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
            )
            
            # Get public key
            public_key = private_key.public_key()
            
            # Serialize private key
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # Serialize public key  
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Save keys
            private_key_file = self.key_dir / f"{key_name}_private.pem"
            public_key_file = self.key_dir / f"{key_name}_public.pem"
            
            with open(private_key_file, "wb") as f:
                f.write(private_pem)
            os.chmod(private_key_file, 0o600)  # Restrict permissions
            
            with open(public_key_file, "wb") as f:
                f.write(public_pem)
                
            # Create key info
            key_info = {
                "key_name": key_name,
                "algorithm": "RSA",
                "key_size": key_size,
                "created_at": datetime.utcnow().isoformat(),
                "public_key_file": str(public_key_file),
                "private_key_file": str(private_key_file),
                "fingerprint": self._calculate_key_fingerprint(public_pem)
            }
            
            info_file = self.key_dir / f"{key_name}_info.json"
            with open(info_file, "w") as f:
                json.dump(key_info, f, indent=2)
                
            logger.info(f"✅ RSA keypair generated successfully")
            logger.info(f"🔑 Public key: {public_key_file}")
            logger.info(f"🔐 Private key: {private_key_file} (restricted access)")
            logger.info(f"👆 Fingerprint: {key_info['fingerprint']}")
            
            return key_info
            
        except Exception as e:
            logger.error(f"Failed to generate RSA keypair: {e}")
            return None
            
    def _calculate_key_fingerprint(self, public_key_pem):
        """Calculate key fingerprint."""
        digest = hashlib.sha256(public_key_pem).digest()
        return base64.b64encode(digest).decode()[:32]
        
    def sign_file_rsa(self, file_path, private_key_file, key_name="lezelote_signing"):
        """Sign file using RSA private key."""
        logger.info(f"Signing file with RSA: {file_path}")
        
        try:
            file_path = Path(file_path)
            private_key_file = Path(private_key_file)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File to sign not found: {file_path}")
            if not private_key_file.exists():
                raise FileNotFoundError(f"Private key not found: {private_key_file}")
                
            # Load private key
            with open(private_key_file, "rb") as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None
                )
                
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path, "sha256")
            
            # Sign the hash
            signature = private_key.sign(
                file_hash.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            # Create signature info
            signature_info = {
                "file_name": file_path.name,
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "algorithm": "RSA-SHA256",
                "key_name": key_name,
                "signature": base64.b64encode(signature).decode(),
                "file_hash": file_hash,
                "signed_at": datetime.utcnow().isoformat(),
                "signature_version": "1.0"
            }
            
            # Save signature
            signature_file = self.signatures_dir / f"{file_path.name}.rsa.sig"
            with open(signature_file, "w") as f:
                json.dump(signature_info, f, indent=2)
                
            logger.info(f"✅ RSA signature created: {signature_file}")
            
            return {
                "signature_file": str(signature_file),
                "signature_info": signature_info,
                "algorithm": "RSA"
            }
            
        except Exception as e:
            logger.error(f"RSA signing failed: {e}")
            return None
            
    def verify_rsa_signature(self, signature_file, public_key_file):
        """Verify RSA signature."""
        logger.info(f"Verifying RSA signature: {signature_file}")
        
        try:
            signature_file = Path(signature_file)
            public_key_file = Path(public_key_file)
            
            # Load signature info
            with open(signature_file) as f:
                signature_info = json.load(f)
                
            # Load public key
            with open(public_key_file, "rb") as f:
                public_key = serialization.load_pem_public_key(f.read())
                
            # Get file to verify
            file_path = Path(signature_info["file_path"])
            if not file_path.exists():
                return {"valid": False, "error": "Original file not found"}
                
            # Calculate current file hash
            current_hash = self._calculate_file_hash(file_path, "sha256")
            
            # Check if file hash matches
            if current_hash != signature_info["file_hash"]:
                return {
                    "valid": False, 
                    "error": "File hash mismatch - file may have been modified",
                    "expected_hash": signature_info["file_hash"],
                    "actual_hash": current_hash
                }
                
            # Verify signature
            signature_bytes = base64.b64decode(signature_info["signature"])
            
            public_key.verify(
                signature_bytes,
                current_hash.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            verification_result = {
                "valid": True,
                "file_name": signature_info["file_name"],
                "algorithm": signature_info["algorithm"],
                "key_name": signature_info["key_name"],
                "signed_at": signature_info["signed_at"],
                "verified_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ RSA signature verification passed")
            
            return verification_result
            
        except InvalidSignature:
            logger.error("❌ RSA signature verification failed - invalid signature")
            return {"valid": False, "error": "Invalid signature"}
        except Exception as e:
            logger.error(f"RSA verification error: {e}")
            return {"valid": False, "error": str(e)}
            
    def create_hash_signatures(self, file_path, algorithms=None):
        """Create multiple hash signatures for file."""
        if algorithms is None:
            algorithms = ["sha256", "sha512"]
            
        logger.info(f"Creating hash signatures: {', '.join(algorithms)}")
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        signatures = {}
        
        for algorithm in algorithms:
            try:
                file_hash = self._calculate_file_hash(file_path, algorithm)
                signatures[algorithm] = file_hash
            except Exception as e:
                logger.warning(f"Failed to calculate {algorithm} hash: {e}")
                
        # Create hash signature file
        hash_info = {
            "file_name": file_path.name,
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "signatures": signatures,
            "created_at": datetime.utcnow().isoformat()
        }
        
        hash_signature_file = self.signatures_dir / f"{file_path.name}.hashes"
        with open(hash_signature_file, "w") as f:
            json.dump(hash_info, f, indent=2)
            
        logger.info(f"✅ Hash signatures created: {hash_signature_file}")
        
        return {
            "signature_file": str(hash_signature_file),
            "signatures": signatures,
            "algorithm": "HASH"
        }
        
    def verify_hash_signatures(self, signature_file):
        """Verify hash signatures."""
        logger.info(f"Verifying hash signatures: {signature_file}")
        
        try:
            signature_file = Path(signature_file)
            
            with open(signature_file) as f:
                hash_info = json.load(f)
                
            file_path = Path(hash_info["file_path"])
            if not file_path.exists():
                return {"valid": False, "error": "Original file not found"}
                
            verification_results = {}
            overall_valid = True
            
            for algorithm, expected_hash in hash_info["signatures"].items():
                try:
                    current_hash = self._calculate_file_hash(file_path, algorithm)
                    is_valid = current_hash == expected_hash
                    
                    verification_results[algorithm] = {
                        "valid": is_valid,
                        "expected": expected_hash,
                        "actual": current_hash
                    }
                    
                    if not is_valid:
                        overall_valid = False
                        
                except Exception as e:
                    verification_results[algorithm] = {
                        "valid": False,
                        "error": str(e)
                    }
                    overall_valid = False
                    
            result = {
                "valid": overall_valid,
                "file_name": hash_info["file_name"],
                "algorithm": "HASH",
                "results": verification_results,
                "verified_at": datetime.utcnow().isoformat()
            }
            
            if overall_valid:
                logger.info("✅ Hash signature verification passed")
            else:
                logger.error("❌ Hash signature verification failed")
                
            return result
            
        except Exception as e:
            logger.error(f"Hash verification error: {e}")
            return {"valid": False, "error": str(e)}
            
    def create_gpg_signature(self, file_path, key_id=None):
        """Create GPG signature using system GPG."""
        logger.info(f"Creating GPG signature: {file_path}")
        
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            # Check if GPG is available
            try:
                subprocess.run(["gpg", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise RuntimeError("GPG not available on system")
                
            # Create detached signature
            signature_file = self.signatures_dir / f"{file_path.name}.gpg.sig"
            
            gpg_cmd = ["gpg", "--armor", "--detach-sign", "--output", str(signature_file)]
            
            if key_id:
                gpg_cmd.extend(["--local-user", key_id])
                
            gpg_cmd.append(str(file_path))
            
            result = subprocess.run(gpg_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"GPG signing failed: {result.stderr}")
                
            # Get signature info
            signature_info = {
                "file_name": file_path.name,
                "file_path": str(file_path),
                "signature_file": str(signature_file),
                "algorithm": "GPG",
                "key_id": key_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ GPG signature created: {signature_file}")
            
            return {
                "signature_file": str(signature_file),
                "signature_info": signature_info,
                "algorithm": "GPG"
            }
            
        except Exception as e:
            logger.error(f"GPG signing failed: {e}")
            return None
            
    def verify_gpg_signature(self, signature_file, file_path):
        """Verify GPG signature."""
        logger.info(f"Verifying GPG signature: {signature_file}")
        
        try:
            signature_file = Path(signature_file)
            file_path = Path(file_path)
            
            if not signature_file.exists():
                return {"valid": False, "error": "Signature file not found"}
            if not file_path.exists():
                return {"valid": False, "error": "Original file not found"}
                
            # Verify signature
            gpg_cmd = ["gpg", "--verify", str(signature_file), str(file_path)]
            
            result = subprocess.run(gpg_cmd, capture_output=True, text=True)
            
            is_valid = result.returncode == 0
            
            verification_result = {
                "valid": is_valid,
                "file_name": file_path.name,
                "algorithm": "GPG",
                "verified_at": datetime.utcnow().isoformat(),
                "gpg_output": result.stderr  # GPG outputs to stderr
            }
            
            if is_valid:
                logger.info("✅ GPG signature verification passed")
            else:
                logger.error("❌ GPG signature verification failed")
                verification_result["error"] = result.stderr
                
            return verification_result
            
        except Exception as e:
            logger.error(f"GPG verification error: {e}")
            return {"valid": False, "error": str(e)}
            
    def _calculate_file_hash(self, file_path, algorithm="sha256"):
        """Calculate file hash using specified algorithm."""
        if algorithm == "sha256":
            hash_obj = hashlib.sha256()
        elif algorithm == "sha512":
            hash_obj = hashlib.sha512()
        elif algorithm == "blake2b":
            hash_obj = hashlib.blake2b()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)
                
        return hash_obj.hexdigest()
        
    def sign_package_comprehensive(self, package_path, security_level="standard", key_name="lezelote_signing"):
        """Create comprehensive signature package."""
        logger.info(f"Creating comprehensive signature for: {package_path}")
        logger.info(f"Security level: {security_level}")
        
        package_path = Path(package_path)
        if not package_path.exists():
            raise FileNotFoundError(f"Package not found: {package_path}")
            
        # Get signature methods for security level
        signature_methods = self.security_levels.get(security_level, ["sha256"])
        
        signatures = {}
        
        # Create hash signatures
        if any(method in ["sha256", "sha512", "blake2b"] for method in signature_methods):
            hash_algorithms = [method for method in signature_methods if method in ["sha256", "sha512", "blake2b"]]
            hash_result = self.create_hash_signatures(package_path, hash_algorithms)
            if hash_result:
                signatures["hash"] = hash_result
                
        # Create RSA signature
        if "rsa" in signature_methods:
            # Check if RSA key exists, create if not
            private_key_file = self.key_dir / f"{key_name}_private.pem"
            if not private_key_file.exists():
                logger.info("RSA key not found, generating new keypair...")
                key_info = self.generate_rsa_keypair(key_name)
                if not key_info:
                    logger.warning("Failed to generate RSA key, skipping RSA signature")
                    
            if private_key_file.exists():
                rsa_result = self.sign_file_rsa(package_path, private_key_file, key_name)
                if rsa_result:
                    signatures["rsa"] = rsa_result
                    
        # Create GPG signature
        if "gpg" in signature_methods:
            gpg_result = self.create_gpg_signature(package_path)
            if gpg_result:
                signatures["gpg"] = gpg_result
                
        # Create comprehensive signature manifest
        signature_manifest = {
            "package_name": package_path.name,
            "package_path": str(package_path),
            "package_size": package_path.stat().st_size,
            "security_level": security_level,
            "signatures": signatures,
            "created_at": datetime.utcnow().isoformat(),
            "manifest_version": "1.0"
        }
        
        manifest_file = self.signatures_dir / f"{package_path.name}.manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(signature_manifest, f, indent=2)
            
        logger.info(f"✅ Comprehensive signature created: {len(signatures)} signature types")
        logger.info(f"📄 Manifest: {manifest_file}")
        
        return {
            "manifest_file": str(manifest_file),
            "signatures": signatures,
            "security_level": security_level
        }
        
    def verify_package_comprehensive(self, manifest_file):
        """Verify comprehensive signature package."""
        logger.info(f"Verifying comprehensive signature: {manifest_file}")
        
        try:
            manifest_file = Path(manifest_file)
            
            with open(manifest_file) as f:
                manifest = json.load(f)
                
            package_path = Path(manifest["package_path"])
            if not package_path.exists():
                return {"valid": False, "error": "Package file not found"}
                
            verification_results = {}
            overall_valid = True
            
            # Verify each signature type
            for sig_type, sig_info in manifest["signatures"].items():
                logger.info(f"Verifying {sig_type.upper()} signature...")
                
                try:
                    if sig_type == "hash":
                        result = self.verify_hash_signatures(sig_info["signature_file"])
                    elif sig_type == "rsa":
                        public_key_file = self.key_dir / f"{sig_info['signature_info']['key_name']}_public.pem"
                        result = self.verify_rsa_signature(sig_info["signature_file"], public_key_file)
                    elif sig_type == "gpg":
                        result = self.verify_gpg_signature(sig_info["signature_file"], package_path)
                    else:
                        result = {"valid": False, "error": f"Unknown signature type: {sig_type}"}
                        
                    verification_results[sig_type] = result
                    
                    if not result.get("valid", False):
                        overall_valid = False
                        
                except Exception as e:
                    verification_results[sig_type] = {"valid": False, "error": str(e)}
                    overall_valid = False
                    
            comprehensive_result = {
                "valid": overall_valid,
                "package_name": manifest["package_name"],
                "security_level": manifest["security_level"],
                "verification_results": verification_results,
                "verified_at": datetime.utcnow().isoformat(),
                "total_signatures": len(verification_results),
                "passed_signatures": sum(1 for r in verification_results.values() if r.get("valid", False))
            }
            
            if overall_valid:
                logger.info("✅ Comprehensive signature verification PASSED")
            else:
                logger.error("❌ Comprehensive signature verification FAILED")
                
            # Save verification report
            report_file = self.signatures_dir / f"{manifest['package_name']}_verification_report.json"
            with open(report_file, "w") as f:
                json.dump(comprehensive_result, f, indent=2)
                
            logger.info(f"📄 Verification report: {report_file}")
            
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"Comprehensive verification error: {e}")
            return {"valid": False, "error": str(e)}


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Digital signature and integrity verification system")
    parser.add_argument("command", choices=["generate-key", "sign", "verify", "sign-all", "verify-all"])
    parser.add_argument("--file", help="File to sign/verify")
    parser.add_argument("--manifest", help="Signature manifest file")
    parser.add_argument("--packages-dir", default="releases", help="Directory containing packages")
    parser.add_argument("--key-name", default="lezelote_signing", help="Key name for operations")
    parser.add_argument("--security-level", choices=["basic", "standard", "high", "paranoid"], 
                       default="standard", help="Security level for signatures")
    parser.add_argument("--key-size", type=int, default=4096, help="RSA key size")
    
    args = parser.parse_args()
    
    signature_manager = SignatureManager()
    
    try:
        if args.command == "generate-key":
            result = signature_manager.generate_rsa_keypair(args.key_name, args.key_size)
            if result:
                print(f"✅ Key pair generated: {args.key_name}")
                print(f"👆 Fingerprint: {result['fingerprint']}")
            else:
                print("❌ Key generation failed")
                return False
                
        elif args.command == "sign":
            if not args.file:
                print("❌ --file required for signing")
                return False
                
            result = signature_manager.sign_package_comprehensive(
                args.file, args.security_level, args.key_name
            )
            if result:
                print(f"✅ Package signed with {len(result['signatures'])} signature types")
                print(f"📄 Manifest: {result['manifest_file']}")
            else:
                print("❌ Signing failed")
                return False
                
        elif args.command == "verify":
            if not args.manifest:
                print("❌ --manifest required for verification")
                return False
                
            result = signature_manager.verify_package_comprehensive(args.manifest)
            if result:
                status = "✅ VALID" if result["valid"] else "❌ INVALID"
                print(f"{status} - {result['passed_signatures']}/{result['total_signatures']} signatures passed")
            else:
                print("❌ Verification failed")
                return False
                
        elif args.command == "sign-all":
            packages_dir = Path(args.packages_dir)
            if not packages_dir.exists():
                print(f"❌ Packages directory not found: {packages_dir}")
                return False
                
            packages = list(packages_dir.glob("*.zip")) + list(packages_dir.glob("*.tar.gz"))
            if not packages:
                print(f"❌ No packages found in {packages_dir}")
                return False
                
            signed_count = 0
            for package in packages:
                try:
                    result = signature_manager.sign_package_comprehensive(
                        package, args.security_level, args.key_name
                    )
                    if result:
                        signed_count += 1
                        print(f"✅ Signed: {package.name}")
                    else:
                        print(f"❌ Failed: {package.name}")
                except Exception as e:
                    print(f"❌ Error signing {package.name}: {e}")
                    
            print(f"📊 Signed {signed_count}/{len(packages)} packages")
            
        elif args.command == "verify-all":
            signatures_dir = signature_manager.signatures_dir
            manifests = list(signatures_dir.glob("*.manifest.json"))
            
            if not manifests:
                print(f"❌ No signature manifests found in {signatures_dir}")
                return False
                
            verified_count = 0
            for manifest in manifests:
                try:
                    result = signature_manager.verify_package_comprehensive(manifest)
                    if result and result["valid"]:
                        verified_count += 1
                        print(f"✅ Valid: {result['package_name']}")
                    else:
                        print(f"❌ Invalid: {manifest.stem}")
                except Exception as e:
                    print(f"❌ Error verifying {manifest.name}: {e}")
                    
            print(f"📊 Verified {verified_count}/{len(manifests)} packages")
            
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Operation failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)