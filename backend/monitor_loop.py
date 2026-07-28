# monitor_loop.py
import threading
import time
import subprocess
import os
import monitor as sql
from misc import parseIntoJson

class SimpleMonitor:
    def __init__(self, interval=60):
        self.interval = interval
        self.courses = set()
        self.running = True
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.script_path = os.path.join(self.script_dir, 'fetch_group.sh')
        self.thread = None
    
    def add_course(self, clave):
        self.courses.add(clave)
        if self.thread is None or not self.thread.is_alive():
            self.start()
    
    def check_all(self):
        for clave in list(self.courses):
            try:
                result = subprocess.run(
                    [self.script_path, str(clave)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.script_dir
                )
                if result.returncode == 0:
                    data = parseIntoJson(clave)
                    if data:
                        sql.add_course(clave, data)
                        print(f"✅ Updated {clave}")
            except Exception as e:
                print(f"❌ Error checking {clave}: {e}")
    
    def run(self):
        while self.running:
            self.check_all()
            time.sleep(self.interval)
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

# Global instance
monitor = SimpleMonitor()