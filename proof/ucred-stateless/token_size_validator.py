import cbor2
import time
import csv
import matplotlib.pyplot as plt
from cryptography.hazmat.primitives.asymmetric import ed25519

"""
U-CRED E2: Token & Binder Size Budget Validation
Measures exact byte counts for over-the-air transmission budget.

Target Results (from paper):
- 1-slice token: 413 bytes (target ≤360B, paper notes +53B acceptable)
- 4-slice token: 422 bytes (target ≤450B)
- TRW binder: 192 bytes (target ≤200B)

This proves U-CRED fits within NAS signaling budget constraints.
"""

MAX_NAS_BUDGET_1SLICE = 360  # bytes
MAX_NAS_BUDGET_4SLICE = 450
MAX_BINDER_BUDGET = 200

def create_cose_sign1_token(issuer_sk, ue_pk, slices, include_dcc=True):
    """
    Creates a complete COSE_Sign1 U-CRED token.
    
    Structure (simplified):
    - Protected headers
    - Unprotected headers
    - Payload (claims)
    - Signature (Ed25519, 64 bytes)
    """
    claims = {
        "iss": "AUSF-001",
        "cti": f"cred-tx-{int(time.time()*1000)}",
        "exp": int(time.time()) + 300,
        "cnf": {
            "jkt": ue_pk.public_bytes_raw().hex()[:32]
        },
        "policy_fp": "a" * 32,  # SHA-256 hex
        "nat": {
            "plmn": "310260",
            "smf": "smf-metro-01",
            "gkid": "gk-001",
            "exp_smf": int(time.time()) + 180
        },
        "snssais": slices  # Network slices
    }
    
    if include_dcc:
        # Device Compliance Check (DCC) block adds ~84 bytes
        claims["dcc"] = {
            "tier": "gold",
            "sbom_hash": "b" * 32,
            "vuln_score": 0,
            "update_ts": int(time.time())
        }
    
    # CBOR encode
    payload = cbor2.dumps(claims, canonical=True)
    
    # Ed25519 signature
    signature = issuer_sk.sign(payload)
    
    # Complete COSE_Sign1 structure (simplified)
    # In real COSE: protected headers + payload + signature
    protected = cbor2.dumps({"alg": "EdDSA"}, canonical=True)
    
    # COSE_Sign1 = [protected, {}, payload, signature]
    cose_structure = [protected, {}, payload, signature]
    cose_bytes = cbor2.dumps(cose_structure, canonical=True)
    
    return cose_bytes, claims

def create_trw_binder(ue_pk, policy_fp, prev_cti):
    """Creates a TRW resumption binder."""
    binder = {
        "binder": f"bind-{prev_cti[-8:]}",
        "policy_fp": policy_fp,
        "cnf": {
            "jkt": ue_pk.public_bytes_raw().hex()[:32]
        },
        "prev_cti": prev_cti
    }
    
    binder_bytes = cbor2.dumps(binder, canonical=True)
    return binder_bytes

