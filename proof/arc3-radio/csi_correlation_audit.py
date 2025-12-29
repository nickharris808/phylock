import numpy as np
import matplotlib.pyplot as plt
from csi_fingerprint_model import CSISimulator
import time

"""
ARC-3: CSI Correlation Audit & Hard-Proof Generator
This script performs 10,000 trials to prove the industrial-grade robustness 
of the Sovereign Handshake Physical Layer Gate.
"""

def generate_heatmap(sim, golden_csi):
    """
    Generates a spatial correlation heatmap showing how correlation drops
    as a function of physical distance (offset).
    """
    offsets = np.linspace(0, 10, 50) # 0 to 10 meters
    correlations = []
    
    for offset in offsets:
        trial_csi = sim.generate_multipath_channel(location_offset=offset)
        # Add noise to simulate real-world capture
        trial_csi_noisy = sim.inject_noise(trial_csi, snr_db=10)
        correlations.append(CSISimulator.calculate_correlation(golden_csi, trial_csi_noisy))
        
    plt.figure(figsize=(10, 6))
    plt.plot(offsets, correlations, linewidth=2, color='#00FF41', label='CSI Correlation')
    plt.axhline(y=0.5, color='r', linestyle='--', label='Rejection Threshold')
    plt.title('ARC-3: CSI Spatial Correlation Decay (The Physics Wall)')
    plt.xlabel('Physical Offset from Legitimate User (Meters)')
    plt.ylabel('Correlation Coefficient (Rho)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig('csi_fingerprint_proof.png')
    print("Saved csi_fingerprint_proof.png")

def generate_histogram(sim, golden_csi, num_trials=10000):
    """
    Runs 10,000 trials to generate the False Accept / False Reject histogram.
    """
    legit_scores = []
    attacker_scores = []
    
    for _ in range(num_trials):
        # Legitimate attempt (0m offset)
        legit_attempt = sim.inject_noise(golden_csi, snr_db=10)
        legit_scores.append(CSISimulator.calculate_correlation(golden_csi, legit_attempt))
        
        # Attacker attempt (5m offset)
        attacker_csi = sim.generate_multipath_channel(location_offset=5.0)
        attacker_attempt = sim.inject_noise(attacker_csi, snr_db=10)
        attacker_scores.append(CSISimulator.calculate_correlation(golden_csi, attacker_attempt))
        
    plt.figure(figsize=(10, 6))
    plt.hist(legit_scores, bins=50, alpha=0.6, label='Legitimate User (0m)', color='blue')
    plt.hist(attacker_scores, bins=50, alpha=0.6, label='Quantum Spoofer (5m)', color='red')
    plt.axvline(x=0.5, color='black', linestyle='--', label='Decision Gate')
    plt.title('ARC-3: False Accept vs. False Reject Distribution')
    plt.xlabel('Correlation Score')
    plt.ylabel('Frequency (10,000 Trials)')
    plt.legend()
    plt.savefig('csi_false_accept_histogram.png')
    print("Saved csi_false_accept_histogram.png")
    
    # Calculate False Accept Rate (FAR)
    far = np.sum(np.array(attacker_scores) > 0.5) / num_trials
    frr = np.sum(np.array(legit_scores) < 0.5) / num_trials
    print(f"Audit Results: FAR = {far:.6f}, FRR = {frr:.6f}")

def generate_pareto():
    """
    Generates the Latency vs. Security Pareto Chart.
    Comparing Standard PQC vs ARC-3 CSI Gate.
    """
    # Benchmarks from Week 1 Technical Brief
    categories = ['Standard PQC (Dilithium)', 'ARC-3 CSI Gate']
    latencies = [2.5 * 1e6, 85] # in nanoseconds
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    color = 'tab:blue'
    ax1.set_xlabel('Admission Method')
    ax1.set_ylabel('Latency (ns) - Log Scale', color=color)
    ax1.bar(categories, latencies, color=['#888888', '#00FF41'])
    ax1.set_yscale('log')
    ax1.tick_params(axis='y', labelcolor=color)
    
    # Add speedup text
    speedup = latencies[0] / latencies[1]
    plt.text(1, latencies[1] * 1.5, f'{speedup:,.0f}x Faster', 
             ha='center', fontweight='bold', color='black')
    
    plt.title('ARC-3: The "Verification Lag" Pareto Chart')
    plt.tight_layout()
    plt.savefig('latency_pareto.png')
    print("Saved latency_pareto.png")

def main():
    print("Starting ARC-3 Sovereign Audit...")
    sim = CSISimulator(seed=42)
    golden_csi = sim.generate_multipath_channel(location_offset=0.0)
    
    generate_heatmap(sim, golden_csi)
    generate_histogram(sim, golden_csi)
    generate_pareto()
    print("Audit Complete. All Sovereign Proofs generated.")

if __name__ == "__main__":
    main()

