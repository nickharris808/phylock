#!/usr/bin/env python3
"""
Red Team PCAP Generator - Synthetic Attack Packet Captures
============================================================
Generates Wireshark-compatible PCAP files demonstrating attack scenarios
and PhyLock/D-Gate+ rejection behavior.

Target Audience: Security Engineers performing due diligence
Value: $10,000 (makes simulation feel "physically real")

Attack Scenarios Generated:
1. Quantum Downgrade Attack (Stingray/IMSI Catcher simulation)
2. Relay Attack (CSI mismatch detection)
3. Protocol Poisoning (NAS manipulation attempts)
4. Signaling Storm (DDoS on 5G control plane)
5. Credential Replay (Token reuse detection)
6. PQC Downgrade (Stripping ML-KEM from hybrid exchange)

Output: Binary PCAP files openable in Wireshark
Format: 5G NAS over SCTP/GTP-U encapsulation

Copyright 2025 Portfolio B - Sovereign Handshake
"""

import struct
import time
import os
import hashlib
import hmac
from datetime import datetime

# ============================================================================
# PCAP FILE FORMAT STRUCTURES
# ============================================================================

class PCAPWriter:
    """
    Writes packets to PCAP format (libpcap compatible).
    Can be opened directly in Wireshark, tcpdump, tshark.
    """
    
    # PCAP magic numbers
    PCAP_MAGIC = 0xa1b2c3d4  # Standard pcap (microsecond resolution)
    PCAP_VERSION_MAJOR = 2
    PCAP_VERSION_MINOR = 4
    PCAP_THISZONE = 0       # GMT
    PCAP_SIGFIGS = 0        # Accuracy of timestamps
    PCAP_SNAPLEN = 65535    # Max packet length
    PCAP_LINKTYPE = 1       # LINKTYPE_ETHERNET
    
    def __init__(self, filename):
        """Initialize PCAP file with global header."""
        self.filename = filename
        self.packets = []
        
    def add_packet(self, data, timestamp=None):
        """Add a packet with timestamp."""
        if timestamp is None:
            timestamp = time.time()
        self.packets.append((timestamp, data))
        
    def write(self):
        """Write all packets to PCAP file."""
        with open(self.filename, 'wb') as f:
            # Global header (24 bytes)
            f.write(struct.pack('<I', self.PCAP_MAGIC))
            f.write(struct.pack('<H', self.PCAP_VERSION_MAJOR))
            f.write(struct.pack('<H', self.PCAP_VERSION_MINOR))
            f.write(struct.pack('<i', self.PCAP_THISZONE))
            f.write(struct.pack('<I', self.PCAP_SIGFIGS))
            f.write(struct.pack('<I', self.PCAP_SNAPLEN))
            f.write(struct.pack('<I', self.PCAP_LINKTYPE))
            
            # Write each packet
            for timestamp, data in self.packets:
                ts_sec = int(timestamp)
                ts_usec = int((timestamp - ts_sec) * 1000000)
                orig_len = len(data)
                incl_len = min(orig_len, self.PCAP_SNAPLEN)
                
                # Packet header (16 bytes)
                f.write(struct.pack('<I', ts_sec))
                f.write(struct.pack('<I', ts_usec))
                f.write(struct.pack('<I', incl_len))
                f.write(struct.pack('<I', orig_len))
                
                # Packet data
                f.write(data[:incl_len])

# ============================================================================
# NETWORK LAYER BUILDERS
# ============================================================================

def build_ethernet_header(src_mac, dst_mac, ethertype=0x0800):
    """Build Ethernet II header (14 bytes)."""
    return dst_mac + src_mac + struct.pack('!H', ethertype)

def build_ip_header(src_ip, dst_ip, protocol=132, payload_len=0):
    """
    Build IPv4 header (20 bytes, no options).
    Protocol 132 = SCTP (5G control plane)
    Protocol 17 = UDP (GTP-U user plane)
    """
    version_ihl = (4 << 4) | 5  # IPv4, 5 dwords (20 bytes)
    dscp_ecn = 0
    total_length = 20 + payload_len
    identification = 0x1234
    flags_fragment = 0x4000  # Don't fragment
    ttl = 64
    checksum = 0  # Would calculate in real impl
    
    header = struct.pack('!BBHHHBBH',
                        version_ihl, dscp_ecn, total_length,
                        identification, flags_fragment,
                        ttl, protocol, checksum)
    header += src_ip + dst_ip
    return header

def build_sctp_header(src_port, dst_port, vtag=0x12345678):
    """
    Build SCTP header (12 bytes) for 5G control plane.
    Used for N2 (AMF-gNB) and N4 (SMF-UPF) interfaces.
    """
    checksum = 0  # Would be CRC32c in real impl
    return struct.pack('!HHII', src_port, dst_port, vtag, checksum)

def build_gtp_header(teid, payload_len, msg_type=0xFF):
    """
    Build GTP-U header (8 bytes) for user plane data.
    TEID = Tunnel Endpoint Identifier
    """
    flags = 0x30  # Version 1, PT=1 (GTP), no extension
    return struct.pack('!BBHI', flags, msg_type, payload_len, teid)

# ============================================================================
# 5G NAS MESSAGE BUILDERS
# ============================================================================

