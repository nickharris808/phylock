import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy import stats

"""
U-CRED E7: Risk-Neutral NPV (rNPV) Financial Model
Economic valuation of the U-CRED stateless admission control patent portfolio.

Revenue Model:
- Target Market: 5G Core vendors (Ericsson, Nokia, Samsung) + Edge cloud providers
- Licensing Structure: 
  1. Per-SMF instance royalty (core vendors)
  2. Per-site licensing (edge cloud deployments)
- Technology Value: 38% CPU savings + 17% CapEx reduction (RAM/state elimination)

Monte Carlo Scenarios:
1. Base Case: Moderate adoption (35% of SMF deployments by Year 10)
2. Aggressive Case: Fast adoption (65% by Year 8) + edge cloud expansion
3. Downside Case: Slow adoption (18% by Year 12) + vendor resistance

Target Results (from paper):
- Base Case Mean: $35.2M rNPV
- Aggressive P80: $87.6M rNPV
- Downside P30: $9.8M rNPV
"""

# Market parameters
TOTAL_SMF_INSTANCES = {
    "2025": 12_000,      # Global carrier deployments
    "2030": 38_000,      # 5G maturity
    "2035": 72_000,      # 6G rollout
}

EDGE_CLOUD_SITES = {
    "2025": 5_000,       # Early edge deployments
    "2030": 25_000,      # Edge explosion (CDN, MEC)
    "2035": 60_000,      # Ubiquitous edge
}

# Financial parameters
WACC = 0.09
PATENT_LIFETIME = 20
NUM_DRAWS = 6000

# Royalty pricing
ROYALTY_SMF_BASE = 18_000         # $/year per SMF instance (base case)
ROYALTY_SMF_AGGRESSIVE = 28_000   # $/year (premium for CapEx savings)
ROYALTY_SMF_DOWNSIDE = 10_000     # $/year (price pressure)

ROYALTY_EDGE_BASE = 8_000         # $/year per edge site (smaller scale)
ROYALTY_EDGE_AGGRESSIVE = 12_000
ROYALTY_EDGE_DOWNSIDE = 4_000

def logistic_adoption_curve(year, max_penetration, inflection_year, steepness):
    """Models technology adoption using logistic curve."""
    return max_penetration / (1 + np.exp(-steepness * (year - inflection_year)))

def project_smf_tam(year):
    """Projects SMF instance TAM."""
    if year <= 5:
        return np.interp(year, [0, 5], [12_000, 38_000])
    elif year <= 10:
        return np.interp(year, [5, 10], [38_000, 72_000])
    else:
        return 72_000 * (1 + 0.015 * (year - 10))  # Slow growth

def project_edge_tam(year):
    """Projects edge cloud site TAM."""
    if year <= 5:
        return np.interp(year, [0, 5], [5_000, 25_000])
    elif year <= 10:
        return np.interp(year, [5, 10], [25_000, 60_000])
    else:
        return 60_000 * (1 + 0.03 * (year - 10))  # Faster growth (edge expansion)

def simulate_revenue_scenario(scenario_name, num_draws=NUM_DRAWS):
    """Simulates rNPV for a given scenario using Monte Carlo."""
    npv_samples = []
    
    for _ in range(num_draws):
        # Scenario-specific parameters
        if scenario_name == "base":
            smf_max_pen = np.random.triangular(0.25, 0.35, 0.45)
            smf_inflection = np.random.triangular(7, 9, 11)
            smf_steepness = np.random.triangular(0.4, 0.5, 0.7)
            smf_royalty = np.random.triangular(15_000, 18_000, 22_000)
            
            edge_max_pen = np.random.triangular(0.10, 0.15, 0.25)
            edge_inflection = np.random.triangular(8, 10, 12)
            edge_steepness = np.random.triangular(0.3, 0.4, 0.6)
            edge_royalty = np.random.triangular(6_000, 8_000, 10_000)
            
        elif scenario_name == "aggressive":
            smf_max_pen = np.random.triangular(0.55, 0.65, 0.80)
            smf_inflection = np.random.triangular(5, 7, 9)
            smf_steepness = np.random.triangular(0.6, 0.8, 1.2)
            smf_royalty = np.random.triangular(22_000, 28_000, 35_000)
            
            edge_max_pen = np.random.triangular(0.25, 0.35, 0.50)
            edge_inflection = np.random.triangular(6, 8, 10)
            edge_steepness = np.random.triangular(0.5, 0.7, 1.0)
            edge_royalty = np.random.triangular(10_000, 12_000, 15_000)
            
        elif scenario_name == "downside":
            smf_max_pen = np.random.triangular(0.10, 0.18, 0.28)
            smf_inflection = np.random.triangular(9, 11, 14)
            smf_steepness = np.random.triangular(0.2, 0.3, 0.5)
            smf_royalty = np.random.triangular(7_000, 10_000, 13_000)
            
            edge_max_pen = np.random.triangular(0.03, 0.08, 0.15)
            edge_inflection = np.random.triangular(10, 12, 15)
            edge_steepness = np.random.triangular(0.2, 0.3, 0.4)
            edge_royalty = np.random.triangular(3_000, 4_000, 6_000)
        
        # Project cash flows for 20 years
        cash_flows = []
        
        for year in range(1, PATENT_LIFETIME + 1):
            # SMF market
            smf_tam = project_smf_tam(year)
            smf_adoption = logistic_adoption_curve(year, smf_max_pen, smf_inflection, smf_steepness)
            smf_licensed = smf_tam * smf_adoption
            smf_revenue = smf_licensed * smf_royalty
            
            # Edge cloud market (starts slower)
            edge_tam = project_edge_tam(year)
            edge_adoption = logistic_adoption_curve(year, edge_max_pen, edge_inflection, edge_steepness)
            edge_licensed = edge_tam * edge_adoption
            edge_revenue = edge_licensed * edge_royalty
            
            # Total revenue
            total_revenue = smf_revenue + edge_revenue
            
            # Costs
            if year <= 3:
                costs = np.random.triangular(600_000, 900_000, 1_400_000)  # Early (standards, R&D)
            elif year <= 8:
                costs = np.random.triangular(250_000, 450_000, 700_000)   # Mid
            else:
                costs = np.random.triangular(120_000, 250_000, 400_000)   # Late
            
            # Net cash flow
            net_cf = total_revenue - costs
            cash_flows.append(net_cf)
        
        # Calculate NPV
        discount_factors = np.array([(1 / (1 + WACC) ** year) for year in range(1, PATENT_LIFETIME + 1)])
        npv = np.sum(np.array(cash_flows) * discount_factors)
        
        npv_samples.append(npv)
    
    return np.array(npv_samples)

