"""
Pentest-USB Toolkit - File Operations
====================================

Secure file operations with compression, backup,
and permission management for pentest data handling.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import os
import shutil
import gzip
import tarfile
import zipfile
import hashlib
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from .logging_handler import get_logger
from .error_handler import PentestError


class FileOperations:
    """
    Comprehensive file operations class for secure file handling
    """
    
    def __init__(self):
        """Initialize file operations manager"""
        self.logger = get_logger(__name__)
    
    def ensure_directory(self, path: Union[str, Path]) -> Path:
        """
        Ensure directory exists, create if necessary
        
        Args:
            path: Directory path to create
            
        Returns:
            Path object of the directory
        """
        path = Path(path)
        try:
            path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Directory ensured: {path}")
            return path
        except Exception as e:
            raise PentestError(f"Failed to create directory {path}: {str(e)}")
    
    def safe_write(self, filepath: Union[str, Path], content: Union[str, bytes], 
                   backup: bool = True, encoding: str = 'utf-8') -> bool:
        """
        Safely write content to file with optional backup
        
        Args:
            filepath: File path to write
            content: Content to write (str or bytes)
            backup: Whether to create backup of existing file
            encoding: Text encoding (for string content)
            
        Returns:
            bool: True if successful
        """
        filepath = Path(filepath)
        
        try:
            # Create directory if needed
            self.ensure_directory(filepath.parent)
            
            # Create backup if file exists and backup is requested
            if backup and filepath.exists():
                backup_path = self._create_backup(filepath)
                self.logger.debug(f"Backup created: {backup_path}")
            
            # Write content
            if isinstance(content, str):
                with open(filepath, 'w', encoding=encoding) as f:
                    f.write(content)
            else:
                with open(filepath, 'wb') as f:
                    f.write(content)
            
            self.logger.debug(f"File written: {filepath}")
            return True
            
        except Exception as e:
            raise PentestError(f"Failed to write file {filepath}: {str(e)}")
    
    def safe_read(self, filepath: Union[str, Path], encoding: str = 'utf-8', 
                  binary: bool = False) -> Union[str, bytes]:
        """
        Safely read file content
        
        Args:
            filepath: File path to read
            encoding: Text encoding (for text mode)
            binary: Whether to read in binary mode
            
        Returns:
            File content as string or bytes
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise PentestError(f"File not found: {filepath}")
        
        try:
            if binary:
                with open(filepath, 'rb') as f:
                    return f.read()
            else:
                with open(filepath, 'r', encoding=encoding) as f:
                    return f.read()
        except Exception as e:
            raise PentestError(f"Failed to read file {filepath}: {str(e)}")
    
    def _create_backup(self, filepath: Path) -> Path:
        """Create timestamped backup of file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = filepath.with_name(f"{filepath.stem}_{timestamp}{filepath.suffix}.bak")
        
        shutil.copy2(filepath, backup_path)
        return backup_path
    
    def compress_file(self, filepath: Union[str, Path], 
                     compression: str = 'gzip') -> Path:
        """
        Compress file using specified algorithm
        
        Args:
            filepath: File to compress
            compression: Compression algorithm (gzip, zip, tar.gz)
            
        Returns:
            Path to compressed file
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise PentestError(f"File not found: {filepath}")
        
        try:
            if compression == 'gzip':
                output_path = filepath.with_suffix(filepath.suffix + '.gz')
                with open(filepath, 'rb') as f_in:
                    with gzip.open(output_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            elif compression == 'zip':
                output_path = filepath.with_suffix('.zip')
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.write(filepath, filepath.name)
            
            elif compression == 'tar.gz':
                output_path = filepath.with_suffix('.tar.gz')
                with tarfile.open(output_path, 'w:gz') as tar:
                    tar.add(filepath, arcname=filepath.name)
            
            else:
                raise PentestError(f"Unsupported compression algorithm: {compression}")
            
            self.logger.info(f"File compressed: {filepath} -> {output_path}")
            return output_path
            
        except Exception as e:
            raise PentestError(f"Failed to compress file {filepath}: {str(e)}")
    
    def decompress_file(self, filepath: Union[str, Path], 
                       output_dir: Optional[Union[str, Path]] = None) -> List[Path]:
        """
        Decompress file to specified directory
        
        Args:
            filepath: Compressed file to decompress
            output_dir: Directory to extract to (same dir if None)
            
        Returns:
            List of extracted file paths
        """
        filepath = Path(filepath)
        output_dir = Path(output_dir) if output_dir else filepath.parent
        
        if not filepath.exists():
            raise PentestError(f"File not found: {filepath}")
        
        self.ensure_directory(output_dir)
        extracted_files = []
        
        try:
            if filepath.suffix == '.gz':
                # Handle .tar.gz and .gz files
                if filepath.suffixes[-2:] == ['.tar', '.gz']:
                    with tarfile.open(filepath, 'r:gz') as tar:
                        tar.extractall(output_dir)
                        extracted_files = [output_dir / member.name for member in tar.getmembers()]
                else:
                    output_file = output_dir / filepath.stem
                    with gzip.open(filepath, 'rb') as f_in:
                        with open(output_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    extracted_files = [output_file]
            
            elif filepath.suffix == '.zip':
                with zipfile.ZipFile(filepath, 'r') as zf:
                    zf.extractall(output_dir)
                    extracted_files = [output_dir / name for name in zf.namelist()]
            
            elif filepath.suffix in ['.tar', '.tgz']:
                with tarfile.open(filepath, 'r:*') as tar:
                    tar.extractall(output_dir)
                    extracted_files = [output_dir / member.name for member in tar.getmembers()]
            
            else:
                raise PentestError(f"Unsupported archive format: {filepath.suffix}")
            
            self.logger.info(f"File decompressed: {filepath} -> {output_dir}")
            return extracted_files
            
        except Exception as e:
            raise PentestError(f"Failed to decompress file {filepath}: {str(e)}")
    
    def calculate_hash(self, filepath: Union[str, Path], 
                      algorithm: str = 'sha256') -> str:
        """
        Calculate file hash using specified algorithm
        
        Args:
            filepath: File to hash
            algorithm: Hash algorithm (md5, sha1, sha256, sha512)
            
        Returns:
            Hexadecimal hash string
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise PentestError(f"File not found: {filepath}")
        
        try:
            hash_obj = hashlib.new(algorithm)
            
            with open(filepath, 'rb') as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            raise PentestError(f"Failed to calculate hash for {filepath}: {str(e)}")
    
    def secure_delete(self, filepath: Union[str, Path], passes: int = 3) -> bool:
        """
        Securely delete file by overwriting with random data
        
        Args:
            filepath: File to delete securely
            passes: Number of overwrite passes
            
        Returns:
            bool: True if successful
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            return True
        
        try:
            file_size = filepath.stat().st_size
            
            # Overwrite file multiple times
            with open(filepath, 'r+b') as f:
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            # Finally delete the file
            filepath.unlink()
            
            self.logger.info(f"File securely deleted: {filepath}")
            return True
            
        except Exception as e:
            raise PentestError(f"Failed to securely delete {filepath}: {str(e)}")
    
    def get_file_info(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Get comprehensive file information
        
        Args:
            filepath: File to analyze
            
        Returns:
            Dict with file information
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise PentestError(f"File not found: {filepath}")
        
        try:
            stat = filepath.stat()
            
            return {
                'name': filepath.name,
                'path': str(filepath.absolute()),
                'size_bytes': stat.st_size,
                'size_human': self._format_bytes(stat.st_size),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'permissions': oct(stat.st_mode)[-3:],
                'is_file': filepath.is_file(),
                'is_directory': filepath.is_dir(),
                'is_symlink': filepath.is_symlink(),
                'extension': filepath.suffix,
                'mime_type': self._get_mime_type(filepath)
            }
            
        except Exception as e:
            raise PentestError(f"Failed to get file info for {filepath}: {str(e)}")
    
    def _format_bytes(self, size: int) -> str:
        """Format byte size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def _get_mime_type(self, filepath: Path) -> str:
        """Get MIME type of file (simplified implementation)"""
        extension_map = {
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.yaml': 'application/yaml',
            '.yml': 'application/yaml',
            '.xml': 'application/xml',
            '.html': 'text/html',
            '.csv': 'text/csv',
            '.pdf': 'application/pdf',
            '.zip': 'application/zip',
            '.gz': 'application/gzip',
            '.tar': 'application/x-tar'
        }
        
        return extension_map.get(filepath.suffix.lower(), 'application/octet-stream')
    
    def load_json(self, filepath: Union[str, Path]) -> Any:
        """Load JSON file"""
        try:
            content = self.safe_read(filepath)
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise PentestError(f"Invalid JSON in {filepath}: {str(e)}")
    
    def save_json(self, filepath: Union[str, Path], data: Any, 
                  indent: int = 2, backup: bool = True) -> bool:
        """Save data as JSON file"""
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            return self.safe_write(filepath, content, backup=backup)
        except (TypeError, ValueError) as e:
            raise PentestError(f"Failed to serialize JSON data: {str(e)}")
    
    def load_yaml(self, filepath: Union[str, Path]) -> Any:
        """Load YAML file"""
        try:
            content = self.safe_read(filepath)
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise PentestError(f"Invalid YAML in {filepath}: {str(e)}")
    
    def save_yaml(self, filepath: Union[str, Path], data: Any, backup: bool = True) -> bool:
        """Save data as YAML file"""
        try:
            content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            return self.safe_write(filepath, content, backup=backup)
        except yaml.YAMLError as e:
            raise PentestError(f"Failed to serialize YAML data: {str(e)}")