def build_nas_registration_request(ue_id, security_cap=0xFF):
    """
    Build 5G NAS Registration Request message.
    Reference: 3GPP TS 24.501 Section 8.2.6
    """
    # Extended protocol discriminator (5GMM = 0x7E)
    epd = 0x7E
    # Security header type (0 = plain NAS, no security)
    security_header = 0x00
    # Message type (Registration Request = 0x41)
    msg_type = 0x41
    # 5GS registration type (initial registration = 0x01)
    reg_type = 0x01
    # 5GS mobile identity (SUCI format, simplified)
    mobile_id_type = 0x01  # SUCI
    mobile_id_len = 8
    
    msg = bytes([epd, security_header, msg_type, reg_type])
    msg += bytes([mobile_id_len]) + ue_id[:8].ljust(8, b'\x00')
    
    # UE security capability (IE type 0x2E)
    msg += bytes([0x2E, 0x02, security_cap, security_cap])
    
    return msg

def build_nas_security_mode_command(nas_ksi=0x01, replay_detect=True, ciphering=0x02, integrity=0x02):
    """
    Build 5G NAS Security Mode Command.
    Reference: 3GPP TS 24.501 Section 8.2.25
    """
    epd = 0x7E
    # Security header type (integrity protected = 0x02)
    security_header = 0x02 if replay_detect else 0x00
    msg_type = 0x5D  # Security Mode Command
    
    # Selected NAS security algorithms
    # Ciphering: 0x00=NULL, 0x01=128-5G-EA1, 0x02=128-5G-EA2
    # Integrity: 0x00=NULL, 0x01=128-5G-IA1, 0x02=128-5G-IA2
    algorithms = (ciphering << 4) | integrity
    
    # ngKSI (NAS key set identifier)
    nas_ksi_field = nas_ksi & 0x0F
    
    # Replayed UE security capabilities
    replayed_sec_cap = bytes([0x2E, 0x02, 0xFF, 0xFF])
    
    msg = bytes([epd, security_header, msg_type, algorithms, nas_ksi_field])
    msg += replayed_sec_cap
    
    if replay_detect:
        # Add IMEISV request (for device binding)
        msg += bytes([0xE1])  # IMEISV request IE
        
    return msg

def build_nas_service_reject(cause_code):
    """
    Build 5G NAS Service Reject message.
    Reference: 3GPP TS 24.501 Section 8.2.22
    Cause codes: 7=5GS services not allowed, 15=no suitable cells
    """
    epd = 0x7E
    security_header = 0x00
    msg_type = 0x4D  # Service Reject
    
    return bytes([epd, security_header, msg_type, cause_code])

# ============================================================================
# PHYLOCK/D-GATE+ SPECIFIC PAYLOADS
# ============================================================================

def build_phylock_token(csi_fingerprint, session_id, timestamp):
    """
    Build PhyLock PLAB token (Physical Layer Attribute Binding).
    Format: TLV-E container with CSI handle and signature.
    Reference: Proposed TS 33.501 CR002
    """
    # IE type for PLAB token (proposed: 0x7D)
    ie_type = 0x7D
    
    # CSI handle (256-bit fingerprint)
    csi_handle = hashlib.sha256(csi_fingerprint).digest()
    
    # Session binding
    session_bytes = session_id.to_bytes(4, 'big')
    
    # Timestamp (32-bit UTC)
    ts_bytes = int(timestamp).to_bytes(4, 'big')
    
    # HMAC signature (simplified - real would be ECDSA/Ed25519)
    signature_input = csi_handle + session_bytes + ts_bytes
    signature = hmac.new(b'phylock_key_material', signature_input, 'sha256').digest()[:16]
    
    # Build TLV-E
    value = csi_handle + session_bytes + ts_bytes + signature
    length = len(value)
    
    return bytes([ie_type]) + struct.pack('!H', length) + value

def build_dgate_permit(ue_id, allowed_rats=0x0E, valid_hours=24):
    """
    Build D-Gate+ Downgrade Permit.
    Format: Signed permit structure per TS 24.501 CR001
    """
    # Permit version
    version = 0x01
    
    # UE identity (5G-GUTI truncated)
    ue_bytes = hashlib.sha256(ue_id).digest()[:8]
    
    # Validity period
    valid_from = int(time.time())
    valid_until = valid_from + (valid_hours * 3600)
    
    # RAT bitmap (bit 3=NR, bit 2=LTE, bit 1=UMTS, bit 0=GSM)
    # 0x0E = LTE+UMTS+GSM allowed (no 5G)
    rat_bitmap = allowed_rats
    
    # Build permit body
    permit_body = bytes([version, rat_bitmap])
    permit_body += ue_bytes
    permit_body += struct.pack('!II', valid_from, valid_until)
    
    # Ed25519 signature (simplified - 64 bytes)
    signature = hmac.new(b'dgate_permit_key', permit_body, 'sha256').digest()
    signature = signature + signature  # Extend to 64 bytes
    
    return permit_body + signature

def build_pqlock_hybrid_kem(include_mlkem=True):
    """
    Build PQLock hybrid key encapsulation.
    Contains both X25519 and ML-KEM-768 ciphertexts.
    Reference: Proposed TS 33.501 CR001
    """
    # X25519 ephemeral public key (32 bytes)
    x25519_pk = os.urandom(32)
    
    # ML-KEM-768 ciphertext (1088 bytes) - or empty if stripped
    if include_mlkem:
        mlkem_ct = os.urandom(1088)
    else:
        mlkem_ct = b''
    
    # Canonical Binding Tag (16 bytes)
    cbt_input = x25519_pk + mlkem_ct
    cbt = hashlib.sha256(cbt_input).digest()[:16]
    
    # TLV-E container
    ie_type = 0x7E  # PQ_KEM_CIPHERTEXT
    value = x25519_pk + mlkem_ct + cbt
    length = len(value)
    
    return bytes([ie_type]) + struct.pack('!H', length) + value

# ============================================================================
# ATTACK SCENARIO GENERATORS
# ============================================================================

