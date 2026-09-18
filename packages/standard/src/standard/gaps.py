MOATS = [
    "braided_multimodal_fusion",
    "self_healing_orchestration",
    "proprietary_datasets",
    "quantization_toolchain",
    "reproducible_build_sbom_attestation",
    "policy_safety_platform",
    "sdk_api",
    "federated_learning_dp",
    "hardware_kernels",
    "orchestration_language",
]

IMPLEMENTED_MOATS = [
    "reproducible_build_sbom_attestation",
]

GAP_MOATS = [m for m in MOATS if m not in IMPLEMENTED_MOATS]

def gap_count():
    return len(GAP_MOATS)

def implemented_count():
    return len(IMPLEMENTED_MOATS)
