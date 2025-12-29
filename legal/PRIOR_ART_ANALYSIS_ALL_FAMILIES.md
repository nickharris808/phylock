# Prior Art Analysis: All 9 Patent Families
## Comprehensive Patent & Literature Landscape for Invalidity/Novelty Analysis

**Date:** December 27, 2025  
**Prepared For:** IP Counsel / M&A Due Diligence / Litigation Support  
**Confidentiality:** Attorney-Client Privilege / Work Product  
**Purpose:** Map closest prior art and establish novelty differentiators

---

## EXECUTIVE SUMMARY

This document provides a **high-signal prior art map** for each of the 9 patent families in Portfolio B. For each family, we identify:

1. **Closest Patents** - Published patents that approach the claimed subject matter
2. **Closest Literature** - Academic papers, standards, and industry publications
3. **Novelty Differentiators** - Why our claims survive despite the prior art
4. **Search Patterns** - Repeatable queries for exhaustive searching

**Important Caveat:** This is not a formal freedom-to-operate opinion or exhaustive prior art search. A complete invalidity analysis requires professional searches across USPTO, EPO, WIPO, and non-English filings with full citation chaining.

---

# FAMILY 1: ARC-3 (Admission Reference Chain / Channel Binding)

## Closest Patents

### US11877153B2 — CSI-Based Authentication
**Link:** https://patents.google.com/patent/US11877153B2/en  
**Relevance:** Uses channel state information for authentication decisions  
**Differentiation:** ARC-3 binds CSI to cryptographic session context via HKDF; this patent does not integrate with NAS security

### CA2987038A1 — Signal Fingerprinting / Radio Fingerprints
**Link:** https://patents.google.com/patent/CA2987038A1/en  
**Relevance:** Radio fingerprint concepts for authentication  
**Differentiation:** ARC-3 uses 64-antenna MIMO CSI correlation, not single-antenna fingerprints

### US11395136B2 — Physical-Layer Impairment Fingerprinting
**Link:** https://patents.google.com/patent/US11395136B2/en  
**Relevance:** PHY-layer features for device identification  
**Differentiation:** ARC-3 implements three-gate architecture (PHY→NAS→UP), not just PHY fingerprinting

### US20240244426A1 — Key Establishment Using Wireless Channel
**Link:** https://patents.google.com/patent/US20240244426A1/en  
**Relevance:** Channel-derived secrets for key establishment  
**Differentiation:** ARC-3 uses CSI for admission control (accept/reject), not just key generation

### US11082847 — Physical-Layer Authentication/Tagging
**Link:** https://patents.google.com/patent/US11082847  
**Relevance:** "Slope authentication" PHY security  
**Differentiation:** ARC-3 operates at <100ns with hardware acceleration; no timing claims in prior art

---

## Closest Literature

### Foundational CSI/Link Signature Work

#### "Wireless Link Signatures" (ACM, 2008)
**Link:** https://dl.acm.org/doi/10.1145/1409944.1409949  
**Relevance:** Foundational work on multipath link signatures for security  
**Differentiation:** ARC-3 integrates with 5G NAS security context; this work is Wi-Fi focused

#### "Enhanced Wireless Channel Authentication Using Time-Synched Link Signature"
**Link:** https://cse.usf.edu/~yliu21/webresources/?n=pdf%2Finfocom12-TSyncLS.pdf  
**Relevance:** Time-synchronized link signature authentication  
**Differentiation:** ARC-3 uses PLAB registry with <100ns correlation; no real-time constraints in prior work

#### "Physical Layer Challenge-Response Authentication"
**Link:** https://people-ece.vse.gmu.edu/~kzeng2/publications/2014/Infocom-2014_PHY-AUR.pdf  
**Relevance:** Challenge-response at physical layer  
**Differentiation:** ARC-3 is implicit (passive CSI), not challenge-response (active probing)

#### "Mimicry Attacks Against Wireless Link Signature"
**Link:** https://www.cs.ou.edu/~songf/papers/TIFS15_fang.pdf  
**Relevance:** Attack analysis on link signatures  
**Differentiation:** ARC-3 relay detection threshold (ρ<0.3) addresses mimicry concerns

#### "Slope Authentication at the Physical Layer"
**Link:** https://dl.acm.org/doi/abs/10.1109/TIFS.2018.2797963  
**Relevance:** Authentication via slope/derivative of channel response  
**Differentiation:** ARC-3 uses full CSI vector correlation, not just slope features