def generate_downgrade_attack_pcap(output_file):
    """
    Scenario 1: Stingray/IMSI Catcher Downgrade Attack
    
    Attack sequence:
    1. Legitimate UE sends Registration Request (5G capable)
    2. Attacker (fake gNB) sends Service Reject cause #15
    3. D-Gate+ REJECTS the downgrade (no valid permit)
    4. UE remains on 5G, attacker fails
    
    Visual in Wireshark: Green → Red → Reject → Safe
    """
    pcap = PCAPWriter(output_file)
    
    # MAC addresses
    ue_mac = bytes.fromhex('001122334455')
    gnb_mac = bytes.fromhex('665544332211')
    attacker_mac = bytes.fromhex('DEADBEEF0001')
    
    # IP addresses
    ue_ip = bytes([192, 168, 1, 100])
    gnb_ip = bytes([192, 168, 1, 1])
    amf_ip = bytes([10, 0, 0, 1])
    attacker_ip = bytes([192, 168, 1, 99])
    
    timestamp = time.time()
    
    # =========================================================================
    # Packet 1: Normal 5G Registration Request (LEGITIMATE)
    # =========================================================================
    nas_reg = build_nas_registration_request(b'UE_NORMAL', security_cap=0xFF)
    
    sctp = build_sctp_header(38412, 38412)  # N2 interface port
    ip = build_ip_header(ue_ip, amf_ip, protocol=132, payload_len=len(sctp) + len(nas_reg))
    eth = build_ethernet_header(ue_mac, gnb_mac)
    
    pkt1 = eth + ip + sctp + nas_reg
    
    # Add comment marker for Wireshark
    # Using raw bytes annotation (visible in hex dump)
    comment = b'[LEGITIMATE] 5G Registration Request - UE connects to real gNB'
    pkt1_annotated = pkt1 + bytes([0x00] * 4) + comment
    
    pcap.add_packet(pkt1_annotated, timestamp)
    
    # =========================================================================
    # Packet 2: Attacker sends fake Service Reject (ATTACK)
    # =========================================================================
    timestamp += 0.050  # 50ms later
    
    # Cause #15 = "No suitable cells in tracking area"
    # This is what Stingray uses to force fallback to 2G/3G
    nas_reject = build_nas_service_reject(cause_code=15)
    
    sctp2 = build_sctp_header(38412, 38412)
    ip2 = build_ip_header(attacker_ip, ue_ip, protocol=132, payload_len=len(sctp2) + len(nas_reject))
    eth2 = build_ethernet_header(attacker_mac, ue_mac)
    
    pkt2 = eth2 + ip2 + sctp2 + nas_reject
    comment2 = b'[ATTACK] Stingray sends Service Reject #15 - Forcing 2G fallback'
    pkt2_annotated = pkt2 + bytes([0x00] * 4) + comment2
    
    pcap.add_packet(pkt2_annotated, timestamp)
    
    # =========================================================================
    # Packet 3: D-Gate+ FSM Rejects (PROTECTION)
    # =========================================================================
    timestamp += 0.008  # 8ms (FSM decision time)
    
    # D-Gate+ rejection - custom message type
    dgate_reject = bytes([
        0x7E,  # Extended protocol discriminator (5GMM)
        0x00,  # Security header
        0xDE, 0xAD,  # Custom: D-Gate+ REJECT
        0x01,  # Reason: No valid downgrade permit
        0x00,  # Permit validation failed
    ])
    
    # Add D-Gate+ state information
    dgate_state = b'FSM_STATE: PERMIT_REQUEST -> REJECT (no valid permit)'
    dgate_reject += bytes([len(dgate_state)]) + dgate_state
    
    sctp3 = build_sctp_header(38412, 38412)
    ip3 = build_ip_header(ue_ip, attacker_ip, protocol=132, payload_len=len(sctp3) + len(dgate_reject))
    eth3 = build_ethernet_header(ue_mac, attacker_mac)
    
    pkt3 = eth3 + ip3 + sctp3 + dgate_reject
    comment3 = b'[PROTECTED] D-Gate+ REJECTS downgrade - No valid permit from home AMF'
    pkt3_annotated = pkt3 + bytes([0x00] * 4) + comment3
    
    pcap.add_packet(pkt3_annotated, timestamp)
    
    # =========================================================================
    # Packet 4: UE continues on 5G (SAFE)
    # =========================================================================
    timestamp += 0.100  # 100ms later
    
    nas_smc = build_nas_security_mode_command(replay_detect=True)
    
    sctp4 = build_sctp_header(38412, 38412)
    ip4 = build_ip_header(gnb_ip, ue_ip, protocol=132, payload_len=len(sctp4) + len(nas_smc))
    eth4 = build_ethernet_header(gnb_mac, ue_mac)
    
    pkt4 = eth4 + ip4 + sctp4 + nas_smc
    comment4 = b'[SAFE] UE continues on 5G with legitimate gNB - Attack FAILED'
    pkt4_annotated = pkt4 + bytes([0x00] * 4) + comment4
    
    pcap.add_packet(pkt4_annotated, timestamp)
    
    pcap.write()
    print(f"✅ Generated: {output_file}")
    print(f"   Packets: 4 (Registration → Attack → Reject → Safe)")
    print(f"   Attack type: Stingray/IMSI Catcher downgrade")
    print(f"   Protection: D-Gate+ FSM rejects without valid permit")

