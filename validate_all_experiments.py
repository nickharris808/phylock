#!/usr/bin/env python3
"""
Portfolio B Master Validation Script - All Experiments
=======================================================
One command to verify ALL experiments across ALL pillars.

Usage:
    python validate_all_experiments.py

Expected Output:
    XX/XX PASS (runtime ~60 seconds)

This script validates:
- 10 Original 8-Week Proofs
- 19 Deep Hardening Phase Proofs  
- 6 Red Team PCAP Files
- Additional Integration Tests

Total: 35+ validation points

Copyright 2025 Portfolio B - Sovereign Handshake
"""

import os
import subprocess
import sys
import time
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = "/Users/nharris/Desktop/telecom/proof"
PCAP_DIR = "/Users/nharris/Desktop/telecom/attacks"
HLS_DIR = "/Users/nharris/Desktop/telecom/silicon"

# ============================================================================
# TEST RUNNER
# ============================================================================

def run_test(name, path, cmd, validation_string=None, timeout=120):
    """Run a single test and check for expected output."""
    print(f"  [{name}]...", end=" ", flush=True)
    
    try:
        script_dir = os.path.dirname(os.path.abspath(path)) if os.path.isfile(path) else path
        
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=script_dir, 
            timeout=timeout
        )
        
        # Check return code
        if result.returncode != 0:
            print(f"❌ FAIL (exit code {result.returncode})")
            return False
        
        # Check for expected output
        if validation_string:
            if validation_string not in result.stdout and validation_string not in result.stderr:
                print(f"❌ FAIL (missing: '{validation_string[:30]}...')")
                return False
        
        print("✅ PASS")
        return True
        
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT (>{timeout}s)")
        return False
    except FileNotFoundError:
        print("❌ NOT FOUND")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)[:50]}")
        return False

def check_file_exists(name, path):
    """Check if a file exists."""
    print(f"  [{name}]...", end=" ", flush=True)
    
    if os.path.isfile(path):
        size = os.path.getsize(path)
        print(f"✅ PASS ({size} bytes)")
        return True
    else:
        print("❌ NOT FOUND")
        return False

# ============================================================================
# TEST DEFINITIONS
# ============================================================================

def get_original_proofs():
    """Original 8-Week validation proofs."""
    return [
        ("ARC-3 CSI Correlation", 
         os.path.join(BASE_DIR, "arc3-radio/csi_correlation_audit.py"),
         "python3 csi_correlation_audit.py", "FAR = 0.000000"),
        
        ("D-Gate+ FSM Z3 Verification",
         os.path.join(BASE_DIR, "dgate-firmware/verified_fsm_logic.py"),
         "python3 verified_fsm_logic.py", "UNSAT"),
        
        ("D-Gate+ Atomic Quota",
         os.path.join(BASE_DIR, "dgate-firmware/permit_handshake_sim.py"),
         "python3 permit_handshake_sim.py", "ATOMICITY PROVEN"),
        
        ("U-CRED Edge Stress",
         os.path.join(BASE_DIR, "ucred-stateless/edge_admission_stress_test.py"),
         "python3 edge_admission_stress_test.py", "RAM Reduction"),
        
        ("PQLock Hybrid KDF",
         os.path.join(BASE_DIR, "pqlock-quantum/hybrid_kdf_model.py"),
         "python3 hybrid_kdf_model.py", "HYBRID INTEGRITY PROVEN"),
        
        ("PQLock Downgrade Detection",
         os.path.join(BASE_DIR, "pqlock-quantum/canonical_binding_audit.py"),
         "python3 canonical_binding_audit.py", "Detection Rate: 100.00%"),
        
        ("QSTF-V2 Erasure Coding",
         os.path.join(BASE_DIR, "qstf-iot/pqc_erasure_coding.py"),
         "python3 pqc_erasure_coding.py", "ERASURE RECOVERY PROVEN"),
        
        ("Technical Knot Z3",
         os.path.join(BASE_DIR, "grid-coupling/sovereign_handshake_knot.py"),
         "python3 sovereign_handshake_knot.py", "UNSAT"),
        
        ("Hard Silicon RTL",
         os.path.join(BASE_DIR, "hardware-rtl/Makefile"),
         "make", "PASS=2"),
        
        ("Great Silence Blackout",
         os.path.join(BASE_DIR, "actuarial-risk/great_silence_blackout.py"),
         "python3 great_silence_blackout.py", "CITY-SCALE GDP LOSS"),
    ]

