import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy import stats

"""
PQLock E7: Risk-Neutral NPV (rNPV) Financial Model
Economic valuation of the PQLock hybrid key exchange patent portfolio.

Revenue Model:
- Target Market: TLS/QUIC protocol stacks (OpenSSL, BoringSSL, etc.)
- Licensing Structure:
  1. Per-server/device royalty (enterprise deployments)
  2. Open-source exception (attribution-based)
- Technology Value: Quantum-resistant + 10-15dB DPA resistance

Monte Carlo Scenarios:
1. Base Case: Moderate adoption (22% of enterprise TLS by Year 12)
2. Aggressive Case: Fast adoption (45% by Year 10) + NIST mandate
3. Downside Case: Slow adoption (10% by Year 15) + competing standards

Target Results (from paper):
- Base Case Mean: $34M rNPV
- Aggressive P85: $89.2M rNPV
- Downside P20: $6.4M rNPV
"""

# Market parameters
ENTERPRISE_TLS_SERVERS = {
    "2025": 25_000_000,    # Enterprise TLS endpoints (servers, load balancers, CDN nodes)
    "2030": 60_000_000,    # Growth (cloud expansion)
    "2035": 120_000_000,   # Ubiquity (edge, IoT gateways)
}

IOT_GATEWAYS = {
    "2025": 8_000_000,     # Industrial IoT gateways (smaller market, higher value)
    "2030": 30_000_000,
    "2035": 80_000_000,
}

# Financial parameters
WACC = 0.09
PATENT_LIFETIME = 20
NUM_DRAWS = 6000

# Royalty pricing
ROYALTY_ENTERPRISE_BASE = 12.00       # $/year per TLS endpoint (base)
ROYALTY_ENTERPRISE_AGGRESSIVE = 22.00 # $/year (premium for side-channel resistance)
ROYALTY_ENTERPRISE_DOWNSIDE = 6.00    # $/year (commoditization)

ROYALTY_IOT_BASE = 18.00              # $/year per IoT gateway (higher value)
ROYALTY_IOT_AGGRESSIVE = 30.00
ROYALTY_IOT_DOWNSIDE = 9.00

def logistic_adoption_curve(year, max_penetration, inflection_year, steepness):
    """Models technology adoption using logistic curve."""
    return max_penetration / (1 + np.exp(-steepness * (year - inflection_year)))

def project_enterprise_tam(year):
    """Projects enterprise TLS endpoint TAM."""
    if year <= 5:
        return np.interp(year, [0, 5], [25_000_000, 60_000_000])
    elif year <= 10:
        return np.interp(year, [5, 10], [60_000_000, 120_000_000])
    else:
        return 120_000_000 * (1 + 0.02 * (year - 10))

def project_iot_tam(year):
    """Projects IoT gateway TAM."""
    if year <= 5:
        return np.interp(year, [0, 5], [8_000_000, 30_000_000])
    elif year <= 10:
        return np.interp(year, [5, 10], [30_000_000, 80_000_000])
    else:
        return 80_000_000 * (1 + 0.04 * (year - 10))

