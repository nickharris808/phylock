/*******************************************************************************
 * D-Gate+ Firmware Security Gating - HLS Header
 * 
 * High-Level Synthesis implementation of the formally verified 12-state
 * Finite State Machine for protocol downgrade prevention.
 * 
 * Target: Xilinx Vivado/Vitis HLS (also compatible with Catapult HLS)
 * Latency Target: 8ns per state transition @ 1GHz
 * 
 * This implements the D-Gate+ FSM from:
 *   Portfolio_B_Sovereign_Handshake/01_DGate_Cellular_Gating/verified_fsm_logic.py
 * 
 * Formal Verification: Z3 SMT solver proves safety/liveness properties
 * 
 * Standards Compliance:
 *   - 3GPP TS 24.501 (5G NAS Protocol)
 *   - 3GPP TS 33.501 (Security Architecture)
 *   - NIST FIPS 186-5 (ECDSA/Ed25519 Signatures)
 * 
 * Copyright 2025 Portfolio B - Sovereign Handshake
 ******************************************************************************/

#ifndef DGATE_FSM_H
#define DGATE_FSM_H

#include <ap_int.h>
#include <ap_fixed.h>
#include <hls_stream.h>

/*******************************************************************************
 * CONFIGURATION PARAMETERS
 ******************************************************************************/

// Maximum permit validity in clock cycles (1 hour @ 1GHz = 3.6T cycles)
// Use 40-bit counter, software handles overflow
#define PERMIT_VALIDITY_CYCLES 3600000000000ULL

// Emergency number detection (E911, E112, etc.)
#define EMERGENCY_911  0x393131UL   // ASCII "911"
#define EMERGENCY_112  0x313132UL   // ASCII "112"

// ECDSA-P256 signature size (64 bytes = 512 bits)
#define SIGNATURE_BITS 512

// Permit structure size (excluding signature)
#define PERMIT_DATA_BITS 256

// Maximum state transitions before fail-safe
#define MAX_TRANSITIONS 64

/*******************************************************************************
 * FSM STATE ENUMERATION
 * 
 * 12 states as specified in 3GPP TS 24.501 CR for D-Gate+
 * Z3 verification proves: No path from 5G_CONNECTED to LEGACY_CONNECTED
 * without passing through PERMIT_VALIDATION with valid signature.
 ******************************************************************************/

typedef enum {
    // Initial and 5G states
    STATE_INIT              = 0,    // Power-on, no network access
    STATE_5G_SCANNING       = 1,    // Searching for 5G cells
    STATE_5G_ATTACHING      = 2,    // Performing 5G NAS registration
    STATE_5G_CONNECTED      = 3,    // Successfully attached to 5G
    
    // Permit states
    STATE_PERMIT_REQUEST    = 4,    // Requesting downgrade permit from home AMF
    STATE_PERMIT_VALIDATION = 5,    // Verifying ECDSA signature on permit
    STATE_LEGACY_ALLOWED    = 6,    // Permit valid, legacy attachment authorized
    
    // Legacy network states
    STATE_LEGACY_ATTACHING  = 7,    // Connecting to 4G/3G/2G network
    STATE_LEGACY_CONNECTED  = 8,    // Successfully attached to non-5G network
    
    // Special states
    STATE_EMERGENCY_BYPASS  = 9,    // E911/E112 call in progress, permit waived
    STATE_REJECT            = 10,   // Downgrade denied, return to 5G scanning
    STATE_FAIL_SAFE         = 11    // Unrecoverable error, emergency-only mode
} dgate_state_t;

/*******************************************************************************
 * INPUT EVENT ENUMERATION
 ******************************************************************************/

typedef enum {
    // Network events
    EVENT_5G_FOUND          = 0,    // 5G cell detected during scan
    EVENT_5G_ATTACHED       = 1,    // 5G registration successful
    EVENT_5G_LOST           = 2,    // 5G signal lost
    EVENT_SERVICE_REJECT    = 3,    // SERVICE_REJECT with cause #15
    
    // Permit events
    EVENT_PERMIT_RECEIVED   = 4,    // Downgrade permit received from AMF
    EVENT_PERMIT_VALID      = 5,    // ECDSA signature verified successfully
    EVENT_PERMIT_INVALID    = 6,    // ECDSA signature verification failed
    EVENT_PERMIT_EXPIRED    = 7,    // Permit validity period exceeded
    
    // Legacy events
    EVENT_LEGACY_ATTACHED   = 8,    // Successfully attached to legacy network
    EVENT_LEGACY_FAILED     = 9,    // Legacy attachment failed
    
    // Emergency events
    EVENT_EMERGENCY_DIAL    = 10,   // User dialed E911/E112
    EVENT_EMERGENCY_END     = 11,   // Emergency call ended
    
    // Error events
    EVENT_TIMEOUT           = 12,   // Operation timeout
    EVENT_ERROR             = 13    // Unspecified error
} dgate_event_t;

