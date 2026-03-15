import pandas as pd
import xgboost as xgb
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import os

# Configuration
INPUT_FILE = 'data/Aegis_Cleaned_Logs.csv'
OUTPUT_FILE = 'data/Aegis_Final_Risk_Report.csv'
XGB_MODEL_PATH = 'data/aegis_xgb_model.json'

def run_ml_pipeline():
    # 1. Check file existence
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Ensure the cleaning script ran successfully.")
        return

    try:
        # 2. Ingest Data
        print("Step 1: Ingesting data...")
        df = pd.read_csv(INPUT_FILE)

        # 3. Select Numerical Features only for ML
        features = ['File_Size_MB', 'Sensitivity_Score', 'Hour', 'Is_Night_Shift']
        X = df[features].astype(float) # Ensure all data is float to avoid dtype errors

        # 4. Step 1: Isolation Forest (Anomaly Tagging)
        print("Step 2: Identifying outliers via Isolation Forest...")
        iso_forest = IsolationForest(contamination=0.0005, random_state=42, n_jobs=-1) 
        # n_jobs=-1 uses all CPU cores for speed
        
        df['Anomaly_Label'] = iso_forest.fit_predict(X)
        df['Target'] = df['Anomaly_Label'].apply(lambda x: 1 if x == -1 else 0)

        # 5. Step 2: XGBoost Classifier
        print("Step 3: Training XGBoost Classifier...")
        y = df['Target']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        # Optimization: tree_method='hist' is faster for large datasets
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            scale_pos_weight=1000, 
            tree_method='hist', 
            random_state=42
        )
        
        xgb_model.fit(X_train, y_train)

        # 6. Evaluation
        y_pred = xgb_model.predict(X_test)
        print("\n--- Model Performance Report ---")
        print(classification_report(y_test, y_pred))

        # 7. Final Output & Export
        print("Finalizing results...")
        df['Risk_Probability'] = xgb_model.predict_proba(X)[:, 1]
        df.to_csv(OUTPUT_FILE, index=False)
        xgb_model.save_model(XGB_MODEL_PATH)
        
        print(f"\n✅ Success: Final Report saved to {OUTPUT_FILE}")

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_ml_pipeline()