def generate_relay_attack_pcap(output_file):
    """
    Scenario 2: Relay Attack Detection via CSI Mismatch
    
    Attack sequence:
    1. Legitimate UE at Position A registers, CSI stored
    2. Attacker relays credentials from Position B (500m away)
    3. ARC-3 detects CSI mismatch (ρ = 0.12 < 0.8 threshold)
    4. Access DENIED, security event logged
    
    Visual in Wireshark: Register → Relay → CSI Check → DENIED
    """
    pcap = PCAPWriter(output_file)
    
    # MACs
    ue_mac = bytes.fromhex('001122334455')
    gnb_mac = bytes.fromhex('665544332211')
    relay_mac = bytes.fromhex('BADBADBADBAD')
    
    # IPs
    ue_ip = bytes([192, 168, 1, 100])
    gnb_ip = bytes([192, 168, 1, 1])
    relay_ip = bytes([192, 168, 1, 200])
    
    timestamp = time.time()
    
    # =========================================================================
    # Packet 1: Original Registration with CSI (BASELINE)
    # =========================================================================
    # Simulate CSI fingerprint from Position A
    csi_position_a = b'CSI_POSITION_A_MULTIPATH_SIGNATURE_64_ANTENNAS'
    phylock_token_a = build_phylock_token(csi_position_a, 0x12345678, timestamp)
    
    nas_reg = build_nas_registration_request(b'LEGIT_UE')
    nas_reg += phylock_token_a
    
    sctp = build_sctp_header(38412, 38412)
    ip = build_ip_header(ue_ip, gnb_ip, protocol=132, payload_len=len(sctp) + len(nas_reg))
    eth = build_ethernet_header(ue_mac, gnb_mac)
    
    pkt1 = eth + ip + sctp + nas_reg
    comment1 = b'[BASELINE] UE registers at Position A - CSI fingerprint stored in PLAB registry'
    pcap.add_packet(pkt1 + bytes([0x00]*4) + comment1, timestamp)
    
    # =========================================================================
    # Packet 2: Attacker relays from Position B (ATTACK)
    # =========================================================================
    timestamp += 5.0  # 5 seconds later
    
    # Different CSI at Position B (500m away)
    csi_position_b = b'CSI_POSITION_B_DIFFERENT_MULTIPATH_COMPLETELY_DIFFERENT'
    phylock_token_b = build_phylock_token(csi_position_b, 0x12345678, timestamp)
    
    # Attacker replays same registration with stolen credentials
    nas_relay = build_nas_registration_request(b'LEGIT_UE')  # Same UE ID!
    nas_relay += phylock_token_b  # But different CSI
    
    sctp2 = build_sctp_header(38412, 38412)
    ip2 = build_ip_header(relay_ip, gnb_ip, protocol=132, payload_len=len(sctp2) + len(nas_relay))
    eth2 = build_ethernet_header(relay_mac, gnb_mac)
    
    pkt2 = eth2 + ip2 + sctp2 + nas_relay
    comment2 = b'[ATTACK] Relay device at Position B (500m away) sends stolen credentials'
    pcap.add_packet(pkt2 + bytes([0x00]*4) + comment2, timestamp)
    
    # =========================================================================
    # Packet 3: ARC-3 CSI Correlation Check (DETECTION)
    # =========================================================================
    timestamp += 0.000085  # 85ns (hardware correlation time)
    
    # CSI correlation result
    arc3_result = bytes([
        0x7E, 0x00,  # NAS header
        0xA3, 0xC3,  # Custom: ARC-3 correlation result
        0x00,        # Gate 1: FAIL
    ])
    
    # Correlation details
    correlation_data = struct.pack('!f', 0.12)  # ρ = 0.12
    threshold_data = struct.pack('!f', 0.80)    # Threshold = 0.80
    arc3_result += correlation_data + threshold_data
    arc3_result += b'RELAY_ATTACK_DETECTED: CSI mismatch from stored handle'
    
    sctp3 = build_sctp_header(38412, 38412)
    ip3 = build_ip_header(gnb_ip, relay_ip, protocol=132, payload_len=len(sctp3) + len(arc3_result))
    eth3 = build_ethernet_header(gnb_mac, relay_mac)
    
    pkt3 = eth3 + ip3 + sctp3 + arc3_result
    comment3 = b'[DETECTED] ARC-3 Gate 1: Correlation=0.12 < 0.80 threshold - RELAY ATTACK'
    pcap.add_packet(pkt3 + bytes([0x00]*4) + comment3, timestamp)
    
    # =========================================================================
    # Packet 4: Access DENIED (PROTECTION)
    # =========================================================================
    timestamp += 0.001  # 1ms
    
    # Registration Reject with cause
    nas_reject = bytes([
        0x7E, 0x00,  # NAS header
        0x44,        # Registration Reject
        0x6F,        # Cause: Protocol error, unspecified (#111)
    ])
    nas_reject += b'ARC3_SECURITY_EVENT: Relay attack blocked, credentials revoked'
    
    sctp4 = build_sctp_header(38412, 38412)
    ip4 = build_ip_header(gnb_ip, relay_ip, protocol=132, payload_len=len(sctp4) + len(nas_reject))
    eth4 = build_ethernet_header(gnb_mac, relay_mac)
    
    pkt4 = eth4 + ip4 + sctp4 + nas_reject
    comment4 = b'[BLOCKED] Registration REJECTED - Relay attack prevented by ARC-3'
    pcap.add_packet(pkt4 + bytes([0x00]*4) + comment4, timestamp)
    
    pcap.write()
    print(f"✅ Generated: {output_file}")
    print(f"   Packets: 4 (Baseline → Relay → Detection → Blocked)")
    print(f"   Attack type: Credential relay (500m separation)")
    print(f"   Protection: ARC-3 CSI correlation (ρ=0.12 < 0.80)")