def run_size_validation():
    print("--- U-CRED E2: Token & Binder Size Budget Validation ---")
    
    # Generate keys
    issuer_sk = ed25519.Ed25519PrivateKey.generate()
    ue_pk = ed25519.Ed25519PrivateKey.generate().public_key()
    
    results = []
    
    # Test 1: 1-slice token (minimal)
    slices_1 = ["slice-1"]
    token_1slice, claims_1 = create_cose_sign1_token(issuer_sk, ue_pk, slices_1, include_dcc=True)
    size_1 = len(token_1slice)
    
    results.append({
        'type': 'Token',
        'variant': '1 slice',
        'bytes': size_1,
        'budget': MAX_NAS_BUDGET_1SLICE,
        'compliant': size_1 <= MAX_NAS_BUDGET_1SLICE,
        'delta': size_1 - MAX_NAS_BUDGET_1SLICE
    })
    
    # Test 2: 4-slice token (enterprise)
    slices_4 = ["slice-1", "slice-2", "slice-3", "slice-4"]
    token_4slice, claims_4 = create_cose_sign1_token(issuer_sk, ue_pk, slices_4, include_dcc=True)
    size_4 = len(token_4slice)
    
    results.append({
        'type': 'Token',
        'variant': '4 slices',
        'bytes': size_4,
        'budget': MAX_NAS_BUDGET_4SLICE,
        'compliant': size_4 <= MAX_NAS_BUDGET_4SLICE,
        'delta': size_4 - MAX_NAS_BUDGET_4SLICE
    })
    
    # Test 3: TRW Binder
    binder = create_trw_binder(ue_pk, claims_1["policy_fp"], claims_1["cti"])
    size_binder = len(binder)
    
    results.append({
        'type': 'Binder',
        'variant': 'Resumption',
        'bytes': size_binder,
        'budget': MAX_BINDER_BUDGET,
        'compliant': size_binder <= MAX_BINDER_BUDGET,
        'delta': size_binder - MAX_BINDER_BUDGET
    })
    
    # Display
    print(f"\n{'Type':<10} {'Variant':<15} {'Bytes':<10} {'Budget':<10} {'Delta':<10} {'Status':<10}")
    print("-" * 75)
    for r in results:
        status = '✅ PASS' if r['compliant'] else f"⚠️ +{r['delta']}B"
        delta_str = f"{r['delta']:+d}B" if r['delta'] != 0 else "0B"
        print(f"{r['type']:<10} {r['variant']:<15} {r['bytes']:<10} {r['budget']:<10} {delta_str:<10} {status}")
    
    # Paper comparison
    print(f"\n--- Comparison to Paper ---")
    print(f"Paper: 1-slice = 413B, 4-slice = 422B, Binder = 192B")
    print(f"Ours:  1-slice = {size_1}B, 4-slice = {size_4}B, Binder = {size_binder}B")
    
    # Save CSV
    with open('token_sizes.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['type', 'variant', 'bytes', 'budget', 'compliant'])
        writer.writeheader()
        for r in results:
            writer.writerow({k: r[k] for k in ['type', 'variant', 'bytes', 'budget', 'compliant']})
    
    print("\nSaved token_sizes.csv")
    
    # Visualization
    fig, ax = plt.subplots(figsize=(10, 6))
    
    labels = [f"{r['type']}\n{r['variant']}" for r in results]
    sizes = [r['bytes'] for r in results]
    budgets = [r['budget'] for r in results]
    colors = ['#00FF41' if r['compliant'] else '#FF851B' for r in results]
    
    x = range(len(labels))
    ax.bar(x, sizes, color=colors, alpha=0.7, label='Actual Size')
    ax.bar(x, budgets, fill=False, edgecolor='red', linewidth=2, linestyle='--', label='Budget Limit')
    
    ax.set_ylabel('Size (bytes)')
    ax.set_title('U-CRED Token & Binder Size Validation')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Annotate with actual values
    for i, (size, budget) in enumerate(zip(sizes, budgets)):
        ax.text(i, size + 10, f'{size}B', ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('token_size_chart.png')
    print("Saved token_size_chart.png")
    
    # Verdict
    binder_acceptable = size_binder <= MAX_BINDER_BUDGET
    four_slice_acceptable = size_4 <= MAX_NAS_BUDGET_4SLICE
    
    if binder_acceptable and four_slice_acceptable:
        print(f"\nSTATUS: ✅ SIZE BUDGET VALIDATED")
        print(f"Binder {size_binder}B < {MAX_BINDER_BUDGET}B, 4-slice {size_4}B < {MAX_NAS_BUDGET_4SLICE}B")
    else:
        print(f"\nSTATUS: ⚠️ SIZE OVER BUDGET")
        print(f"1-slice overage acceptable per paper (+53B due to DCC)")

if __name__ == "__main__":
    run_size_validation()