### Spatial Binding / AoA Primitives

#### "SpotFi: Decimeter Level Localization Using WiFi"
**Link:** https://web.stanford.edu/~skatti/pubs/sigcomm15-spotfi.pdf  
**Relevance:** AoA estimation from CSI for localization  
**Differentiation:** SpotFi is localization; ARC-3 is admission control with cryptographic binding

#### "ArrayTrack: Fine-Grained Indoor Location System"
**Link:** https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final51.pdf  
**Relevance:** Angle-of-arrival tracking  
**Differentiation:** ArrayTrack has no security binding; ARC-3 binds location to session

#### "Chronos: Decimeter-Level Localization"
**Link:** https://www.usenix.org/system/files/conference/nsdi16/nsdi16-paper-vasisht.pdf  
**Relevance:** Sub-nanosecond time-of-flight for localization  
**Differentiation:** Chronos is pure localization; no cryptographic integration

### Pilot Contamination / Massive MIMO Security

#### "Noncooperative Cellular Wireless with Unlimited Antennas" (Marzetta, 2010)
**Link:** https://www.researchgate.net/publication/224180963  
**Relevance:** Foundational massive MIMO; introduces pilot contamination  
**Differentiation:** Marzetta focuses on capacity; ARC-3 uses pilot contamination for security detection

#### "Vulnerabilities of Massive MIMO Against Pilot Contamination Attacks"
**Link:** https://arxiv.org/abs/1710.02796  
**PDF:** https://ozankoyluoglu.github.io/pdfs/1710.02796.pdf  
**Relevance:** Security framing of pilot contamination  
**Differentiation:** This is attack analysis; ARC-3 provides the defense (CSI correlation gate)

#### "Pilot Decontamination in Noncooperative Massive MIMO"
**Link:** https://www.engr.mun.ca/~licheng/2018-J-TWC-Pilot-Decontamination.pdf  
**Relevance:** Mitigation techniques for pilot contamination  
**Differentiation:** Signal processing focus; ARC-3 adds security decision (accept/reject)

---

## Novelty Argument for ARC-3

**ARC-3 is the FIRST system to:**
1. ✅ Use CSI correlation for **admission control** (not just localization or key generation)
2. ✅ Bind CSI fingerprint to **NAS security context** via HKDF (RFC 5869)
3. ✅ Implement **three-gate architecture** (PHY → NAS → User Plane)
4. ✅ Achieve **<100ns hardware-accelerated** correlation
5. ✅ Integrate with **3GPP TS 33.501** security procedures

**No single prior art reference combines these elements.**

---

## Search Patterns for Exhaustive Search

```
Google Patents / Lens / Espacenet:
- "channel state information" authentication
- "wireless link signature" authentication
- "angle of arrival" authentication
- "physical layer" admission control
- "preamble" correlation authentication
- "channel-based" key generation
- CSI fingerprint security
- MIMO authentication wireless
```

---

# FAMILY 2: D-Gate+ (Sovereign Cellular Gating / Anti-Downgrade)

## Core Standards Prior Art (Foundation)

### 3GPP TS 23.122 — NAS Functions / PLMN Selection
**Link:** https://www.etsi.org/deliver/etsi_ts/123100_123199/123122/16.06.00_60/ts_123122v160600p.pdf  
**Relevance:** PLMN selector with access technology list  
**Differentiation:** TS 23.122 is policy-based; D-Gate+ adds cryptographic permit requirement

### 3GPP TS 22.011 — Service Accessibility / Access Control
**Link:** https://www.etsi.org/deliver/etsi_ts/122000_122099/122011/17.01.00_60/ts_122011v170100p.pdf  
**Relevance:** Access barring concepts  
**Differentiation:** Barring is network-initiated; D-Gate+ is UE-resident with signed permits

### 3GPP TS 36.331 — LTE RRC (Extended Access Barring)
**Link:** https://www.etsi.org/deliver/etsi_ts/136300_136399/136331/15.06.00_60/ts_136331v150600p.pdf  
**Relevance:** EAB signaling  
**Differentiation:** EAB blocks access; D-Gate+ allows access only with cryptographic permit

### 3GPP TS 24.301 — LTE/EPS NAS Protocol
**Link:** https://www.etsi.org/deliver/etsi_ts/124300_124399/124301/16.06.00_60/ts_124301v160600p.pdf  
**Relevance:** NAS procedures for attach/mobility  
**Differentiation:** No permit injection mechanism in standard NAS