/*******************************************************************************
 * DATA TYPES
 ******************************************************************************/

// Timestamp (40-bit for 1 hour validity @ 1GHz)
typedef ap_uint<40> timestamp_t;

// UE identifier (5G-GUTI truncated)
typedef ap_uint<64> ue_id_t;

// Radio Access Technology bitmap
// Bit 3: NR (5G), Bit 2: LTE (4G), Bit 1: UMTS (3G), Bit 0: GSM (2G)
typedef ap_uint<4> rat_bitmap_t;

// PLMN identifier (MCC-MNC)
typedef ap_uint<24> plmn_id_t;

// Geographic coordinates (Q16.16 fixed-point, degrees)
typedef ap_fixed<32, 16> geo_coord_t;

// ECDSA signature (512 bits = 64 bytes for P-256)
typedef ap_uint<SIGNATURE_BITS> signature_t;

// SHA-256 hash (256 bits)
typedef ap_uint<256> hash_t;

// State transition counter
typedef ap_uint<8> transition_count_t;

/*******************************************************************************
 * DOWNGRADE PERMIT STRUCTURE
 * 
 * Matches the TLV-E format specified in 3GPP TS 24.501 §9.11.3.X
 ******************************************************************************/

typedef struct {
    // Header (8 bits)
    ap_uint<8>      version;        // Permit format version (0x01)
    
    // Identity (96 bits)
    ue_id_t         issued_to;      // UE 5G-GUTI (truncated to 64 bits)
    plmn_id_t       issued_by;      // Home network PLMN-ID
    
    // Authorization (16 bits)
    rat_bitmap_t    allowed_rats;   // Bitmap of permitted RATs
    ap_uint<1>      emergency_only; // If 1, only E911/E112 traffic
    ap_uint<11>     reserved;       // Reserved for future use
    
    // Validity (80 bits)
    timestamp_t     valid_from;     // Permit activation time
    timestamp_t     valid_until;    // Permit expiration time
    
    // Geographic bounds (optional, 80 bits if present)
    ap_uint<1>      has_geo_bounds; // 1 if geographic restriction present
    geo_coord_t     latitude;       // Center latitude (if geo_bounds)
    geo_coord_t     longitude;      // Center longitude (if geo_bounds)
    ap_uint<16>     radius_km;      // Restriction radius in km
    
    // Signature (512 bits)
    signature_t     signature;      // ECDSA-P256 or Ed25519 signature
    
} downgrade_permit_t;

/*******************************************************************************
 * FSM CONTEXT STRUCTURE
 * 
 * Maintains all state for a single UE's D-Gate+ FSM instance.
 ******************************************************************************/

typedef struct {
    // Current FSM state
    dgate_state_t       current_state;
    
    // UE identity
    ue_id_t             ue_id;
    
    // Permit storage (cached if valid)
    downgrade_permit_t  cached_permit;
    ap_uint<1>          has_permit;
    
    // State history (for formal verification)
    transition_count_t  transition_count;
    dgate_state_t       previous_state;
    
    // Timing
    timestamp_t         state_entry_time;
    timestamp_t         permit_expiry;
    
    // Emergency state
    ap_uint<1>          in_emergency;
    ap_uint<32>         emergency_number;
    
    // Error counters
    ap_uint<8>          permit_failures;
    ap_uint<8>          attach_failures;
    
} fsm_context_t;

/*******************************************************************************
 * AXI4-STREAM INTERFACES
 ******************************************************************************/

// Input event stream
typedef struct {
    dgate_event_t       event;          // Event type
    ue_id_t             ue_id;          // UE identifier
    timestamp_t         timestamp;      // Event timestamp
    
    // Event-specific payload
    union {
        downgrade_permit_t  permit;     // For EVENT_PERMIT_RECEIVED
        ap_uint<32>         dialed_num; // For EVENT_EMERGENCY_DIAL
        ap_uint<8>          cause_code; // For EVENT_SERVICE_REJECT
    } payload;
    
    ap_uint<1>          last;           // TLAST for AXI4-Stream
} fsm_input_t;