def generate_pqc_downgrade_pcap(output_file):
    """
    Scenario 3: PQC Downgrade Attack (Stripping ML-KEM)
    
    Attack sequence:
    1. UE offers hybrid PQC capability (X25519 + ML-KEM-768)
    2. Attacker strips ML-KEM, forwards only X25519
    3. PQLock detects CBT mismatch (quantum attack indicator)
    4. Authentication ABORTED, re-authentication required
    
    Visual: Hybrid Offer → Strip Attack → CBT Mismatch → Abort
    """
    pcap = PCAPWriter(output_file)
    
    ue_mac = bytes.fromhex('001122334455')
    gnb_mac = bytes.fromhex('665544332211')
    attacker_mac = bytes.fromhex('CAFEBABE0001')
    
    ue_ip = bytes([192, 168, 1, 100])
    ausf_ip = bytes([10, 0, 0, 10])
    attacker_ip = bytes([192, 168, 1, 50])
    
    timestamp = time.time()
    
    # =========================================================================
    # Packet 1: UE sends hybrid PQC key exchange (LEGITIMATE)
    # =========================================================================
    pqlock_full = build_pqlock_hybrid_kem(include_mlkem=True)
    
    nas_auth = bytes([0x7E, 0x00, 0x57])  # Authentication Response
    nas_auth += pqlock_full
    
    sctp = build_sctp_header(38412, 38412)
    ip = build_ip_header(ue_ip, ausf_ip, protocol=132, payload_len=len(sctp) + len(nas_auth))
    eth = build_ethernet_header(ue_mac, gnb_mac)
    
    pkt1 = eth + ip + sctp + nas_auth
    comment1 = b'[LEGITIMATE] UE sends hybrid PQC: X25519 (32B) + ML-KEM-768 (1088B) + CBT'
    pcap.add_packet(pkt1 + bytes([0x00]*4) + comment1, timestamp)
    
    # =========================================================================
    # Packet 2: Attacker strips ML-KEM, forwards classical only (ATTACK)
    # =========================================================================
    timestamp += 0.010
    
    # Attacker removes ML-KEM ciphertext, leaving only X25519
    pqlock_stripped = build_pqlock_hybrid_kem(include_mlkem=False)
    
    nas_auth_stripped = bytes([0x7E, 0x00, 0x57])
    nas_auth_stripped += pqlock_stripped
    
    sctp2 = build_sctp_header(38412, 38412)
    ip2 = build_ip_header(attacker_ip, ausf_ip, protocol=132, payload_len=len(sctp2) + len(nas_auth_stripped))
    eth2 = build_ethernet_header(attacker_mac, gnb_mac)
    
    pkt2 = eth2 + ip2 + sctp2 + nas_auth_stripped
    comment2 = b'[ATTACK] MitM strips ML-KEM-768 - Only X25519 remains (quantum vulnerable!)'
    pcap.add_packet(pkt2 + bytes([0x00]*4) + comment2, timestamp)
    
    # =========================================================================
    # Packet 3: PQLock detects CBT mismatch (DETECTION)
    # =========================================================================
    timestamp += 0.005
    
    pqlock_detect = bytes([
        0x7E, 0x02,  # Security protected
        0x50, 0x51,  # Custom: PQLock alert
        0x01,        # Reason: CBT mismatch
    ])
    pqlock_detect += b'CBT_MISMATCH: Expected hybrid CBT, received classical-only'
    pqlock_detect += b' | QUANTUM_ATTACK_INDICATOR: ML-KEM component stripped'
    
    sctp3 = build_sctp_header(38412, 38412)
    ip3 = build_ip_header(ausf_ip, ue_ip, protocol=132, payload_len=len(sctp3) + len(pqlock_detect))
    eth3 = build_ethernet_header(gnb_mac, ue_mac)
    
    pkt3 = eth3 + ip3 + sctp3 + pqlock_detect
    comment3 = b'[DETECTED] PQLock CBT mismatch - Quantum downgrade attack detected!'
    pcap.add_packet(pkt3 + bytes([0x00]*4) + comment3, timestamp)
    
    # =========================================================================
    # Packet 4: Authentication ABORTED (PROTECTION)
    # =========================================================================
    timestamp += 0.002
    
    auth_abort = bytes([
        0x7E, 0x02,
        0x5C,        # Authentication Reject
        0x15,        # Cause: Synch failure (forces re-auth)
    ])
    auth_abort += b'PQLOCK_SECURITY_EVENT: Hybrid key exchange tampered, aborting'
    
    sctp4 = build_sctp_header(38412, 38412)
    ip4 = build_ip_header(ausf_ip, ue_ip, protocol=132, payload_len=len(sctp4) + len(auth_abort))
    eth4 = build_ethernet_header(gnb_mac, ue_mac)
    
    pkt4 = eth4 + ip4 + sctp4 + auth_abort
    comment4 = b'[PROTECTED] Authentication ABORTED - PQLock prevents quantum downgrade'
    pcap.add_packet(pkt4 + bytes([0x00]*4) + comment4, timestamp)
    
    pcap.write()
    print(f"✅ Generated: {output_file}")
    print(f"   Packets: 4 (Hybrid → Strip → Detection → Abort)")
    print(f"   Attack type: PQC downgrade (strip ML-KEM-768)")
    print(f"   Protection: PQLock Canonical Binding Tag (CBT)")

