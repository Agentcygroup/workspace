class SLI:
    def __init__(self, name, good, total):
        self.name = name
        self.good = good
        self.total = total
    def ratio(self):
        return self.good / self.total if self.total else 1.0

class SLO:
    def __init__(self, name, target):
        if not 0 <= target <= 1:
            raise ValueError("target must be in [0,1]")
        self.name = name
        self.target = target

class ErrorBudget:
    def __init__(self, slo):
        self.slo = slo
    def consumed(self, sli):
        allowed = 1.0 - self.slo.target
        if allowed == 0:
            return 0.0 if sli.ratio() >= 1.0 else 1.0
        bad = 1.0 - sli.ratio()
        return min(1.0, bad / allowed)
    def burn_rate(self, sli, window_hours):
        allowed = 1.0 - self.slo.target
        if allowed == 0 or window_hours <= 0:
            return float("inf") if sli.ratio() < 1.0 else 0.0
        return (1.0 - sli.ratio()) / allowed * (1.0 / window_hours)
