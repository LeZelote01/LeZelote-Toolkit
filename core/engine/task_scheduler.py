"""
Pentest-USB Toolkit - Task Scheduler
====================================

Advanced task scheduling system with priority queue, dependencies,
and intelligent resource allocation.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import time
import threading
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field

from ..utils.logging_handler import get_logger
from ..utils.error_handler import PentestError


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING = "waiting"


@dataclass
class Task:
    """Task definition with metadata"""
    id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    timeout: Optional[int] = None
    retries: int = 3
    
    # Runtime fields
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    attempt_count: int = 0


class TaskScheduler:
    """
    Advanced task scheduler with priority queue and dependency management.
    
    Features:
    - Priority-based task queuing
    - Dependency resolution
    - Retry mechanism with backoff
    - Timeout handling
    - Resource-aware scheduling
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize task scheduler
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        # Task storage
        self.tasks: Dict[str, Task] = {}
        self.task_queue = queue.PriorityQueue()
        self.completed_tasks: Dict[str, Task] = {}
        
        # Scheduling state
        self.running = False
        self.worker_threads = []
        self.max_workers = config.get('global', {}).get('max_concurrent_tasks', 4)
        
        # Synchronization
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        
        self.logger.info(f"TaskScheduler initialized with {self.max_workers} workers")
    
    def add_task(self, task: Task) -> str:
        """
        Add a task to the scheduler
        
        Args:
            task: Task object to schedule
            
        Returns:
            str: Task ID
        """
        with self.lock:
            # Validate dependencies
            for dep_id in task.dependencies:
                if dep_id not in self.tasks and dep_id not in self.completed_tasks:
                    raise PentestError(f"Dependency not found: {dep_id}")
            
            self.tasks[task.id] = task
            
            # Check if task can be queued immediately
            if self._can_execute_task(task):
                self._queue_task(task)
            
            self.logger.debug(f"Task added: {task.name} (ID: {task.id})")
            
            # Notify waiting threads
            self.condition.notify_all()
            
        return task.id
    
    def _can_execute_task(self, task: Task) -> bool:
        """Check if task dependencies are satisfied"""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
            if self.completed_tasks[dep_id].status != TaskStatus.COMPLETED:
                return False
        return True
    
    def _queue_task(self, task: Task):
        """Add task to priority queue"""
        # Use negative priority for max-heap behavior
        priority_value = -task.priority.value
        timestamp = task.created_at.timestamp()
        
        # Queue item: (priority, timestamp, task_id)
        self.task_queue.put((priority_value, timestamp, task.id))
        task.status = TaskStatus.PENDING
    
    def start_scheduler(self):
        """Start the task scheduler with worker threads"""
        if self.running:
            return
        
        self.running = True
        self.logger.info("Starting task scheduler")
        
        # Start worker threads
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_thread, 
                name=f"TaskWorker-{i+1}",
                daemon=True
            )
            worker.start()
            self.worker_threads.append(worker)
        
        self.logger.info(f"Started {len(self.worker_threads)} worker threads")
    
    def stop_scheduler(self, timeout: int = 30):
        """Stop the task scheduler gracefully"""
        self.logger.info("Stopping task scheduler")
        self.running = False
        
        # Wake up all waiting threads
        with self.condition:
            self.condition.notify_all()
        
        # Wait for workers to finish
        for worker in self.worker_threads:
            worker.join(timeout=timeout)
        
        self.worker_threads.clear()
        self.logger.info("Task scheduler stopped")
    
    def _worker_thread(self):
        """Worker thread that executes tasks"""
        thread_name = threading.current_thread().name
        self.logger.debug(f"Worker thread {thread_name} started")
        
        while self.running:
            try:
                # Get next task from queue
                try:
                    priority, timestamp, task_id = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Execute the task
                with self.lock:
                    if task_id not in self.tasks:
                        continue
                    task = self.tasks[task_id]
                
                self._execute_task(task)
                
                # Check for newly executable tasks
                self._check_dependent_tasks()
                
            except Exception as e:
                self.logger.error(f"Worker thread error: {str(e)}")
        
        self.logger.debug(f"Worker thread {thread_name} stopped")
    
    def _execute_task(self, task: Task):
        """Execute a single task with timeout and retry logic"""
        self.logger.info(f"Executing task: {task.name} (ID: {task.id})")
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        task.attempt_count += 1
        
        try:
            # Execute task function with timeout
            if task.timeout:
                result = self._execute_with_timeout(task)
            else:
                result = task.func(*task.args, **task.kwargs)
            
            # Task completed successfully
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            # Move to completed tasks
            with self.lock:
                self.completed_tasks[task.id] = task
                del self.tasks[task.id]
            
            duration = (task.completed_at - task.started_at).total_seconds()
            self.logger.info(f"Task completed: {task.name} in {duration:.2f}s")
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Task failed: {task.name} - {error_msg}")
            
            # Handle retry logic
            if task.attempt_count < task.retries:
                self.logger.info(f"Retrying task: {task.name} (attempt {task.attempt_count + 1}/{task.retries})")
                
                # Add delay before retry (exponential backoff)
                delay = 2 ** task.attempt_count
                time.sleep(min(delay, 60))  # Cap at 60 seconds
                
                # Re-queue the task
                task.status = TaskStatus.PENDING
                self._queue_task(task)
            else:
                # Task failed permanently
                task.status = TaskStatus.FAILED
                task.error = error_msg
                task.completed_at = datetime.now()
                
                with self.lock:
                    self.completed_tasks[task.id] = task
                    del self.tasks[task.id]
    
    def _execute_with_timeout(self, task: Task) -> Any:
        """Execute task with timeout using threading"""
        result = None
        exception = None
        
        def target():
            nonlocal result, exception
            try:
                result = task.func(*task.args, **task.kwargs)
            except Exception as e:
                exception = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=task.timeout)
        
        if thread.is_alive():
            # Timeout occurred
            raise TimeoutError(f"Task {task.name} timed out after {task.timeout} seconds")
        
        if exception:
            raise exception
        
        return result
    
    def _check_dependent_tasks(self):
        """Check if any waiting tasks can now be executed"""
        with self.lock:
            for task in list(self.tasks.values()):
                if task.status == TaskStatus.WAITING and self._can_execute_task(task):
                    self._queue_task(task)
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get status of a specific task"""
        with self.lock:
            if task_id in self.tasks:
                return self.tasks[task_id].status
            elif task_id in self.completed_tasks:
                return self.completed_tasks[task_id].status
        return None
    
    def get_task_result(self, task_id: str) -> Any:
        """Get result of a completed task"""
        with self.lock:
            if task_id in self.completed_tasks:
                task = self.completed_tasks[task_id]
                if task.status == TaskStatus.COMPLETED:
                    return task.result
                elif task.status == TaskStatus.FAILED:
                    raise PentestError(f"Task {task.name} failed: {task.error}")
        raise PentestError(f"Task {task_id} not found or not completed")
    
    def wait_for_completion(self, task_ids: List[str] = None, timeout: Optional[int] = None) -> bool:
        """
        Wait for specified tasks to complete
        
        Args:
            task_ids: List of task IDs to wait for (None = all tasks)
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if all tasks completed, False if timeout
        """
        start_time = datetime.now()
        
        while True:
            with self.lock:
                if task_ids:
                    # Check specific tasks
                    all_completed = all(
                        tid in self.completed_tasks for tid in task_ids
                    )
                else:
                    # Check all tasks
                    all_completed = len(self.tasks) == 0
                
                if all_completed:
                    return True
            
            # Check timeout
            if timeout and (datetime.now() - start_time).total_seconds() > timeout:
                return False
            
            time.sleep(0.1)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.CANCELLED
                    del self.tasks[task_id]
                    self.completed_tasks[task_id] = task
                    self.logger.info(f"Task cancelled: {task.name}")
                    return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        with self.lock:
            pending_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
            running_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
            completed_count = sum(1 for t in self.completed_tasks.values() if t.status == TaskStatus.COMPLETED)
            failed_count = sum(1 for t in self.completed_tasks.values() if t.status == TaskStatus.FAILED)
            
            return {
                'pending_tasks': pending_count,
                'running_tasks': running_count,
                'completed_tasks': completed_count,
                'failed_tasks': failed_count,
                'total_tasks': len(self.tasks) + len(self.completed_tasks),
                'queue_size': self.task_queue.qsize(),
                'active_workers': len(self.worker_threads)
            }