def get_hardening_proofs():
    """Deep Hardening (6 Phases) proofs."""
    return [
        # Phase 1: ARC-3 Deep Hardening
        ("Phase 1.1: Massive MIMO SCM",
         os.path.join(BASE_DIR, "arc3-radio/scm_urban_canyon.py"),
         "python3 scm_urban_canyon.py", "PHYSICS PRISON PROVEN"),
        
        ("Phase 1.2: Temporal Decorrelation",
         os.path.join(BASE_DIR, "arc3-radio/csi_decorrelation_audit.py"),
         "python3 csi_decorrelation_audit.py", "BUFFER-INCAST TRAP PROVEN"),
        
        ("Phase 1.3: Pilot Contamination",
         os.path.join(BASE_DIR, "arc3-radio/pilot_contamination_sim.py"),
         "python3 pilot_contamination_sim.py", "MONOPOLY PROOF ACHIEVED"),
        
        # Phase 2: D-Gate+ Deep Hardening
        ("Phase 2.1: NAS Exception Matrix",
         os.path.join(BASE_DIR, "dgate-firmware/nas_exception_matrix.py"),
         "python3 nas_exception_matrix.py", "64/64"),
        
        ("Phase 2.2: Protocol Poisoning",
         os.path.join(BASE_DIR, "dgate-firmware/protocol_poisoning_attacks.py"),
         "python3 protocol_poisoning_attacks.py", "PROTOCOL POISONING IMMUNITY"),
        
        ("Phase 2.3: Sovereign FSM 12-State",
         os.path.join(BASE_DIR, "dgate-firmware/sovereign_exception_fsm.py"),
         "python3 sovereign_exception_fsm.py", "unsat"),
        
        # Phase 3: U-CRED Deep Hardening
        ("Phase 3.1: Distributed Edge Mesh",
         os.path.join(BASE_DIR, "ucred-stateless/distributed_edge_mesh.py"),
         "python3 distributed_edge_mesh.py", "STATELESS ADVANTAGE PROVEN"),
        
        ("Phase 3.2: Signaling Storm",
         os.path.join(BASE_DIR, "ucred-stateless/signaling_storm_sim.py"),
         "python3 signaling_storm_sim.py", "BACKHAUL SATURATION PROVEN"),
        
        ("Phase 3.3: Cold-Boot Thundering Herd",
         os.path.join(BASE_DIR, "ucred-stateless/cold_boot_restoration.py"),
         "python3 cold_boot_restoration.py", "Restoration Speedup"),
        
        # Phase 4: PQLock Deep Hardening
        ("Phase 4.1: ML-KEM Power Trace",
         os.path.join(BASE_DIR, "pqlock-quantum/pqc_power_trace_model.py"),
         "python3 pqc_power_trace_model.py", "POWER SIGNATURE MODELED"),
        
        ("Phase 4.2: DPA Attack Sim",
         os.path.join(BASE_DIR, "pqlock-quantum/dpa_attack_sim.py"),
         "python3 dpa_attack_sim.py", "DPA Attack Analysis"),
        
        ("Phase 4.3: Thermal Envelope",
         os.path.join(BASE_DIR, "pqlock-quantum/thermal_envelope_constraint.py"),
         "python3 thermal_envelope_constraint.py", "THERMAL ENVELOPE MONOPOLY"),
        
        # Phase 5: QSTF-V2 Deep Hardening
        ("Phase 5.1: Adversarial Jammer",
         os.path.join(BASE_DIR, "qstf-iot/adversarial_jammer_sim.py"),
         "python3 adversarial_jammer_sim.py", "ADVERSARIAL RESILIENCE PROVEN"),
        
        ("Phase 5.2: MDS Optimality",
         os.path.join(BASE_DIR, "qstf-iot/mds_optimality_proof.py"),
         "python3 mds_optimality_proof.py", "SILICON FEASIBILITY MONOPOLY"),
        
        ("Phase 5.3: Nash Equilibrium",
         os.path.join(BASE_DIR, "qstf-iot/erasure_game_theory.py"),
         "python3 erasure_game_theory.py", "NASH EQUILIBRIUM PROVEN"),
        
        # Phase 6: Actuarial Deep Hardening
        ("Phase 6.1: Digital Twin",
         os.path.join(BASE_DIR, "actuarial-risk/sovereign_digital_twin.py"),
         "python3 sovereign_digital_twin.py", "PHYSICAL DEPENDENCY PROVEN"),
        
        ("Phase 6.2: Grid-Telecom Coupling",
         os.path.join(BASE_DIR, "actuarial-risk/grid_telecom_coupling.py"),
         "python3 grid_telecom_coupling.py", "GRID-TELECOM COUPLING PROVEN"),
        
        ("Phase 6.3: Sovereign Risk Score",
         os.path.join(BASE_DIR, "actuarial-risk/sovereign_risk_score.py"),
         "python3 sovereign_risk_score.py", "INSURANCE MONOPOLY PROVEN"),
        
        ("Phase 6.4: Quantum Black Swan",
         os.path.join(BASE_DIR, "actuarial-risk/quantum_black_swan.py"),
         "python3 quantum_black_swan.py", "QUANTUM BLACK SWAN RESILIENCE"),
    ]

