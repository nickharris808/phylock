# 📁 Portfolio B: Complete Directory Guide

## Overview

This guide provides complete navigation for the Portfolio B repository, organized by purpose and audience.

---

## 🎯 Quick Links by Audience

### For Everyone (Start Here)
| File | Purpose |
|------|---------|
| `README.md` | Executive overview with quick validation |
| `validate_all_experiments.py` | One-command validation (49 tests) |

### For Engineering
| File/Folder | Purpose |
|-------------|---------|
| `Portfolio_B_Sovereign_Handshake/` | All source code (75+ Python files) |
| `src/hls/` | Silicon-ready HLS C++ cores |
| `data/pcaps/` | Attack demonstration PCAPs |

### For Legal/IP
| File/Folder | Purpose |
|-------------|---------|
| `legal/` | Claim charts + prior art analysis |
| `Portfolio_B_Sovereign_Handshake/PROVISIONAL_PATENT_*.md` | 4 ready-to-file patents |
| `Portfolio_B_Sovereign_Handshake/PATENT_FAMILIES_COMPLETE.md` | All 9 families |

### For Standards
| File/Folder | Purpose |
|-------------|---------|
| `docs/standards/` | 3 complete 3GPP Change Requests |

### For Business/M&A
| File | Purpose |
|------|---------|
| `Portfolio_B_Sovereign_Handshake/BUSINESS_SUMMARY.md` | Realistic $40-60M valuation |
| `Portfolio_B_Sovereign_Handshake/EXECUTIVE_SUMMARY.md` | Dual valuation framework |

---

## 📦 Root Level Structure

```
telecom/
├── README.md                    ⭐ START HERE - Executive overview
├── DIRECTORY_GUIDE.md           📁 THIS FILE - Navigation guide
├── validate_all_experiments.py  🏆 Master validation (49 tests)
├── portfolio_b_final_check.py   ✅ File integrity checker
│
├── Portfolio_B_Sovereign_Handshake/  📦 Main codebase (75+ Python files)
├── src/                              💎 Silicon-ready HLS cores
├── data/                             🔴 Attack demonstration PCAPs
├── docs/                             📚 All documentation
├── legal/                            ⚖️ Litigation materials
└── whitepapers/                      📄 Academic papers (WP1-WP4)
```

---

## 📦 Portfolio_B_Sovereign_Handshake/ (Main Codebase)

The core of the portfolio. Contains all 9 pillars and key documentation.

### Pillar Directories (01-09)

