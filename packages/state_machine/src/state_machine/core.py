class TransitionError(Exception):
    pass

class Machine:
    def __init__(self, initial):
        self.state = initial
        self.initial = initial
        self.transitions = {}
        self.history = [{"from": None, "to": initial, "event": "init"}]
        self.effects = []

    def on(self, src, event, dst, guard=None, effect=None):
        self.transitions.setdefault((src, event), []).append({"dst": dst, "guard": guard, "effect": effect})
        return self

    def fire(self, event, ctx=None):
        ctx = ctx or {}
        key = (self.state, event)
        if key not in self.transitions:
            raise TransitionError("no transition from " + self.state + " on " + event)
        for t in self.transitions[key]:
            if t["guard"] is None or t["guard"](ctx):
                self.state = t["dst"]
                if t["effect"]:
                    r = t["effect"](ctx)
                    self.effects.append({"event": event, "result": r})
                self.history.append({"from": self.history[-1]["to"], "to": self.state, "event": event})
                return self.state
        raise TransitionError("no guard satisfied")

    def reset(self):
        self.state = self.initial
        self.history.append({"from": None, "to": self.initial, "event": "reset"})
