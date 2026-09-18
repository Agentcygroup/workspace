import hashlib, json, datetime
from dataclasses import dataclass, field
from policy import Policy, Rule, ALLOW, DENY

@dataclass
class AuditEntry:
    ts: str
    tenant: str
    decision: str
    rule: str
    reason: str
    ctx_hash: str

def _hash(o): return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

@dataclass
class Tenant:
    tenant_id: str
    policy: Policy

@dataclass
class Platform:
    tenants: dict = field(default_factory=dict)
    audit: list = field(default_factory=list)
    def register(self, tid, policy=None):
        if tid in self.tenants:
            raise ValueError("tenant exists: " + tid)
        self.tenants[tid] = Tenant(tid, policy or Policy(default=DENY))
        return self.tenants[tid]
    def evaluate(self, tid, ctx):
        t = self.tenants.get(tid)
        if t is None:
            raise KeyError("unknown tenant: " + tid)
        d = t.policy.evaluate(ctx)
        entry = AuditEntry(
            ts=datetime.datetime.now(datetime.UTC).isoformat(),
            tenant=tid, decision=d.effect, rule=d.rule_name,
            reason=d.reason, ctx_hash=_hash(ctx))
        self.audit.append(entry)
        return d
    def audit_report(self):
        by_tenant = {}
        by_decision = {}
        for e in self.audit:
            by_tenant[e.tenant] = by_tenant.get(e.tenant, 0) + 1
            by_decision[e.decision] = by_decision.get(e.decision, 0) + 1
        return {"total": len(self.audit), "by_tenant": by_tenant, "by_decision": by_decision}
