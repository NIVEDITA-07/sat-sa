import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.sample_data import generate_sample_data

def export_data():
    data = generate_sample_data()
    alerts_df = data["alerts_df"]
    assets_df = data["assets_df"]
    cases_df = data["cases_df"]
    
    out_dir = os.path.dirname(__file__)
    
    alerts_df.to_csv(os.path.join(out_dir, "alerts.csv"), index=False)
    assets_df.to_csv(os.path.join(out_dir, "assets.csv"), index=False)
    cases_df.to_csv(os.path.join(out_dir, "cases.csv"), index=False)
    
    print(f"Exported {len(alerts_df)} alerts, {len(assets_df)} assets, and {len(cases_df)} cases.")

if __name__ == "__main__":
    export_data()
