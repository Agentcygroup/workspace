from dataclasses import dataclass, field

@dataclass
class Node:
    id: str
    children: list = field(default_factory=list)
    def add(self, child):
        self.children.append(child)
        return child
    def depth(self):
        return 0 if not self.children else 1 + max(c.depth() for c in self.children)
    def size(self):
        return 1 + sum(c.size() for c in self.children)

class Tree:
    def __init__(self, root):
        self.root = root
    def preorder(self):
        out = []
        def go(n):
            out.append(n.id)
            for c in n.children: go(c)
        go(self.root)
        return out
    def postorder(self):
        out = []
        def go(n):
            for c in n.children: go(c)
            out.append(n.id)
        go(self.root)
        return out
    def depth(self): return self.root.depth()
    def size(self): return self.root.size()
