"""All Hands: actors, archetypes, functions, work-unit schema, validator."""
__version__ = "0.1.0"

HUMAN_HANDS = [
    "founder","shareholder","board_director","executive_officer","governor",
    "functional_leader","people_manager","program_leader","architect",
    "scientist","engineer","designer","analyst","licensed_professional",
    "tradesperson","technician","operator","administrator","coordinator",
    "advisor","investigator","inspector","assessor","auditor","seller",
    "educator","caregiver","responder","maintainer","apprentice","beneficiary",
]

COLLECTIVE_HANDS = [
    "board","executive_committee","steering_committee","investment_committee",
    "risk_committee","audit_committee","ethics_committee","safety_board",
    "architecture_review_board","change_advisory_board","incident_command",
    "program_team","product_team","platform_team","service_team","ops_crew",
    "research_group","guild","union","customer_council","citizen_panel",
    "standards_body","consortium",
]

ORGANIZATIONAL_HANDS = [
    "parent_company","holding_company","subsidiary","business_unit",
    "joint_venture","cooperative","partnership","franchise","supplier",
    "contractor","professional_services_firm","cloud_provider",
    "distributor","customer_org","academic_institution","nonprofit",
    "government_agency","regulator","certification_body","insurer","bank",
    "federation_member","sovereign_node",
]

MACHINE_HANDS = [
    "information_system","software_service","api","deterministic_automation",
    "workflow_engine","rules_engine","scheduler","monitoring_system",
    "ai_assistant","ai_evaluator","software_agent","autonomous_agent",
    "multi_agent_collective","robot","drone","vehicle","sensor",
    "industrial_controller","manufacturing_machine","medical_device",
    "network_appliance","edge_device",
]

HYBRID_HANDS = [
    "human_with_decision_support","human_with_automation",
    "human_supervised_agent","human_approved_agent",
    "exception_supervised_autonomous","dual_control_pair","human_agent_team",
    "multi_agent_team_with_commander","remote_operator_and_robot",
    "clinician_and_diagnostic","engineer_and_generative_dev",
]

ARCHETYPES = [
    "originator","beneficiary","sponsor","owner","governor","strategist",
    "funder","architect","planner","designer","researcher","engineer",
    "builder","integrator","implementer","operator","maintainer","responder",
    "provider","coordinator","communicator","educator","analyst","advisor",
    "approver","reviewer","challenger","verifier","validator","qualifier",
    "certifier","auditor","regulator","steward","custodian","representative",
    "consumer","affected_party",
]

FUNCTIONS = [
    "purpose_and_direction","governance_and_authority",
    "discovery_and_intelligence","definition_and_design",
    "creation_and_transformation","acquisition_and_provisioning",
    "delivery_and_service","operations","protection","assurance",
    "sustainment_and_change","learning_and_regeneration",
]

WORKFLOW_STATES = [
    "observed","captured","interpreted","reconciled","proposed","authorized",
    "planned","resourced","ready","executing","reviewed","verified",
    "validated","accepted","released","operated","monitored","sustained",
    "retired","archived",
]

EXCEPTION_STATES = [
    "ambiguous","contested","waiting","blocked","paused","escalated","rejected",
    "failed","degraded","quarantined","revoked","recalled","cancelled","superseded",
]

DECISION_CLASSES = [
    "constitutional","strategic","portfolio","investment","architectural",
    "product","operational","technical","financial","personnel","commercial",
    "legal","regulatory","safety","security","privacy","ethical","emergency",
    "automated_bounded",
]

AUTHORITY_FORMS = [
    "constitutional","ownership","fiduciary","statutory","contractual",
    "executive","managerial","professional","technical","operational",
    "financial","data","access","emergency","delegated_agent",
]

HANDOFF_MODES = [
    "assignment","delegation","referral","consultation","escalation",
    "approval_request","review_request","service_request","incident_transfer",
    "shift_turnover","custody_transfer","data_exchange","asset_transfer",
    "contractual_delivery","federation_routing",
]

ALLOCATIONS = [
    "human_only","assisted","human_approved","human_supervised",
    "exception_supervised","dual_control","agent_executed",
    "machine_executed","multi_agent","prohibited",
]

ROOT_INVARIANT = [
    "identity","competence","qualification","authority","execution",
    "observation","evidence","acceptance",
]

REQUIRED_WORK_FIELDS = [
    "id","version","purpose","outcome","beneficiary_refs","originator_ref",
    "accountable_owner_ref","performer_refs","domain","scope","jurisdictions",
    "functions","authority","accountability","required_competencies",
    "required_qualifications","inputs","assumptions","constraints","dependencies",
    "resources","controls","evidence_requirements","acceptance_criteria",
    "measures","risks","stop_conditions","escalation_paths","state",
]

ALL_HAND_KINDS = (HUMAN_HANDS + COLLECTIVE_HANDS + ORGANIZATIONAL_HANDS
                   + MACHINE_HANDS + HYBRID_HANDS)

def is_hand(token): return token in ALL_HAND_KINDS
def is_archetype(token): return token in ARCHETYPES
def is_function(token): return token in FUNCTIONS
def is_state(token): return token in WORKFLOW_STATES or token in EXCEPTION_STATES
def is_decision(token): return token in DECISION_CLASSES
def is_authority(token): return token in AUTHORITY_FORMS
def is_handoff(token): return token in HANDOFF_MODES
def is_allocation(token): return token in ALLOCATIONS

def validate_assignment(a):
    errs = []
    for f in REQUIRED_WORK_FIELDS:
        if f not in a:
            errs.append(f"missing field: {f}")
    st = a.get("state")
    if st and not is_state(st):
        errs.append("unknown state: " + str(st))
    refs = a.get("performer_refs") or []
    if isinstance(refs, list):
        for r in refs:
            if isinstance(r, dict) and r.get("kind") and not is_hand(r["kind"]):
                errs.append("unknown hand kind: " + str(r["kind"]))
    for f in (a.get("functions") or []):
        if not is_function(f):
            errs.append("unknown function: " + str(f))
    for ar in (a.get("actor_modes") or []):
        if not is_archetype(ar):
            errs.append("unknown archetype: " + str(ar))
    auth = a.get("authority") or {}
    if isinstance(auth, dict):
        for g in (auth.get("grants") or []):
            if isinstance(g, dict) and g.get("form") and not is_authority(g["form"]):
                errs.append("unknown authority form: " + str(g["form"]))
    alloc = a.get("allocation")
    if alloc and not is_allocation(alloc):
        errs.append("unknown allocation: " + str(alloc))
    collapsed = ("identity_is_authority", "competence_is_authority",
                 "qualification_is_authority", "authority_is_execution")
    for k in collapsed:
        if a.get(k) is True:
            errs.append("root invariant violated: " + k)
    return errs