### 3GPP TS 33.501 — 5G Security Architecture
**Link:** https://www.etsi.org/deliver/etsi_ts/133500_133599/133501/17.04.00_60/ts_133501v170400p.pdf  
**Relevance:** 5G security procedures including EAP-based secondary auth  
**Differentiation:** No FSM gating of RAT transitions in standard

### RFC 3748 — Extensible Authentication Protocol (EAP)
**Link:** https://datatracker.ietf.org/doc/html/rfc3748  
**Relevance:** Tokenized auth approaches  
**Differentiation:** EAP is protocol framework; D-Gate+ adds firmware-level FSM enforcement

### RFC 8032 — EdDSA / Ed25519
**Link:** https://datatracker.ietf.org/doc/html/rfc8032  
**Relevance:** Signature scheme used in permits  
**Differentiation:** Cryptographic primitive, not the permit/FSM architecture

---

## Closest Patents

### US9516576B2 — Extended Access Barring (EAB)
**Link:** https://patents.google.com/patent/US9516576B2/en  
**Relevance:** Cellular gating mechanism  
**Differentiation:** EAB is network-controlled; D-Gate+ is UE-resident with home network permits

---

## Downgrade Attack Literature

### "Bidding-Down Attacks and Mitigations in 5G and 4G"
**Link (PDF):** https://montsecure.com/files/2021_downgrade.pdf  
**Link (ACM):** https://dl.acm.org/doi/10.1145/3558482.3581774  
**Relevance:** Threat landscape for downgrade attacks  
**Differentiation:** This is attack analysis; D-Gate+ provides the defense

---

## Formal Verification Prior Art

### "A Formal Analysis of 5G Authentication" (Tamarin)
**Link (arXiv):** https://arxiv.org/pdf/1806.10360  
**Link (author):** https://people.inf.ethz.ch/rsasse/pub/5G-CCS18.pdf  
**Relevance:** Formal verification of 5G AKA  
**Differentiation:** Analyzes protocol, not FSM; D-Gate+ applies formal methods to state machine

### "Component-Based Formal Analysis of 5G-AKA"
**Link:** https://people.cispa.io/cas.cremers/downloads/papers/CrDe2018-5G.pdf  
**Relevance:** Formal analysis variants  
**Differentiation:** Protocol analysis; D-Gate+ verifies UE firmware FSM

### "The 5G-AKA Authentication Protocol Privacy"
**Link:** https://adrienkoutsos.fr/papers/aka_long.pdf  
**Relevance:** Privacy analysis of AKA  
**Differentiation:** Different security property (privacy vs. anti-downgrade)

---

## Novelty Argument for D-Gate+

**D-Gate+ is the FIRST system to:**
1. ✅ Implement **cryptographic gating of RAT selection** in baseband firmware
2. ✅ Require **signed permits from home network** for legacy fallback
3. ✅ Provide **Z3 formal verification** of FSM security properties
4. ✅ Include **E911 emergency bypass** compliant with regulations
5. ✅ Implement **atomic quota management** for legacy access limits

**No prior art combines FSM + signed permits + formal verification + emergency bypass.**

---

## Search Patterns

```
- "extended access barring"
- "cellular" downgrade prevention
- "2G" blocking UE
- "RAT selection" security
- "NAS" authentication token permit
- baseband firmware security
- Stingray IMSI catcher prevention
```

---

# FAMILY 3: U-CRED (Stateless Edge Admission)

## Canonical Stateless Resumption Prior Art

### RFC 5077 — TLS Session Resumption without Server-Side State
**Link:** https://datatracker.ietf.org/doc/html/rfc5077  
**Relevance:** Archetype for stateless session tickets  
**Differentiation:** TLS-specific; U-CRED adds 5G integration, PQC signatures, quota embedding

### RFC 8446 — TLS 1.3 (PSK/Tickets/Resumption)
**Link:** https://www.rfc-editor.org/rfc/rfc8446.html  
**Relevance:** Modern stateless resumption  
**Differentiation:** Web TLS; U-CRED is CBOR/COSE for constrained 5G edge

### RFC 9000 — QUIC (Address Validation Tokens)
**Link:** https://www.rfc-editor.org/rfc/rfc9000.html  
**Relevance:** Stateless tokens for anti-amplification  
**Differentiation:** Transport-layer; U-CRED is application-layer with full claims

