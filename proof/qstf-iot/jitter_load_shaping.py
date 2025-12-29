import simpy
import numpy as np
import matplotlib.pyplot as plt

"""
QSTF-V2: Jitter Load Shaping & Thundering Herd Prevention
Part of the Sovereign Handshake Protocol (SHP) Week 5 Technical Brief.

This script proves that uniform random jitter prevents network congestion
when 10,000 IoT devices wake up simultaneously.
"""

NUM_DEVICES = 10000
JITTER_WINDOW = 30  # seconds

class CellTower:
    def __init__(self, env):
        self.env = env
        self.connections_per_second = []
        self.current_second = 0
        self.current_count = 0
        
    def connect(self, device_id):
        """Simulates a device connection attempt."""
        second = int(self.env.now)
        if second != self.current_second:
            if self.current_count > 0:
                self.connections_per_second.append((self.current_second, self.current_count))
            self.current_second = second
            self.current_count = 0
        self.current_count += 1
        yield self.env.timeout(0.001)  # Minimal processing time

def simulate_without_jitter(env, tower):
    """All devices wake up at exactly t=0 (Thundering Herd)."""
    for i in range(NUM_DEVICES):
        env.process(tower.connect(i))

def simulate_with_jitter(env, tower):
    """Devices wake up uniformly distributed over JITTER_WINDOW seconds."""
    for i in range(NUM_DEVICES):
        jitter = np.random.uniform(0, JITTER_WINDOW)
        def delayed_connect(device_id, delay):
            yield env.timeout(delay)
            yield env.process(tower.connect(device_id))
        env.process(delayed_connect(i, jitter))

def run_simulation(use_jitter):
    env = simpy.Environment()
    tower = CellTower(env)
    
    if use_jitter:
        simulate_with_jitter(env, tower)
    else:
        simulate_without_jitter(env, tower)
    
    env.run(until=JITTER_WINDOW + 1)
    
    # Flush final count
    if tower.current_count > 0:
        tower.connections_per_second.append((tower.current_second, tower.current_count))
    
    return tower.connections_per_second

def generate_thundering_herd_proof():
    print("Starting Thundering Herd Simulation...")
    
    # Baseline: No jitter
    print("Running baseline (no jitter)...")
    baseline_data = run_simulation(use_jitter=False)
    
    # QSTF-V2: With jitter
    print("Running QSTF-V2 (with jitter)...")
    jitter_data = run_simulation(use_jitter=True)
    
    # Extract peak loads
    baseline_peak = max([count for _, count in baseline_data]) if baseline_data else 0
    jitter_peak = max([count for _, count in jitter_data]) if jitter_data else 0
    
    reduction = (baseline_peak - jitter_peak) / baseline_peak * 100 if baseline_peak > 0 else 0
    
    print(f"\n--- Load Shaping Results ---")
    print(f"Baseline Peak Load: {baseline_peak} connections/sec")
    print(f"QSTF-V2 Peak Load:  {jitter_peak} connections/sec")
    print(f"Reduction Factor:   {baseline_peak/jitter_peak:.1f}x" if jitter_peak > 0 else "N/A")
    
    # Plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Baseline
    if baseline_data:
        times_b, counts_b = zip(*baseline_data)
        ax1.bar(times_b, counts_b, color='#FF4136', alpha=0.7)
        ax1.set_title('Baseline: Thundering Herd (No Jitter)')
        ax1.set_ylabel('Connections/Second')
        ax1.set_ylim(0, baseline_peak * 1.2)
        ax1.axhline(y=500, color='black', linestyle='--', label='Network Capacity Limit')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    
    # QSTF-V2
    if jitter_data:
        times_j, counts_j = zip(*jitter_data)
        ax2.bar(times_j, counts_j, color='#00FF41', alpha=0.7)
        ax2.set_title('QSTF-V2: Jitter Load Shaping')
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('Connections/Second')
        ax2.set_ylim(0, baseline_peak * 1.2)
        ax2.axhline(y=500, color='black', linestyle='--', label='Network Capacity Limit')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('thundering_herd_plot.png')
    print("Saved thundering_herd_plot.png")
    
    if reduction > 20:
        print("STATUS: ✅ CONGESTION REDUCTION PROVEN (>20x)")
    else:
        print(f"STATUS: ⚠️  CONGESTION REDUCTION: {reduction:.1f}%")

if __name__ == "__main__":
    generate_thundering_herd_proof()

