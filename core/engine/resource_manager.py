"""
Pentest-USB Toolkit - Resource Manager
=====================================

System resource monitoring and management for optimal performance
and system stability during penetration testing operations.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import os
import sys
import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..utils.logging_handler import get_logger
from ..utils.error_handler import PentestError


@dataclass
class ResourceThresholds:
    """Resource usage thresholds"""
    max_cpu_percent: float = 80.0
    max_memory_percent: float = 80.0
    max_disk_percent: float = 90.0
    min_free_space_mb: int = 1024
    max_network_mbps: float = 100.0


@dataclass
class ResourceUsage:
    """Current system resource usage"""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: int
    disk_percent: float
    disk_free_mb: int
    network_sent_mbps: float
    network_recv_mbps: float
    load_average: Tuple[float, float, float]
    timestamp: datetime


class ResourceManager:
    """
    System resource monitoring and management class.
    
    Features:
    - Real-time resource monitoring
    - Automatic throttling when resources are constrained
    - Resource usage prediction
    - Performance optimization suggestions
    - Resource allocation for tasks
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize resource manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        # Load resource limits from config
        resource_config = config.get('resource_limits', {})
        self.thresholds = ResourceThresholds(
            max_cpu_percent=resource_config.get('max_cpu_usage', 80),
            max_memory_percent=resource_config.get('max_memory_usage', 80),
            max_disk_percent=resource_config.get('max_disk_usage', 90),
            min_free_space_mb=resource_config.get('min_free_space', 1024)
        )
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.usage_history: List[ResourceUsage] = []
        self.max_history_size = 100
        
        # Resource allocation tracking
        self.allocated_resources = {
            'cpu_percent': 0.0,
            'memory_mb': 0.0,
            'disk_mb': 0.0
        }
        
        # Network monitoring baseline
        self._network_baseline = self._get_network_baseline()
        
        # Synchronization
        self.lock = threading.Lock()
        
        self.logger.info("ResourceManager initialized")
    
    def start_monitoring(self, interval: float = 5.0):
        """
        Start continuous resource monitoring
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True,
            name="ResourceMonitor"
        )
        self.monitor_thread.start()
        
        self.logger.info(f"Resource monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            self.monitor_thread = None
        
        self.logger.info("Resource monitoring stopped")
    
    def _monitor_loop(self, interval: float):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                usage = self.get_current_usage()
                
                with self.lock:
                    self.usage_history.append(usage)
                    
                    # Trim history to max size
                    if len(self.usage_history) > self.max_history_size:
                        self.usage_history = self.usage_history[-self.max_history_size:]
                
                # Check for resource constraints
                self._check_resource_constraints(usage)
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Resource monitoring error: {str(e)}")
                time.sleep(interval)
    
    def get_current_usage(self) -> ResourceUsage:
        """Get current system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_mb = memory.available // (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_free_mb = disk.free // (1024 * 1024)
            
            # Network usage
            network_sent_mbps, network_recv_mbps = self._get_network_usage()
            
            # Load average (Unix systems only)
            try:
                load_average = os.getloadavg()
            except (AttributeError, OSError):
                load_average = (0.0, 0.0, 0.0)
            
            return ResourceUsage(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_mb=memory_available_mb,
                disk_percent=disk_percent,
                disk_free_mb=disk_free_mb,
                network_sent_mbps=network_sent_mbps,
                network_recv_mbps=network_recv_mbps,
                load_average=load_average,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error getting resource usage: {str(e)}")
            raise PentestError(f"Failed to get resource usage: {str(e)}")
    
    def _get_network_baseline(self) -> Dict[str, int]:
        """Get network baseline for calculating usage"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'timestamp': time.time()
            }
        except Exception:
            return {'bytes_sent': 0, 'bytes_recv': 0, 'timestamp': time.time()}
    
    def _get_network_usage(self) -> Tuple[float, float]:
        """Calculate current network usage in Mbps"""
        try:
            current_time = time.time()
            net_io = psutil.net_io_counters()
            
            time_diff = current_time - self._network_baseline['timestamp']
            
            if time_diff > 0:
                sent_diff = net_io.bytes_sent - self._network_baseline['bytes_sent']
                recv_diff = net_io.bytes_recv - self._network_baseline['bytes_recv']
                
                # Convert to Mbps
                sent_mbps = (sent_diff * 8) / (time_diff * 1024 * 1024)
                recv_mbps = (recv_diff * 8) / (time_diff * 1024 * 1024)
                
                # Update baseline
                self._network_baseline = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'timestamp': current_time
                }
                
                return sent_mbps, recv_mbps
            
            return 0.0, 0.0
            
        except Exception:
            return 0.0, 0.0
    
    def check_resources(self) -> bool:
        """
        Check if system resources are within acceptable limits
        
        Returns:
            bool: True if resources are OK, False if constrained
        """
        usage = self.get_current_usage()
        
        constraints = []
        
        if usage.cpu_percent > self.thresholds.max_cpu_percent:
            constraints.append(f"CPU usage: {usage.cpu_percent:.1f}%")
        
        if usage.memory_percent > self.thresholds.max_memory_percent:
            constraints.append(f"Memory usage: {usage.memory_percent:.1f}%")
        
        if usage.disk_percent > self.thresholds.max_disk_percent:
            constraints.append(f"Disk usage: {usage.disk_percent:.1f}%")
        
        if usage.disk_free_mb < self.thresholds.min_free_space_mb:
            constraints.append(f"Low disk space: {usage.disk_free_mb}MB free")
        
        if constraints:
            self.logger.warning(f"Resource constraints detected: {', '.join(constraints)}")
            return False
        
        return True
    
    def _check_resource_constraints(self, usage: ResourceUsage):
        """Check for resource constraints and log warnings"""
        if usage.cpu_percent > self.thresholds.max_cpu_percent:
            self.logger.warning(f"High CPU usage: {usage.cpu_percent:.1f}%")
        
        if usage.memory_percent > self.thresholds.max_memory_percent:
            self.logger.warning(f"High memory usage: {usage.memory_percent:.1f}%")
        
        if usage.disk_free_mb < self.thresholds.min_free_space_mb:
            self.logger.warning(f"Low disk space: {usage.disk_free_mb}MB free")
    
    def allocate_resources(self, cpu_percent: float = 0, memory_mb: float = 0, 
                          disk_mb: float = 0) -> bool:
        """
        Allocate resources for a task
        
        Args:
            cpu_percent: CPU percentage to allocate
            memory_mb: Memory in MB to allocate
            disk_mb: Disk space in MB to allocate
            
        Returns:
            bool: True if allocation successful, False if insufficient resources
        """
        usage = self.get_current_usage()
        
        # Check if allocation would exceed limits
        total_cpu = usage.cpu_percent + cpu_percent
        total_memory_mb = (usage.memory_percent / 100) * psutil.virtual_memory().total // (1024 * 1024) + memory_mb
        
        if total_cpu > self.thresholds.max_cpu_percent:
            return False
        
        if usage.memory_available_mb < memory_mb:
            return False
        
        if usage.disk_free_mb < disk_mb:
            return False
        
        # Allocate resources
        with self.lock:
            self.allocated_resources['cpu_percent'] += cpu_percent
            self.allocated_resources['memory_mb'] += memory_mb
            self.allocated_resources['disk_mb'] += disk_mb
        
        self.logger.debug(f"Resources allocated: CPU={cpu_percent}%, MEM={memory_mb}MB, DISK={disk_mb}MB")
        return True
    
    def deallocate_resources(self, cpu_percent: float = 0, memory_mb: float = 0, disk_mb: float = 0):
        """Deallocate previously allocated resources"""
        with self.lock:
            self.allocated_resources['cpu_percent'] = max(0, self.allocated_resources['cpu_percent'] - cpu_percent)
            self.allocated_resources['memory_mb'] = max(0, self.allocated_resources['memory_mb'] - memory_mb)
            self.allocated_resources['disk_mb'] = max(0, self.allocated_resources['disk_mb'] - disk_mb)
        
        self.logger.debug(f"Resources deallocated: CPU={cpu_percent}%, MEM={memory_mb}MB, DISK={disk_mb}MB")
    
    def get_resource_recommendation(self, task_type: str) -> Dict[str, int]:
        """
        Get resource allocation recommendation for a task type
        
        Args:
            task_type: Type of task (scan, exploit, etc.)
            
        Returns:
            Dict with recommended resource allocation
        """
        recommendations = {
            'network_scan': {'max_workers': 4, 'memory_per_worker': 100, 'cpu_intensive': False},
            'web_scan': {'max_workers': 2, 'memory_per_worker': 200, 'cpu_intensive': True},
            'vuln_scan': {'max_workers': 2, 'memory_per_worker': 300, 'cpu_intensive': True},
            'exploitation': {'max_workers': 1, 'memory_per_worker': 500, 'cpu_intensive': False},
            'brute_force': {'max_workers': 8, 'memory_per_worker': 50, 'cpu_intensive': True}
        }
        
        base_rec = recommendations.get(task_type, recommendations['network_scan'])
        usage = self.get_current_usage()
        
        # Adjust based on current resources
        available_memory_mb = usage.memory_available_mb
        cpu_headroom = self.thresholds.max_cpu_percent - usage.cpu_percent
        
        # Calculate optimal worker count
        memory_limited_workers = available_memory_mb // base_rec['memory_per_worker']
        cpu_limited_workers = max(1, int(cpu_headroom / 20)) if base_rec['cpu_intensive'] else base_rec['max_workers']
        
        optimal_workers = min(base_rec['max_workers'], memory_limited_workers, cpu_limited_workers)
        
        return {
            'max_workers': max(1, optimal_workers),
            'memory_per_worker': base_rec['memory_per_worker'],
            'total_memory_needed': optimal_workers * base_rec['memory_per_worker'],
            'cpu_intensive': base_rec['cpu_intensive']
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        with self.lock:
            if not self.usage_history:
                return {}
            
            recent_usage = self.usage_history[-10:]  # Last 10 measurements
            
            avg_cpu = sum(u.cpu_percent for u in recent_usage) / len(recent_usage)
            avg_memory = sum(u.memory_percent for u in recent_usage) / len(recent_usage)
            avg_disk = sum(u.disk_percent for u in recent_usage) / len(recent_usage)
            
            return {
                'average_cpu_percent': avg_cpu,
                'average_memory_percent': avg_memory,
                'average_disk_percent': avg_disk,
                'samples_count': len(recent_usage),
                'monitoring_duration': (
                    recent_usage[-1].timestamp - recent_usage[0].timestamp
                ).total_seconds() if len(recent_usage) > 1 else 0,
                'allocated_resources': dict(self.allocated_resources)
            }
    
    def optimize_for_task(self, task_type: str) -> Dict[str, Any]:
        """
        Optimize system settings for specific task type
        
        Args:
            task_type: Type of task to optimize for
            
        Returns:
            Dict with optimization settings applied
        """
        recommendations = self.get_resource_recommendation(task_type)
        
        # Apply optimizations based on task type
        optimizations = {
            'max_workers': recommendations['max_workers'],
            'memory_allocation': recommendations['total_memory_needed'],
            'priority': 'high' if task_type in ['exploitation', 'brute_force'] else 'normal'
        }
        
        self.logger.info(f"Optimizing system for {task_type}: {optimizations}")
        return optimizations
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'memory_total_gb': psutil.virtual_memory().total // (1024 ** 3),
                'disk_total_gb': psutil.disk_usage('/').total // (1024 ** 3),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                'platform': os.name,
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {str(e)}")
            return {}