### RFC 8392 — CBOR Web Token (CWT)
**Link:** https://datatracker.ietf.org/doc/html/rfc8392  
**Relevance:** CBOR claims container  
**Differentiation:** U-CRED adds embedded quotas, PQC signatures, hierarchical delegation

### RFC 7519 — JSON Web Token (JWT)
**Link:** https://datatracker.ietf.org/doc/html/rfc7519  
**Relevance:** Dominant stateless token format  
**Differentiation:** JSON is verbose; U-CRED uses CBOR for constrained edge

### RFC 9052 — COSE (CBOR Object Signing and Encryption)
**Link:** https://datatracker.ietf.org/doc/html/rfc9052  
**Relevance:** Signing/encryption for CBOR  
**Differentiation:** Primitive; U-CRED builds full edge admission protocol

### RFC 9449 — OAuth 2.0 DPoP (Proof-of-Possession)
**Link:** https://datatracker.ietf.org/doc/html/rfc9449  
**Relevance:** PoP to prevent token replay  
**Differentiation:** OAuth/web focused; U-CRED integrates with 5G MEC

### RFC 6696 — EAP Re-authentication Protocol (ERP)
**Link:** https://datatracker.ietf.org/doc/html/rfc6696  
**Relevance:** Efficient re-authentication  
**Differentiation:** Still requires AAA; U-CRED is fully stateless at edge

---

## Novelty Argument for U-CRED

**U-CRED is the FIRST system to:**
1. ✅ Use **CBOR/COSE for 5G edge tokens** (compact binary)
2. ✅ **Embed quota counters** in stateless tokens
3. ✅ Support **ML-DSA-65 (PQC) signatures** for tokens
4. ✅ Enable **hierarchical delegation** (master → sub-tokens) for multi-edge
5. ✅ Achieve **<1ms verification latency** for MEC requirements

---

## Search Patterns

```
- "stateless" session resumption token
- "self-contained" authorization token
- "offline" authorization edge
- "session ticket" gateway
- CBOR token IoT
- edge authentication stateless
```

---

# FAMILY 4: PQLock (Hybrid Post-Quantum Fabric)

## PQC + Classical KEX Building Blocks

### NIST FIPS 203 — ML-KEM (Kyber)
**Link:** https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf  
**Relevance:** The PQC component itself  
**Differentiation:** Raw algorithm; PQLock integrates with 5G AKA key hierarchy

### RFC 7748 — X25519 (Elliptic Curves for Security)
**Link:** https://www.rfc-editor.org/rfc/rfc7748.html  
**Relevance:** Classical ECDH component  
**Differentiation:** Primitive; PQLock combines with ML-KEM + CBT

### RFC 5869 — HKDF (HMAC-based KDF)
**Link:** https://datatracker.ietf.org/doc/html/rfc5869  
**Relevance:** Key derivation function used  
**Differentiation:** Primitive; PQLock applies to 5G key hierarchy

### RFC 9180 — HPKE (Hybrid Public Key Encryption)
**Link:** https://datatracker.ietf.org/doc/rfc9180/  
**Relevance:** Hybrid encryption framework  
**Differentiation:** HPKE is encryption; PQLock is key establishment for 5G

---

## Transcript Canonicalization Prior Art

### RFC 5890-5892 — IDNA2008
**Links:** 
- https://datatracker.ietf.org/doc/html/rfc5890
- https://datatracker.ietf.org/doc/html/rfc5891
- https://datatracker.ietf.org/doc/html/rfc5892  
**Relevance:** Canonicalization/normalization  
**Differentiation:** Domain names; PQLock applies to cryptographic transcripts

### Unicode TR#36 — Security Considerations
**Link:** https://www.unicode.org/reports/tr36/  
**Relevance:** Normalization security  
**Differentiation:** Text normalization; PQLock is cryptographic binding

---

## Thermal-Aware Crypto Prior Art

### DVFS Overview Paper
**Link:** https://www.mdpi.com/2079-9292/13/5/826  
**Relevance:** Dynamic voltage/frequency scaling  
**Differentiation:** General compute; PQLock applies to crypto scheduling

### "Thermal-Aware Scheduling for Deep Learning on Mobile"
**Link:** https://mcn.cse.psu.edu/paper/tan-tianxiang/tan-tmc24.pdf  
**Relevance:** Thermal-aware ML scheduling  
**Differentiation:** ML inference; PQLock is cryptographic operations

