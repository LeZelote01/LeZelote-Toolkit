"""
Pentest-USB Toolkit - Parallel Executor
=======================================

High-performance parallel execution engine with resource monitoring,
load balancing and fault tolerance.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, Future
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime

from ..utils.logging_handler import get_logger
from ..utils.error_handler import PentestError
from .resource_manager import ResourceManager


@dataclass
class ExecutionResult:
    """Result of task execution"""
    task_name: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ParallelExecutor:
    """
    Advanced parallel execution engine with intelligent load balancing.
    
    Features:
    - Thread and process pool management
    - Dynamic scaling based on system resources
    - Task batching and optimization
    - Progress tracking and monitoring
    - Automatic fault tolerance
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize parallel executor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        # Resource management
        self.resource_manager = ResourceManager(config)
        
        # Execution pools
        self.thread_pool: Optional[ThreadPoolExecutor] = None
        self.process_pool: Optional[ProcessPoolExecutor] = None
        
        # Pool configuration
        self.max_threads = config.get('global', {}).get('max_concurrent_tasks', 4)
        self.max_processes = min(multiprocessing.cpu_count(), 4)
        
        # Execution state
        self.active_futures: Dict[Future, str] = {}
        self.execution_stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_execution_time': 0.0
        }
        
        # Synchronization
        self.lock = threading.Lock()
        
        self.logger.info(f"ParallelExecutor initialized (threads: {self.max_threads}, processes: {self.max_processes})")
    
    def execute_tasks(self, tasks: List[Tuple[str, Callable, List[Any]]], 
                     execution_mode: str = "thread", 
                     batch_size: Optional[int] = None) -> Dict[str, ExecutionResult]:
        """
        Execute multiple tasks in parallel
        
        Args:
            tasks: List of (name, function, args) tuples
            execution_mode: "thread" or "process"
            batch_size: Number of tasks to execute in each batch
            
        Returns:
            Dict mapping task names to ExecutionResult objects
        """
        if not tasks:
            return {}
        
        self.logger.info(f"Executing {len(tasks)} tasks in {execution_mode} mode")
        
        # Check system resources
        if not self.resource_manager.check_resources():
            self.logger.warning("System resources are constrained, reducing parallelism")
            self._adjust_pool_sizes(0.5)
        
        try:
            if batch_size and len(tasks) > batch_size:
                return self._execute_in_batches(tasks, execution_mode, batch_size)
            else:
                return self._execute_single_batch(tasks, execution_mode)
        finally:
            self._cleanup_pools()
    
    def _execute_single_batch(self, tasks: List[Tuple[str, Callable, List[Any]]], 
                             execution_mode: str) -> Dict[str, ExecutionResult]:
        """Execute tasks in a single batch"""
        results = {}
        
        # Create appropriate executor
        executor = self._get_executor(execution_mode)
        
        try:
            # Submit all tasks
            future_to_task = {}
            for task_name, func, args in tasks:
                future = executor.submit(self._execute_task_wrapper, task_name, func, args)
                future_to_task[future] = task_name
                
                with self.lock:
                    self.active_futures[future] = task_name
            
            # Collect results as they complete
            for future in as_completed(future_to_task.keys()):
                task_name = future_to_task[future]
                
                try:
                    result = future.result()
                    results[task_name] = result
                    
                    if result.success:
                        self.execution_stats['tasks_completed'] += 1
                    else:
                        self.execution_stats['tasks_failed'] += 1
                    
                    self.execution_stats['total_execution_time'] += result.execution_time
                    
                    self.logger.debug(f"Task completed: {task_name} in {result.execution_time:.2f}s")
                    
                except Exception as e:
                    error_msg = str(e)
                    results[task_name] = ExecutionResult(
                        task_name=task_name,
                        success=False,
                        error=error_msg
                    )
                    self.execution_stats['tasks_failed'] += 1
                    self.logger.error(f"Task failed: {task_name} - {error_msg}")
                
                finally:
                    with self.lock:
                        self.active_futures.pop(future, None)
        
        finally:
            if execution_mode == "thread" and self.thread_pool:
                self.thread_pool.shutdown(wait=True)
                self.thread_pool = None
            elif execution_mode == "process" and self.process_pool:
                self.process_pool.shutdown(wait=True)
                self.process_pool = None
        
        self.logger.info(f"Batch completed: {len(results)} tasks")
        return results
    
    def _execute_in_batches(self, tasks: List[Tuple[str, Callable, List[Any]]], 
                           execution_mode: str, batch_size: int) -> Dict[str, ExecutionResult]:
        """Execute tasks in multiple batches"""
        all_results = {}
        
        # Split tasks into batches
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(tasks) + batch_size - 1) // batch_size
            
            self.logger.info(f"Executing batch {batch_num}/{total_batches} ({len(batch)} tasks)")
            
            # Execute batch
            batch_results = self._execute_single_batch(batch, execution_mode)
            all_results.update(batch_results)
            
            # Check resources between batches
            if not self.resource_manager.check_resources():
                self.logger.warning("Resource constraints detected, pausing between batches")
                time.sleep(2)
        
        return all_results
    
    def _execute_task_wrapper(self, task_name: str, func: Callable, args: List[Any]) -> ExecutionResult:
        """Wrapper function for task execution with timing and error handling"""
        start_time = datetime.now()
        
        try:
            result = func(*args)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return ExecutionResult(
                task_name=task_name,
                success=True,
                result=result,
                execution_time=execution_time,
                start_time=start_time,
                end_time=end_time
            )
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return ExecutionResult(
                task_name=task_name,
                success=False,
                error=str(e),
                execution_time=execution_time,
                start_time=start_time,
                end_time=end_time
            )
    
    def _get_executor(self, execution_mode: str):
        """Get or create appropriate executor"""
        if execution_mode == "thread":
            if not self.thread_pool:
                self.thread_pool = ThreadPoolExecutor(
                    max_workers=self.max_threads,
                    thread_name_prefix="PentestWorker"
                )
            return self.thread_pool
        
        elif execution_mode == "process":
            if not self.process_pool:
                self.process_pool = ProcessPoolExecutor(
                    max_workers=self.max_processes
                )
            return self.process_pool
        
        else:
            raise PentestError(f"Unknown execution mode: {execution_mode}")
    
    def _adjust_pool_sizes(self, factor: float):
        """Adjust pool sizes based on available resources"""
        self.max_threads = max(1, int(self.max_threads * factor))
        self.max_processes = max(1, int(self.max_processes * factor))
        
        self.logger.info(f"Pool sizes adjusted: threads={self.max_threads}, processes={self.max_processes}")
    
    def _cleanup_pools(self):
        """Clean up executor pools"""
        if self.thread_pool:
            self.thread_pool.shutdown(wait=False)
            self.thread_pool = None
        
        if self.process_pool:
            self.process_pool.shutdown(wait=False)
            self.process_pool = None
    
    def execute_single_task(self, task_name: str, func: Callable, args: List[Any], 
                           timeout: Optional[int] = None) -> ExecutionResult:
        """
        Execute a single task with optional timeout
        
        Args:
            task_name: Name of the task
            func: Function to execute
            args: Function arguments
            timeout: Maximum execution time in seconds
            
        Returns:
            ExecutionResult object
        """
        self.logger.debug(f"Executing single task: {task_name}")
        
        executor = self._get_executor("thread")
        
        try:
            future = executor.submit(self._execute_task_wrapper, task_name, func, args)
            
            if timeout:
                result = future.result(timeout=timeout)
            else:
                result = future.result()
            
            return result
            
        except TimeoutError:
            return ExecutionResult(
                task_name=task_name,
                success=False,
                error=f"Task timed out after {timeout} seconds"
            )
        except Exception as e:
            return ExecutionResult(
                task_name=task_name,
                success=False,
                error=str(e)
            )
        finally:
            self._cleanup_pools()
    
    def get_active_tasks(self) -> List[str]:
        """Get list of currently running task names"""
        with self.lock:
            return list(self.active_futures.values())
    
    def cancel_all_tasks(self):
        """Cancel all active tasks"""
        with self.lock:
            for future in self.active_futures.keys():
                future.cancel()
            self.active_futures.clear()
        
        self.logger.info("All active tasks cancelled")
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        with self.lock:
            return {
                'tasks_completed': self.execution_stats['tasks_completed'],
                'tasks_failed': self.execution_stats['tasks_failed'],
                'total_execution_time': self.execution_stats['total_execution_time'],
                'active_tasks': len(self.active_futures),
                'success_rate': (
                    self.execution_stats['tasks_completed'] / 
                    max(1, self.execution_stats['tasks_completed'] + self.execution_stats['tasks_failed'])
                ) * 100,
                'average_execution_time': (
                    self.execution_stats['total_execution_time'] / 
                    max(1, self.execution_stats['tasks_completed'] + self.execution_stats['tasks_failed'])
                )
            }
    
    def wait_for_completion(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for all active tasks to complete
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if all tasks completed, False if timeout
        """
        start_time = time.time()
        
        while True:
            with self.lock:
                if not self.active_futures:
                    return True
            
            if timeout and (time.time() - start_time) > timeout:
                return False
            
            time.sleep(0.1)