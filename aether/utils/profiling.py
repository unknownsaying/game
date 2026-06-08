"""
Performance Profiling Tools
Timers, profiler, memory tracking
"""

import time
import functools
from collections import defaultdict
import numpy as np
import psutil
import os

class Timer:
    """Context manager and decorator for timing"""
    def __init__(self, name="", print_on_exit=False):
        self.name = name
        self.print_on_exit = print_on_exit
        self.start_time = None
        self.elapsed = 0.0
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self.start_time
        if self.print_on_exit:
            print(f"{self.name}: {self.elapsed*1000:.2f} ms")
    
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper

class Profiler:
    """Collects and reports timing statistics"""
    def __init__(self):
        self.records = defaultdict(list)
        self.start_times = {}
    
    def start(self, name):
        self.start_times[name] = time.perf_counter()
    
    def stop(self, name):
        if name in self.start_times:
            elapsed = time.perf_counter() - self.start_times[name]
            self.records[name].append(elapsed)
            del self.start_times[name]
    
    def profile(self, func):
        """Decorator to profile function"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.start(func.__name__)
            result = func(*args, **kwargs)
            self.stop(func.__name__)
            return result
        return wrapper
    
    def report(self):
        print("=== Profiler Report ===")
        for name, times in sorted(self.records.items()):
            if times:
                avg = np.mean(times) * 1000
                std = np.std(times) * 1000
                total = np.sum(times) * 1000
                count = len(times)
                print(f"{name}: avg={avg:.2f}ms, std={std:.3f}ms, total={total:.2f}ms, calls={count}")
    
    def reset(self):
        self.records.clear()
        self.start_times.clear()

class MemoryTracker:
    """Track memory usage"""
    @staticmethod
    def get_current_memory_usage():
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss / (1024 * 1024)  # MB
        return mem
    
    @staticmethod
    def get_system_memory():
        mem = psutil.virtual_memory()
        return {
            'total': mem.total / (1024**3),
            'available': mem.available / (1024**3),
            'percent': mem.percent
        }