```
Portfolio_B_Sovereign_Handshake/
├── 01_DGate_Cellular_Gating/         🔒 D-Gate+ (Stingray prevention)
│   ├── verified_fsm_logic.py         Z3 formal verification
│   ├── permit_handshake_sim.py       Atomic quota management
│   ├── nas_exception_matrix.py       64/64 exception coverage
│   ├── protocol_poisoning_attacks.py Attack immunity proof
│   ├── sovereign_exception_fsm.py    12-state FSM
│   └── *.csv, *.png                  Results & visualizations
│
├── 02_UCRED_Stateless_Admission/     🌐 U-CRED (Edge scaling)
│   ├── edge_admission_stress_test.py 88.7% CPU, 91.9% RAM savings
│   ├── distributed_edge_mesh.py      Mesh topology proof
│   ├── signaling_storm_sim.py        DDoS mitigation
│   ├── cold_boot_restoration.py      Thundering herd handling
│   └── security_invariants_test.py   Security invariant proofs
│
├── 03_PQLock_Hybrid_Fabric/          🔐 PQLock (Post-quantum crypto)
│   ├── hybrid_kdf_model.py           X25519 + ML-KEM-768 hybrid
│   ├── canonical_binding_audit.py    100% downgrade detection
│   ├── pqc_power_trace_model.py      NIST Hamming Weight model
│   ├── dpa_attack_sim.py             Side-channel analysis
│   ├── thermal_envelope_constraint.py Thermal prison proof
│   └── pqlock_rnpv_economics.py      Economic model
│
├── 04_ARC3_Channel_Binding/          📡 ARC-3 (Radio security)
│   ├── csi_correlation_audit.py      CSI fingerprinting
│   ├── csi_fingerprint_model.py      Core CSI model
│   ├── scm_urban_canyon.py           Massive MIMO channel model
│   ├── csi_decorrelation_audit.py    Temporal analysis
│   ├── pilot_contamination_sim.py    90-100% throughput protection
│   └── pop_adversarial_test.py       Proof-of-Position tests
│
├── 05_QSTF_IoT_Resilience/           📶 QSTF-V2 (IoT erasure coding)
│   ├── pqc_erasure_coding.py         19x smaller than Reed-Solomon
│   ├── adversarial_jammer_sim.py     Jammer resilience
│   ├── mds_optimality_proof.py       MDS optimality proof
│   ├── erasure_game_theory.py        Nash equilibrium
│   └── attestation_roc.py            ROC analysis
│
├── 06_The_Technical_Knot/            ⚡ Grid-Telecom Coupling
│   ├── sovereign_handshake_knot.py   Z3 coupling proof
│   └── Visualizations                Grid-telecom diagrams
│
├── 07_Hard_Engineering_Proofs/       💎 ASIC Implementation
│   ├── aipp_sh_gate.v                Verilog RTL
│   ├── test_sh_gate.py               CocoTB testbench
│   ├── Makefile                      Build automation
│   └── timing_closure_report.txt     Timing analysis
│
├── 08_Actuarial_Loss_Models/         📊 Cyber Insurance
│   ├── great_silence_blackout.py     City-scale loss model
│   ├── sovereign_digital_twin.py     Multi-domain simulation
│   ├── grid_telecom_coupling.py      Physical coupling proof
│   ├── sovereign_risk_score.py       30x premium differential
│   └── quantum_black_swan.py         Black swan resilience
│
└── 09_NTN_Fast_Roaming/              🛰️ Satellite Handover
    └── ntn_handover_sim.py           39x faster LEO roaming
```

### Key Documentation Files

```
Portfolio_B_Sovereign_Handshake/
├── README.md                    Technical overview
├── EXECUTIVE_SUMMARY.md         Portfolio summary + dual valuation
├── BUSINESS_SUMMARY.md          Realistic $40-60M valuation
├── PATENT_FAMILIES_COMPLETE.md  All 9 patent families
├── PATENT_CLAIMS_WITH_DATA.md   Claims with experimental evidence
│
├── PROVISIONAL_PATENT_THE_KNOT.md        Ready to file
├── PROVISIONAL_PATENT_HARD_SILICON.md    Ready to file ⭐ STRONGEST
├── PROVISIONAL_PATENT_ACTUARIAL_ORACLE.md Ready to file
└── PROVISIONAL_PATENT_NTN_ROAMING.md     Ready to file
```

---

## 💎 src/hls/ (Silicon-Ready Pack - $30K Value)

HLS C++ cores ready for FPGA/ASIC synthesis.

```
src/hls/
├── README.md                      📖 Complete usage documentation
├── SILICON_READY_PACK_COMPLETE.md 📋 Delivery report
├── Makefile                       🔧 Build system (Vivado HLS)
│
├── arc3_csi_correlator.h          ARC-3 data types & interfaces
├── arc3_csi_correlator.cpp        Synthesizable CSI engine
├── arc3_csi_correlator_tb.cpp     Testbench with golden vectors
│
├── dgate_fsm.h                    D-Gate+ 12-state FSM types
├── dgate_fsm.cpp                  Synthesizable FSM engine
└── dgate_fsm_tb.cpp               FSM testbench
```

**Quick Start:**
```bash
cd src/hls
make csim     # Run C simulation
make synth    # Synthesize to RTL (requires Vivado)
```

