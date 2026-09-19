"""Enterprise framework vocabulary as terms in the substrate.

Reads the thirty-layer vocabulary (lexical, semantic, ontological,
...) and constructs each layer as a term: an axiom naming the layer,
a collection of the layer's primitives, and an invariant that checks
the layer's cardinality.

Uses only the nine primitives and six constructors already in
substrate/__init__.py. Adds nothing to the kernel.

Each layer is one term of type `layer:<name>`. Each layer's items are
terms of type `layer:<name>:<item>`. The whole enterprise vocabulary
is one term: the collection of thirty layers.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from substrate import (
    Term, atom, collection, grammar, axiom, invariant, structure,
)


LAYERS: dict[str, tuple[str, ...]] = {
    "lexical":       ("Prefix", "Root", "Suffix", "Language", "Etymology",
                      "Acronym", "Naming convention"),
    "semantic":      ("Meaning", "Intent", "Purpose", "Context",
                      "Abstraction", "Interpretation"),
    "ontological":   ("Entity", "Object", "Event", "Process", "Property",
                      "Relation", "State", "Resource", "Agent"),
    "epistemic":     ("Observation", "Evidence", "Confidence", "Provenance",
                      "Verification", "Falsifiability", "Uncertainty"),
    "logical":       ("Axioms", "Rules", "Inference", "Proof",
                      "Consistency", "Completeness", "Decidability"),
    "mathematical":  ("Algebra", "Geometry", "Topology", "Analysis",
                      "Statistics", "Optimization", "Category theory",
                      "Graph theory"),
    "structural":    ("Tree", "Graph", "Lattice", "Matrix", "Hypergraph",
                      "Mesh", "Pipeline", "Network"),
    "functional":    ("Input", "Output", "Behavior", "Capability",
                      "Responsibility", "Contract"),
    "behavioral":    ("Deterministic", "Stochastic", "Adaptive",
                      "Autonomous", "Reactive", "Proactive", "Emergent"),
    "temporal":      ("Lifetime", "Ordering", "Frequency", "Duration",
                      "Version", "Evolution"),
    "spatial":       ("Location", "Region", "Scale", "Topology",
                      "Locality", "Distribution"),
    "computational": ("Complexity", "Performance", "Scalability",
                      "Parallelism", "Distribution", "Resources"),
    "information":   ("Entropy", "Compression", "Encoding",
                      "Representation", "Fidelity", "Redundancy"),
    "operational":   ("Design", "Build", "Test", "Deploy", "Operate",
                      "Monitor", "Optimize", "Retire"),
    "security":      ("Identity", "Authentication", "Authorization",
                      "Confidentiality", "Integrity", "Availability",
                      "Non-repudiation"),
    "trust":         ("Attestation", "Provenance", "Reputation",
                      "Certification", "Supply chain"),
    "governance":    ("Policy", "Compliance", "Risk", "Audit",
                      "Standards", "Ethics", "Regulation"),
    "legal":         ("Jurisdiction", "Copyright", "Copyleft", "Patents",
                      "Trademarks", "Licensing", "Contracts"),
    "economic":      ("Cost", "Value", "Incentives", "Budget", "Revenue",
                      "Market"),
    "organizational": ("Roles", "Teams", "Ownership", "Authority",
                       "Stakeholders", "Responsibilities"),
    "lifecycle":     ("Discovery", "Specification", "Design", "Development",
                      "Validation", "Deployment", "Maintenance", "Retirement"),
    "physical":      ("Hardware", "Materials", "Energy", "Manufacturing",
                      "Environment"),
    "biological":    ("Organism", "Evolution", "Genetics", "Ecology"),
    "social":        ("Culture", "Communication", "Collaboration",
                      "Institutions", "Networks"),
    "cognitive":     ("Knowledge", "Learning", "Memory", "Reasoning",
                      "Decision-making"),
    "domain":        ("Medicine", "Finance", "Law", "Education",
                      "Aerospace", "Agriculture", "Manufacturing",
                      "Telecommunications"),
    "quality":       ("Correctness", "Reliability", "Maintainability",
                      "Portability", "Interoperability", "Usability"),
    "interface":     ("API", "Protocol", "Schema", "Contract", "Message",
                      "UI"),
    "dependency":    ("Composition", "Inheritance", "Coupling", "Cohesion",
                      "Imports", "References"),
    "change":        ("Versioning", "Configuration", "Migration",
                      "Evolution", "Deprecation"),
}


def build_layer(name: str, items: tuple[str, ...]) -> Term:
    """One layer: a collection of items, each an axiom of the layer.

    The layer's type is `structure:layer:<name>`. Its body is a tuple
    of terms, one per item. Each item is a term of type
    `axiom:layer:<name>:<item>`.
    """
    item_terms = tuple(
        axiom(f"layer:{name}:{i}") for i in items
    )
    # Wrap the items in a term whose body is the tuple itself, so that
    # len(layer.body) is the item count, not a dict length.
    layer = collection(*item_terms)
    return Term(
        id=layer.id,
        kind=layer.kind,
        body=layer.body,
        type=f"structure:layer:{name}",
        derivation=layer.derivation,
    )


LAYER_TERMS: dict[str, Term] = {
    name: build_layer(name, items) for name, items in LAYERS.items()
}


ENTERPRISE_VOCABULARY = collection(*LAYER_TERMS.values())


def check() -> tuple[bool, str]:
    total_layers = len(LAYER_TERMS)
    total_items = sum(len(v.body) for v in LAYER_TERMS.values())
    for name, term in LAYER_TERMS.items():
        if not term.type.startswith(f"structure:layer:{name}"):
            return False, f"layer type wrong: {name} -> {term.type}"
        if len(term.body) != len(LAYERS[name]):
            return False, f"layer count wrong: {name}"
    return True, (
        f"layers={total_layers} items={total_items} "
        f"enterprise_terms={len(ENTERPRISE_VOCABULARY.body)}"
    )


def _main() -> int:
    for name, term in LAYER_TERMS.items():
        print(f"  {name:18} {len(term.body):2} items   type={term.type}")
    print()
    ok, reason = check()
    print(f"INVARIANTS: {'hold' if ok else 'FAIL'}")
    print(f"  {reason}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_main())
