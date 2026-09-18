CLASSES = [
    "O(1)","O(log n)","O(sqrt n)","O(n)","O(n log n)","O(n^2)","O(n^3)",
    "O(2^n)","O(n!)","O(n^n)","polynomial","exponential","undecidable"
]

RELATIONS = [
    ("O(1)","O(log n)"),
    ("O(log n)","O(sqrt n)"),
    ("O(sqrt n)","O(n)"),
    ("O(n)","O(n log n)"),
    ("O(n log n)","O(n^2)"),
    ("O(n^2)","O(n^3)"),
    ("O(n^3)","O(2^n)"),
    ("O(2^n)","O(n!)"),
    ("O(n!)","O(n^n)"),
    ("polynomial","exponential"),
]

class Class:
    def __init__(self, name):
        if name not in CLASSES:
            raise ValueError("unknown class: " + name)
        self.name = name

def dominates(a, b):
    if a == b:
        return True
    frontier = [a]
    seen = set()
    while frontier:
        cur = frontier.pop()
        for x, y in RELATIONS:
            if x == cur and y not in seen:
                if y == b:
                    return True
                seen.add(y); frontier.append(y)
    return False

def is_class(name): return name in CLASSES