---

## ⚖️ legal/ (Litigation Pack - $20K Value)

Standards Essential Patent (SEP) claim charts and prior art analysis.

```
legal/
├── CLAIM_CHART_ARC3_TS33501.md         ARC-3: 5 claims → TS 33.501
├── CLAIM_CHART_DGATE_TS24501.md        D-Gate+: 6 claims → TS 24.501
├── CLAIM_CHART_PQLOCK_TS33501.md       PQLock: 5 claims → NIST/3GPP
├── CLAIM_CHART_UCRED_TS33501.md        U-CRED: 4 claims → MEC/IETF
├── CLAIM_CHART_QSTF_TS38331.md         QSTF: 5 claims → IoT standards
│
├── PRIOR_ART_ANALYSIS_ALL_FAMILIES.md  100+ patent/literature refs
├── SEP_ESSENTIALITY_SUMMARY.md         Royalty analysis (1.4-2.0%)
└── LITIGATION_PACK_COMPLETE.md         Delivery report
```

**Key Finding:** 25 claims across 5 families map to 3GPP/NIST standards.

---

## 🔴 data/pcaps/ (Red Team Pack - $10K Value)

Wireshark-compatible attack demonstration PCAPs.

```
data/pcaps/
├── README.md                       📖 Usage documentation
├── RED_TEAM_PACK_COMPLETE.md       📋 Delivery report
├── generate_attack_pcaps.py        🔧 PCAP generator script
│
├── quantum_downgrade_attack.pcap   Stingray blocked by D-Gate+
├── relay_attack_detection.pcap     Relay blocked by ARC-3 CSI
├── pqc_downgrade_attack.pcap       ML-KEM stripping detected
├── signaling_storm_ddos.pcap       DDoS mitigated by U-CRED
├── protocol_poisoning.pcap         Malformed NAS blocked
└── valid_permit_flow.pcap          Legitimate fallback flow
```

**Quick Start:**
```bash
wireshark data/pcaps/quantum_downgrade_attack.pcap
```

---

## 📋 docs/standards/ (Standards-Ready Pack - $40K Value)

Complete 3GPP Change Request documents ready for submission.

```
docs/standards/
├── 3GPP_TS33.501_CR001_PQLock_Hybrid_PQC.md          PQLock CR
├── 3GPP_TS33.501_CR002_ARC3_Physical_Layer_Binding.md ARC-3 CR
├── 3GPP_TS24.501_CR001_DGate_Firmware_Security_Gating.md D-Gate+ CR
│
├── 3GPP_STANDARDS_READY_PACK_INDEX.md    Navigation guide
└── STANDARDS_READY_PACK_COMPLETE_REPORT.md Delivery report
```

**Format:** Each CR follows official 3GPP TDoc template.

---

## 📚 docs/ (General Documentation)

```
docs/
├── standards/                    📋 3GPP Change Requests (see above)
│
├── reports/                      📊 Technical Reports
│   ├── PORTFOLIO_B_MASTER_SUMMARY.md    Comprehensive tech summary
│   ├── FIRST_PRINCIPLES_PHYSICS_UPGRADE.md Physics model details
│   ├── REVISED_VALUATION_5G.md          5G compatibility analysis
│   ├── WHY_THIS_MATTERS.md              Value explanation
│   ├── MD_CONFLICT_RESOLUTION_REPORT.md Documentation audit
│   └── *.md                             Various technical reports
│
├── audit/                        🔍 Audit Results
│   ├── DEEP_SCIENTIFIC_AUDIT.md         Scientific validation
│   ├── buyer_stress_test.py             Buyer validation script
│   └── *.md                             Audit reports
│
├── status/                       📈 Project Status
│   └── *.md                             Status updates
│
└── archive/                      📦 Historical Versions
    └── *.md                             Previous versions
```

---

## 📄 whitepapers/ (Academic Papers)

