"""
Scheduler for automated checks
"""
import time
from datetime import datetime

class CMHPScheduler:
    def __init__(self):
        self.tasks = []
        self.running = False
    
    def add_task(self, name, interval_seconds, function):
        """Add a scheduled task"""
        self.tasks.append({
            'name': name,
            'interval': interval_seconds,
            'function': function,
            'last_run': None
        })
    
    def run_once(self):
        """Run all tasks once"""
        results = []
        for task in self.tasks:
            try:
                print(f"Running task: {task['name']}")
                result = task['function']()
                task['last_run'] = datetime.utcnow().isoformat()
                results.append({
                    'task': task['name'],
                    'success': True,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'task': task['name'],
                    'success': False,
                    'error': str(e)
                })
        return results
    
    def start(self, interval_seconds=300):
        """Start continuous scheduling (mock for now)"""
        print(f"Scheduler starting with {interval_seconds}s interval")
        self.running = True
        return {'status': 'mock_mode', 'interval': interval_seconds}

# Example tasks
def check_health_task():
    return {'system': 'health', 'status': 'checked'}

def check_ebay_task():
    return {'system': 'ebay', 'status': 'checked'}

def check_finances_task():
    return {'system': 'finances', 'status': 'checked'}

# Global scheduler
scheduler = CMHPScheduler()
scheduler.add_task('health_check', 300, check_health_task)
scheduler.add_task('ebay_check', 600, check_ebay_task)
scheduler.add_task('finance_check', 1800, check_finances_task)
