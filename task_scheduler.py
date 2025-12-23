"""
Task scheduler and queue system for PassportApp
Handle background tasks and scheduled jobs
"""

from datetime import datetime, timedelta
import time
import threading
from queue import Queue, PriorityQueue
from functools import wraps
import schedule


class TaskQueue:
    """Task queue for background job processing"""
    
    def __init__(self, max_workers=4):
        self.queue = Queue()
        self.priority_queue = PriorityQueue()
        self.max_workers = max_workers
        self.workers = []
        self.running = False
        self.completed_tasks = []
        self.failed_tasks = []
    
    def start(self):
        """Start task queue workers"""
        if self.running:
            return
        
        self.running = True
        
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """Stop task queue workers"""
        self.running = False
        
        for _ in range(self.max_workers):
            self.queue.put(None)
    
    def _worker(self):
        """Worker thread to process tasks"""
        while self.running:
            task = self.queue.get()
            
            if task is None:
                break
            
            try:
                task_id, func, args, kwargs = task
                
                result = func(*args, **kwargs)
                
                self.completed_tasks.append({
                    'task_id': task_id,
                    'completed_at': datetime.utcnow().isoformat(),
                    'result': result
                })
            
            except Exception as e:
                self.failed_tasks.append({
                    'task_id': task_id,
                    'failed_at': datetime.utcnow().isoformat(),
                    'error': str(e)
                })
            
            finally:
                self.queue.task_done()
    
    def enqueue(self, func, *args, **kwargs):
        """Add task to queue"""
        task_id = f"task_{int(time.time() * 1000)}"
        self.queue.put((task_id, func, args, kwargs))
        return task_id
    
    def enqueue_priority(self, priority, func, *args, **kwargs):
        """Add priority task to queue (lower number = higher priority)"""
        task_id = f"priority_task_{int(time.time() * 1000)}"
        self.priority_queue.put((priority, task_id, func, args, kwargs))
        return task_id
    
    def get_stats(self):
        """Get queue statistics"""
        return {
            'queue_size': self.queue.qsize(),
            'priority_queue_size': self.priority_queue.qsize(),
            'workers': len(self.workers),
            'completed': len(self.completed_tasks),
            'failed': len(self.failed_tasks),
            'running': self.running
        }


class TaskScheduler:
    """Schedule recurring tasks"""
    
    def __init__(self):
        self.jobs = []
        self.running = False
        self.scheduler_thread = None
    
    def start(self):
        """Start scheduler"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def stop(self):
        """Stop scheduler"""
        self.running = False
    
    def _run_scheduler(self):
        """Run scheduler loop"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def schedule_daily(self, time_str, func, *args, **kwargs):
        """Schedule daily task"""
        job = schedule.every().day.at(time_str).do(func, *args, **kwargs)
        self.jobs.append(job)
        return job
    
    def schedule_hourly(self, func, *args, **kwargs):
        """Schedule hourly task"""
        job = schedule.every().hour.do(func, *args, **kwargs)
        self.jobs.append(job)
        return job
    
    def schedule_interval(self, minutes, func, *args, **kwargs):
        """Schedule task at interval"""
        job = schedule.every(minutes).minutes.do(func, *args, **kwargs)
        self.jobs.append(job)
        return job
    
    def schedule_weekly(self, day, time_str, func, *args, **kwargs):
        """Schedule weekly task"""
        day_map = {
            'monday': schedule.every().monday,
            'tuesday': schedule.every().tuesday,
            'wednesday': schedule.every().wednesday,
            'thursday': schedule.every().thursday,
            'friday': schedule.every().friday,
            'saturday': schedule.every().saturday,
            'sunday': schedule.every().sunday
        }
        
        if day.lower() in day_map:
            job = day_map[day.lower()].at(time_str).do(func, *args, **kwargs)
            self.jobs.append(job)
            return job
        
        return None
    
    def clear_jobs(self):
        """Clear all scheduled jobs"""
        schedule.clear()
        self.jobs.clear()
    
    def get_jobs(self):
        """Get all scheduled jobs"""
        return [
            {
                'job': str(job.job_func),
                'next_run': str(job.next_run),
                'interval': str(job.interval)
            }
            for job in self.jobs
        ]


# Global instances
task_queue = TaskQueue()
task_scheduler = TaskScheduler()


def background_task(func):
    """Decorator to run function as background task"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return task_queue.enqueue(func, *args, **kwargs)
    return wrapper


def scheduled_task(schedule_type, **schedule_kwargs):
    """Decorator to schedule recurring task"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if schedule_type == 'daily':
                return task_scheduler.schedule_daily(
                    schedule_kwargs.get('time', '00:00'),
                    func, *args, **kwargs
                )
            elif schedule_type == 'hourly':
                return task_scheduler.schedule_hourly(func, *args, **kwargs)
            elif schedule_type == 'interval':
                return task_scheduler.schedule_interval(
                    schedule_kwargs.get('minutes', 60),
                    func, *args, **kwargs
                )
            elif schedule_type == 'weekly':
                return task_scheduler.schedule_weekly(
                    schedule_kwargs.get('day', 'monday'),
                    schedule_kwargs.get('time', '00:00'),
                    func, *args, **kwargs
                )
        return wrapper
    return decorator


# Common scheduled tasks
def cleanup_old_data():
    """Cleanup old data - scheduled task"""
    from backup_manager import backup_manager
    
    # Cleanup old backups (30 days)
    removed = backup_manager.cleanup_old_backups(30)
    
    # Cleanup cache
    from cache_utils import cleanup_all_caches
    cleanup_all_caches()
    
    # Cleanup rate limiter
    from rate_limiter import cleanup_rate_limiter
    cleanup_rate_limiter()
    
    return f'Cleanup completed: {removed} old backups removed'


def daily_backup():
    """Create daily backup - scheduled task"""
    from backup_manager import create_automated_backup
    
    result = create_automated_backup()
    return result


def monitor_system_health():
    """Monitor system health - scheduled task"""
    from health_monitor import health_checker
    
    health = health_checker.comprehensive_health_check()
    
    if health['overall_status'] in ['critical', 'unhealthy']:
        # Send alert
        print(f"ALERT: System health is {health['overall_status']}")
    
    return health


def sync_blockchain_data():
    """Sync blockchain data - scheduled task"""
    # Implement blockchain sync logic
    return 'Blockchain data synced'


def initialize_tasks():
    """Initialize all scheduled tasks"""
    # Start queue and scheduler
    task_queue.start()
    task_scheduler.start()
    
    # Schedule tasks
    task_scheduler.schedule_daily('02:00', daily_backup)
    task_scheduler.schedule_daily('03:00', cleanup_old_data)
    task_scheduler.schedule_interval(15, monitor_system_health)
    task_scheduler.schedule_hourly(sync_blockchain_data)
    
    return True


def shutdown_tasks():
    """Shutdown task queue and scheduler"""
    task_queue.stop()
    task_scheduler.stop()