def generate_signaling_storm_pcap(output_file):
    """
    Scenario 4: Signaling Storm DDoS Attack
    
    Attack sequence:
    1. Normal control plane traffic
    2. Attacker floods with attach requests (10,000/sec)
    3. U-CRED stateless verification handles load
    4. Attacker requests throttled, legitimate traffic continues
    
    Visual: Normal → Storm → Throttle → Continue
    """
    pcap = PCAPWriter(output_file)
    
    legit_mac = bytes.fromhex('001122334455')
    gnb_mac = bytes.fromhex('665544332211')
    
    legit_ip = bytes([192, 168, 1, 100])
    gnb_ip = bytes([192, 168, 1, 1])
    
    timestamp = time.time()
    
    # =========================================================================
    # Packet 1: Normal attach (BASELINE)
    # =========================================================================
    nas_normal = build_nas_registration_request(b'NORMAL_UE')
    
    sctp = build_sctp_header(38412, 38412)
    ip = build_ip_header(legit_ip, gnb_ip, protocol=132, payload_len=len(sctp) + len(nas_normal))
    eth = build_ethernet_header(legit_mac, gnb_mac)
    
    pkt1 = eth + ip + sctp + nas_normal
    comment1 = b'[NORMAL] Legitimate UE registration - baseline traffic'
    pcap.add_packet(pkt1 + bytes([0x00]*4) + comment1, timestamp)
    
    # =========================================================================
    # Packets 2-11: Signaling storm (ATTACK - 10 sample packets)
    # =========================================================================
    for i in range(10):
        timestamp += 0.0001  # 100μs apart (10,000/sec rate)
        
        attacker_mac = bytes([0xDE, 0xAD, 0x00, 0x00, i >> 8, i & 0xFF])
        attacker_ip = bytes([10, i, (i*7) % 256, (i*13) % 256])
        
        # Random fake UE ID
        fake_ue_id = f'FAKE_UE_{i:04d}'.encode()
        nas_storm = build_nas_registration_request(fake_ue_id)
        
        sctp_storm = build_sctp_header(38412, 38412)
        ip_storm = build_ip_header(attacker_ip, gnb_ip, protocol=132, 
                                   payload_len=len(sctp_storm) + len(nas_storm))
        eth_storm = build_ethernet_header(attacker_mac, gnb_mac)
        
        pkt_storm = eth_storm + ip_storm + sctp_storm + nas_storm
        comment_storm = f'[STORM #{i+1}] DDoS attack - {10000} requests/sec flood'.encode()
        pcap.add_packet(pkt_storm + bytes([0x00]*4) + comment_storm, timestamp)
    
    # =========================================================================
    # Packet 12: U-CRED stateless throttle (PROTECTION)
    # =========================================================================
    timestamp += 0.001
    
    ucred_throttle = bytes([
        0x7E, 0x00,
        0x55, 0x43,  # Custom: U-CRED rate limit
        0x01,        # Action: Throttle
    ])
    ucred_throttle += b'UCRED_STORM_DETECTED: 10000 req/s exceeds 5000 threshold'
    ucred_throttle += b' | STATELESS_THROTTLE: Token bucket depleted for attack IPs'
    
    sctp_throttle = build_sctp_header(38412, 38412)
    ip_throttle = build_ip_header(gnb_ip, bytes([10, 0, 0, 1]), protocol=132,
                                  payload_len=len(sctp_throttle) + len(ucred_throttle))
    eth_throttle = build_ethernet_header(gnb_mac, bytes([0xFF]*6))
    
    pkt_throttle = eth_throttle + ip_throttle + sctp_throttle + ucred_throttle
    comment_throttle = b'[THROTTLED] U-CRED stateless rate limiting activated - DDoS mitigated'
    pcap.add_packet(pkt_throttle + bytes([0x00]*4) + comment_throttle, timestamp)
    
    # =========================================================================
    # Packet 13: Legitimate traffic continues (PROTECTED)
    # =========================================================================
    timestamp += 0.050
    
    nas_continue = build_nas_security_mode_command()
    
    sctp_continue = build_sctp_header(38412, 38412)
    ip_continue = build_ip_header(gnb_ip, legit_ip, protocol=132,
                                  payload_len=len(sctp_continue) + len(nas_continue))
    eth_continue = build_ethernet_header(gnb_mac, legit_mac)
    
    pkt_continue = eth_continue + ip_continue + sctp_continue + nas_continue
    comment_continue = b'[PROTECTED] Legitimate UE continues unaffected - DDoS absorbed'
    pcap.add_packet(pkt_continue + bytes([0x00]*4) + comment_continue, timestamp)
    
    pcap.write()
    print(f"✅ Generated: {output_file}")
    print(f"   Packets: 13 (Normal → 10 Storm → Throttle → Continue)")
    print(f"   Attack type: Signaling storm DDoS (10,000 req/s)")
    print(f"   Protection: U-CRED stateless rate limiting")

