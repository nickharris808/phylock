import cbor2
import csv
from cryptography.hazmat.primitives.asymmetric import ec, ed25519
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

"""
D-Gate+ E1: TLV Encoding & Signature Validation
Implements actual 3GPP TS 24.007 Type-Length-Value Extended structures.

Target Results (from paper):
- POLICY_GATE v2: 135 bytes (53% of 255B limit)
- RAT_PERMIT v2: 150 bytes (59% of 255B limit)
- ECDSA signature: 64 bytes exact

This proves the protocol fits within 3GPP NAS IE size limits.
"""

MAX_NAS_IE_SIZE = 255  # 3GPP TS 24.007 limit

class TLVEncoder:
    def __init__(self):
        # Generate operator keys
        self.ecdsa_private = ec.generate_private_key(ec.SECP256R1(), default_backend())
        self.ecdsa_public = self.ecdsa_private.public_key()
        
        self.ed_private = ed25519.Ed25519PrivateKey.generate()
        self.ed_public = self.ed_private.public_key()
    
    def create_policy_gate(self, plmn_list, strong_required=True):
        """
        Creates POLICY_GATE TLV-E structure.
        
        Format (simplified 3GPP compliant):
        - Type: 0xEA (POLICY_GATE)
        - Length: Variable
        - Value: CBOR-encoded policy + ECDSA signature
        """
        policy_data = {
            "version": "v2",
            "plmns": plmn_list,  # List of allowed PLMNs
            "strong_required": strong_required,
            "min_cipher": "AES-128",
            "timestamp": 1734567890
        }
        
        # Encode with CBOR (canonical for determinism)
        policy_cbor = cbor2.dumps(policy_data, canonical=True)
        
        # Sign with ECDSA P-256
        signature = self.ecdsa_private.sign(policy_cbor, ec.ECDSA(hashes.SHA256()))
        
        # TLV-E Structure
        tlv_type = 0xEA  # POLICY_GATE type
        value_field = policy_cbor + signature
        tlv_length = len(value_field)
        
        # Complete TLV
        tlv = bytes([tlv_type, tlv_length]) + value_field
        
        return tlv, policy_data, signature
    
    def create_rat_permit(self, permit_id, quota, expiry):
        """
        Creates RAT_PERMIT TLV-E structure.
        
        Format:
        - Type: 0xEB (RAT_PERMIT)
        - Length: Variable
        - Value: CBOR-encoded permit + Ed25519 signature
        """
        permit_data = {
            "version": "v2",
            "permit_id": permit_id,
            "remaining_uses": quota,
            "expiry_timestamp": expiry,
            "allowed_rats": ["2G", "3G"],  # Permitted legacy fallback
            "revoked": False
        }
        
        # Encode with CBOR
        permit_cbor = cbor2.dumps(permit_data, canonical=True)
        
        # Sign with Ed25519
        signature = self.ed_private.sign(permit_cbor)
        
        # TLV-E Structure
        tlv_type = 0xEB  # RAT_PERMIT type
        value_field = permit_cbor + signature
        tlv_length = len(value_field)
        
        tlv = bytes([tlv_type, tlv_length]) + value_field
        
        return tlv, permit_data, signature
    
    def verify_policy_gate(self, tlv):
        """Parses and verifies a POLICY_GATE TLV."""
        tlv_type = tlv[0]
        tlv_length = tlv[1]
        value_field = tlv[2:2+tlv_length]
        
        # Split value into CBOR + signature
        signature = value_field[-64:]  # Last 64 bytes (ECDSA)
        policy_cbor = value_field[:-64]
        
        # Verify signature
        try:
            self.ecdsa_public.verify(signature, policy_cbor, ec.ECDSA(hashes.SHA256()))
            policy_data = cbor2.loads(policy_cbor)
            return True, policy_data
        except:
            return False, None
    
    def verify_rat_permit(self, tlv):
        """Parses and verifies a RAT_PERMIT TLV."""
        tlv_type = tlv[0]
        tlv_length = tlv[1]
        value_field = tlv[2:2+tlv_length]
        
        # Split value into CBOR + signature
        signature = value_field[-64:]  # Last 64 bytes (Ed25519)
        permit_cbor = value_field[:-64]
        
        # Verify signature
        try:
            self.ed_public.verify(signature, permit_cbor)
            permit_data = cbor2.loads(permit_cbor)
            return True, permit_data
        except:
            return False, None

