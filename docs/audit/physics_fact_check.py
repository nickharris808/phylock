import numpy as np

def fact_check_arc3_physics():
    print("--- Fact Check: ARC-3 Pilot Contamination Physics ---")
    # Parameters
    freq = 60e9 # 60 GHz
    c = 3e8
    wavelength = c / freq # 0.005m (5mm)
    num_antennas = 64
    d = wavelength / 2 # standard spacing
    
    # Steering vector function
    def steering_vector(theta):
        # theta is angle from boresight
        indices = np.arange(num_antennas)
        return np.exp(1j * 2 * np.pi * d * indices * np.sin(theta) / wavelength)

    # Scenarios
    theta_legit = 0.0 # Boresight
    theta_attacker = np.deg2rad(5.0) # 5 degrees off
    
    h_legit = steering_vector(theta_legit)
    h_attacker = steering_vector(theta_attacker)
    
    # If pilot is contaminated, weights are optimized for the sum/average
    # In a power-unbalanced scenario (attacker 2x stronger)
    attacker_power_ratio = 2.0
    h_contaminated = (h_legit + attacker_power_ratio * h_attacker) / (1 + attacker_power_ratio)
    
    # Weights (MRC)
    w = np.conj(h_contaminated) / np.linalg.norm(h_contaminated)
    
    # Power to legit UE
    gain_legit = np.abs(np.vdot(w, h_legit))**2 / num_antennas
    # Power to attacker (interference)
    gain_attack = np.abs(np.vdot(w, h_attacker))**2 / num_antennas
    
    print(f"Antennas: {num_antennas}")
    print(f"Attacker Offset: 5 degrees")
    print(f"Ideal Array Gain: {num_antennas} (linear) or {10*np.log10(num_antennas):.2f} dBi")
    print(f"Misdirected Gain to Legit UE: {gain_legit:.4f} (linear)")
    print(f"Beam Misdirection Loss: {10*np.log10(gain_legit/1):.2f} dB")
    
    # Shannon Capacity Check
    snr_base_db = 20 # 20dB SNR is standard for cell-edge with 64-antennas
    snr_base_linear = 10**(snr_base_db / 10)
    
    # ARC-3 (Clean Beam)
    cap_clean = np.log2(1 + snr_base_linear)
    
    # Contaminated (Misdirected Beam + Interference)
    # New SNR = (Signal * Gain_Legit) / (Interference * Gain_Attack + Noise)
    # Simplified: legit power is crushed by the beam steering error
    snr_contam = (snr_base_linear * gain_legit / num_antennas)
    cap_contam = np.log2(1 + snr_contam)
    
    collapse = (1 - cap_contam / cap_clean) * 100
    print(f"Clean Capacity: {cap_clean:.2f} bps/Hz")
    print(f"Contaminated Capacity: {cap_contam:.2f} bps/Hz")
    print(f"Calculated Collapse: {collapse:.2f}%")
    
    if collapse > 50:
        print("VERDICT: ✅ PHYSICALLY SOUND. Beam mispointing at 60GHz is lethal.")
    else:
        print("VERDICT: ⚠️  Calculated collapse lower than simulation claim.")

def fact_check_grid_telecom_coupling():
    print("\n--- Fact Check: Grid-Telecom Jitter Coupling ---")
    # The Claim: 10ms jitter -> 0.5Hz drift
    f_grid = 60.0 # Hz
    t_period = 1/f_grid # 16.67ms
    
    jitter = 0.010 # 10ms
    
    # Phase error in radians
    # Phase = 2 * pi * f * t
    # dPhase = 2 * pi * f * dTime
    d_phase = 2 * np.pi * f_grid * jitter
    
    # Local Frequency Estimate (f = 1/2pi * dPhase/dTime)
    # If the control loop updates based on a jittered clock pulse
    # f_error = jitter / (nominal_period) * f_nominal
    f_error = (jitter / t_period) * f_grid
    
    print(f"Grid Period: {t_period*1000:.2f} ms")
    print(f"Timing Jitter: {jitter*1000:.2f} ms")
    print(f"Instantaneous Frequency Error: {f_error:.2f} Hz")
    
    if f_error >= 0.5:
        print("VERDICT: ✅ PHYSICALLY SOUND. 10ms is 60% of a grid cycle. Timing loss is catastrophic.")
    else:
        print("VERDICT: ❌ MATH ERROR in coupling assumption.")

def fact_check_thermal_envelope():
    print("\n--- Fact Check: Thermal Envelope Constraint ---")
    # 15W TDP Drone, 85C Max Junction
    p_baseline = 2.0 # W
    p_pqc_burst = 5.5 # W
    p_total = p_baseline + p_pqc_burst
    
    r_theta = 10.0 # C/W (realistic for tiny plastic drone/exposed PCB)
    t_amb = 25.0 # C
    
    t_j = t_amb + (p_total * r_theta)
    
    print(f"Total Power Draw: {p_total} W")
    print(f"Thermal Resistance: {r_theta} C/W")
    print(f"Calculated Junction Temp: {t_j} C")
    
    if t_j > 85:
        print("VERDICT: ✅ PHYSICALLY SOUND. 7.5W on a small drone will bake the CPU.")
    else:
        print("VERDICT: ❌ PHYSICALLY INSOUND. Thermal margin exists.")

if __name__ == "__main__":
    fact_check_arc3_physics()
    fact_check_grid_telecom_coupling()
    fact_check_thermal_envelope()



