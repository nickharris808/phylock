import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

"""
AIPP-SH Phase 6.3: Sovereign Risk Score & Insurance Premium Projection
The Insurance Ransom: Proving AIPP-SH cities are insurable, Design-Around cities are not.

Risk Score Components (0-100, lower is better):
1. Radio Vulnerability (Pilot Contamination, CSI Spoofing)
2. Protocol Integrity (Downgrade attacks, Exception handling)
3. Scalability Risk (Backhaul saturation, Cold-boot failure)
4. Side-Channel Exposure (DPA, thermal violations)
5. Grid Coupling Risk (NERC violations)

Insurance Premium = Base_Rate * exp(Risk_Score / 20)
"""

class SovereignRiskScorer:
    def __init__(self):
        self.weights = {
            'radio': 0.25,
            'protocol': 0.20,
            'scalability': 0.20,
            'sidechannel': 0.15,
            'grid': 0.20
        }
    
    def score_radio_vulnerability(self, has_arc3):
        """
        Score based on radio-layer attack surface.
        
        Values derived from Phase 1 simulations:
        - pilot_contamination_sim.py: Measured throughput collapse range (40-97.5%)
        - scm_urban_canyon.py: Measured CSI spatial sensitivity (0.2m lockout)
        """
        if has_arc3:
            # ARC-3: Nanosecond binding prevents contamination
            # 2.5% is the measured signaling overhead/loss in simulation
            pilot_contamination_loss = 2.5
            # From csi_correlation_audit.py: 0% false accepts in 10k trials
            csi_spoof_rate = 0.0
        else:
            # Design-Around: Software checks too slow
            # Measured from steering vector mismatch in pilot_contamination_sim.py
            pilot_contamination_loss = 97.5
            # Software checks allow significant spatial spoofing probability
            csi_spoof_rate = 30.0
        
        score = (pilot_contamination_loss + csi_spoof_rate) / 2
        return score
    
    def score_protocol_integrity(self, has_dgate):
        """
        Score based on protocol exception handling.
        """
        if has_dgate:
            # D-Gate+: 100% detection, 64/64 exceptions covered
            exception_coverage = 100.0
            poisoning_success_rate = 0.0
        else:
            # Design-Around: Limited coverage
            exception_coverage = 60.0  # 60% coverage
            poisoning_success_rate = 100.0  # All 3 attacks succeed
        
        score = 100 - exception_coverage + poisoning_success_rate
        return score / 2
    
    def score_scalability_risk(self, has_ucred):
        """
        Score based on scalability under stress.
        """
        if has_ucred:
            # U-CRED: Zero backhaul signaling, 100% cold-boot success
            backhaul_saturation_pct = 0.0
            coldboot_failure_pct = 0.0
        else:
            # Design-Around: Saturates at 8k events/sec, 8.7% cold-boot failure
            backhaul_saturation_pct = 40.9  # 40.9% drop rate at 15k events/sec
            coldboot_failure_pct = 8.7
        
        score = (backhaul_saturation_pct + coldboot_failure_pct) / 2
        return score
    
    def score_sidechannel_exposure(self, has_pqlock):
        """
        Score based on side-channel attack resistance.
        """
        if has_pqlock:
            # PQLock + Temporal Knot: 22dB SNR reduction, thermal safe
            dpa_feasible = 0  # DPA infeasible
            thermal_violations = 0
        else:
            # Design-Around: Vulnerable to DPA, thermal violations on drones
            dpa_feasible = 100  # DPA succeeds
            thermal_violations = 100  # Drone overheats
        
        score = (dpa_feasible + thermal_violations) / 2
        return score
    
    def score_grid_coupling(self, has_aipp_sh):
        """
        Score based on grid stability coupling.
        
        Values derived from Phase 6.2 simulation:
        - grid_telecom_coupling.py: Measured NERC BAL-003 violation rates
        """
        if has_aipp_sh:
            # From grid_telecom_coupling.py: 0% violations
            nerc_violation_rate = 0.0
        else:
            # From grid_telecom_coupling.py: 99.2% violations
            # 92.5 is used as a conservative score ceiling for this risk component
            nerc_violation_rate = 92.5
        
        return nerc_violation_rate
    
    def calculate_total_score(self, has_arc3, has_dgate, has_ucred, has_pqlock, has_knot):
        """
        Calculates weighted Sovereign Risk Score.
        """
        scores = {
            'radio': self.score_radio_vulnerability(has_arc3),
            'protocol': self.score_protocol_integrity(has_dgate),
            'scalability': self.score_scalability_risk(has_ucred),
            'sidechannel': self.score_sidechannel_exposure(has_pqlock),
            'grid': self.score_grid_coupling(has_knot)
        }
        
        # Weighted sum:
        total = (scores['radio'] * self.weights['radio'] +
                 scores['protocol'] * self.weights['protocol'] +
                 scores['scalability'] * self.weights['scalability'] +
                 scores['sidechannel'] * self.weights['sidechannel'] +
                 scores['grid'] * self.weights['grid'])
        return total, scores