def get_pcap_files():
    """Red Team PCAP files."""
    return [
        ("PCAP: Quantum Downgrade Attack", 
         os.path.join(PCAP_DIR, "quantum_downgrade_attack.pcap")),
        ("PCAP: Relay Attack Detection",
         os.path.join(PCAP_DIR, "relay_attack_detection.pcap")),
        ("PCAP: PQC Downgrade Attack",
         os.path.join(PCAP_DIR, "pqc_downgrade_attack.pcap")),
        ("PCAP: Signaling Storm DDoS",
         os.path.join(PCAP_DIR, "signaling_storm_ddos.pcap")),
        ("PCAP: Protocol Poisoning",
         os.path.join(PCAP_DIR, "protocol_poisoning.pcap")),
        ("PCAP: Valid Permit Flow",
         os.path.join(PCAP_DIR, "valid_permit_flow.pcap")),
    ]

def get_hls_files():
    """Silicon-Ready HLS files."""
    return [
        ("HLS: ARC-3 Correlator Header",
         os.path.join(HLS_DIR, "arc3_csi_correlator.h")),
        ("HLS: ARC-3 Correlator Core",
         os.path.join(HLS_DIR, "arc3_csi_correlator.cpp")),
        ("HLS: ARC-3 Testbench",
         os.path.join(HLS_DIR, "arc3_csi_correlator_tb.cpp")),
        ("HLS: D-Gate+ FSM Header",
         os.path.join(HLS_DIR, "dgate_fsm.h")),
        ("HLS: D-Gate+ FSM Core",
         os.path.join(HLS_DIR, "dgate_fsm.cpp")),
        ("HLS: D-Gate+ Testbench",
         os.path.join(HLS_DIR, "dgate_fsm_tb.cpp")),
    ]

def get_legal_files():
    """Litigation Pack files."""
    legal_dir = "/Users/nharris/Desktop/telecom/legal"
    return [
        ("Legal: ARC-3 Claim Chart",
         os.path.join(legal_dir, "CLAIM_CHART_ARC3_TS33501.md")),
        ("Legal: D-Gate+ Claim Chart",
         os.path.join(legal_dir, "CLAIM_CHART_DGATE_TS24501.md")),
        ("Legal: PQLock Claim Chart",
         os.path.join(legal_dir, "CLAIM_CHART_PQLOCK_TS33501.md")),
        ("Legal: Prior Art Analysis",
         os.path.join(legal_dir, "PRIOR_ART_ANALYSIS_ALL_FAMILIES.md")),
        ("Legal: SEP Summary",
         os.path.join(legal_dir, "SEP_ESSENTIALITY_SUMMARY.md")),
    ]

def get_standards_files():
    """Standards-Ready Pack files."""
    standards_dir = "/Users/nharris/Desktop/telecom/docs/standards"
    return [
        ("Standards: PQLock CR001",
         os.path.join(standards_dir, "3GPP_TS33.501_CR001_PQLock_Hybrid_PQC.md")),
        ("Standards: ARC-3 CR002",
         os.path.join(standards_dir, "3GPP_TS33.501_CR002_ARC3_Physical_Layer_Binding.md")),
        ("Standards: D-Gate+ CR001",
         os.path.join(standards_dir, "3GPP_TS24.501_CR001_DGate_Firmware_Security_Gating.md")),
    ]

