"""AX: allocation matrix mapping every ontology role to an allocation mode."""
__version__ = "0.1.0"

SCOPES = [
    "enterprise","federation","organization","region","jurisdiction",
    "domain","platform","product","service","tenant","node","program",
    "project","team","runtime",
]

FUNCTIONS = [
    "discover","research","define","design","architect","engineer","build",
    "integrate","configure","test","verify","validate","qualify","certify",
    "deploy","operate","monitor","detect","respond","recover","audit","govern",
    "maintain","modernize","retire",
]

AX = {
    "1_executive_leadership_governance": {
        "allocation": "assisted",
        "rationale": "Fiduciary and constitutional decisions require a named human; agents prepare options and evidence.",
        "human_required": ["founder","board_director","ceo","chairperson","corporate_secretary"],
        "agent_capable": ["chief_of_staff","operating_partner","policy_governance_director"],
    },
    "2_enterprise_architecture": {
        "allocation": "human_approved",
        "rationale": "Architectural decisions bind downstream systems; agent drafts, human approves.",
        "agent_capable": ["enterprise_architect","solution_architect","integration_architect","api_architect","data_architect"],
        "human_required": ["chief_architect","architecture_review_board_lead"],
    },
    "3_systems_engineering": {
        "allocation": "human_supervised",
        "rationale": "Verification and validation are agent-executable under human supervision; certification requires human.",
        "agent_capable": ["requirements_engineer","verification_engineer","validation_engineer","modeling_simulation_engineer"],
        "human_required": ["certification_engineer","safety_engineer"],
    },
    "4_product_portfolio_engineering": {
        "allocation": "assisted",
        "rationale": "Portfolio decisions allocate capital; agents analyze and recommend.",
        "agent_capable": ["product_analyst","product_operations_manager","roadmap_manager"],
        "human_required": ["chief_product_officer","portfolio_manager"],
    },
    "5_software_engineering": {
        "allocation": "agent_executed",
        "rationale": "Code authoring, review, and refactoring are agent-executable within human-defined boundaries.",
        "agent_capable": ["software_engineer","backend_engineer","frontend_engineer","full_stack_engineer","test_engineer","refactoring_engineer"],
        "human_required": ["principal_engineer","distinguished_engineer","staff_engineer"],
    },
    "6_platform_cloud_infrastructure": {
        "allocation": "agent_executed",
        "rationale": "Infrastructure-as-code, provisioning, and cost optimization are deterministic.",
        "agent_capable": ["platform_engineer","cloud_engineer","kubernetes_engineer","finops_engineer","infrastructure_automation_engineer"],
        "human_required": ["chief_infrastructure_officer","infrastructure_director"],
    },
    "7_devops_devsecops_delivery": {
        "allocation": "agent_executed",
        "rationale": "Pipelines, builds, releases, and supply-chain attestation are automatable end to end.",
        "agent_capable": ["devops_engineer","devsecops_engineer","ci_cd_engineer","release_engineer","sbom_engineer","reproducible_build_engineer"],
        "human_required": ["release_train_engineer","change_enablement_manager"],
    },
    "8_site_reliability_operations": {
        "allocation": "exception_supervised",
        "rationale": "Routine operations are agent-executed; exceptions escalate to on-call humans.",
        "agent_capable": ["sre","production_engineer","ops_engineer","runbook_engineer","chaos_engineer"],
        "human_required": ["incident_commander","major_incident_manager","post_incident_review_lead"],
    },
    "9_networking_telecommunications": {
        "allocation": "agent_executed",
        "rationale": "Network configuration, routing, and DNS are software-defined and automatable.",
        "agent_capable": ["network_engineer","network_automation_engineer","sdn_engineer","routing_engineer","dns_engineer"],
        "human_required": ["chief_network_architect"],
    },
    "10_cybersecurity": {
        "allocation": "dual_control",
        "rationale": "Offensive and defensive operations require dual human-machine control to preserve evidence and prevent error.",
        "agent_capable": ["security_engineer","detection_engineer","threat_hunter","vulnerability_analyst","malware_analyst","pentester"],
        "human_required": ["ciso","security_director","incident_response_engineer"],
    },
    "11_identity_trust_federation": {
        "allocation": "human_supervised",
        "rationale": "Credential issuance and trust frameworks are high-blast-radius; agents execute under supervision.",
        "agent_capable": ["identity_engineer","iam_engineer","pam_engineer","certificate_engineer","federation_engineer"],
        "human_required": ["chief_identity_officer","trust_framework_architect"],
    },
    "12_data_engineering_management": {
        "allocation": "agent_executed",
        "rationale": "Pipelines, lineage, cataloging, and quality are deterministic and verifiable.",
        "agent_capable": ["data_engineer","etl_engineer","streaming_engineer","lineage_engineer","data_quality_engineer","data_catalog_engineer"],
        "human_required": ["chief_data_officer","data_steward"],
    },
    "13_ai_ml": {
        "allocation": "human_supervised",
        "rationale": "Training, evaluation, and serving are automatable; model risk acceptance requires human.",
        "agent_capable": ["ml_engineer","mlops_engineer","model_evaluation_engineer","ai_red_team_engineer","alignment_researcher"],
        "human_required": ["chief_ai_officer","model_risk_manager","ai_ethics_officer"],
    },
    "14_automation_autonomous_systems": {
        "allocation": "multi_agent",
        "rationale": "Orchestration of autonomous systems requires agent collectives with human command.",
        "agent_capable": ["automation_engineer","workflow_engineer","rpa_engineer","orchestration_engineer","multi_agent_systems_engineer"],
        "human_required": ["chief_automation_officer","autonomous_operations_supervisor"],
    },
    "15_hardware_electronics": {
        "allocation": "assisted",
        "rationale": "Design is human-led; simulation, verification, and testing are agent-assisted.",
        "agent_capable": ["verification_engineer","simulation_engineer","test_engineer","component_engineer"],
        "human_required": ["hardware_architect","silicon_design_engineer","fpga_engineer"],
    },
    "16_research_science": {
        "allocation": "assisted",
        "rationale": "Scientific judgment is human; literature review, simulation, and analysis are agent-assisted.",
        "agent_capable": ["computational_researcher","patent_researcher","technology_scout","statistician"],
        "human_required": ["principal_scientist","research_director","lab_director"],
    },
    "17_quality_engineering": {
        "allocation": "agent_executed",
        "rationale": "Test design, execution, and reporting are deterministic and repeatable.",
        "agent_capable": ["qa_engineer","test_automation_engineer","regression_engineer","performance_test_engineer","accessibility_test_engineer"],
        "human_required": ["chief_quality_officer","quality_auditor"],
    },
    "18_safety_assurance_certification": {
        "allocation": "dual_control",
        "rationale": "Safety certification carries legal weight; requires human authority plus agent evidence gathering.",
        "agent_capable": ["hazard_analyst","fmea_analyst","fault_tree_analyst","risk_engineer"],
        "human_required": ["chief_safety_officer","certification_manager","certification_authority_liaison"],
    },
    "19_privacy_ethics_responsible_tech": {
        "allocation": "human_only",
        "rationale": "Ethical and privacy judgments cannot be delegated to agents; agents inform, humans decide.",
        "agent_capable": ["privacy_analyst","bias_evaluation_engineer","transparency_engineer"],
        "human_required": ["chief_privacy_officer","data_protection_officer","ai_ethics_officer"],
    },
    "20_legal_regulatory_ip": {
        "allocation": "human_only",
        "rationale": "Legal advice is a licensed-human activity in every jurisdiction represented.",
        "agent_capable": ["contract_analyst","paralegal","legal_operations_manager"],
        "human_required": ["general_counsel","patent_attorney","regulatory_affairs_director"],
    },
    "21_risk_compliance_audit": {
        "allocation": "dual_control",
        "rationale": "Audit independence requires separation; agent gathers evidence, human attests.",
        "agent_capable": ["controls_engineer","grc_engineer","evidence_manager"],
        "human_required": ["chief_audit_executive","internal_auditor","chief_risk_officer"],
    },
    "22_finance_economics": {
        "allocation": "human_approved",
        "rationale": "Financial reporting is regulated; agent prepares, human approves.",
        "agent_capable": ["financial_analyst","fp_and_a_analyst","unit_economics_analyst","pricing_analyst"],
        "human_required": ["cfo","controller","corporate_treasurer"],
    },
    "23_procurement_vendors_supply_chain": {
        "allocation": "human_approved",
        "rationale": "Contractual commitments bind the entity; agent negotiates within bounds, human signs.",
        "agent_capable": ["buyer","supplier_risk_analyst","demand_planner","inventory_manager","logistics_manager"],
        "human_required": ["chief_procurement_officer","contract_negotiator"],
    },
    "24_business_analysis_process": {
        "allocation": "agent_executed",
        "rationale": "Analysis, mapping, and process mining are automatable.",
        "agent_capable": ["business_analyst","process_analyst","process_mining_engineer","value_stream_analyst"],
        "human_required": ["chief_process_officer"],
    },
    "25_service_management": {
        "allocation": "exception_supervised",
        "rationale": "Tier 1 and Tier 2 support are agent-executed; escalations reach humans.",
        "agent_capable": ["service_desk_analyst","technical_support_engineer","incident_manager","problem_manager"],
        "human_required": ["service_owner","escalation_manager"],
    },
    "26_ux_design": {
        "allocation": "human_supervised",
        "rationale": "Design judgment is human; prototyping, research synthesis, and evaluation are agent-assisted.",
        "agent_capable": ["user_researcher","usability_analyst","prototyping_engineer","design_ops_manager"],
        "human_required": ["chief_design_officer","product_designer","interaction_designer"],
    },
    "27_documentation_knowledge": {
        "allocation": "agent_executed",
        "rationale": "Documentation drafting, indexing, and curation are automatable with human review.",
        "agent_capable": ["technical_writer","documentation_engineer","knowledge_engineer","taxonomist","ontologist"],
        "human_required": ["chief_knowledge_officer"],
    },
    "28_developer_relations_ecosystem": {
        "allocation": "assisted",
        "rationale": "Community engagement is inherently human; content generation and scheduling are agent-assisted.",
        "agent_capable": ["technical_content_creator","community_engineer","api_community_manager"],
        "human_required": ["developer_advocate","developer_relations_director"],
    },
    "29_sales_engineering_solutions": {
        "allocation": "human_supervised",
        "rationale": "Customer commitments require human; technical scoping and demo preparation are agent-assisted.",
        "agent_capable": ["solutions_engineer","presales_engineer","technical_account_manager","proposal_manager"],
        "human_required": ["chief_revenue_officer","enterprise_account_executive"],
    },
    "30_customer_delivery_success": {
        "allocation": "exception_supervised",
        "rationale": "Routine delivery is agent-executed; escalations and renewals reach humans.",
        "agent_capable": ["onboarding_specialist","adoption_manager","implementation_engineer","customer_operations_analyst"],
        "human_required": ["chief_customer_officer","renewals_manager"],
    },
    "31_people_organization_workforce": {
        "allocation": "human_only",
        "rationale": "Employment decisions are regulated and carry human consequence.",
        "agent_capable": ["workforce_analytics_engineer","talent_sourcing_specialist"],
        "human_required": ["chief_people_officer","hr_business_partner","employee_relations_manager"],
    },
    "32_communications_coordination": {
        "allocation": "assisted",
        "rationale": "Drafting and scheduling are agent-capable; publication is human.",
        "agent_capable": ["internal_comms_manager","content_strategist","community_manager"],
        "human_required": ["chief_comms_officer","crisis_comms_manager"],
    },
    "33_facilities_physical_operations": {
        "allocation": "exception_supervised",
        "rationale": "Physical security, access control, and maintenance are agent-monitored with human response.",
        "agent_capable": ["facilities_engineer","power_systems_engineer","cooling_systems_engineer","security_ops_manager"],
        "human_required": ["chief_facilities_officer","physical_security_director"],
    },
    "34_manufacturing_industrial": {
        "allocation": "multi_agent",
        "rationale": "Production lines are increasingly agent-orchestrated; safety oversight remains human.",
        "agent_capable": ["manufacturing_engineer","automation_engineer","controls_engineer","mes_engineer","production_planner"],
        "human_required": ["plant_manager","factory_safety_engineer"],
    },
    "35_federation_control_plane": {
        "allocation": "human_supervised",
        "rationale": "Cross-sovereign coordination requires human authority; operational flows are agent-executed.",
        "agent_capable": ["federation_protocol_engineer","federation_registry_operator","federation_service_broker","federation_interop_engineer"],
        "human_required": ["federation_executive","federation_governance_officer","federation_sovereignty_officer"],
    },
    "36_policy_authority_decision": {
        "allocation": "dual_control",
        "rationale": "Policy authoring and enforcement must be separable; agent enforces, human authors.",
        "agent_capable": ["policy_engineer","policy_evaluator","policy_as_code_engineer","delegation_engineer"],
        "human_required": ["policy_architect","authority_architect","conflict_resolution_engineer"],
    },
    "37_runtime_judgment_autonomous": {
        "allocation": "multi_agent",
        "rationale": "Runtime decision loops are agent-executed within human-defined boundaries.",
        "agent_capable": ["runtime_decision_engineer","event_correlation_engineer","anomaly_detection_engineer","trust_evaluation_engineer"],
        "human_required": ["human_escalation_coordinator","autonomous_action_auditor"],
    },
    "38_evidence_measurement_observability": {
        "allocation": "agent_executed",
        "rationale": "Telemetry, tracing, and evidence capture are deterministic.",
        "agent_capable": ["observability_engineer","telemetry_engineer","metrics_engineer","evidence_engineer","provenance_engineer"],
        "human_required": ["chief_measurement_officer","evidence_custodian"],
    },
    "39_standards_interoperability": {
        "allocation": "assisted",
        "rationale": "Conformance testing is agent-executed; standards negotiation is human.",
        "agent_capable": ["conformance_engineer","interop_engineer","schema_engineer","test_suite_engineer"],
        "human_required": ["chief_standards_officer","technical_committee_chair"],
    },
    "40_strategy_innovation_corp_dev": {
        "allocation": "assisted",
        "rationale": "Strategic judgment is human; intelligence gathering and scenario modeling are agent-assisted.",
        "agent_capable": ["competitive_intelligence_analyst","market_intelligence_analyst","scenario_planner","technology_scout"],
        "human_required": ["chief_strategy_officer","corporate_development_director"],
    },
    "41_specialized_industry_engineering": {
        "allocation": "human_supervised",
        "rationale": "Industry engineering is domain-regulated; agents execute design and test under human authority.",
        "agent_capable": ["aerospace_systems_engineer","automotive_engineer","trading_systems_engineer","clinical_systems_engineer"],
        "human_required": ["medical_device_engineer","defense_systems_engineer"],
    },
    "42_essential_supporting_occupations": {
        "allocation": "human_only",
        "rationale": "These are licensed, fiduciary, or human-relationship professions.",
        "agent_capable": [],
        "human_required": ["attorney","auditor","accountant","medical_professional","banker"],
    },
}

def allocation_for(category):
    entry = AX.get(category)
    return entry["allocation"] if entry else None

def categories():
    return sorted(AX.keys())

def agent_capable(category):
    entry = AX.get(category) or {}
    return entry.get("agent_capable", [])

def human_required(category):
    entry = AX.get(category) or {}
    return entry.get("human_required", [])

def coverage():
    counts = {}
    for cat, e in AX.items():
        counts[e["allocation"]] = counts.get(e["allocation"], 0) + 1
    return counts

def scope_variants(role, base_scope="enterprise"):
    if base_scope not in SCOPES:
        raise ValueError("unknown scope: " + base_scope)
    out = []
    for s in SCOPES:
        for fn in FUNCTIONS:
            out.append({"role": role, "scope": s, "function": fn})
    return out
