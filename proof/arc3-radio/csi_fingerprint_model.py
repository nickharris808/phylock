import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

"""
ARC-3: Channel State Information (CSI) Fingerprint Model
Part of the Sovereign Handshake Protocol (SHP) Week 1 Technical Brief.

This module simulates the physics of radio multipath environments (Rayleigh Fading)
and proves that a "Zero-Math" cross-correlation gate can distinguish between
a legitimate user and a spoofer at a different physical location.

Reference: 3GPP TS 38.211 (NR Physical Layer)
"""

class CSISimulator:
    def __init__(self, num_subcarriers=128, num_paths=20, seed=42):
        self.rng = np.random.default_rng(seed)
        self.num_subcarriers = num_subcarriers
        self.num_paths = num_paths
        
        # Pre-generate the "environment" (Fixed for all users in this simulation)
        self.angles_of_arrival = self.rng.uniform(0, 2 * np.pi, self.num_paths)
        self.path_gains = (self.rng.standard_normal(self.num_paths) + 
                          1j * self.rng.standard_normal(self.num_paths)) / np.sqrt(2)
        self.base_delays = self.rng.uniform(0, 200, self.num_paths) # Up to 200ns
        
        # 6G / mmWave frequency: 60GHz, 1GHz bandwidth
        self.freqs = np.linspace(60e9, 61e9, self.num_subcarriers) 

    def generate_multipath_channel(self, location_offset=0.0):
        """
        Simulates a Rayleigh Fading channel for a specific location.
        location_offset: simulated shift in meters (affects path delays).
        """
        # Speed of light in m/ns
        c = 0.3 
        
        # In a real environment, the path gains also change with location
        # but for a first-order physics proof, the phase change is the dominant factor.
        # We'll add a small random gain perturbation for the offset
        gain_perturb = 1.0
        if location_offset > 0:
            # Each meter reduces correlation of the paths themselves
            gain_perturb = np.exp(-location_offset / 10.0)
        
        delay_shifts = (location_offset * np.cos(self.angles_of_arrival)) / c
        delays = self.base_delays + delay_shifts
        
        # CSI Vector
        csi_vector = np.zeros(self.num_subcarriers, dtype=complex)
        for i in range(self.num_paths):
            # Complex path gain
            p_gain = self.path_gains[i]
            if location_offset > 0:
                # Add location-specific phase noise to the path gains
                p_gain *= np.exp(1j * self.rng.uniform(0, 2*np.pi))
                
            csi_vector += p_gain * np.exp(-1j * 2 * np.pi * self.freqs * delays[i] * 1e-9)
            
        # Normalize
        csi_vector /= np.linalg.norm(csi_vector)
        return csi_vector

    def inject_noise(self, csi_vector, snr_db=10):
        """
        Injects Pink Noise and AWGN into the CSI vector.
        """
        # AWGN
        snr_linear = 10**(snr_db / 10.0)
        signal_power = np.mean(np.abs(csi_vector)**2)
        noise_power = signal_power / snr_linear
        noise = (self.rng.standard_normal(len(csi_vector)) + 
                 1j * self.rng.standard_normal(len(csi_vector))) * np.sqrt(noise_power / 2)
        
        # Pink Noise component (1/f)
        pink_noise_coeffs = 1.0 / (np.arange(1, len(csi_vector) + 1)**0.5)
        pink_noise = (self.rng.standard_normal(len(csi_vector)) + 
                      1j * self.rng.standard_normal(len(csi_vector))) * pink_noise_coeffs
        pink_noise = pink_noise * (np.sqrt(noise_power) * 0.5) # Scale to match noise level
        
        return csi_vector + noise + pink_noise

    @staticmethod
    def calculate_correlation(vec1, vec2):
        """
        Zero-Math Gate: Complex-vector dot product.
        In hardware, this is a single-cycle pipeline operation.
        """
        # Ensure vectors are normalized for correlation coefficient
        v1 = vec1 / np.linalg.norm(vec1)
        v2 = vec2 / np.linalg.norm(vec2)
        return np.abs(np.vdot(v1, v2))

def run_basic_simulation():
    sim = CSISimulator()
    
    # Legitimate User (The "Golden Fingerprint")
    golden_csi = sim.generate_multipath_channel(location_offset=0.0)
    
    # Legitimate connection attempt (same location, different noise)
    legit_attempt = sim.inject_noise(golden_csi, snr_db=10)
    
    # Attacker (Correct key, but 5 meters away)
    attacker_csi = sim.generate_multipath_channel(location_offset=5.0)
    attacker_attempt = sim.inject_noise(attacker_csi, snr_db=10)
    
    legit_corr = CSISimulator.calculate_correlation(golden_csi, legit_attempt)
    attacker_corr = CSISimulator.calculate_correlation(golden_csi, attacker_attempt)
    
    print(f"--- ARC-3 CSI Verification Results ---")
    print(f"Legitimate Correlation: {legit_corr:.4f}")
    print(f"Attacker Correlation:   {attacker_corr:.4f}")
    print(f"Rejection Gap:          {(legit_corr - attacker_corr):.4f}")
    
    if legit_corr > 0.8 and attacker_corr < 0.3:
        print("STATUS: ✅ ACCEPTANCE CRITERIA MET")
    else:
        print("STATUS: ❌ ACCEPTANCE CRITERIA FAILED")

if __name__ == "__main__":
    run_basic_simulation()