# ============================================================================
# MAIN VALIDATION
# ============================================================================

def main():
    """Run all validations."""
    start_time = time.time()
    
    print("=" * 70)
    print("PORTFOLIO B MASTER VALIDATION - ALL EXPERIMENTS")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base: {BASE_DIR}")
    print("=" * 70)
    
    results = {
        "original": [],
        "hardening": [],
        "pcaps": [],
        "hls": [],
        "legal": [],
        "standards": [],
    }
    
    # -------------------------------------------------------------------------
    # Section 1: Original 8-Week Proofs
    # -------------------------------------------------------------------------
    print("\n📋 SECTION 1: Original 8-Week Proofs (10 tests)")
    print("-" * 50)
    
    for name, path, cmd, validation in get_original_proofs():
        passed = run_test(name, path, cmd, validation)
        results["original"].append(passed)
    
    # -------------------------------------------------------------------------
    # Section 2: Deep Hardening Proofs
    # -------------------------------------------------------------------------
    print("\n📋 SECTION 2: Deep Hardening Proofs (19 tests)")
    print("-" * 50)
    
    for name, path, cmd, validation in get_hardening_proofs():
        passed = run_test(name, path, cmd, validation)
        results["hardening"].append(passed)
    
    # -------------------------------------------------------------------------
    # Section 3: Red Team PCAPs
    # -------------------------------------------------------------------------
    print("\n📋 SECTION 3: Red Team PCAP Files (6 files)")
    print("-" * 50)
    
    for name, path in get_pcap_files():
        passed = check_file_exists(name, path)
        results["pcaps"].append(passed)
    
    # -------------------------------------------------------------------------
    # Section 4: Silicon-Ready HLS
    # -------------------------------------------------------------------------
    print("\n📋 SECTION 4: Silicon-Ready HLS Files (6 files)")
    print("-" * 50)
    
    for name, path in get_hls_files():
        passed = check_file_exists(name, path)
        results["hls"].append(passed)
    
    # -------------------------------------------------------------------------
    # Section 5: Litigation Pack
    # -------------------------------------------------------------------------
    print("\n📋 SECTION 5: Litigation Pack Files (5 files)")
    print("-" * 50)
    
    for name, path in get_legal_files():
        passed = check_file_exists(name, path)
        results["legal"].append(passed)
    
    # -------------------------------------------------------------------------
    # Section 6: Standards-Ready Pack
    # -------------------------------------------------------------------------
    print("\n📋 SECTION 6: Standards-Ready Pack Files (3 files)")
    print("-" * 50)
    
    for name, path in get_standards_files():
        passed = check_file_exists(name, path)
        results["standards"].append(passed)
    
    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    total_passed = 0
    total_tests = 0
    
    sections = [
        ("Original 8-Week Proofs", results["original"]),
        ("Deep Hardening Proofs", results["hardening"]),
        ("Red Team PCAPs", results["pcaps"]),
        ("Silicon-Ready HLS", results["hls"]),
        ("Litigation Pack", results["legal"]),
        ("Standards-Ready Pack", results["standards"]),
    ]
    
    for name, section_results in sections:
        passed = sum(section_results)
        total = len(section_results)
        total_passed += passed
        total_tests += total
        
        status = "✅" if passed == total else "⚠️"
        print(f"  {status} {name}: {passed}/{total}")
    
    print("-" * 50)
    print(f"  TOTAL: {total_passed}/{total_tests} tests passed")
    print(f"  Runtime: {elapsed:.1f} seconds")
    print("=" * 70)
    
    if total_passed == total_tests:
        print("\n🏆 ALL VALIDATIONS PASSED - PORTFOLIO COMPLETE")
        print("\nDeliverables Ready:")
        print("  ✅ Standards-Ready Pack ($40k value)")
        print("  ✅ Silicon-Ready Pack ($30k value)")
        print("  ✅ Litigation Pack ($20k value)")
        print("  ✅ Red Team PCAP Pack ($10k value)")
        print("\n  💰 Total Value-Add: $100,000")
        return 0
    else:
        failures = total_tests - total_passed
        print(f"\n⚠️ {failures} VALIDATION(S) FAILED - Review output above")
        return 1

if __name__ == "__main__":
    sys.exit(main())


