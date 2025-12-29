import time
import numpy as np
import matplotlib.pyplot as plt
from cryptography.hazmat.primitives.asymmetric import ec, ed25519
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import csv

"""
D-Gate+ E2: Cryptographic Performance Benchmarking
Replicating the original research paper's crypto timing experiments.

Target Results (from paper):
- ECDSA P-256: 0.048ms p50 (2,083x under 100ms budget)
- Ed25519: 0.191ms p50 (510x under 100ms budget)

This proves that cryptographic permit verification will NOT timeout the NAS layer.
"""

NUM_TRIALS = 5000
NAS_BUDGET_MS = 100.0

def benchmark_ecdsa_p256():
    """
    Benchmarks ECDSA P-256 signature verification.
    """
    # Generate key pair
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()
    
    # Pre-generate 5000 signed messages
    messages = [f"PERMIT_{i:05d}".encode() for i in range(NUM_TRIALS)]
    signatures = []
    
    for msg in messages:
        sig = private_key.sign(msg, ec.ECDSA(hashes.SHA256()))
        signatures.append(sig)
    
    # Benchmark verification
    timings = []
    for msg, sig in zip(messages, signatures):
        start = time.perf_counter()
        try:
            public_key.verify(sig, msg, ec.ECDSA(hashes.SHA256()))
        except:
            pass  # Invalid signatures would fail, but we're timing valid ones
        end = time.perf_counter()
        timings.append((end - start) * 1000)  # Convert to ms
    
    return np.array(timings)

def benchmark_ed25519():
    """
    Benchmarks Ed25519 signature verification.
    """
    # Generate key pair
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    # Pre-generate 5000 signed messages
    messages = [f"PERMIT_{i:05d}".encode() for i in range(NUM_TRIALS)]
    signatures = []
    
    for msg in messages:
        sig = private_key.sign(msg)
        signatures.append(sig)
    
    # Benchmark verification
    timings = []
    for msg, sig in zip(messages, signatures):
        start = time.perf_counter()
        try:
            public_key.verify(sig, msg)
        except:
            pass
        end = time.perf_counter()
        timings.append((end - start) * 1000)  # ms
    
    return np.array(timings)

def generate_crypto_bench_report():
    print("--- D-Gate+ E2: Cryptographic Performance Benchmarking ---")
    print(f"Trials: {NUM_TRIALS} per scheme")
    print(f"NAS Budget: {NAS_BUDGET_MS} ms\n")
    
    # Benchmark ECDSA P-256
    print("Benchmarking ECDSA P-256...")
    ecdsa_timings = benchmark_ecdsa_p256()
    
    # Benchmark Ed25519
    print("Benchmarking Ed25519...")
    ed_timings = benchmark_ed25519()
    
    # Statistics
    results = {
        'ECDSA P-256': {
            'p50': np.percentile(ecdsa_timings, 50),
            'p95': np.percentile(ecdsa_timings, 95),
            'mean': np.mean(ecdsa_timings),
            'max': np.max(ecdsa_timings),
            'margin': NAS_BUDGET_MS / np.percentile(ecdsa_timings, 50)
        },
        'Ed25519': {
            'p50': np.percentile(ed_timings, 50),
            'p95': np.percentile(ed_timings, 95),
            'mean': np.mean(ed_timings),
            'max': np.max(ed_timings),
            'margin': NAS_BUDGET_MS / np.percentile(ed_timings, 50)
        }
    }
    
    # Display results
    print(f"\n{'Scheme':<15} {'n':<8} {'p50 (ms)':<12} {'p95 (ms)':<12} {'Budget Margin':<15}")
    print("-" * 70)
    for scheme, stats in results.items():
        print(f"{scheme:<15} {NUM_TRIALS:<8} {stats['p50']:<12.3f} {stats['p95']:<12.3f} {stats['margin']:<15.1f}x")
    
    # Save to CSV
    with open('crypto_bench.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Scheme', 'Trials', 'p50_ms', 'p95_ms', 'mean_ms', 'max_ms', 'budget_margin'])
        for scheme, stats in results.items():
            writer.writerow([scheme, NUM_TRIALS, stats['p50'], stats['p95'], stats['mean'], stats['max'], stats['margin']])
    
    print("\nSaved crypto_bench.csv")
    
    # Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Timing distributions
    ax1.hist(ecdsa_timings, bins=50, alpha=0.7, label='ECDSA P-256', color='blue')
    ax1.hist(ed_timings, bins=50, alpha=0.7, label='Ed25519', color='green')
    ax1.axvline(NAS_BUDGET_MS, color='red', linestyle='--', label='NAS Budget (100ms)')
    ax1.set_xlabel('Verification Time (ms)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Crypto Verification Performance Distribution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, min(5, max(ecdsa_timings.max(), ed_timings.max())))
    
    # Budget margin comparison
    schemes = ['ECDSA P-256', 'Ed25519']
    margins = [results[s]['margin'] for s in schemes]
    ax2.bar(schemes, margins, color=['blue', 'green'])
    ax2.set_ylabel('Budget Margin (×)')
    ax2.set_title('Crypto Performance vs. NAS Budget')
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_yscale('log')
    
    plt.tight_layout()
    plt.savefig('crypto_performance_chart.png')
    print("Saved crypto_performance_chart.png")
    
    # Verdict
    if results['ECDSA P-256']['p50'] < 0.1 and results['Ed25519']['p50'] < 0.5:
        print(f"\nSTATUS: ✅ CRYPTO BUDGET VERIFIED")
        print(f"ECDSA P-256: {results['ECDSA P-256']['margin']:.0f}x under budget")
        print(f"Ed25519: {results['Ed25519']['margin']:.0f}x under budget")
    else:
        print(f"\nSTATUS: ❌ CRYPTO TOO SLOW")

if __name__ == "__main__":
    generate_crypto_bench_report()
