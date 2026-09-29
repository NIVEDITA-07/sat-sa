import pandas as pd
from engine.bootstrap import load_and_run_pipeline

def run_integration_test():
    print("Running SAT-SA Integration Test...")
    
    # Run the pipeline (this loads the 4 CSVs and performs schema validation + engine execution)
    res = load_and_run_pipeline('CONTROLLED_DEMO')
    
    val_metrics = res.get("validation_metrics", {})
    summary = val_metrics.get("summary", {})
    
    print("\n--- Validation Report ---")
    print(f"Ground-truth scenarios: {summary.get('expected_total')}")
    print(f"Detected: {summary.get('detected')}")
    print(f"Not detected: {summary.get('not_detected')}")
    print(f"Unexpected detections: {summary.get('unexpected_detections')}")
    
    print("\n--- Detailed Results ---")
    results = val_metrics.get("results", [])
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        print(df_results.to_string())
    
    # Check if any FAIL
    fails = [r for r in results if r["Status"] == "FAIL"]
    if fails:
        print("\n[!] The following scenarios failed to detect:")
        for f in fails:
            print(f"  - {f['Scenario']} for {f['CSE']} (Entity: {f['Entity']})")
    else:
        print("\n[+] All ground-truth scenarios were successfully detected!")
        
if __name__ == "__main__":
    run_integration_test()