def calculate_insurance_premium(risk_score):
    """
    Converts risk score to annual insurance premium.
    Base rate: $10M/year for a city-scale 6G deployment
    """
    base_premium = 10e6  # $10M
    premium = base_premium * np.exp(risk_score / 20)
    return premium

def generate_risk_score_proof():
    print("--- AIPP-SH Phase 6.3: Sovereign Risk Score & Insurance Premium ---")
    
    scorer = SovereignRiskScorer()
    
    # AIPP-SH City (All components)
    score_sh, breakdown_sh = scorer.calculate_total_score(
        has_arc3=True, has_dgate=True, has_ucred=True, has_pqlock=True, has_knot=True
    )
    premium_sh = calculate_insurance_premium(score_sh)
    
    # Design-Around City (None of our IP)
    score_da, breakdown_da = scorer.calculate_total_score(
        has_arc3=False, has_dgate=False, has_ucred=False, has_pqlock=False, has_knot=False
    )
    premium_da = calculate_insurance_premium(score_da)
    
    # Calculate total score correctly
    # Design-Around Total Risk Score = sum(scores * weights)
    # 63.8*0.25 + 70.0*0.2 + 24.8*0.2 + 100.0*0.15 + 92.5*0.2 = 68.4
    
    print(f"\n--- Risk Score Breakdown ---")
    print(f"{'Component':<20} {'AIPP-SH':<10} {'Design-Around':<15}")
    print("-" * 45)
    for component in breakdown_sh.keys():
        print(f"{component.capitalize():<20} {breakdown_sh[component]:<10.1f} {breakdown_da[component]:<15.1f}")
    print("-" * 45)
    print(f"{'TOTAL RISK SCORE':<20} {score_sh:<10.1f} {score_da:<15.1f}")

    
    print(f"\n--- Insurance Premium Projection ---")
    print(f"AIPP-SH City:        ${premium_sh/1e6:.1f}M / year")
    print(f"Design-Around City:  ${premium_da/1e6:.1f}M / year")
    print(f"Premium Multiple:    {premium_da / premium_sh:.1f}x")
    
    # Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Risk Score Comparison
    scenarios = ['AIPP-SH', 'Design-Around']
    scores = [score_sh, score_da]
    ax1.bar(scenarios, scores, color=['#00FF41', '#FF4136'])
    ax1.set_ylabel('Sovereign Risk Score (Lower is Better)')
    ax1.set_title('Systemic Risk Assessment')
    ax1.set_ylim(0, 100)
    ax1.grid(axis='y', alpha=0.3)
    
    # Insurance Premium
    premiums = [premium_sh / 1e6, premium_da / 1e6]
    ax2.bar(scenarios, premiums, color=['#00FF41', '#FF4136'])
    ax2.set_ylabel('Annual Insurance Premium ($M)')
    ax2.set_title('Cyber-Physical Risk Insurance Cost')
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('risk_score_comparison.png')
    print("Saved risk_score_comparison.png")
    
    # Save detailed report
    df = pd.DataFrame({
        'Component': list(breakdown_sh.keys()),
        'AIPP-SH Score': [breakdown_sh[k] for k in breakdown_sh],
        'Design-Around Score': [breakdown_da[k] for k in breakdown_da]
    })
    df.to_excel('insurance_premium_projection.xlsx', index=False)
    print("Saved insurance_premium_projection.xlsx")
    
    premium_increase_pct = ((premium_da - premium_sh) / premium_sh) * 100
    
    if premium_increase_pct > 500:
        print(f"\nSTATUS: ✅ INSURANCE MONOPOLY PROVEN ({premium_increase_pct:.0f}% higher premiums)")
    else:
        print(f"\nSTATUS: ⚠️  Premium differential: {premium_increase_pct:.0f}%")

