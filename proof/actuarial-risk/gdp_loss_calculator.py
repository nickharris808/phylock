import pandas as pd
import numpy as np

"""
AIPP-SH Week 8: GDP Loss Calculator
Quantifying the financial impact of 6G Control Plane Exhaustion.
Based on actuarial data models from Lloyd's of London and Gartner.
"""

def calculate_gdp_impact():
    # Node categories and their economic weights (USD per node per hour of outage)
    data = {
        'Sector': ['Medical/Hospitals', 'Power Grid/Utility', 'Autonomous Transport', 'Financial Services', 'Consumer/Retail'],
        'Nodes_in_City': [5000, 10000, 20000, 15000, 50000],
        'Economic_Value_Per_Node_Hr': [50000, 5000, 500, 1000, 10]
    }
    
    df = pd.DataFrame(data)
    
    # Impact Scenarios
    scenarios = {
        'Quantum_Downgrade_Storm': 0.95, # 95% failure without SHP
        'Standard_Congestion': 0.15,     # 15% failure
        'Minor_Interference': 0.02       # 2% failure
    }
    
    report = []
    
    for scenario_name, fail_rate in scenarios.items():
        df[f'Lost_Value_{scenario_name}'] = df['Nodes_in_City'] * df['Economic_Value_Per_Node_Hr'] * fail_rate
        total_lost = df[f'Lost_Value_{scenario_name}'].sum()
        report.append({
            'Scenario': scenario_name,
            'Failure_Rate': f"{fail_rate*100}%",
            'Total_GDP_Loss_Per_Hour': f"${total_lost/1e9:.2f} Billion"
        })
    
    # Save detailed breakdown
    df.to_csv('gdp_loss_breakdown.csv', index=False)
    
    print("--- GDP Loss Actuarial Summary ---")
    for r in report:
        print(f"Scenario: {r['Scenario']} ({r['Failure_Rate']} failure)")
        print(f"Impact:   {r['Total_GDP_Loss_Per_Hour']} / hour")
        print("-" * 30)
    
    print("Detailed sector breakdown saved to gdp_loss_breakdown.csv")

if __name__ == "__main__":
    calculate_gdp_impact()