def run_rnpv_analysis():
    """Main analysis: Run Monte Carlo for all 3 scenarios."""
    print("--- U-CRED E7: Risk-Neutral NPV Economic Model ---")
    print(f"Monte Carlo draws per scenario: {NUM_DRAWS:,}")
    print(f"Patent lifetime: {PATENT_LIFETIME} years")
    print(f"WACC: {WACC*100:.1f}%\n")
    
    # Run scenarios
    scenarios = ["base", "aggressive", "downside"]
    results = {}
    
    for scenario in scenarios:
        print(f"Simulating {scenario.upper()} scenario...")
        npv_samples = simulate_revenue_scenario(scenario)
        results[scenario] = npv_samples
    
    # Statistics
    print(f"\n{'Scenario':<15} {'Mean':<12} {'Median':<12} {'P30':<12} {'P80':<12} {'P95':<12}")
    print("-" * 85)
    
    for scenario in scenarios:
        samples = results[scenario]
        mean = np.mean(samples)
        median = np.median(samples)
        p30 = np.percentile(samples, 30)
        p80 = np.percentile(samples, 80)
        p95 = np.percentile(samples, 95)
        
        print(f"{scenario.upper():<15} ${mean/1e6:>6.1f}M    ${median/1e6:>6.1f}M    ${p30/1e6:>6.1f}M    ${p80/1e6:>6.1f}M    ${p95/1e6:>6.1f}M")
    
    # Target validation
    base_mean = np.mean(results["base"])
    aggressive_p80 = np.percentile(results["aggressive"], 80)
    downside_p30 = np.percentile(results["downside"], 30)
    
    print(f"\n--- Target Validation ---")
    print(f"Base Case Mean:       ${base_mean/1e6:.1f}M (Target: $35.2M)")
    print(f"Aggressive P80:       ${aggressive_p80/1e6:.1f}M (Target: $87.6M)")
    print(f"Downside P30:         ${downside_p30/1e6:.1f}M (Target: $9.8M)")
    
    # Save CSV
    with open('ucred_rnpv_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['scenario', 'draw', 'npv_usd'])
        
        for scenario in scenarios:
            for i, npv in enumerate(results[scenario]):
                writer.writerow([scenario, i, npv])
    
    print("\nSaved ucred_rnpv_results.csv")
    
    # Visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Distribution comparison
    colors = {'base': '#00FF41', 'aggressive': '#0074D9', 'downside': '#FF4136'}
    
    for scenario in scenarios:
        samples = results[scenario] / 1e6
        ax1.hist(samples, bins=60, alpha=0.5, label=scenario.upper(), 
                color=colors[scenario], edgecolor='black')
    
    ax1.set_xlabel('rNPV (Million USD)', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.set_title('U-CRED Patent Portfolio: rNPV Distribution', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(axis='y', alpha=0.3)
    ax1.axvline(base_mean / 1e6, color=colors['base'], linestyle='--', linewidth=2, alpha=0.7)
    
    # 2. Box plot
    box_data = [results[s] / 1e6 for s in scenarios]
    bp = ax2.boxplot(box_data, labels=[s.upper() for s in scenarios], 
                     patch_artist=True, notch=True, widths=0.6)
    
    for patch, scenario in zip(bp['boxes'], scenarios):
        patch.set_facecolor(colors[scenario])
        patch.set_alpha(0.6)
    
    ax2.set_ylabel('rNPV (Million USD)', fontsize=12)
    ax2.set_title('rNPV Scenario Comparison', fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    # Annotate means
    for i, scenario in enumerate(scenarios, 1):
        mean = np.mean(results[scenario]) / 1e6
        ax2.text(i, mean, f'${mean:.1f}M', ha='left', va='center',
                fontweight='bold', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 3. Revenue sources (base case)
    # Simulate single draw to show SMF vs Edge breakdown
    years = np.arange(1, 21)
    smf_revenues = []
    edge_revenues = []
    
    for year in years:
        smf_tam = project_smf_tam(year)
        smf_adoption = logistic_adoption_curve(year, 0.35, 9, 0.5)
        smf_rev = smf_tam * smf_adoption * 18_000
        
        edge_tam = project_edge_tam(year)
        edge_adoption = logistic_adoption_curve(year, 0.15, 10, 0.4)
        edge_rev = edge_tam * edge_adoption * 8_000
        
        smf_revenues.append(smf_rev / 1e6)
        edge_revenues.append(edge_rev / 1e6)
    
    ax3.stackplot(years, smf_revenues, edge_revenues, 
                 labels=['SMF Core Vendors', 'Edge Cloud Sites'],
                 colors=['#0074D9', '#FFDC00'], alpha=0.7)
    ax3.set_xlabel('Year', fontsize=12)
    ax3.set_ylabel('Annual Revenue (Million USD)', fontsize=12)
    ax3.set_title('Revenue Breakdown: SMF vs. Edge Cloud (Base Case)', fontsize=13, fontweight='bold')
    ax3.legend(loc='upper left', fontsize=11)
    ax3.grid(True, alpha=0.3)
    
    # 4. Adoption curves
    years_plot = np.linspace(0, 20, 200)
    
    # Base case adoption
    smf_adoption_base = [logistic_adoption_curve(y, 0.35, 9, 0.5) for y in years_plot]
    edge_adoption_base = [logistic_adoption_curve(y, 0.15, 10, 0.4) for y in years_plot]
    
    ax4.plot(years_plot, np.array(smf_adoption_base) * 100, 
            label='SMF (Base: 35% max)', color='#0074D9', linewidth=2.5)
    ax4.plot(years_plot, np.array(edge_adoption_base) * 100, 
            label='Edge Cloud (Base: 15% max)', color='#FFDC00', linewidth=2.5, linestyle='--')
    
    ax4.set_xlabel('Year', fontsize=12)
    ax4.set_ylabel('Market Penetration (%)', fontsize=12)
    ax4.set_title('Technology Adoption Curves (Base Case)', fontsize=13, fontweight='bold')
    ax4.legend(fontsize=11)
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim([0, 20])
    ax4.set_ylim([0, 40])
    
    plt.tight_layout()
    plt.savefig('ucred_rnpv_distribution.png', dpi=300)
    print("Saved ucred_rnpv_distribution.png")
    
    # Risk assessment
    print(f"\n--- Risk Assessment ---")
    prob_positive_base = np.sum(results["base"] > 0) / len(results["base"])
    prob_above_25m_base = np.sum(results["base"] > 25e6) / len(results["base"])
    prob_above_60m_agg = np.sum(results["aggressive"] > 60e6) / len(results["aggressive"])
    
    print(f"Base Case: {prob_positive_base*100:.1f}% probability of positive NPV")
    print(f"Base Case: {prob_above_25m_base*100:.1f}% probability of exceeding $25M")
    print(f"Aggressive: {prob_above_60m_agg*100:.1f}% probability of exceeding $60M")
    
    # Key drivers
    print(f"\n--- Key Drivers ---")
    print(f"1. Dual Revenue Streams: SMF core + edge cloud deployments")
    print(f"2. CapEx Value Proposition: 17% RAM savings (38% CPU + state elimination)")
    print(f"3. Market Tailwinds: Edge cloud explosion (5k → 60k sites)")
    
    # Final verdict
    print(f"\n--- Economic Verdict ---")
    if base_mean > 30e6:
        print(f"STATUS: ✅ HIGHLY COMMERCIALLY VIABLE")
        print(f"Base case mean of ${base_mean/1e6:.1f}M significantly exceeds licensing minimum.")
    elif base_mean > 20e6:
        print(f"STATUS: ✅ COMMERCIALLY VIABLE")
    else:
        print(f"STATUS: ⚠️  MARGINAL VIABILITY")
    
    print(f"\nConclusion: U-CRED represents a ${base_mean/1e6:.1f}M mean opportunity")
    print(f"in stateless admission control for 5G core + edge cloud, with upside to")
    print(f"${aggressive_p80/1e6:.1f}M under aggressive adoption.")

if __name__ == "__main__":
    run_rnpv_analysis()