def generate_protocol_poisoning_pcap(output_file):
    """
    Scenario 5: Protocol Poisoning Attack
    
    Attack sequence:
    1. Attacker sends malformed NAS message
    2. D-Gate+ validates against exception matrix
    3. Invalid state transition blocked
    4. FSM remains in safe state
    
    Visual: Poison → Validate → Block → Safe
    """
    pcap = PCAPWriter(output_file)
    
    attacker_mac = bytes.fromhex('CAFEBABE0001')
    gnb_mac = bytes.fromhex('665544332211')
    
    attacker_ip = bytes([192, 168, 1, 66])
    gnb_ip = bytes([192, 168, 1, 1])
    
    timestamp = time.time()
    
    # =========================================================================
    # Packet 1: Malformed NAS with invalid IEs (ATTACK)
    # =========================================================================
    # Craft a poisoned message with:
    # - Invalid IE type
    # - Truncated length field
    # - Impossible state transition
    poisoned_nas = bytes([
        0x7E, 0x00,  # 5GMM
        0x41,        # Registration Request
        0x01,        # Initial registration
        0xFF,        # Invalid IE type (reserved)
        0x00, 0x10,  # Length claims 16 bytes
        # But only 4 bytes follow (truncated)
        0xDE, 0xAD, 0xBE, 0xEF,
    ])
    
    sctp = build_sctp_header(38412, 38412)
    ip = build_ip_header(attacker_ip, gnb_ip, protocol=132, payload_len=len(sctp) + len(poisoned_nas))
    eth = build_ethernet_header(attacker_mac, gnb_mac)
    
    pkt1 = eth + ip + sctp + poisoned_nas
    comment1 = b'[POISON] Malformed NAS: Invalid IE 0xFF, truncated length field'
    pcap.add_packet(pkt1 + bytes([0x00]*4) + comment1, timestamp)
    
    # =========================================================================
    # Packet 2: D-Gate+ exception validation (DETECTION)
    # =========================================================================
    timestamp += 0.002
    
    dgate_validate = bytes([
        0x7E, 0x00,
        0xD6, 0x47,  # Custom: D-Gate+ validation
        0x02,        # Status: Exception detected
    ])
    dgate_validate += b'EXCEPTION_MATRIX_CHECK: IE 0xFF not in valid set'
    dgate_validate += b' | TLV_VALIDATION: Length 16 > remaining bytes 4'
    dgate_validate += b' | FSM_STATE: Transition blocked per Z3 invariant'
    
    sctp2 = build_sctp_header(38412, 38412)
    ip2 = build_ip_header(gnb_ip, attacker_ip, protocol=132, payload_len=len(sctp2) + len(dgate_validate))
    eth2 = build_ethernet_header(gnb_mac, attacker_mac)
    
    pkt2 = eth2 + ip2 + sctp2 + dgate_validate
    comment2 = b'[VALIDATED] D-Gate+ exception matrix: Invalid IE and truncated TLV detected'
    pcap.add_packet(pkt2 + bytes([0x00]*4) + comment2, timestamp)
    
    # =========================================================================
    # Packet 3: Protocol error response (BLOCKED)
    # =========================================================================
    timestamp += 0.001
    
    error_response = bytes([
        0x7E, 0x00,
        0x44,        # Registration Reject
        0x6F,        # Cause: Protocol error (#111)
    ])
    error_response += b'DGATE_POISON_BLOCKED: FSM refused invalid transition'
    
    sctp3 = build_sctp_header(38412, 38412)
    ip3 = build_ip_header(gnb_ip, attacker_ip, protocol=132, payload_len=len(sctp3) + len(error_response))
    eth3 = build_ethernet_header(gnb_mac, attacker_mac)
    
    pkt3 = eth3 + ip3 + sctp3 + error_response
    comment3 = b'[BLOCKED] Protocol poisoning rejected - D-Gate+ FSM remains safe'
    pcap.add_packet(pkt3 + bytes([0x00]*4) + comment3, timestamp)
    
    pcap.write()
    print(f"✅ Generated: {output_file}")
    print(f"   Packets: 3 (Poison → Validate → Block)")
    print(f"   Attack type: Protocol poisoning (malformed NAS)")
    print(f"   Protection: D-Gate+ exception matrix + Z3 FSM")

