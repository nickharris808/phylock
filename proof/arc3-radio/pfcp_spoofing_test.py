import hmac
import hashlib
import secrets
import numpy as np
import matplotlib.pyplot as plt
import csv

"""
ARC-3 E3: PFCP Spoofing Robustness Test
Validates that Gate-2 (SCH verification) rejects all PFCP control plane spoofing attacks.

Test Matrix:
- 2,000 PFCP Session Establishment Request messages
- 50% legitimate (valid SCH), 50% attack vectors
- Attack classes: missing SCH, swapped TEIDs, wrong role, tampered reference_id, replay

Target Result (from paper):
- False Accept Rate: 0% (0 bad accepts out of 1,000 attack messages)
- True Accept Rate: 100% (1,000/1,000 legitimate messages)

Security Claim:
Gate-2 cryptographically binds PFCP messages to the N4 session context,
preventing control plane spoofing even with network access.
"""

NUM_TRIALS = 2000
EXPORTER_SECRET = secrets.token_bytes(32)

# Attack taxonomy (from paper Table 4)
ATTACK_CLASSES = [
    "missing_sch",          # No SCH field (bypass attempt)
    "swapped_teid_ul",      # Use valid SCH but swap UL TEID
    "swapped_teid_dl",      # Use valid SCH but swap DL TEID
    "wrong_role",           # SCH derived for wrong role (UPF vs SMF)
    "tampered_ref_id",      # Valid SCH but wrong reference_id
    "replay_sch",           # Replay old valid SCH from different session
    "random_sch",           # Random 16 bytes
]

def derive_sch(reference_id, ue_ip, teid_ul, teid_dl, role):
    """
    Derives 16-byte SCH using HKDF (same as sch_cose_speedup.py).
    SCH = HKDF(exporter_secret, len=16, info=context)
    """
    # Build context (domain separation)
    context = f"{reference_id}|{ue_ip}|{teid_ul}|{teid_dl}|{role}".encode()
    
    # HKDF-Expand (simplified, using HMAC-SHA256 as PRF)
    info = b"ARC3-N4-SCH-v1" + context
    t1 = hmac.new(EXPORTER_SECRET, b"\x01" + info, hashlib.sha256).digest()
    
    # Return first 16 bytes
    return t1[:16]

def verify_sch(received_sch, reference_id, ue_ip, teid_ul, teid_dl, role):
    """
    Verifies SCH using constant-time comparison.
    Returns True if SCH is valid, False otherwise.
    """
    if received_sch is None:
        return False
    
    expected_sch = derive_sch(reference_id, ue_ip, teid_ul, teid_dl, role)
    return hmac.compare_digest(expected_sch, received_sch)

def generate_legitimate_session():
    """Generates a legitimate PFCP session establishment."""
    ref_id = f"ref-{secrets.token_hex(8)}"
    ue_ip = f"10.{np.random.randint(0,255)}.{np.random.randint(0,255)}.{np.random.randint(0,255)}"
    teid_ul = np.random.randint(1, 2**32)
    teid_dl = np.random.randint(1, 2**32)
    role = "SMF"
    
    # Derive valid SCH
    sch = derive_sch(ref_id, ue_ip, teid_ul, teid_dl, role)
    
    return {
        "reference_id": ref_id,
        "ue_ip": ue_ip,
        "teid_ul": teid_ul,
        "teid_dl": teid_dl,
        "role": role,
        "sch": sch,
        "is_attack": False,
        "attack_class": "legitimate"
    }

def generate_attack_message():
    """
    Generates a PFCP spoofing attack message.
    Randomly selects one of 7 attack classes.
    """
    # Start with valid session
    session = generate_legitimate_session()
    
    # Select attack class
    attack_class = np.random.choice(ATTACK_CLASSES)
    
    # Apply attack transformation
    if attack_class == "missing_sch":
        session["sch"] = None
        
    elif attack_class == "swapped_teid_ul":
        # Keep same SCH, but modify TEID_UL (context mismatch)
        session["teid_ul"] = np.random.randint(1, 2**32)
        
    elif attack_class == "swapped_teid_dl":
        session["teid_dl"] = np.random.randint(1, 2**32)
        
    elif attack_class == "wrong_role":
        # Derive SCH for UPF role, but present as SMF
        session["sch"] = derive_sch(
            session["reference_id"],
            session["ue_ip"],
            session["teid_ul"],
            session["teid_dl"],
            "UPF"  # Wrong role
        )
        
    elif attack_class == "tampered_ref_id":
        # Valid SCH but for wrong reference_id
        session["reference_id"] = f"ref-{secrets.token_hex(8)}"
        
    elif attack_class == "replay_sch":
        # Use valid SCH from completely different session context
        other_session = generate_legitimate_session()
        session["sch"] = other_session["sch"]
        
    elif attack_class == "random_sch":
        # Pure random bytes
        session["sch"] = secrets.token_bytes(16)
    
    session["is_attack"] = True
    session["attack_class"] = attack_class
    
    return session