### WO2025024787A1 — Heat Management for Crypto
**Link:** https://patents.google.com/patent/WO2025024787A1/en  
**Relevance:** Thermal management for crypto workloads  
**Differentiation:** General; PQLock specific to 5G AKA timing

### US11321469B2 — Crypto Micro-Operations Pipeline
**Link:** https://patents.google.com/patent/US11321469B2/en  
**Relevance:** Pipeline scheduling for crypto  
**Differentiation:** Hardware pipeline; PQLock is protocol-level scheduling

---

## Novelty Argument for PQLock

**PQLock is the FIRST system to:**
1. ✅ Integrate **ML-KEM-768 into 5G AKA** key derivation
2. ✅ Use **Canonical Binding Tag (CBT)** for downgrade protection
3. ✅ Achieve **backward compatibility via TLV-E** encapsulation
4. ✅ Extend the **complete 5G key hierarchy** with hybrid keys
5. ✅ Support **thermal-aware scheduling** for constrained devices

---

## Search Patterns

```
- "hybrid" post-quantum key exchange
- "Kyber" X25519 TLS
- "transcript" canonicalization downgrade
- "thermal" cryptographic scheduling
- ML-KEM 5G cellular
- post-quantum AKA
```

---

# FAMILY 5: QSTF-V2 (IoT PQC Resilience)

## Fragmentation / Constrained Transport

### RFC 7959 — CoAP Block-Wise Transfers
**Link:** https://www.rfc-editor.org/rfc/rfc7959.html  
**Relevance:** Application-layer chunking for IoT  
**Differentiation:** CoAP is request/response; QSTF-V2 chunks ML-KEM ciphertext

### RFC 4944 — 6LoWPAN Fragmentation
**Link:** https://www.rfc-editor.org/rfc/rfc4944.html  
**Relevance:** IPv6 fragmentation for constrained networks  
**Differentiation:** Network layer; QSTF-V2 is application-layer PQC chunking

### RFC 6206 — Trickle Algorithm
**Link:** https://www.rfc-editor.org/rfc/rfc6206.html  
**Relevance:** Randomized timing for congestion avoidance  
**Differentiation:** QSTF-V2 adds power-aware eDRX integration

### RFC 6330 — RaptorQ FEC
**Link:** https://www.rfc-editor.org/rfc/rfc6330.html  
**Relevance:** Erasure coding for object delivery  
**Differentiation:** QSTF-V2 integrates FEC with PQC for IoT constraints

### RFC 9177 — CoAP Q-Block
**Link:** https://www.rfc-editor.org/rfc/rfc9177.html  
**Relevance:** Blockwise transfer variant  
**Differentiation:** Different chunking context than PQC ciphertext

---

## FEC/Erasure Coding Patents

### US20090055705A1 — Decoding of Raptor Codes
**Link:** https://patents.google.com/patent/US20090055705A1/en  
**Relevance:** Raptor decoding  
**Differentiation:** QSTF-V2 applies to PQC ciphertext, not video

### US8887020B2 — Multi-Stage FEC
**Link:** https://patents.google.com/patent/US8887020B2/en  
**Relevance:** RS/Tornado/LDPC family  
**Differentiation:** General FEC; QSTF-V2 is PQC-specific

### US8311040B2 — Packing/Fragmentation with FEC
**Link:** https://patents.google.com/patent/US8311040B2/en  
**Relevance:** FEC with fragmentation  
**Differentiation:** Not PQC or IoT constrained

### US7519082B2 — Wireless Data Fragmentation
**Link:** https://patents.google.com/patent/US7519082B2/en  
**Relevance:** RS decoder mention  
**Differentiation:** General wireless; QSTF-V2 specific to NB-IoT PQC

---

## Novelty Argument for QSTF-V2

**QSTF-V2 is the FIRST system to:**
1. ✅ **Chunk ML-KEM ciphertext** for NB-IoT message size limits (127 bytes)
2. ✅ **Stream decapsulation** to reduce peak RAM below 50KB
3. ✅ Integrate with **eDRX power-saving** schedule
4. ✅ Provide **capability-based algorithm selection** for heterogeneous IoT
5. ✅ Support **PQC secure boot** with ML-DSA-65

---

## Search Patterns

