from threading import Thread, active_count
import time

class WorkerManager:
    def __init__(self, target_func):
        self._is_running = True
        self.worker_thread = Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        self.target_func = target_func

    def _worker(self):
        while self._is_running:
            try:
                self.target_func()
            except Exception as e:
                print(f"Error in worker thread: {e}")

    def stop_worker(self):
        self._is_running = False

    @staticmethod
    def get_active_thread_count():
        return active_count()




def main():
    while True:
        print("Thread main")
        print(f"Number of active threads: {WorkerManager.get_active_thread_count()}")
        time.sleep(5)

def thread_extra():
    print("Thread extra")
    print(f"Number of active threads: {WorkerManager.get_active_thread_count()}")
    time.sleep(1)

if __name__ == "__main__":
    worker_manager = WorkerManager(thread_extra)
    print(worker_manager.worker_thread)

    time.sleep(5)
    worker_manager.stop_worker()
    print(f"Kill thread: {worker_manager.worker_thread}")
    print(f"Number of active threads: {WorkerManager.get_active_thread_count()}")

    try:
        main()
    except KeyboardInterrupt:
        print("EXIT")