// Output action stream
typedef struct {
    ue_id_t             ue_id;          // UE identifier
    dgate_state_t       new_state;      // State after transition
    
    // Action to take
    ap_uint<1>          allow_attach;   // 1 = proceed with attachment
    ap_uint<1>          request_permit; // 1 = send permit request to AMF
    ap_uint<1>          log_security;   // 1 = log security event
    rat_bitmap_t        allowed_rats;   // Which RATs are allowed
    
    // Diagnostic info
    dgate_state_t       prev_state;     // State before transition
    dgate_event_t       trigger_event;  // Event that triggered transition
    
    ap_uint<1>          last;           // TLAST for AXI4-Stream
} fsm_output_t;

/*******************************************************************************
 * TOP-LEVEL FUNCTION DECLARATIONS
 ******************************************************************************/

/**
 * @brief Main D-Gate+ FSM engine (top-level synthesizable function)
 * 
 * Processes input events and updates FSM state, enforcing the
 * "No downgrade without permit" security policy.
 * 
 * @param event_in  Input stream of FSM events (AXI4-Stream)
 * @param action_out Output stream of actions to take (AXI4-Stream)
 * 
 * Target latency: 8ns per state transition (8 clock cycles @ 1GHz)
 */
void dgate_fsm_engine(
    hls::stream<fsm_input_t>& event_in,
    hls::stream<fsm_output_t>& action_out
);

/**
 * @brief Process state transition
 * 
 * Core FSM logic: Given current state and input event, compute next state.
 * Implements the 12-state machine proven safe by Z3.
 * 
 * @param ctx       FSM context (current state, cached permit, etc.)
 * @param event     Input event
 * @param timestamp Current timestamp
 * @return          Output action to take
 */
fsm_output_t process_transition(
    fsm_context_t& ctx,
    const fsm_input_t& event,
    timestamp_t timestamp
);

/**
 * @brief Verify ECDSA-P256 signature on permit
 * 
 * Hardware-accelerated signature verification.
 * Uses elliptic curve point multiplication.
 * 
 * @param permit    Permit to verify
 * @param amf_pubkey AMF's public key (256 bits)
 * @return          true if signature valid, false otherwise
 */
bool verify_permit_signature(
    const downgrade_permit_t& permit,
    const ap_uint<256>& amf_pubkey
);

/**
 * @brief Check if permit is within validity period
 * 
 * @param permit    Permit to check
 * @param current   Current timestamp
 * @return          true if permit valid, false if expired
 */
inline bool is_permit_valid(
    const downgrade_permit_t& permit,
    timestamp_t current
) {
    return (current >= permit.valid_from && current <= permit.valid_until);
}

/**
 * @brief Check if dialed number is emergency
 * 
 * @param number    Dialed number (ASCII)
 * @return          true if E911/E112/etc
 */
inline bool is_emergency_number(ap_uint<32> number) {
    return (number == EMERGENCY_911 || 
            number == EMERGENCY_112 ||
            (number >> 8) == 0x393131 ||   // "911x"
            (number >> 8) == 0x313132);    // "112x"
}

/*******************************************************************************
 * FSM SAFETY INVARIANTS (for Z3 verification)
 * 
 * These properties are proven by the Z3 SMT solver in verified_fsm_logic.py:
 * 
 * 1. SAFETY: Cannot reach LEGACY_CONNECTED from 5G_CONNECTED without 
 *    passing through PERMIT_VALIDATION with permit.valid == true.
 * 
 * 2. LIVENESS: From any state, can reach EMERGENCY_BYPASS within 2 
 *    transitions if EVENT_EMERGENCY_DIAL occurs.
 * 
 * 3. TERMINATION: No infinite loops. All paths terminate within 
 *    MAX_TRANSITIONS transitions.
 * 
 * 4. NO_UNSAFE_ATTACH: If current_state ∈ {INIT, 5G_*, REJECT} and 
 *    event ≠ PERMIT_VALID, then next_state ∉ {LEGACY_ALLOWED, 
 *    LEGACY_ATTACHING, LEGACY_CONNECTED}.
 ******************************************************************************/

#endif // DGATE_FSM_H