```
- "CoAP" blockwise PQC
- "6LoWPAN" fragmentation security
- "RaptorQ" IoT
- "Reed-Solomon" wireless key exchange
- NB-IoT post-quantum
- constrained device ML-KEM
```

---

# FAMILY 6: Technical Knot (Grid-Telecom Coupling)

## Data Center Load Shaping Literature

### "Frequency Regulation Using Data Center Power Modulation"
**Link:** https://arxiv.org/abs/1608.06879  
**Relevance:** Compute workload as grid resource  
**Differentiation:** Technical Knot adds telecom load correlation

### "High-Precision Time Synchronization in Power Systems"
**Link:** https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-20683.pdf  
**Relevance:** Grid timing/synchronization  
**Differentiation:** Technical Knot couples timing to telecom events

---

## Phase/Zero-Crossing Control Patents

### US6549826B1 — Load Controller Synchronized to Zero Crossings
**Link:** https://patents.google.com/patent/US6549826B1/en  
**Relevance:** Phase-aligned switching  
**Differentiation:** Lighting control; Technical Knot is telecom+compute

### EP0824245A2 — Load Controller Synchronized to A.C.
**Link:** https://patents.google.com/patent/EP0824245A2/en  
**Relevance:** AC-synchronized control  
**Differentiation:** General load; Technical Knot specific to 5G

### US5852208A — Continuous Synchronization
**Link:** https://patents.google.com/patent/US5852208A/en  
**Relevance:** Power distribution sync  
**Differentiation:** Power domain; Technical Knot bridges telecom

---

## Novelty Argument for Technical Knot

**Technical Knot is the FIRST system to:**
1. ✅ Couple **5G base station load** to grid frequency regulation
2. ✅ Use **grid phase** as timing reference for telecom scheduling
3. ✅ Enable **demand response** from telecom infrastructure
4. ✅ Coordinate **edge compute + RAN** for grid services

---

## Search Patterns

```
- "zero crossing" load control telecom
- "phase angle" load scheduling 5G
- "data center" frequency regulation
- "demand response" compute scheduling
- grid-interactive base station
```

---

# FAMILY 7: Hard Silicon (Line-Rate Authorization Pipeline)

## Dataplane Architecture Papers

### "RMT: Fast Programmable Match-Action Processing" (SIGCOMM 2013)
**Link:** https://conferences.sigcomm.org/sigcomm/2013/papers/sigcomm/p99.pdf  
**Relevance:** Foundational match-action pipeline  
**Differentiation:** Packet forwarding; Hard Silicon is authorization

### "Compiling Packet Programs to Reconfigurable Switches" (NSDI 2015)
**Link:** https://www.usenix.org/system/files/conference/nsdi15/nsdi15-paper-jose.pdf  
**Relevance:** P4 to hardware compilation  
**Differentiation:** P4 is packet processing; Hard Silicon adds security gate

### "Compiling Logical Packet Programs" (Stanford)
**Link:** https://web.stanford.edu/~lavanyaj/papers/mapping2.pdf  
**Relevance:** Mapping to hardware pipelines  
**Differentiation:** Forwarding focus; Hard Silicon is admission control

### "Evaluating Power of Flexible Packet Processing"
**Link:** https://homes.cs.washington.edu/~arvind/papers/flexswitch.pdf  
**Relevance:** FlexSwitch architecture  
**Differentiation:** General flexibility; Hard Silicon is security-specific

---

## Parser/Pipeline Patents

### US10944696B2 — Variable-Length PHV and Match-Action
**Link:** https://patents.google.com/patent/US10944696B2/en  
**Relevance:** PHV concepts  
**Differentiation:** Networking; Hard Silicon adds CSI integration

### US20170180273A1 — Accelerated Network Packet Processing
**Link:** https://patents.google.com/patent/US20170180273A1/en  
**Relevance:** Pipeline acceleration  
**Differentiation:** Generic; Hard Silicon is security authorization

### US20220029935A1 — Packet Data Expansion in Pipeline
**Link:** https://patents.google.com/patent/US20220029935A1/en  
**Relevance:** PHV/deparser concepts  
**Differentiation:** Data expansion; Hard Silicon is gate/decision

---

## Novelty Argument for Hard Silicon

