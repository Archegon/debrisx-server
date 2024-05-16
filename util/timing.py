import time

class TimingTest:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.started = False

    def start(self):
        self.start_time = time.time()
        self.started = True

    def stop(self):
        self.end_time = time.time()
        self.started = False

    def get_elapsed_time(self, log=True):
        if self.start_time is None or self.end_time is None:
            raise ValueError("Timing test not started or stopped")
        
        if log:
            print(f"Elapsed time for {self}: {self.end_time - self.start_time} seconds")
        return self.end_time - self.start_time