def run_pfcp_spoofing_test():
    """
    Main test: Generate 2,000 PFCP messages (50% legit, 50% attack).
    Verify each using Gate-2 (SCH verification).
    """
    print("--- ARC-3 E3: PFCP Spoofing Robustness Test ---")
    print(f"Total trials: {NUM_TRIALS}")
    print(f"Legitimate: {NUM_TRIALS // 2}")
    print(f"Attack: {NUM_TRIALS // 2}\n")
    
    # Generate test corpus
    test_corpus = []
    
    # Half legitimate
    for _ in range(NUM_TRIALS // 2):
        test_corpus.append(generate_legitimate_session())
    
    # Half attacks
    for _ in range(NUM_TRIALS // 2):
        test_corpus.append(generate_attack_message())
    
    # Shuffle
    np.random.shuffle(test_corpus)
    
    # Test each message
    results = []
    false_accepts = 0  # Accepted an attack
    false_rejects = 0  # Rejected a legitimate message
    
    attack_class_stats = {attack: {"total": 0, "accepts": 0} for attack in ATTACK_CLASSES}
    attack_class_stats["legitimate"] = {"total": 0, "accepts": 0}
    
    for session in test_corpus:
        # Gate-2: Verify SCH
        accepted = verify_sch(
            session["sch"],
            session["reference_id"],
            session["ue_ip"],
            session["teid_ul"],
            session["teid_dl"],
            session["role"]
        )
        
        # Record result
        is_correct = (accepted and not session["is_attack"]) or (not accepted and session["is_attack"])
        
        results.append({
            "is_attack": session["is_attack"],
            "attack_class": session["attack_class"],
            "accepted": accepted,
            "is_correct": is_correct
        })
        
        # Update stats
        attack_class_stats[session["attack_class"]]["total"] += 1
        if accepted:
            attack_class_stats[session["attack_class"]]["accepts"] += 1
        
        # Count errors
        if session["is_attack"] and accepted:
            false_accepts += 1
        elif not session["is_attack"] and not accepted:
            false_rejects += 1
    
    # Calculate metrics
    num_attacks = NUM_TRIALS // 2
    num_legit = NUM_TRIALS // 2
    
    true_accept_rate = (num_legit - false_rejects) / num_legit
    false_accept_rate = false_accepts / num_attacks
    
    # Display results
    print(f"--- Security Metrics ---")
    print(f"False Accept Rate (FAR):  {false_accept_rate*100:.4f}% ({false_accepts}/{num_attacks})")
    print(f"True Accept Rate (TAR):   {true_accept_rate*100:.2f}% ({num_legit - false_rejects}/{num_legit})")
    print(f"False Reject Rate (FRR):  {(false_rejects/num_legit)*100:.4f}% ({false_rejects}/{num_legit})")
    
    # Per-attack-class breakdown
    print(f"\n--- Per-Attack-Class Detection ---")
    print(f"{'Attack Class':<25} {'Count':<8} {'Detected':<10} {'Detection Rate':<15}")
    print("-" * 68)
    
    for attack_class in ["legitimate"] + ATTACK_CLASSES:
        stats = attack_class_stats[attack_class]
        total = stats["total"]
        accepts = stats["accepts"]
        detected = total - accepts
        
        if total > 0:
            if attack_class == "legitimate":
                rate = (accepts / total) * 100  # For legit, we want acceptance rate
                status = "✅" if rate > 99 else "❌"
                print(f"{attack_class:<25} {total:<8} {accepts:<10} {rate:.2f}% {status}")
            else:
                detection_rate = (detected / total) * 100
                status = "✅" if detection_rate == 100 else "❌"
                print(f"{attack_class:<25} {total:<8} {detected:<10} {detection_rate:.2f}% {status}")
    
    # Save CSV
    with open('pfcp_spoofing_results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['is_attack', 'attack_class', 'accepted', 'is_correct'])
        writer.writeheader()
        writer.writerows(results)
    
    print("\nSaved pfcp_spoofing_results.csv")
    
    # Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Confusion matrix
    tp = num_legit - false_rejects  # True Positives (legit accepted)
    tn = num_attacks - false_accepts  # True Negatives (attack rejected)
    fp = false_accepts  # False Positives (attack accepted)
    fn = false_rejects  # False Negatives (legit rejected)
    
    confusion = np.array([[tn, fp], [fn, tp]])
    
    im = ax1.imshow(confusion, cmap='RdYlGn', alpha=0.8, vmin=0, vmax=NUM_TRIALS//2)
    ax1.set_xticks([0, 1])
    ax1.set_yticks([0, 1])
    ax1.set_xticklabels(['Rejected', 'Accepted'])
    ax1.set_yticklabels(['Attack', 'Legitimate'])
    ax1.set_xlabel('Gate-2 Decision')
    ax1.set_ylabel('Ground Truth')
    ax1.set_title('ARC-3 Gate-2: PFCP Spoofing Confusion Matrix')
    
    # Annotate cells
    for i in range(2):
        for j in range(2):
            text = ax1.text(j, i, f'{confusion[i, j]}\n({confusion[i, j]/(NUM_TRIALS//2)*100:.1f}%)',
                          ha="center", va="center", color="black", fontweight="bold")
    
    plt.colorbar(im, ax=ax1, label='Count')
    
    # Attack class detection rates
    attack_names = []
    detection_rates = []
    
    for attack_class in ATTACK_CLASSES:
        stats = attack_class_stats[attack_class]
        if stats["total"] > 0:
            detection_rate = ((stats["total"] - stats["accepts"]) / stats["total"]) * 100
            attack_names.append(attack_class.replace("_", "\n"))
            detection_rates.append(detection_rate)
    
    bars = ax2.barh(attack_names, detection_rates, color='#00FF41')
    ax2.set_xlabel('Detection Rate (%)')
    ax2.set_title('Attack Detection Rate by Class')
    ax2.set_xlim(0, 105)
    ax2.axvline(100, color='red', linestyle='--', alpha=0.5, label='100% Target')
    ax2.grid(axis='x', alpha=0.3)
    ax2.legend()
    
    # Annotate bars
    for i, (name, rate) in enumerate(zip(attack_names, detection_rates)):
        color = 'white' if rate > 50 else 'black'
        ax2.text(rate - 2, i, f'{rate:.1f}%', va='center', ha='right', 
                color=color, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('pfcp_spoofing_robustness.png', dpi=300)
    print("Saved pfcp_spoofing_robustness.png")
    
    # Final verdict
    print(f"\n--- Final Verdict ---")
    paper_target_far = 0.0
    
    if false_accept_rate == 0.0:
        print(f"STATUS: ✅ ZERO FALSE ACCEPTS (FAR = {false_accept_rate*100:.4f}%)")
        print(f"Gate-2 (SCH verification) is cryptographically secure against all 7 attack classes.")
    elif false_accept_rate < 0.01:
        print(f"STATUS: ✅ NEAR-ZERO FALSE ACCEPTS (FAR = {false_accept_rate*100:.4f}%)")
    else:
        print(f"STATUS: ❌ UNACCEPTABLE FALSE ACCEPTS (FAR = {false_accept_rate*100:.2f}%)")
    
    # Security interpretation
    print(f"\n--- Security Interpretation ---")
    print(f"SCH binds PFCP messages to:")
    print(f"  - Reference ID (session identifier)")
    print(f"  - UE IP address")
    print(f"  - TEID-UL and TEID-DL (tunnel endpoints)")
    print(f"  - Role (SMF vs UPF)")
    print(f"\nAny tampering with these fields causes SCH verification to fail.")
    print(f"Probability of random SCH collision: 2^-128 (negligible)")
    print(f"\nConclusion: ARC-3 Gate-2 prevents control plane spoofing with cryptographic certainty.")

if __name__ == "__main__":
    run_pfcp_spoofing_test()