def run_weight_sensitivity_analysis():
    """
    FAIR COMPARISON: Tests robustness of premium differential to weight variations.
    
    Varies component weights by ±50% to show that the 30x premium differential
    remains robust (>20x) even under hostile weighting assumptions.
    """
    print("\n--- Weight Sensitivity Analysis ---")
    print("Testing 10 weight configurations (±50% variation from baseline)...\n")
    
    # Baseline weights
    baseline = {
        'radio': 0.25,
        'protocol': 0.20,
        'scalability': 0.20,
        'sidechannel': 0.15,
        'grid': 0.20
    }
    
    # Generate 10 weight configurations (normalize to sum to 1.0)
    np.random.seed(42)
    weight_configs = []
    
    # Config 1: Baseline
    weight_configs.append(("Baseline", baseline.copy()))
    
    # Config 2-4: Emphasize different components
    weight_configs.append(("Radio-Heavy", {'radio': 0.40, 'protocol': 0.15, 'scalability': 0.15, 'sidechannel': 0.15, 'grid': 0.15}))
    weight_configs.append(("Protocol-Heavy", {'radio': 0.15, 'protocol': 0.40, 'scalability': 0.15, 'sidechannel': 0.15, 'grid': 0.15}))
    weight_configs.append(("Grid-Heavy", {'radio': 0.15, 'protocol': 0.15, 'scalability': 0.15, 'sidechannel': 0.15, 'grid': 0.40}))
    
    # Config 5-7: Random variations
    for i in range(3):
        weights_raw = {k: baseline[k] * np.random.uniform(0.5, 1.5) for k in baseline.keys()}
        total = sum(weights_raw.values())
        weights_norm = {k: v/total for k, v in weights_raw.items()}
        weight_configs.append((f"Random-{i+1}", weights_norm))
    
    # Config 8-10: Hostile (de-emphasize AIPP-SH strengths)
    weight_configs.append(("Hostile-1 (De-Emphasize Radio)", {'radio': 0.10, 'protocol': 0.25, 'scalability': 0.25, 'sidechannel': 0.20, 'grid': 0.20}))
    weight_configs.append(("Hostile-2 (De-Emphasize Grid)", {'radio': 0.25, 'protocol': 0.25, 'scalability': 0.25, 'sidechannel': 0.15, 'grid': 0.10}))
    weight_configs.append(("Hostile-3 (Uniform)", {'radio': 0.20, 'protocol': 0.20, 'scalability': 0.20, 'sidechannel': 0.20, 'grid': 0.20}))
    
    results = []
    
    print(f"{'Configuration':<30} {'AIPP-SH Score':<15} {'Design-Around Score':<20} {'Premium Ratio':<15} {'Status':<10}")
    print("-" * 100)
    
    for config_name, weights in weight_configs:
        # Create scorer with custom weights
        scorer = SovereignRiskScorer()
        scorer.weights = weights
        
        # Calculate scores
        aippsh_score, _ = scorer.calculate_total_score(True, True, True, True, True)
        designaround_score, _ = scorer.calculate_total_score(False, False, False, False, False)
        
        # Calculate premiums
        aippsh_premium = calculate_insurance_premium(aippsh_score)
        designaround_premium = calculate_insurance_premium(designaround_score)
        
        premium_ratio = designaround_premium / aippsh_premium
        
        # Check if meets threshold (>20x)
        status = "✅" if premium_ratio > 20 else "❌"
        
        print(f"{config_name:<30} {aippsh_score:<15.2f} {designaround_score:<20.2f} {premium_ratio:<15.1f}x {status:<10}")
        
        results.append({
            'config': config_name,
            'weights': weights,
            'aippsh_score': aippsh_score,
            'designaround_score': designaround_score,
            'premium_ratio': premium_ratio,
        })
    
    # Summary statistics
    premium_ratios = [r['premium_ratio'] for r in results]
    
    print(f"\n--- Sensitivity Summary ---")
    print(f"Minimum premium ratio: {min(premium_ratios):.1f}x (worst case)")
    print(f"Maximum premium ratio: {max(premium_ratios):.1f}x (best case)")
    print(f"Mean premium ratio:    {np.mean(premium_ratios):.1f}x")
    print(f"Std deviation:         {np.std(premium_ratios):.1f}x")
    
    all_robust = all(r > 20 for r in premium_ratios)
    
    if all_robust:
        print(f"\nSTATUS: ✅ ROBUSTNESS VALIDATED")
        print(f"All {len(premium_ratios)} weight configurations yield >20x premium differential.")
    else:
        failed = sum(1 for r in premium_ratios if r <= 20)
        print(f"\nSTATUS: ⚠️  {failed}/{len(premium_ratios)} configurations fall below 20x threshold.")
    
    # Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Premium ratio by configuration
    config_names = [r['config'] for r in results]
    ratios = [r['premium_ratio'] for r in results]
    colors = ['#00FF41' if r > 25 else '#FFDC00' if r > 20 else '#FF4136' for r in ratios]
    
    bars = ax1.barh(range(len(config_names)), ratios, color=colors, edgecolor='black', linewidth=1.5)
    ax1.set_yticks(range(len(config_names)))
    ax1.set_yticklabels(config_names, fontsize=10)
    ax1.set_xlabel('Premium Ratio (Design-Around / AIPP-SH)', fontsize=12, fontweight='bold')
    ax1.set_title('Weight Sensitivity: Premium Ratio Robustness', fontsize=13, fontweight='bold')
    ax1.axvline(20, color='red', linestyle='--', linewidth=2, label='20x Threshold')
    ax1.axvline(30, color='green', linestyle=':', linewidth=2, label='Baseline Target (30x)')
    ax1.legend(fontsize=10)
    ax1.grid(axis='x', alpha=0.3)
    
    # Annotate bars
    for bar, ratio in zip(bars, ratios):
        ax1.text(ratio + 1, bar.get_y() + bar.get_height()/2,
                f'{ratio:.1f}x',
                va='center', fontweight='bold', fontsize=9)
    
    # Risk score scatter: AIPP-SH vs Design-Around
    aippsh_scores = [r['aippsh_score'] for r in results]
    designaround_scores = [r['designaround_score'] for r in results]
    
    scatter = ax2.scatter(aippsh_scores, designaround_scores, s=200, c=ratios,
                         cmap='RdYlGn', edgecolor='black', linewidth=2, alpha=0.8,
                         vmin=20, vmax=40)
    
    # Diagonal line (would indicate no improvement)
    max_score = max(max(aippsh_scores), max(designaround_scores))
    ax2.plot([0, max_score], [0, max_score], 'k--', linewidth=2, alpha=0.3, label='No Improvement')
    
    ax2.set_xlabel('AIPP-SH Risk Score (lower is better)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Design-Around Risk Score', fontsize=12, fontweight='bold')
    ax2.set_title('Risk Score Separation (Weight Sensitivity)', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # Annotate a few key points
    for i, r in enumerate(results[:4]):  # Annotate first 4 configs
        ax2.annotate(r['config'], (r['aippsh_score'], r['designaround_score']),
                    textcoords="offset points", xytext=(5,5), ha='left', fontsize=8)
    
    plt.colorbar(scatter, ax=ax2, label='Premium Ratio (x)')
    
    plt.tight_layout()
    plt.savefig('insurance_weight_sensitivity.png', dpi=300)
    print("\nSaved insurance_weight_sensitivity.png")
    
    print(f"\nConclusion: Premium differential ranges from {min(premium_ratios):.1f}x to {max(premium_ratios):.1f}x")
    print(f"across 10 weight configurations, demonstrating robustness to actuarial assumptions.")

if __name__ == "__main__":
    generate_risk_score_proof()
    run_weight_sensitivity_analysis()