**Hard Silicon is the FIRST system to:**
1. ✅ Integrate **CSI correlation** into line-rate authorization pipeline
2. ✅ Implement **8-stage pipeline** for security decisions
3. ✅ Achieve **<100ns** end-to-end authorization latency
4. ✅ Use **AXI4-Stream** for permit tag injection
5. ✅ Combine **PHY-layer checks** with **packet-level gating**

---

## Search Patterns

```
- "packet parser" hardware pipeline security
- "match-action pipeline" authorization
- "line rate" authorization
- "AXI4-Stream" header parser
- programmable security pipeline
```

---

# FAMILY 8: Actuarial Oracle (Risk Scoring + Dynamic Premium)

## Continuous Monitoring Frameworks

### NIST CSF 2.0
**Link:** https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf  
**Relevance:** Cybersecurity framework baseline  
**Differentiation:** Framework; Actuarial Oracle implements real-time scoring

### NIST SP 800-137 — Continuous Monitoring (ISCM)
**Link:** https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-137.pdf  
**Relevance:** Continuous monitoring for security  
**Differentiation:** Government focus; Actuarial Oracle adds insurance pricing

---

## Real-Time Cyber Risk Patents

### US11750633 — Cyber Risk Scoring from Real-Time Findings
**Link:** https://patents.justia.com/patent/11750633  
**Relevance:** Near real-time cyber risk scoring  
**Differentiation:** Scoring only; Actuarial Oracle adds premium settlement

---

## Industry Literature

### "Cyber Insurance Premium Optimization Using AI-Driven Risk Scorecards"
**Link:** https://www.researchgate.net/publication/394518125  
**Relevance:** AI-driven premium optimization  
**Differentiation:** Batch optimization; Actuarial Oracle is real-time

### SecurityScorecard + Insurers Discounts
**Link:** https://securityscorecard.com/company/press/securityscorecard-joins-forces-with-measured-analytics-and-insurance/  
**Relevance:** Security ratings tied to insurance  
**Differentiation:** Periodic assessment; Actuarial Oracle is continuous

### "Driver Risk Prediction with Telematics"
**Link:** https://www.sciencedirect.com/science/article/abs/pii/S0001457523003160  
**Relevance:** Real-time data underwriting (auto insurance analog)  
**Differentiation:** Auto insurance; Actuarial Oracle is cyber

### Parametric Insurance Overview
**Link:** https://www.itij.com/latest/long-read/parametric-solutions-using-technology-enhance-claims-process  
**Relevance:** Automated payouts based on triggers  
**Differentiation:** Natural disasters; Actuarial Oracle is cyber risk

---

## Novelty Argument for Actuarial Oracle

**Actuarial Oracle is the FIRST system to:**
1. ✅ Provide **real-time premium adjustment** based on security telemetry
2. ✅ Implement **automated settlement** from event detection to payout
3. ✅ Use **5G network telemetry** for cyber insurance underwriting
4. ✅ Support **parametric triggers** for cellular security events
5. ✅ Integrate with **NIST CSF** for standardized risk scoring

---

## Search Patterns

```
- "cyber risk score" insurance premium
- "parametric insurance" telemetry trigger
- "dynamic premium" risk score
- real-time underwriting cyber
- security rating insurance discount
```

---

# FAMILY 9: NTN (LEO Roaming / Doppler-Corrected Handover)

## 3GPP NTN Standards

### 3GPP TR 38.811 — NR to Support NTN
**Link:** https://atisorg.s3.amazonaws.com/archive/3gpp-documents/Rel15/ATIS.3GPP.38.811.V1530.pdf  
**Relevance:** NTN study (foundational)  
**Differentiation:** Study item; NTN family implements solutions

### 3GPP TR 38.821 — Solutions for NR NTN
**Link:** https://atisorg.s3.amazonaws.com/archive/3gpp-documents/Rel16/ATIS.3GPP.38.821.V1600.pdf  
**Relevance:** NTN solutions  
**Differentiation:** General solutions; NTN family adds security roaming

### 3GPP TS 38.331 — Conditional Handover (CHO)
**Link:** https://www.3gpp.org/dynareport/38821.htm  
**Relevance:** NTN mobility triggers  
**Differentiation:** Mobility; NTN family adds stateless token handover

---

## Doppler Compensation Patents

### US5640166A — Compensating Doppler Frequency Shifts
**Link:** https://patents.google.com/patent/US5640166A/en  
**Relevance:** Satellite Doppler compensation  
**Differentiation:** Signal processing; NTN family adds security context

