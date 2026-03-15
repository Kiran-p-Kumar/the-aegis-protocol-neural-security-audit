import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. Configuration
INPUT_FILE = 'data/Aegis_Final_Risk_Report.csv'
REPORT_DIR = 'reports/'

def generate_visual_audit():
    # Ensure data exists
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Please run the ML Pipeline script first.")
        return

    # Create reports directory
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

    # Load Final Data
    df = pd.read_csv(INPUT_FILE)

    # Fix: Ensure Risk_Level column exists for plotting
    if 'Risk_Level' not in df.columns:
        df['Risk_Level'] = df['Target'].map({1: 'High Risk', 0: 'Low Risk'})

    # Set professional visual style
    sns.set_theme(style="whitegrid")

    # ---------------------------------------------------------
    # CHART 1: Risk Distribution (With Log Scale for Visibility)
    # ---------------------------------------------------------
    print("Generating Risk Distribution Chart (Log Scale)...")
    plt.figure(figsize=(10, 6))
    
    # Using log=True in histplot or plt.yscale('log') makes small values visible
    ax = sns.countplot(data=df, x='Risk_Level', hue='Risk_Level', 
                       palette={'Low Risk': 'skyblue', 'High Risk': 'red'}, 
                       legend=False)
    
    plt.yscale('log') # This is the magic line!
    
    plt.title('Aegis Protocol: Global Risk Distribution (Logarithmic Scale)', fontsize=14, fontweight='bold')
    plt.xlabel('Security Risk Assessment', fontsize=12)
    plt.ylabel('Event Count (Log Scale)', fontsize=12)
    
    # Adding count labels on top of bars
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontweight='bold')

    plt.savefig(os.path.join(REPORT_DIR, 'risk_distribution_fixed.png'))
    plt.close()

    # ---------------------------------------------------------
    # CHART 2: Temporal Exposure (Hourly Trend)
    # ---------------------------------------------------------
    print("Generating Temporal Anomaly Heatmap...")
    plt.figure(figsize=(12, 6))
    high_risk_df = df[df['Risk_Level'] == 'High Risk']
    
    if not high_risk_df.empty:
        # Using a line plot with markers to show exactly where the leaks are
        hourly_counts = high_risk_df['Hour'].value_counts().sort_index()
        plt.plot(hourly_counts.index, hourly_counts.values, marker='o', color='red', linewidth=2, markersize=8)
        plt.fill_between(hourly_counts.index, hourly_counts.values, color='red', alpha=0.2)
        
        plt.title('Critical Exposure Window: High-Risk Anomalies by Hour', fontsize=14, fontweight='bold')
        plt.xlabel('Hour of Day (0-23)', fontsize=12)
        plt.ylabel('Detected Anomalies', fontsize=12)
        plt.xticks(range(0, 24))
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.savefig(os.path.join(REPORT_DIR, 'hourly_risk_exposure_fixed.png'))
    else:
        print("Warning: No High-Risk records found to visualize.")
    
    plt.close()

    # ---------------------------------------------------------
    # STEP 3: Save Critical Summary CSV
    # ---------------------------------------------------------
    print("Exporting Final Audit Summary...")
    top_threats = df[df['Target'] == 1].sort_values(by='Risk_Probability', ascending=False).head(10)
    top_threats.to_csv('data/Aegis_Security_Audit_Summary.csv', index=False)

    print(f"\n✅ Audit Success! Charts saved in '{REPORT_DIR}' folder.")

if __name__ == "__main__":
    generate_visual_audit()