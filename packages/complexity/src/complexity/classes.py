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
    """Return True if a is at least as complex as b.

    RELATIONS is a list of (cheaper, more_expensive) pairs. To ask whether
    a dominates b, walk forward from b: if a appears on the path, then a
    is at least as expensive as b.
    """
    if a == b:
        return True
    frontier = [b]
    seen = set()
    while frontier:
        cur = frontier.pop()
        for x, y in RELATIONS:
            if x == cur and y not in seen:
                if y == a:
                    return True
                seen.add(y); frontier.append(y)
    return False

def is_class(name): return name in CLASSES
