from dataclasses import dataclass, field
from .dp import dp_mean

@dataclass
class Client:
    client_id: str
    vector: list

@dataclass
class FederatedRound:
    clients: list = field(default_factory=list)
    rounds: int = 0
    history: list = field(default_factory=list)
    def add_client(self, cid, vector):
        self.clients.append(Client(cid, vector))
        return self.clients[-1]
    def aggregate(self, bound=1.0, sigma=0.01):
        vectors = [c.vector for c in self.clients]
        if not vectors:
            raise ValueError("no clients")
        agg = dp_mean(vectors, bound, sigma)
        self.rounds += 1
        self.history.append({"round": self.rounds, "aggregate": agg, "clients": len(self.clients)})
        return agg