```
whitepapers/
├── README.md                              Index and reading guide
├── WHITE_PAPER_1_THERMODYNAMICS_OF_TRUST.md   Theoretical foundations (~95KB)
├── WHITE_PAPER_02_SOVEREIGN_ARCHITECTURE.md   System architecture (~89KB)
├── WHITE_PAPER_3_ECONOMIC_MONOPOLY.md         Economic analysis (~80KB)
├── WHITE_PAPER_4_METHODOLOGY_OF_TRUTH.md      Validation methodology (~70KB)
└── [Supporting files for each white paper]
```

---

## 🔍 Finding Specific Files

### By Technology

| Technology | Main Directory |
|------------|---------------|
| D-Gate+ | `Portfolio_B_Sovereign_Handshake/01_DGate_Cellular_Gating/` |
| U-CRED | `Portfolio_B_Sovereign_Handshake/02_UCRED_Stateless_Admission/` |
| PQLock | `Portfolio_B_Sovereign_Handshake/03_PQLock_Hybrid_Fabric/` |
| ARC-3 | `Portfolio_B_Sovereign_Handshake/04_ARC3_Channel_Binding/` |
| QSTF-V2 | `Portfolio_B_Sovereign_Handshake/05_QSTF_IoT_Resilience/` |
| Technical Knot | `Portfolio_B_Sovereign_Handshake/06_The_Technical_Knot/` |
| Hard Silicon | `Portfolio_B_Sovereign_Handshake/07_Hard_Engineering_Proofs/` |
| Actuarial Oracle | `Portfolio_B_Sovereign_Handshake/08_Actuarial_Loss_Models/` |
| NTN Roaming | `Portfolio_B_Sovereign_Handshake/09_NTN_Fast_Roaming/` |

### By File Type

| Type | Locations |
|------|-----------|
| Python Source | `Portfolio_B_Sovereign_Handshake/01-09/` |
| HLS C++ | `src/hls/` |
| Verilog RTL | `Portfolio_B_Sovereign_Handshake/07_Hard_Engineering_Proofs/` |
| PCAP Files | `data/pcaps/` |
| Claim Charts | `legal/` |
| 3GPP CRs | `docs/standards/` |
| Patents | `Portfolio_B_Sovereign_Handshake/PROVISIONAL_PATENT_*.md` |
| Visualizations | `Portfolio_B_Sovereign_Handshake/*/` (*.png files) |
| Datasets | `Portfolio_B_Sovereign_Handshake/*/` (*.csv files) |

### By Audience

| Audience | Start Here |
|----------|-----------|
| Engineer | `Portfolio_B_Sovereign_Handshake/README.md` |
| IP Lawyer | `legal/SEP_ESSENTIALITY_SUMMARY.md` |
| Standards | `docs/standards/3GPP_STANDARDS_READY_PACK_INDEX.md` |
| Security | `data/pcaps/README.md` |
| Business | `Portfolio_B_Sovereign_Handshake/BUSINESS_SUMMARY.md` |
| Executive | `README.md` (root) |

---

## 📊 File Statistics

| Category | Count |
|----------|-------|
| Python Files | ~86 |
| HLS C++ Files | 6 |
| Verilog Files | 1 |
| PCAP Files | 6 |
| Markdown Docs | ~112 |
| PNG Visualizations | ~54 |
| CSV Datasets | ~14 |
| Provisional Patents | 4 |
| Claim Charts | 5 |
| 3GPP Change Requests | 3 |
| **Total Tests** | **49** |

---

## ✅ Validation Commands

```bash
# Full validation (49 tests, ~2 minutes)
python validate_all_experiments.py

# File integrity check
python portfolio_b_final_check.py

# HLS C simulation
cd src/hls && make csim

# View attack PCAPs
wireshark data/pcaps/*.pcap
```

---

**Last Updated:** December 28, 2025  
**Status:** Clean repository (duplicates removed)  
**Validation:** 49/49 tests pass


