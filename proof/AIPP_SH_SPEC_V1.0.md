# AIPP Sovereign Handshake Protocol (SHP) Specification v1.0
**The Physical Constitution of Global Connectivity**

## 1. Executive Mandate
In the post-quantum era, the authorization of a radio link must be treated as a physical law, not a software preference. This specification defines the mandatory requirements for all 6G-compliant User Equipment (UE) and Base Stations (gNB) to ensure sovereign integrity, spectrum efficiency, and power stability.

---

## 2. Pillar 1: The Physical Lock (ARC-3)
### 2.1 Protocol: Zero-Math PHY Attestation
*   **Mandate:** Every connection request MUST be preceded by a **Channel State Information (CSI) Fingerprint** verification.
*   **Mechanism:** The gNB performs a complex-vector cross-correlation between the incoming physical wave and the stored **ARC-3 SCH Handle**.
*   **Threshold:** A correlation coefficient (Rho) of $< 0.5$ MUST result in immediate hardware-level rejection in $\le 100ns$.

### 2.2 Packet Format: ARC-3 SCH Header
```text
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Version     |     Type      |          Reserved             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       SCH Handle (Bits 63:32)                 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       SCH Handle (Bits 31:0)                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 CSI Fingerprint Digest (32-bit CRC)           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

---

## 3. Pillar 2: The Firmware Gate (D-Gate+)
### 3.1 Protocol: Formally Verified Gating
*   **Mandate:** The UE Baseband MUST implement the **D-Gate+ 5-State Machine** verified by the Z3 theorem prover.
*   **Mechanism:** Transitions to unencrypted or legacy states (2G/3G) are FORBIDDEN unless the device holds a **Time-Bounded Cryptographic Permit** signed by the home operator using Ed25519.
*   **Safety Invariant:** `NextState == Sovereign_Attach` IFF `Permit_Verified == True`.

### 3.2 Packet Format: Sovereign Permit TLV
```text
Type (1 byte): 0xEA (RAT_PERMIT)
Length (2 bytes): 0x0080 (128 bytes)
Value:
+---------------------------------------------------------------+
|                      Permit ID (8 bytes)                      |
+---------------------------------------------------------------+
|                    Expiry Timestamp (8 bytes)                 |
+---------------------------------------------------------------+
|                   Ed25519 Signature (64 bytes)                |
+---------------------------------------------------------------+
|                    Optional Policy (48 bytes)                 |
+---------------------------------------------------------------+
```

---

## 4. Pillar 3: The Stateless Mandate (U-CRED)
### 4.1 Protocol: State-Sparse Admission
*   **Mandate:** Resumed sessions MUST use **65-byte Stateless Binders** (Canonical CBOR) to prevent Edge-Switch memory exhaustion.
*   **Mechanism:** Full PQC verification is performed only once. Subsequent resumptions use the **Single-Verify PoP** path, reducing CPU cycles by 51%.
*   **Outage Mode:** The **Edge-Graded Enforcement (EGE)** allows valid binders to connect during central policy engine blackouts.

### 4.2 Packet Format: U-CRED Stateless Binder (CBOR Mapping)
```text
{
  "n": h'01234567',              // 8-byte Nonce
  "t": h'abcdef...01',           // 20-byte Thumbprint (Truncated SHA-256)
  "p": h'987654...ff',           // 20-byte Policy Hash
  "s": 1734567890                // 8-byte Timestamp
}
// Serialized Size: ~65 bytes
```

---

## 5. Pillar 4: The Hybrid Shield (PQLock)
### 5.1 Protocol: Post-Quantum Hybrid KDF
*   **Mandate:** All session keys MUST be derived using a **Hybrid KDF** mixing X25519 (Classical) and ML-KEM-768 (Quantum) secrets.
*   **Mechanism:** `PRK = HKDF_Extract(salt, s_classical || s_pq)`.
*   **Downgrade Detection:** Every handshake MUST include a **Canonical Binding Tag (CBT)** that HMACs the entire transcript. Any bit-level mismatch results in immediate session termination.

### 5.2 Packet Format: PQLock Hybrid Handshake TLV-E
```text
Type (1 byte): 0xEB (PQ_FABRIC)
Length (2 bytes): 0x0900 (2304 bytes)
Value:
+---------------------------------------------------------------+
|                    X25519 Public Key (32 bytes)               |
+---------------------------------------------------------------+
|                    ML-KEM-768 Ciphertext (1088 bytes)         |
+---------------------------------------------------------------+
|                    Canonical Binding Tag (32 bytes)           |
+---------------------------------------------------------------+
|                    Padding / Future Ext (1152 bytes)          |
+---------------------------------------------------------------+
```

---

## 6. Pillar 5: IoT Resiliency (QSTF-V2)
### 6.1 Protocol: Erasure-Coded PQC
*   **Mandate:** Large PQC payloads on NB-IoT MUST use **Temporal Erasure Coding** (14 data chunks + 4 parity chunks).
*   **Mechanism:** Devices MUST be capable of reconstructing the 768-byte key from any 14 chunks without retransmission.
*   **Congestion:** Devices MUST implement **Uniform Random Jitter** (0–30s) before connection attempts to prevent thundering herd crashes.

---

## 7. The Technical Knot: Power-Security Bridge
### 7.1 Protocol: Temporal Phase-Locking
*   **Mandate:** High-energy cryptographic operations (PQC verification) MUST be scheduled during the **"Quiet Valleys"** of the local power grid heartbeat.
*   **Synchronicity:** Handshakes MUST be phase-locked to the 100Hz grid cycle to neutralize voltage droops ($di/dt$ reduction of 40%).

---

## 8. Compliance and Certification
Failure to implement the AIPP Sovereign Handshake Standard renders the infrastructure **Uninsurable**. Compliance is verified through the **Master Sovereign Audit** suite.

*Signed,*
**The Sovereign Architect**

