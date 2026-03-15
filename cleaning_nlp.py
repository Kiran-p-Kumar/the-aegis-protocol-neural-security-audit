import pandas as pd
import numpy as np
import re
import os

# 1. Path Configuration
# Paths are relative to the root folder where the terminal is running
input_file = 'data/Aegis_Messy_Logs.csv'
output_file = 'data/Aegis_Cleaned_Logs.csv'

def clean_and_process():
    # Check if the raw data file exists in the data directory
    if not os.path.exists(input_file):
        print(f"Error: Could not find {input_file}. Ensure you are running from the root folder.")
        return

    # Load Dataset
    print("Initiating Data Ingestion: Loading 1M+ records...")
    df = pd.read_csv(input_file)

    # 2. Data Integrity & Cleaning
    print("Processing Data Integrity: Handling nulls and malformed strings...")
    
    # Standardize Timestamps
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Timestamp'] = df['Timestamp'].ffill()

    # Regex: Clean IP Addresses (Remove noise and standardize format)
    df['IP_Address'] = df['IP_Address'].apply(lambda x: re.sub(r'\.unknown$', '', str(x)))

    # Handle Anomalous File Sizes using Median Imputation
    median_val = df[df['File_Size_MB'] > 0]['File_Size_MB'].median()
    df['File_Size_MB'] = df['File_Size_MB'].apply(lambda x: median_val if x <= 0 else x)

    # 3. NLP Feature Engineering (Sensitivity Scoring)
    print("Executing NLP Analysis: Generating Metadata Sensitivity Scores...")
    sensitive_keywords = ['confidential', 'pii', 'revenue', 'strategy', 'database', 'backup', 'internal', 'sql']

    def calculate_sensitivity(file_name):
        score = 0
        file_name = str(file_name).lower()
        for word in sensitive_keywords:
            if word in file_name:
                score += 1
        return score

    df['Sensitivity_Score'] = df['File_Name'].apply(calculate_sensitivity)

    # 4. Behavioral Feature Extraction
    # Flagging Night Shift activities for anomaly context
    df['Hour'] = df['Timestamp'].dt.hour
    df['Is_Night_Shift'] = df['Hour'].apply(lambda x: 1 if (x >= 22 or x <= 5) else 0)

    # 5. Export Cleaned Dataset
    df.to_csv(output_file, index=False)
    print(f"Pipeline Complete: Cleaned dataset saved to {output_file}")

if __name__ == "__main__":
    clean_and_process()