"""Graph acronyms and the minimal kernel, as terms in the substrate.

The document names ~250 graph acronyms (DAG, DCG, UG, DG, BN, MRF, ...)
and the kernel K = (Distinction, Persistence, Linkage, Transformation,
Evidence), plus the executable representation X = (ID, STATE, REL,
PROC, EVID) and the update equation X_{t+1} = F(X_t).

This file constructs:

  GRAPH_ACRONYMS  — one term per acronym, of type `graph:<id>`
  KERNEL          — the kernel as a term
  OBSERVABLE      — X = (ID, STATE, REL, PROC, EVID)
  F               — the update function as a term, composable

It uses only the nine primitives and six constructors in
substrate/__init__.py. Adds nothing to the kernel.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from substrate import (
    Term, Refusal, atom, compose, product, collection, axiom, function,
)


GRAPH_NAMES: tuple[str, ...] = (
    "DAG", "DCG", "UDAG", "UG", "DG", "MDAG", "PDAG", "CPDAG",
    "ADMG", "MAG", "PAG", "CG", "FG", "HG", "DHG", "BG", "MPG",
    "Kn", "Null", "Tree-Rooted", "Tree-Unrooted", "Forest",
    "Arborescence", "Polytree", "SPG", "Planar", "Dual", "Line",
    "Clique", "Intersection", "Interval", "Chordal", "Circular-Arc",
    "Permutation", "Comparability", "Co-comparability", "Distance",
    "UnitDisk", "Geometric", "Random", "SmallWorld", "ScaleFree",
    "Expander", "Cayley", "DeBruijn", "Kautz", "Hypercube", "Grid",
    "Lattice", "TensorProduct", "CartesianProduct", "StrongProduct",
    "LexicographicProduct", "FlowNetwork", "Residual", "StateTransition",
    "CFG", "DFG", "PDG", "SDG", "CallGraph", "Interprocedural",
    "ExecutionGraph", "TaskGraph", "JobGraph", "WorkflowGraph",
    "BuildGraph", "DependencyGraph", "KnowledgeGraph", "SemanticGraph",
    "PropertyGraph", "LabeledGraph", "AttributedGraph", "Heterogeneous",
    "Homogeneous", "DynamicGraph", "TemporalGraph", "StreamingGraph",
    "ProbabilisticGraph", "BN", "MRF", "CRF", "InfluenceDiagram",
    "CausalGraph", "SCM", "AndOrGraph", "SceneGraph", "ConceptGraph",
    "OntologyGraph", "EventGraph", "InteractionGraph", "SocialGraph",
    "CommunicationGraph", "NetworkTopology", "RoutingGraph",
    "OverlayNetwork", "PeerToPeer", "BlockchainGraph", "MerkleDAG",
    "ContentAddressable", "VersionControl", "GitDAG", "ComputationGraph",
    "TensorGraph", "NeuralNetworkGraph", "AttentionGraph",
    "MessagePassing", "GNN", "FactorizationGraph", "ConstraintGraph",
    "SATGraph", "ClauseVariable", "SearchGraph", "GameTree",
    "MinimaxGraph", "MCTree", "ProofGraph", "InferenceGraph",
    "ResolutionGraph", "RewriteGraph", "TermGraph", "CategoryDiagram",
    "FunctorGraph", "MorphismGraph", "SheafGraph", "FiberBundle",
    "TopologicalGraph", "SimplicialComplex", "CellComplex", "CWComplex",
    "NerveGraph", "ReebGraph", "MapperGraph", "PersistenceGraph",
    "SpectralGraph", "LaplacianGraph", "EnergyGraph",
    "InteractionEnergy", "FlowField", "VectorField", "PhaseSpace",
    "StateSpace", "AttractorGraph", "TransitionSystem", "Kripke",
    "PetriNet", "ColoredPetriNet", "TimedPetriNet", "SignalFlow",
    "BlockDiagram", "CircuitGraph", "NetlistGraph", "TimingGraph",
    "PlacementGraph", "RoutingResource", "PowerGrid", "ClockTree",
    "HardwareDependency", "NoC", "InterconnectGraph", "GPUTaskGraph",
    "CUDAGraph", "KernelDependency", "MemoryAccess", "CacheCoherence",
    "IOGraph", "FilesystemGraph", "DirectoryTree", "ObjectGraph",
    "HeapGraph", "ReferenceGraph", "PointerGraph", "AliasGraph",
    "OwnershipGraph", "BorrowGraph", "RegionGraph", "LifetimeGraph",
    "VersionGraph", "DiffGraph", "PatchGraph", "MergeGraph",
    "ConflictGraph", "ClusterGraph", "PartitionGraph", "CommunityGraph",
    "AffinityGraph", "SimilarityGraph", "DistanceMatrix", "KNNGraph",
    "EpsilonGraph", "DelaunayGraph", "VoronoiGraph", "MSTGraph",
    "ShortestPathTree", "CutGraph", "MatchingGraph", "FlowGraph",
    "ResidualCapacity", "AugmentingPath", "DualFlow",
    "TransportationGraph", "SupplyChain", "LogisticsGraph",
    "ProcessGraph", "ManufacturingGraph", "ResourceAllocation",
    "DeadlockGraph", "WaitForGraph", "SchedulingGraph", "TimelineGraph",
    "GanttGraph", "PrecedenceGraph", "ConstraintSatisfaction",
    "DependencyResolution", "ExecutionPlan", "QueryPlan",
    "RelationalAlgebra", "JoinGraph", "IndexGraph", "DataLineage",
    "ETLGraph", "PipelineGraph", "FeatureStore", "EmbeddingGraph",
    "VectorIndexGraph", "RetrievalGraph", "RAGGraph", "AgentGraph",
    "ToolGraph", "PolicyGraph", "RewardGraph", "ValueGraph",
    "DecisionGraph", "InfluenceNetwork", "BeliefGraph",
    "UncertaintyGraph", "RiskGraph", "AttackGraph", "ThreatGraph",
    "TrustGraph", "ReputationGraph", "AccessControl", "PermissionGraph",
    "IdentityGraph", "FederationGraph", "ComplianceGraph", "AuditGraph",
    "ProvenanceGraph", "TraceGraph", "TelemetryGraph",
    "ObservabilityGraph", "MetricGraph", "LogGraph", "EventStream",
    "CausalEventGraph", "TemporalCausalGraph", "SpatioTemporal",
    "MobilityGraph", "TrafficGraph", "TransportationNetwork",
    "InfrastructureGraph", "UtilityGrid", "PowerNetwork",
    "WaterNetwork", "CommunicationNetwork", "InternetGraph",
    "ASLevelGraph", "RouterLevelGraph", "WirelessNetwork",
    "SensorNetworkGraph", "IoTGraph", "SwarmGraph",
    "MultiAgentInteraction", "CoordinationGraph", "CoalitionGraph",
    "GameTheoreticGraph", "MarketGraph", "EconomicGraph", "TradeGraph",
    "FinancialTransaction", "PaymentGraph", "CreditGraph", "FraudGraph",
    "SupplyDemandGraph", "MatchingMarket", "AuctionGraph",
    "OrderBookGraph", "PriceGraph", "SignalGraph", "TimeSeriesGraph",
    "CorrelationGraph", "CausationGraph", "GrangerGraph",
    "TransferEntropy", "InformationFlow", "EntropyGraph",
    "MutualInformation", "CompressionGraph", "CodingGraph",
    "ErrorCorrecting", "TannerGraph", "LDPCGraph", "TurboGraph",
    "QuantumCircuitGraph", "TensorNetworkGraph", "ZXCalculus",
    "QuantumInteraction", "EntanglementGraph", "MeasurementGraph",
    "StabilizerGraph", "QuantumError", "SpinNetwork", "CausalSet",
    "ProcessNetwork", "ReactionGraph", "MolecularGraph",
    "ChemicalReactionNetwork", "MetabolicNetwork",
    "GeneRegulatoryNetwork", "ProteinInteraction", "NeuralConnectome",
    "BrainNetworkGraph", "CognitiveGraph", "ConceptualGraph",
    "LanguageGraph", "SyntaxTree", "DependencyParse",
    "SemanticRoleGraph", "CoreferenceGraph", "DiscourseGraph",
    "KnowledgeRepresentation",
)


GRAPH_ACRONYMS: tuple[Term, ...] = tuple(
    axiom(f"graph:{name}") for name in GRAPH_NAMES
)


# --- the kernel K = (Distinction, Persistence, Linkage, Transformation, Evidence)

DISTINCTION     = axiom("kernel:distinction")
PERSISTENCE     = axiom("kernel:persistence")
LINKAGE         = axiom("kernel:linkage")
TRANSFORMATION  = axiom("kernel:transformation")
EVIDENCE        = axiom("kernel:evidence")

KERNEL = collection(
    DISTINCTION, PERSISTENCE, LINKAGE, TRANSFORMATION, EVIDENCE,
)


# --- the executable representation X = (ID, STATE, REL, PROC, EVID)

ID_FIELD    = axiom("observable:id")
STATE_FIELD = axiom("observable:state")
REL_FIELD   = axiom("observable:rel")
PROC_FIELD  = axiom("observable:proc")
EVID_FIELD  = axiom("observable:evid")

OBSERVABLE = collection(
    ID_FIELD, STATE_FIELD, REL_FIELD, PROC_FIELD, EVID_FIELD,
)


# --- the update equation X_{t+1} = F(X_t), F = observe ∘ compare ∘
# relate ∘ transform ∘ validate

OBSERVE   = function("op:observe",   lambda x=None: ("observe", x))
COMPARE   = function("op:compare",   lambda x=None: ("compare", x))
RELATE    = function("op:relate",    lambda x=None: ("relate", x))
TRANSFORM = function("op:transform", lambda x=None: ("transform", x))
VALIDATE  = function("op:validate",  lambda x=None: ("validate", x))

# composes right-to-left: F = observe ∘ compare ∘ relate ∘ transform ∘ validate
F = compose(OBSERVE, compose(COMPARE, compose(RELATE, compose(TRANSFORM, VALIDATE))))


def check() -> tuple[bool, str]:
    if len(GRAPH_NAMES) != len(GRAPH_ACRONYMS):
        return False, "acronym count mismatch"
    if len(set(GRAPH_NAMES)) != len(GRAPH_NAMES):
        return False, "duplicate acronym"
    if len(KERNEL.body) != 5:
        return False, "kernel is not 5"
    if len(OBSERVABLE.body) != 5:
        return False, "observable is not 5"
    if F.kind != "fn":
        return False, f"F is not fn, got {F.kind}"
    return True, (
        f"graphs={len(GRAPH_ACRONYMS)} "
        f"kernel={len(KERNEL.body)} "
        f"observable={len(OBSERVABLE.body)} "
        f"F={F.type}"
    )


def _main() -> int:
    print(f"graph acronyms : {len(GRAPH_ACRONYMS)}")
    print(f"kernel parts   : {len(KERNEL.body)}  {KERNEL.type}")
    print(f"observable     : {len(OBSERVABLE.body)}  {OBSERVABLE.type}")
    print(f"F              : {F.type}")
    print()
    ok, reason = check()
    print(f"INVARIANTS: {'hold' if ok else 'FAIL'}")
    print(f"  {reason}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_main())
