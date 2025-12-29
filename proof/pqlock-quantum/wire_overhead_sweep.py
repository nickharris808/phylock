import numpy as np
import matplotlib.pyplot as plt
import csv

"""
PQLock E5: Wire Overhead & NTN Feasibility
Sweeps link rates from 8 kbps to 1024 kbps to validate satellite compatibility.

Target Results (from paper):
- Classical AKA: 48 bytes
- PQLock: 2,344 bytes (1184B pubkey + 1088B ciphertext + 72B overhead)
- At 128 kbps NTN: 146.5ms wire time (< 200ms target)
- % of 3-second NTN budget: 4.9% (< 5%)

This proves PQLock works on slow satellite links.
"""

# Payload sizes
CLASSICAL_AKA_BYTES = 48
PQLOCK_BYTES = 2344  # 1184 + 1088 + 72

# Link rates to test (kbps)
LINK_RATES = [8, 16, 32, 64, 128, 256, 512, 1024]

# NTN critical parameters
NTN_RATE_KBPS = 128
NTN_BUDGET_MS = 200  # Max acceptable wire time
NTN_TOTAL_AUTH_S = 3.0  # 3-second total auth budget

def calculate_wire_time(payload_bytes, rate_kbps):
    """Calculates wire transmission time in milliseconds."""
    bits = payload_bytes * 8
    rate_bps = rate_kbps * 1000
    time_s = bits / rate_bps
    return time_s * 1000  # Convert to ms

def run_wire_overhead_sweep():
    print("--- PQLock E5: Wire Overhead & NTN Feasibility ---")
    print(f"Classical AKA: {CLASSICAL_AKA_BYTES} bytes")
    print(f"PQLock: {PQLOCK_BYTES} bytes")
    print(f"Overhead: +{PQLOCK_BYTES - CLASSICAL_AKA_BYTES} bytes (+{((PQLOCK_BYTES/CLASSICAL_AKA_BYTES)-1)*100:.0f}%)\n")
    
    results = []
    
    for rate_kbps in LINK_RATES:
        classical_ms = calculate_wire_time(CLASSICAL_AKA_BYTES, rate_kbps)
        pqlock_ms = calculate_wire_time(PQLOCK_BYTES, rate_kbps)
        delta_ms = pqlock_ms - classical_ms
        pct_increase = ((pqlock_ms / classical_ms) - 1) * 100
        pct_of_ntn_budget = (pqlock_ms / (NTN_TOTAL_AUTH_S * 1000)) * 100
        
        results.append({
            'rate_kbps': rate_kbps,
            'classical_ms': classical_ms,
            'pqlock_ms': pqlock_ms,
            'delta_ms': delta_ms,
            'pct_increase': pct_increase,
            'pct_ntn_budget': pct_of_ntn_budget
        })
    
    # Display table
    print(f"{'Rate':<10} {'Classical':<12} {'PQLock':<12} {'Delta':<12} {'% Increase':<12} {'% NTN Budget':<15}")
    print("-" * 80)
    for r in results:
        print(f"{r['rate_kbps']:<10} kbps {r['classical_ms']:<12.1f}ms {r['pqlock_ms']:<12.1f}ms {r['delta_ms']:<12.1f}ms {r['pct_increase']:<12.0f}% {r['pct_ntn_budget']:<15.1f}%")
    
    # Save CSV
    with open('attach_overhead.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['rate_kbps', 'classical_ms', 'pqlock_ms', 'delta_ms', 'pct_increase', 'pct_ntn_budget'])
        writer.writeheader()
        writer.writerows(results)
    
    print("\nSaved attach_overhead.csv")
    
    # Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Wire time vs. link rate
    rates = [r['rate_kbps'] for r in results]
    classical_times = [r['classical_ms'] for r in results]
    pqlock_times = [r['pqlock_ms'] for r in results]
    
    ax1.plot(rates, classical_times, marker='o', label='Classical AKA', linewidth=2)
    ax1.plot(rates, pqlock_times, marker='s', label='PQLock', linewidth=2, color='#00FF41')
    ax1.axhline(y=NTN_BUDGET_MS, color='red', linestyle='--', label='NTN Budget (200ms)')
    ax1.axvline(x=NTN_RATE_KBPS, color='gray', linestyle=':', alpha=0.5, label='NTN Rate (128kbps)')
    ax1.set_xlabel('Link Rate (kbps)')
    ax1.set_ylabel('Wire Time (ms)')
    ax1.set_title('PQLock Wire Overhead vs. Link Rate')
    ax1.set_xscale('log', base=2)
    ax1.set_yscale('log')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # % of NTN budget
    ntn_pcts = [r['pct_ntn_budget'] for r in results]
    ax2.bar(range(len(rates)), ntn_pcts, color=['red' if r['rate_kbps'] == NTN_RATE_KBPS else 'gray' for r in results])
    ax2.axhline(y=5.0, color='black', linestyle='--', label='5% Target')
    ax2.set_xlabel('Link Rate')
    ax2.set_ylabel('% of 3-second NTN Budget')
    ax2.set_title('PQLock NTN Budget Impact')
    ax2.set_xticks(range(len(rates)))
    ax2.set_xticklabels([f"{r}k" for r in rates], rotation=45)
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('wire_time_vs_rate.png')
    print("Saved wire_time_vs_rate.png")
    
    # Find NTN result
    ntn_result = next(r for r in results if r['rate_kbps'] == NTN_RATE_KBPS)
    
    print(f"\n--- NTN Feasibility (128 kbps) ---")
    print(f"Wire Time: {ntn_result['pqlock_ms']:.1f}ms")
    print(f"Budget: < {NTN_BUDGET_MS}ms")
    print(f"% of Total Auth: {ntn_result['pct_ntn_budget']:.1f}%")
    
    if ntn_result['pqlock_ms'] < NTN_BUDGET_MS and ntn_result['pct_ntn_budget'] < 5.0:
        print(f"\nSTATUS: ✅ NTN FEASIBILITY PROVEN")
        print(f"PQLock wire time ({ntn_result['pqlock_ms']:.1f}ms) fits within 3-second satellite budget")
    else:
        print(f"\nSTATUS: ❌ NTN BUDGET EXCEEDED")

if __name__ == "__main__":
    run_wire_overhead_sweep()
