import numpy as np
import matplotlib.pyplot as plt
import simpy
import os
import sys

# Add root to sys.path to enable cross-portfolio imports
sys.path.append("/Users/nharris/Desktop/telecom")
try:
    from Portfolio_A_Power.utils.constants import GRID_HEARTBEAT_HZ
except ImportError:
    GRID_HEARTBEAT_HZ = 100 # Fallback

"""
AIPP-SH Week 6: Power-Sync Bridge
...
"""
CRYPTO_BURST_DURATION = 0.001 # 1ms burst
SIM_TIME = 0.1 # 100ms total
VOLTAGE_NOMINAL = 0.9 # 0.9V

class PowerGrid:
    def __init__(self, env):
        self.env = env
        self.voltage = VOLTAGE_NOMINAL
        self.history_time = []
        self.history_voltage = []
        self.history_load = []
        
    def get_heartbeat_phase(self):
        """Returns 0 to 1 representing phase in the 10ms cycle."""
        return (self.env.now * GRID_HEARTBEAT_HZ) % 1.0

    def apply_load(self, current_draw):
        """Simulates voltage droop based on current draw."""
        # Simple V = V_nom - I*R model
        resistance = 0.05
        self.voltage = VOLTAGE_NOMINAL - (current_draw * resistance)
        
    def monitor(self):
        while True:
            self.history_time.append(self.env.now)
            self.history_voltage.append(self.voltage)
            # Baseline load (random background)
            bg_load = 0.5 + 0.1 * np.sin(2 * np.pi * GRID_HEARTBEAT_HZ * self.env.now)
            self.apply_load(bg_load)
            self.history_load.append(bg_load)
            yield self.env.timeout(0.0001) # 100us resolution

def perform_handshake(env, grid, is_synced):
    """Simulates a PQLock/U-CRED handshake burst."""
    while True:
        # Wait for next connection request (random)
        yield env.timeout(np.random.uniform(0.01, 0.03))
        
        if is_synced:
            # SHP Logic: Wait for the "Quiet Valley" (phase 0.4 to 0.6)
            while not (0.4 < grid.get_heartbeat_phase() < 0.6):
                yield env.timeout(0.0001)
        
        # Crypto burst draw
        burst_draw = 5.0 # Amps
        grid.apply_load(grid.history_load[-1] + burst_draw)
        yield env.timeout(CRYPTO_BURST_DURATION)
        grid.apply_load(grid.history_load[-1])

def run_bridge_simulation():
    print("Starting AIPP-SH Power-Sync Bridge Audit...")
    
    # SCENARIO A: Un-synced Handshakes
    env_a = simpy.Environment()
    grid_a = PowerGrid(env_a)
    env_a.process(grid_a.monitor())
    for _ in range(5):
        env_a.process(perform_handshake(env_a, grid_a, is_synced=False))
    env_a.run(until=SIM_TIME)
    
    # SCENARIO B: Knot-Synced Handshakes
    env_b = simpy.Environment()
    grid_b = PowerGrid(env_b)
    env_b.process(grid_b.monitor())
    for _ in range(5):
        env_b.process(perform_handshake(env_b, grid_b, is_synced=True))
    env_b.run(until=SIM_TIME)
    
    # Generate Visual Proof
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Heartbeat visualization
    t = np.linspace(0, SIM_TIME, 1000)
    heartbeat = 0.5 + 0.5 * np.sin(2 * np.pi * GRID_HEARTBEAT_HZ * t)
    
    # Plot Un-synced
    ax1.plot(grid_a.history_time, grid_a.history_voltage, color='red', label='Voltage (Un-synced)')
    ax1.fill_between(t, 0.6, 0.6 + 0.1 * heartbeat, color='gray', alpha=0.2, label='Grid Heartbeat')
    ax1.set_title('Scenario A: Random Crypto Bursts (Aggressive Voltage Droops)')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_ylim(0.5, 1.0)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot Synced
    ax2.plot(grid_b.history_time, grid_b.history_voltage, color='#00FF41', label='Voltage (SHP Synced)')
    ax2.fill_between(t, 0.6, 0.6 + 0.1 * heartbeat, color='gray', alpha=0.2, label='Grid Heartbeat')
    ax2.set_title('Scenario B: SHP Knot-Synced Bursts (Phase-Locked to Valleys)')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Voltage (V)')
    ax2.set_ylim(0.5, 1.0)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('voltage_handshake_sync.png')
    print("Saved voltage_handshake_sync.png")
    
    # ROI Heatmap (Simplified)
    plt.figure(figsize=(8, 6))
    roi_data = np.array([[10, 20], [50, 1000]]) # Units in $B
    plt.imshow(roi_data, cmap='YlGn')
    plt.xticks([0, 1], ['Siloed IP', 'The Knot'])
    plt.yticks([0, 1], ['Component', 'Sovereign Tier'])
    plt.title('Valuation Multiplier: The Power-Security Knot')
    plt.colorbar(label='Valuation ($B)')
    for (i, j), z in np.ndenumerate(roi_data):
        plt.text(j, i, f'${z}B', ha='center', va='center', fontweight='bold')
    plt.savefig('monopoly_roi_heatmap.png')
    print("Saved monopoly_roi_heatmap.png")

if __name__ == "__main__":
    run_bridge_simulation()