def simulate_revenue_scenario(scenario_name, num_draws=NUM_DRAWS):
    """Simulates rNPV for a given scenario using Monte Carlo."""
    npv_samples = []
    
    for _ in range(num_draws):
        # Scenario-specific parameters
        if scenario_name == "base":
            enterprise_max_pen = np.random.triangular(0.15, 0.22, 0.30)
            enterprise_inflection = np.random.triangular(9, 11, 13)
            enterprise_steepness = np.random.triangular(0.3, 0.5, 0.7)
            enterprise_royalty = np.random.triangular(10.00, 12.00, 15.00)
            
            iot_max_pen = np.random.triangular(0.08, 0.12, 0.18)
            iot_inflection = np.random.triangular(10, 12, 14)
            iot_steepness = np.random.triangular(0.3, 0.4, 0.6)
            iot_royalty = np.random.triangular(15.00, 18.00, 22.00)
            
        elif scenario_name == "aggressive":
            enterprise_max_pen = np.random.triangular(0.35, 0.45, 0.60)
            enterprise_inflection = np.random.triangular(7, 9, 11)
            enterprise_steepness = np.random.triangular(0.5, 0.7, 1.0)
            enterprise_royalty = np.random.triangular(18.00, 22.00, 28.00)
            
            iot_max_pen = np.random.triangular(0.20, 0.30, 0.45)
            iot_inflection = np.random.triangular(8, 10, 12)
            iot_steepness = np.random.triangular(0.4, 0.6, 0.9)
            iot_royalty = np.random.triangular(24.00, 30.00, 38.00)
            
        elif scenario_name == "downside":
            enterprise_max_pen = np.random.triangular(0.05, 0.10, 0.16)
            enterprise_inflection = np.random.triangular(12, 14, 17)
            enterprise_steepness = np.random.triangular(0.2, 0.3, 0.4)
            enterprise_royalty = np.random.triangular(4.00, 6.00, 8.00)
            
            iot_max_pen = np.random.triangular(0.03, 0.06, 0.12)
            iot_inflection = np.random.triangular(13, 15, 18)
            iot_steepness = np.random.triangular(0.2, 0.3, 0.4)
            iot_royalty = np.random.triangular(6.00, 9.00, 12.00)
        
        # Project cash flows for 20 years
        cash_flows = []
        
        for year in range(1, PATENT_LIFETIME + 1):
            # Enterprise market
            enterprise_tam = project_enterprise_tam(year)
            enterprise_adoption = logistic_adoption_curve(year, enterprise_max_pen, 
                                                         enterprise_inflection, enterprise_steepness)
            enterprise_licensed = enterprise_tam * enterprise_adoption
            enterprise_revenue = enterprise_licensed * enterprise_royalty
            
            # IoT gateway market
            iot_tam = project_iot_tam(year)
            iot_adoption = logistic_adoption_curve(year, iot_max_pen, iot_inflection, iot_steepness)
            iot_licensed = iot_tam * iot_adoption
            iot_revenue = iot_licensed * iot_royalty
            
            # Total revenue
            total_revenue = enterprise_revenue + iot_revenue
            
            # Costs
            if year <= 3:
                costs = np.random.triangular(450_000, 700_000, 1_100_000)  # Early (R&D, NIST engagement)
            elif year <= 8:
                costs = np.random.triangular(200_000, 350_000, 550_000)   # Mid
            else:
                costs = np.random.triangular(100_000, 200_000, 350_000)   # Late
            
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
    print("--- PQLock E7: Risk-Neutral NPV Economic Model ---")
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
    print(f"\n{'Scenario':<15} {'Mean':<12} {'Median':<12} {'P20':<12} {'P85':<12} {'P95':<12}")
    print("-" * 85)
    
    for scenario in scenarios:
        samples = results[scenario]
        mean = np.mean(samples)
        median = np.median(samples)
        p20 = np.percentile(samples, 20)
        p85 = np.percentile(samples, 85)
        p95 = np.percentile(samples, 95)
        
        print(f"{scenario.upper():<15} ${mean/1e6:>6.1f}M    ${median/1e6:>6.1f}M    ${p20/1e6:>6.1f}M    ${p85/1e6:>6.1f}M    ${p95/1e6:>6.1f}M")
    
    # Target validation
    base_mean = np.mean(results["base"])
    aggressive_p85 = np.percentile(results["aggressive"], 85)
    downside_p20 = np.percentile(results["downside"], 20)
    
    print(f"\n--- Target Validation ---")
    print(f"Base Case Mean:       ${base_mean/1e6:.1f}M (Target: $34M)")
    print(f"Aggressive P85:       ${aggressive_p85/1e6:.1f}M (Target: $89.2M)")
    print(f"Downside P20:         ${downside_p20/1e6:.1f}M (Target: $6.4M)")
    
    # Save CSV
    with open('pqlock_rnpv_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['scenario', 'draw', 'npv_usd'])
        
        for scenario in scenarios:
            for i, npv in enumerate(results[scenario]):
                writer.writerow([scenario, i, npv])
    
    print("\nSaved pqlock_rnpv_results.csv")
    
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
    ax1.set_title('PQLock Patent Portfolio: rNPV Distribution', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(axis='y', alpha=0.3)
    ax1.axvline(base_mean / 1e6, color=colors['base'], linestyle='--', linewidth=2, alpha=0.7)
    
    # 2. Cumulative distribution function
    for scenario in scenarios:
        samples = np.sort(results[scenario] / 1e6)
        probabilities = np.linspace(0, 1, len(samples))
        ax2.plot(samples, probabilities, label=scenario.upper(), color=colors[scenario], linewidth=2.5)
    
    ax2.set_xlabel('rNPV (Million USD)', fontsize=12)
    ax2.set_ylabel('Cumulative Probability', fontsize=12)
    ax2.set_title('Cumulative Distribution Function', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(0.5, color='gray', linestyle=':', alpha=0.5, label='Median')
    
    # 3. Revenue breakdown (base case)
    years = np.arange(1, 21)
    enterprise_revenues = []
    iot_revenues = []
    
    for year in years:
        enterprise_tam = project_enterprise_tam(year)
        enterprise_adoption = logistic_adoption_curve(year, 0.22, 11, 0.5)
        enterprise_rev = enterprise_tam * enterprise_adoption * 12.00
        
        iot_tam = project_iot_tam(year)
        iot_adoption = logistic_adoption_curve(year, 0.12, 12, 0.4)
        iot_rev = iot_tam * iot_adoption * 18.00
        
        enterprise_revenues.append(enterprise_rev / 1e6)
        iot_revenues.append(iot_rev / 1e6)
    
    ax3.stackplot(years, enterprise_revenues, iot_revenues,
                 labels=['Enterprise TLS', 'IoT Gateways'],
                 colors=['#0074D9', '#FFDC00'], alpha=0.7)
    ax3.set_xlabel('Year', fontsize=12)
    ax3.set_ylabel('Annual Revenue (Million USD)', fontsize=12)
    ax3.set_title('Revenue Breakdown: Enterprise vs. IoT (Base Case)', fontsize=13, fontweight='bold')
    ax3.legend(loc='upper left', fontsize=11)
    ax3.grid(True, alpha=0.3)
    
    # 4. Risk metrics
    scenarios_labels = [s.upper() for s in scenarios]
    
    # Probability of exceeding $20M
    prob_20m = [np.sum(results[s] > 20e6) / len(results[s]) * 100 for s in scenarios]
    # Probability of exceeding $50M
    prob_50m = [np.sum(results[s] > 50e6) / len(results[s]) * 100 for s in scenarios]
    
    x_pos = np.arange(len(scenarios))
    width = 0.35
    
    ax4.bar(x_pos - width/2, prob_20m, width, label='>$20M', color='#00FF41', edgecolor='black', alpha=0.7)
    ax4.bar(x_pos + width/2, prob_50m, width, label='>$50M', color='#0074D9', edgecolor='black', alpha=0.7)
    
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(scenarios_labels)
    ax4.set_ylabel('Probability (%)', fontsize=12)
    ax4.set_title('Probability of Exceeding NPV Thresholds', fontsize=13, fontweight='bold')
    ax4.legend(fontsize=11)
    ax4.grid(axis='y', alpha=0.3)
    
    # Annotate bars
    for i, (p20, p50) in enumerate(zip(prob_20m, prob_50m)):
        ax4.text(i - width/2, p20 + 2, f'{p20:.1f}%', ha='center', fontweight='bold', fontsize=9)
        ax4.text(i + width/2, p50 + 2, f'{p50:.1f}%', ha='center', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('pqlock_rnpv_distribution.png', dpi=300)
    print("Saved pqlock_rnpv_distribution.png")
    
    # Risk assessment
    print(f"\n--- Risk Assessment ---")
    prob_positive_base = np.sum(results["base"] > 0) / len(results["base"])
    prob_above_30m_base = np.sum(results["base"] > 30e6) / len(results["base"])
    prob_above_70m_agg = np.sum(results["aggressive"] > 70e6) / len(results["aggressive"])
    
    print(f"Base Case: {prob_positive_base*100:.1f}% probability of positive NPV")
    print(f"Base Case: {prob_above_30m_base*100:.1f}% probability of exceeding $30M")
    print(f"Aggressive: {prob_above_70m_agg*100:.1f}% probability of exceeding $70M")
    
    # Key drivers
    print(f"\n--- Key Drivers ---")
    print(f"1. NIST PQC Standardization: Regulatory tailwind for quantum-resistant crypto")
    print(f"2. Side-Channel Resistance: 10-15dB DPA SNR reduction (monopoly differentiator)")
    print(f"3. Dual Markets: Enterprise TLS (25M → 120M) + IoT gateways (8M → 80M)")
    
    # Final verdict
    print(f"\n--- Economic Verdict ---")
    if base_mean > 30e6:
        print(f"STATUS: ✅ HIGHLY COMMERCIALLY VIABLE")
        print(f"Base case mean of ${base_mean/1e6:.1f}M significantly exceeds crypto licensing minimum.")
    elif base_mean > 20e6:
        print(f"STATUS: ✅ COMMERCIALLY VIABLE")
    else:
        print(f"STATUS: ⚠️  MARGINAL VIABILITY")
    
    print(f"\nConclusion: PQLock represents a ${base_mean/1e6:.1f}M mean opportunity")
    print(f"in hybrid PQC key exchange for enterprise TLS + IoT, with upside to")
    print(f"${aggressive_p85/1e6:.1f}M under NIST mandate and aggressive adoption.")

if __name__ == "__main__":
    run_rnpv_analysis()