def generate_valid_permit_flow_pcap(output_file):
    """
    Scenario 6: Legitimate Downgrade with Valid Permit
    
    This shows the CORRECT flow when D-Gate+ permit is used properly:
    1. UE in 5G coverage loses signal
    2. Requests downgrade permit from home AMF
    3. Receives signed permit (Ed25519)
    4. D-Gate+ validates and allows LTE fallback
    5. UE connects to LTE with valid authorization
    
    Visual: 5G Lost → Permit Request → Valid Permit → LTE Allowed
    """
    pcap = PCAPWriter(output_file)
    
    ue_mac = bytes.fromhex('001122334455')
    gnb_mac = bytes.fromhex('665544332211')
    enb_mac = bytes.fromhex('778899AABBCC')  # LTE eNB
    
    ue_ip = bytes([192, 168, 1, 100])
    amf_ip = bytes([10, 0, 0, 1])
    mme_ip = bytes([10, 0, 0, 2])  # LTE MME
    
    timestamp = time.time()
    
    # =========================================================================
    # Packet 1: 5G Service Lost (TRIGGER)
    # =========================================================================
    nas_detach = bytes([
        0x7E, 0x00,
        0x45,        # Deregistration Request (network initiated)
        0x02,        # Re-registration required
    ])
    nas_detach += b'CAUSE: 5G coverage lost, switching to legacy'
    
    sctp = build_sctp_header(38412, 38412)
    ip = build_ip_header(amf_ip, ue_ip, protocol=132, payload_len=len(sctp) + len(nas_detach))
    eth = build_ethernet_header(gnb_mac, ue_mac)
    
    pkt1 = eth + ip + sctp + nas_detach
    comment1 = b'[TRIGGER] 5G coverage lost - UE needs to fall back to LTE'
    pcap.add_packet(pkt1 + bytes([0x00]*4) + comment1, timestamp)
    
    # =========================================================================
    # Packet 2: D-Gate+ Permit Request (FSM ACTION)
    # =========================================================================
    timestamp += 0.100
    
    permit_req = bytes([
        0x7E, 0x02,  # Integrity protected
        0xD6, 0x01,  # Custom: D-Gate+ permit request
    ])
    permit_req += b'FSM_STATE: 5G_CONNECTED -> PERMIT_REQUEST'
    permit_req += b' | REQUESTING: Downgrade permit from home AMF'
    
    sctp2 = build_sctp_header(38412, 38412)
    ip2 = build_ip_header(ue_ip, amf_ip, protocol=132, payload_len=len(sctp2) + len(permit_req))
    eth2 = build_ethernet_header(ue_mac, gnb_mac)
    
    pkt2 = eth2 + ip2 + sctp2 + permit_req
    comment2 = b'[REQUEST] D-Gate+ FSM requests downgrade permit from home AMF'
    pcap.add_packet(pkt2 + bytes([0x00]*4) + comment2, timestamp)
    
    # =========================================================================
    # Packet 3: Valid Permit Received (AUTHORIZATION)
    # =========================================================================
    timestamp += 0.200
    
    permit = build_dgate_permit(b'VALID_UE_ID', allowed_rats=0x06, valid_hours=1)  # LTE+UMTS
    
    permit_resp = bytes([
        0x7E, 0x02,
        0xD6, 0x02,  # Custom: D-Gate+ permit response
    ])
    permit_resp += bytes([len(permit)]) + permit
    permit_resp += b' | SIGNATURE: Ed25519 verified by home AMF'
    
    sctp3 = build_sctp_header(38412, 38412)
    ip3 = build_ip_header(amf_ip, ue_ip, protocol=132, payload_len=len(sctp3) + len(permit_resp))
    eth3 = build_ethernet_header(gnb_mac, ue_mac)
    
    pkt3 = eth3 + ip3 + sctp3 + permit_resp
    comment3 = b'[AUTHORIZED] Valid permit received - Ed25519 signed by home AMF'
    pcap.add_packet(pkt3 + bytes([0x00]*4) + comment3, timestamp)
    
    # =========================================================================
    # Packet 4: D-Gate+ Validates and Allows (FSM TRANSITION)
    # =========================================================================
    timestamp += 0.008
    
    validate = bytes([
        0x7E, 0x02,
        0xD6, 0x03,  # Custom: D-Gate+ validation result
        0x00,        # Status: VALID
    ])
    validate += b'FSM_STATE: PERMIT_VALIDATION -> LEGACY_ALLOWED'
    validate += b' | ALLOWED_RATS: LTE (4G), UMTS (3G)'
    validate += b' | QUOTA_REMAINING: 10 legacy sessions'
    
    sctp4 = build_sctp_header(38412, 38412)
    ip4 = build_ip_header(ue_ip, mme_ip, protocol=132, payload_len=len(sctp4) + len(validate))
    eth4 = build_ethernet_header(ue_mac, enb_mac)
    
    pkt4 = eth4 + ip4 + sctp4 + validate
    comment4 = b'[ALLOWED] D-Gate+ validates permit - LTE fallback authorized'
    pcap.add_packet(pkt4 + bytes([0x00]*4) + comment4, timestamp)
    
    # =========================================================================
    # Packet 5: LTE Attach Success (CONNECTED)
    # =========================================================================
    timestamp += 0.500
    
    lte_attach = bytes([
        0x07,        # EPS Mobility Management
        0x42,        # Attach Accept
        0x01,        # EPS attach result: combined attach
    ])
    lte_attach += b'LEGACY_CONNECTED: LTE attach successful with valid D-Gate+ permit'
    
    sctp5 = build_sctp_header(36412, 36412)  # S1-AP port
    ip5 = build_ip_header(mme_ip, ue_ip, protocol=132, payload_len=len(sctp5) + len(lte_attach))
    eth5 = build_ethernet_header(enb_mac, ue_mac)
    
    pkt5 = eth5 + ip5 + sctp5 + lte_attach
    comment5 = b'[CONNECTED] LTE attach SUCCESS - Legitimate fallback with valid permit'
    pcap.add_packet(pkt5 + bytes([0x00]*4) + comment5, timestamp)
    
    pcap.write()
    print(f"✅ Generated: {output_file}")
    print(f"   Packets: 5 (5G Lost → Request → Permit → Validate → LTE)")
    print(f"   Scenario: Legitimate downgrade with valid D-Gate+ permit")
    print(f"   Shows: Correct security flow when permit is properly used")

# ============================================================================
# MAIN GENERATOR
# ============================================================================

def main():
    """Generate all attack scenario PCAPs."""
    print("=" * 70)
    print("RED TEAM PCAP GENERATOR - Portfolio B Sovereign Handshake")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output: data/pcaps/")
    print("=" * 70)
    print()
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Generate all attack scenarios
    scenarios = [
        ("quantum_downgrade_attack.pcap", generate_downgrade_attack_pcap,
         "Stingray/IMSI Catcher downgrade blocked by D-Gate+"),
        ("relay_attack_detection.pcap", generate_relay_attack_pcap,
         "Credential relay blocked by ARC-3 CSI correlation"),
        ("pqc_downgrade_attack.pcap", generate_pqc_downgrade_pcap,
         "ML-KEM stripping detected by PQLock CBT"),
        ("signaling_storm_ddos.pcap", generate_signaling_storm_pcap,
         "DDoS attack mitigated by U-CRED stateless throttling"),
        ("protocol_poisoning.pcap", generate_protocol_poisoning_pcap,
         "Malformed NAS blocked by D-Gate+ exception matrix"),
        ("valid_permit_flow.pcap", generate_valid_permit_flow_pcap,
         "Legitimate LTE fallback with valid D-Gate+ permit"),
    ]
    
    for filename, generator, description in scenarios:
        filepath = os.path.join(output_dir, filename)
        print(f"\n📦 {description}")
        generator(filepath)
    
    print("\n" + "=" * 70)
    print("PCAP GENERATION COMPLETE")
    print("=" * 70)
    print(f"\n📁 Output directory: {output_dir}")
    print(f"📊 Total scenarios: {len(scenarios)}")
    print(f"🔍 Open in Wireshark: wireshark data/pcaps/*.pcap")
    print("\n💡 Each PCAP contains annotated packets showing:")
    print("   - Attack attempt (red flag)")
    print("   - Detection mechanism (analysis)")
    print("   - Protection response (green shield)")
    print("\n🎯 Value: Security engineers can see protocol behavior without RF equipment")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


