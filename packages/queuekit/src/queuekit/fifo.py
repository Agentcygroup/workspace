from collections import deque

class QueueFull(Exception): pass
class QueueEmpty(Exception): pass

class FIFO:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.q = deque()
    def push(self, item):
        if len(self.q) >= self.capacity:
            raise QueueFull("queue at capacity " + str(self.capacity))
        self.q.append(item)
        return item
    def pop(self):
        if not self.q:
            raise QueueEmpty("empty queue")
        return self.q.popleft()
    def size(self): return len(self.q)
    def is_full(self): return len(self.q) >= self.capacity
    def is_empty(self): return len(self.q) == 0
