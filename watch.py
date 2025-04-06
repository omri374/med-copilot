import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class RestartOnChange(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = self.start_process()

    def start_process(self):
        return subprocess.Popen([sys.executable, self.script])

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"🔄 {event.src_path} changed. Restarting...")
            self.process.terminate()
            self.process.wait()
            self.process = self.start_process()


if __name__ == "__main__":
    script_to_run = "medication_copilot.py"
    event_handler = RestartOnChange(script_to_run)
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
