"""
Background worker queue system for PassportApp
Process long-running tasks asynchronously
"""

from threading import Thread
import queue
import time
from datetime import datetime
import traceback
import json


class TaskPriority:
    """Task priority levels"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class Task:
    """Background task"""
    
    def __init__(self, task_id, func, args=None, kwargs=None, priority=TaskPriority.NORMAL):
        self.task_id = task_id
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.priority = priority
        self.status = 'pending'
        self.result = None
        self.error = None
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.attempts = 0
        self.max_attempts = 3
    
    def execute(self):
        """Execute the task"""
        self.attempts += 1
        self.started_at = datetime.utcnow()
        self.status = 'running'
        
        try:
            self.result = self.func(*self.args, **self.kwargs)
            self.status = 'completed'
            self.completed_at = datetime.utcnow()
            return True
        
        except Exception as e:
            self.error = str(e)
            self.status = 'failed'
            self.completed_at = datetime.utcnow()
            print(f"Task {self.task_id} failed: {e}")
            traceback.print_exc()
            return False
    
    def should_retry(self):
        """Check if task should be retried"""
        return self.status == 'failed' and self.attempts < self.max_attempts
    
    def __lt__(self, other):
        """Compare tasks by priority for priority queue"""
        return self.priority > other.priority


class WorkerQueue:
    """Queue for background tasks"""
    
    def __init__(self, num_workers=4):
        self.queue = queue.PriorityQueue()
        self.workers = []
        self.num_workers = num_workers
        self.running = False
        self.tasks = {}
        self.completed_tasks = []
        self.max_completed = 1000
    
    def start(self):
        """Start worker threads"""
        self.running = True
        
        for i in range(self.num_workers):
            worker = Thread(target=self._worker, name=f'Worker-{i}')
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
        
        print(f"Started {self.num_workers} worker threads")
    
    def stop(self):
        """Stop worker threads"""
        print("Stopping worker threads...")
        self.running = False
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5)
        
        print("All workers stopped")
    
    def _worker(self):
        """Worker thread for processing tasks"""
        while self.running:
            try:
                # Get task from queue (with timeout to allow checking running flag)
                priority, task = self.queue.get(timeout=1)
                
                # Execute task
                success = task.execute()
                
                # Retry if needed
                if not success and task.should_retry():
                    print(f"Retrying task {task.task_id} (attempt {task.attempts + 1}/{task.max_attempts})")
                    time.sleep(2 ** task.attempts)  # Exponential backoff
                    self.queue.put((task.priority, task))
                else:
                    # Move to completed
                    self._complete_task(task)
                
                self.queue.task_done()
            
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in worker thread: {e}")
                traceback.print_exc()
    
    def _complete_task(self, task):
        """Mark task as completed"""
        if task.task_id in self.tasks:
            del self.tasks[task.task_id]
        
        self.completed_tasks.append(task)
        
        # Trim completed tasks
        if len(self.completed_tasks) > self.max_completed:
            self.completed_tasks = self.completed_tasks[-self.max_completed:]
    
    def enqueue(self, task):
        """Add task to queue"""
        self.tasks[task.task_id] = task
        self.queue.put((task.priority, task))
        return task.task_id
    
    def get_task_status(self, task_id):
        """Get status of a task"""
        # Check active tasks
        if task_id in self.tasks:
            return self.tasks[task_id]
        
        # Check completed tasks
        for task in reversed(self.completed_tasks):
            if task.task_id == task_id:
                return task
        
        return None
    
    def get_queue_stats(self):
        """Get queue statistics"""
        total_completed = len(self.completed_tasks)
        successful = sum(1 for t in self.completed_tasks if t.status == 'completed')
        failed = sum(1 for t in self.completed_tasks if t.status == 'failed')
        
        return {
            'active': len(self.tasks),
            'queued': self.queue.qsize(),
            'completed': total_completed,
            'successful': successful,
            'failed': failed,
            'workers': self.num_workers
        }
    
    def get_pending_tasks(self):
        """Get list of pending tasks"""
        return [task for task in self.tasks.values() if task.status == 'pending']
    
    def get_running_tasks(self):
        """Get list of running tasks"""
        return [task for task in self.tasks.values() if task.status == 'running']


class BackgroundTaskManager:
    """Manage background tasks"""
    
    def __init__(self, num_workers=4):
        self.queue = WorkerQueue(num_workers)
        self.task_counter = 0
    
    def start(self):
        """Start task processing"""
        self.queue.start()
    
    def stop(self):
        """Stop task processing"""
        self.queue.stop()
    
    def submit_task(self, func, *args, priority=TaskPriority.NORMAL, **kwargs):
        """Submit a task for background processing"""
        self.task_counter += 1
        task_id = f"task_{self.task_counter}_{int(time.time())}"
        
        task = Task(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority
        )
        
        self.queue.enqueue(task)
        return task_id
    
    def get_task_result(self, task_id):
        """Get result of a task"""
        task = self.queue.get_task_status(task_id)
        
        if not task:
            return None
        
        if task.status == 'completed':
            return task.result
        elif task.status == 'failed':
            raise Exception(f"Task failed: {task.error}")
        else:
            return None  # Still running or pending
    
    def wait_for_task(self, task_id, timeout=60):
        """Wait for task to complete"""
        start = time.time()
        
        while time.time() - start < timeout:
            task = self.queue.get_task_status(task_id)
            
            if not task:
                return None
            
            if task.status in ['completed', 'failed']:
                return task
            
            time.sleep(0.1)
        
        return None
    
    def get_stats(self):
        """Get task manager statistics"""
        return self.queue.get_queue_stats()


# Global task manager
task_manager = None


def init_background_workers(num_workers=4):
    """Initialize background worker system"""
    global task_manager
    task_manager = BackgroundTaskManager(num_workers)
    task_manager.start()
    return task_manager


def submit_background_task(func, *args, priority=TaskPriority.NORMAL, **kwargs):
    """Submit a task for background processing"""
    if not task_manager:
        raise RuntimeError("Background worker system not initialized")
    
    return task_manager.submit_task(func, *args, priority=priority, **kwargs)


# Example background tasks
def process_passport_image(passport_id, image_path):
    """Process passport image in background"""
    print(f"Processing image for passport {passport_id}: {image_path}")
    time.sleep(2)  # Simulate processing
    return {'status': 'success', 'passport_id': passport_id}


def generate_nft_metadata(nft_id, passport_data):
    """Generate NFT metadata in background"""
    print(f"Generating metadata for NFT {nft_id}")
    
    metadata = {
        'name': f"Passport NFT #{nft_id}",
        'description': f"Digital passport for {passport_data.get('first_name')} {passport_data.get('last_name')}",
        'attributes': [
            {'trait_type': 'Nationality', 'value': passport_data.get('nationality')},
            {'trait_type': 'Issue Date', 'value': passport_data.get('issue_date')},
            {'trait_type': 'Expiry Date', 'value': passport_data.get('expiry_date')}
        ]
    }
    
    time.sleep(1)  # Simulate metadata generation
    return metadata


def upload_to_ipfs(file_path):
    """Upload file to IPFS in background"""
    print(f"Uploading to IPFS: {file_path}")
    time.sleep(3)  # Simulate upload
    return {'ipfs_hash': 'QmExample...', 'url': 'https://ipfs.io/ipfs/QmExample...'}


def send_notification_email(user_email, subject, message):
    """Send email notification in background"""
    print(f"Sending email to {user_email}: {subject}")
    time.sleep(1)  # Simulate email sending
    return {'status': 'sent', 'recipient': user_email}


def verify_blockchain_transaction(tx_hash):
    """Verify blockchain transaction in background"""
    print(f"Verifying transaction: {tx_hash}")
    time.sleep(5)  # Simulate blockchain query
    return {
        'confirmed': True,
        'block_number': 12345678,
        'status': 'success'
    }


def generate_analytics_report(user_id, date_range):
    """Generate analytics report in background"""
    print(f"Generating analytics for user {user_id}")
    time.sleep(10)  # Simulate report generation
    return {
        'user_id': user_id,
        'total_passports': 5,
        'total_nfts': 3,
        'transactions': 15
    }


def backup_database():
    """Backup database in background"""
    print("Creating database backup...")
    time.sleep(8)  # Simulate backup
    return {
        'status': 'success',
        'backup_file': f'backup_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.sql',
        'size_mb': 125
    }


def cleanup_old_files(days=30):
    """Clean up old files in background"""
    print(f"Cleaning up files older than {days} days")
    time.sleep(3)  # Simulate cleanup
    return {
        'files_deleted': 42,
        'space_freed_mb': 256
    }