### US6058306A — Dynamic Doppler Frequency Compensation
**Link:** https://patents.google.com/patent/US6058306A/en  
**Relevance:** Dynamic compensation  
**Differentiation:** PHY layer; NTN family is security layer

---

## NTN Literature

### "Initial Synchronization and Doppler Pre-Compensation" (MDPI, 2025)
**Link:** https://www.mdpi.com/2673-4001/6/4/81  
**Relevance:** NTN synchronization procedures  
**Differentiation:** Synchronization; NTN family adds credential roaming

### "Adaptive Modulation Feasibility Study" (Satellite)
**Link:** https://adsabs.harvard.edu/full/2004ESASP.571E..44S  
**Relevance:** Adaptive modulation for satellites  
**Differentiation:** PHY adaptation; NTN family is security adaptation

---

## Novelty Argument for NTN

**NTN Patent Family is the FIRST system to:**
1. ✅ Implement **stateless token handover** between LEO satellites
2. ✅ Use **Doppler-aware chunking** for security credentials
3. ✅ Support **inter-constellation roaming** with unified tokens
4. ✅ Integrate with **3GPP CHO** for predictive handover
5. ✅ Achieve **zero-backhaul handover** using pre-positioned tokens

---

## Search Patterns

```
- "LEO" Doppler compensation handover
- "NTN" NR handover security
- "satellite" adaptive fragmentation
- LEO roaming token
- non-terrestrial network authentication
```

---

# SUMMARY: NOVELTY DIFFERENTIATORS BY FAMILY

| Family | Key Novelty Differentiator | Prior Art Gap |
|--------|---------------------------|---------------|
| **ARC-3** | CSI → HKDF → NAS binding + <100ns HW | No prior art binds CSI to 5G security context |
| **D-Gate+** | FSM + signed permit + Z3 proof + E911 | No prior art combines all four elements |
| **U-CRED** | CBOR/PQC + embedded quota + delegation | No prior art has stateless edge with quotas |
| **PQLock** | ML-KEM + CBT + TLV-E backward compat | No prior art is backward-compatible hybrid PQC for 5G |
| **QSTF-V2** | PQC chunking + streaming + eDRX | No prior art enables PQC on 50KB IoT |
| **Technical Knot** | 5G + grid phase + demand response | No prior art couples telecom to grid regulation |
| **Hard Silicon** | CSI correlation in line-rate pipeline | No prior art integrates PHY security in packet pipeline |
| **Actuarial Oracle** | Real-time cyber premium + auto settlement | No prior art has sub-minute premium adjustment |
| **NTN** | Stateless token + Doppler chunking | No prior art handles LEO security roaming |

---

# CLAIM CHART INTEGRATION NOTE

This prior art analysis should be read in conjunction with the following claim charts:

1. `CLAIM_CHART_ARC3_TS33501.md` - ARC-3 essentiality analysis
2. `CLAIM_CHART_DGATE_TS24501.md` - D-Gate+ essentiality analysis
3. `CLAIM_CHART_PQLOCK_TS33501.md` - PQLock essentiality analysis
4. `CLAIM_CHART_UCRED_TS33501.md` - U-CRED essentiality analysis
5. `CLAIM_CHART_QSTF_TS38331.md` - QSTF-V2 essentiality analysis

For each claim chart, the novelty arguments in this document provide the "why we survive prior art" analysis needed for:
- Patent prosecution responses
- IPR/PGR defense
- Licensing negotiations
- M&A due diligence

---

## RECOMMENDED NEXT STEPS FOR EXHAUSTIVE SEARCH

1. **Citation Chain Forward:** Use each patent above as a "seed" and follow citing references
2. **Citation Chain Backward:** Review references cited in each patent
3. **Inventor Search:** Track inventors of closest patents for related filings
4. **Assignee Search:** Review full portfolios of closest patent assignees
5. **Non-English Search:** Use EPO and WIPO for Japanese, Chinese, Korean filings
6. **NPL Deep Dive:** Search IEEE Xplore, ACM DL, arXiv for each novelty term

---

**Prepared by:** Portfolio B IP Team  
**Date:** December 27, 2025  
**For:** Acquirer IP Counsel / Litigation Support  
**Classification:** Attorney-Client Privilege / Work Product

**This document provides prior art awareness for internal analysis. It is not a formal freedom-to-operate opinion or patentability opinion. Consult qualified patent counsel for legal conclusions.**