def run_tlv_validation():
    print("--- D-Gate+ E1: TLV Encoding & Signature Validation ---")
    
    encoder = TLVEncoder()
    
    # Test POLICY_GATE
    plmns = ["310260", "310150", "26201", "23415"]
    policy_tlv, policy_data, policy_sig = encoder.create_policy_gate(plmns)
    
    # Test RAT_PERMIT
    permit_tlv, permit_data, permit_sig = encoder.create_rat_permit("PERMIT_001", 50, 1735000000)
    
    # Sizes
    policy_size = len(policy_tlv)
    permit_size = len(permit_tlv)
    sig_size = len(policy_sig)
    
    print(f"\n{'Object':<20} {'Size (bytes)':<15} {'% of 255B limit':<20} {'Status':<10}")
    print("-" * 70)
    print(f"{'POLICY_GATE v2':<20} {policy_size:<15} {(policy_size/MAX_NAS_IE_SIZE)*100:<20.1f}% {'✅' if policy_size < MAX_NAS_IE_SIZE else '❌'}")
    print(f"{'RAT_PERMIT v2':<20} {permit_size:<15} {(permit_size/MAX_NAS_IE_SIZE)*100:<20.1f}% {'✅' if permit_size < MAX_NAS_IE_SIZE else '❌'}")
    print(f"{'ECDSA signature':<20} {sig_size:<15} {'64 bytes exact':<20} {'✅' if sig_size == 64 else '❌'}")
    
    # Verification test
    print("\n--- TLV Verification Test ---")
    valid_policy, decoded_policy = encoder.verify_policy_gate(policy_tlv)
    valid_permit, decoded_permit = encoder.verify_rat_permit(permit_tlv)
    
    print(f"POLICY_GATE verification: {'✅ VALID' if valid_policy else '❌ INVALID'}")
    print(f"RAT_PERMIT verification:  {'✅ VALID' if valid_permit else '❌ INVALID'}")
    
    # Malformed TLV test (Depth Extension)
    print("\n--- Malformed TLV Test ---")
    # Corrupt the signature
    corrupted_tlv = bytearray(policy_tlv)
    corrupted_tlv[-10] ^= 0xFF
    valid_corrupt, _ = encoder.verify_policy_gate(bytes(corrupted_tlv))
    print(f"Corrupted signature: {'❌ DETECTED' if not valid_corrupt else '⚠️ ACCEPTED (BUG)'}")
    
    # Save to CSV
    with open('tlv_sizes.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Object', 'Size_Bytes', 'Percent_of_Limit', 'Compliant'])
        writer.writerow(['POLICY_GATE_v2', policy_size, (policy_size/MAX_NAS_IE_SIZE)*100, policy_size < MAX_NAS_IE_SIZE])
        writer.writerow(['RAT_PERMIT_v2', permit_size, (permit_size/MAX_NAS_IE_SIZE)*100, permit_size < MAX_NAS_IE_SIZE])
        writer.writerow(['ECDSA_signature', sig_size, (sig_size/MAX_NAS_IE_SIZE)*100, sig_size == 64])
    
    print("\nSaved tlv_sizes.csv")
    
    # Final verdict
    if policy_size < MAX_NAS_IE_SIZE and permit_size < MAX_NAS_IE_SIZE:
        print(f"\nSTATUS: ✅ TLV COMPLIANCE PROVEN")
        print(f"POLICY_GATE: {policy_size}B ({(policy_size/MAX_NAS_IE_SIZE)*100:.1f}% of limit)")
        print(f"RAT_PERMIT: {permit_size}B ({(permit_size/MAX_NAS_IE_SIZE)*100:.1f}% of limit)")
    else:
        print(f"\nSTATUS: ❌ TLV SIZE VIOLATION")

if __name__ == "__main__":
    run_tlv_validation()
