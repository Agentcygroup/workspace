class CycleError(Exception):
    pass

class DAG:
    def __init__(self):
        self.nodes = set()
        self.edges = []
        self.incoming = {}

    def add_node(self, n):
        self.nodes.add(n)
        self.incoming.setdefault(n, [])
        return n

    def add_edge(self, src, dst):
        self.add_node(src); self.add_node(dst)
        self.edges.append((src, dst))
        self.incoming[dst].append(src)
        return (src, dst)

    def topo(self):
        incoming = {n: list(self.incoming[n]) for n in self.nodes}
        ready = [n for n in self.nodes if not incoming[n]]
        order = []
        while ready:
            n = ready.pop(0)
            order.append(n)
            for s, d in self.edges:
                if s == n and d in incoming:
                    incoming[d].remove(s)
                    if not incoming[d] and d not in order:
                        ready.append(d)
        if len(order) != len(self.nodes):
            raise CycleError("cycle detected")
        return order

    def has_cycle(self):
        try:
            self.topo(); return False
        except CycleError:
            return True
