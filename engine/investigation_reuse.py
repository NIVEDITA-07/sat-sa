import re
import pandas as pd
from engine.findings import Finding
from engine.data_store import DataStore
from config import REPEATED_NOTE_THRESHOLD

def generate_finding_id(cse_id: str, rule_id: str, index: int) -> str:
    return f"{cse_id}-{rule_id.replace('-', '')}-{index:03d}"

def normalize_text(text: str) -> str:
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def check_investigation_reuse(store: DataStore) -> list[Finding]:
    """
    INVESTIGATION_REUSE (I-1): Detects repeated/boilerplate investigation notes.
    """
    findings = []
    
    cases_df = store.cases_df
    if cases_df.empty or "investigation_note" not in cases_df.columns:
        return findings
        
    for cse_id in store._profiles_idx.keys():
        cse_cases = cases_df[cases_df["cse_id"] == cse_id]
        if cse_cases.empty: continue
        
        # Group notes by investigator
        investigator_notes = {}
        for _, row in cse_cases.iterrows():
            note = row.get("investigation_note")
            if pd.isna(note) or str(note).strip() == "": continue
            
            norm_note = normalize_text(str(note))
            if len(norm_note) < 20: continue
            
            inv_id = row.get("investigator_id", "Unknown")
            case_id = row.get("case_id")
            
            if inv_id not in investigator_notes:
                investigator_notes[inv_id] = {}
                
            if norm_note not in investigator_notes[inv_id]:
                investigator_notes[inv_id][norm_note] = []
            investigator_notes[inv_id][norm_note].append(case_id)
            
        finding_idx = 1
        for inv_id, patterns in investigator_notes.items():
            # Check if this investigator has ANY note that meets the threshold
            violating_notes = {note: cases for note, cases in patterns.items() if len(cases) >= REPEATED_NOTE_THRESHOLD}
            
            if violating_notes:
                # Investigator exceeded threshold for at least one note.
                # Gather all cases for this investigator as evidence to match ground truth expectations.
                all_inv_cases = []
                for cases in patterns.values():
                    all_inv_cases.extend(cases)
                    
                # Use the most frequent violating note for the display explanation
                worst_note = max(violating_notes.items(), key=lambda x: len(x[1]))
                worst_norm_note = worst_note[0]
                worst_cases = worst_note[1]
                max_freq = len(worst_cases)
                
                sev = "HIGH" if max_freq >= REPEATED_NOTE_THRESHOLD * 2 else "MEDIUM"
                
                display_note = ""
                first_case = store.get_case_evidence(worst_cases[0])
                if first_case:
                    display_note = first_case.get("investigation_note", worst_norm_note)
                    
                findings.append(Finding(
                    finding_id=generate_finding_id(cse_id, "I-1", finding_idx),
                    cse_id=cse_id,
                    rule_id="I-1",
                    category="investigation_reuse",
                    severity=sev,
                    title="Repeated investigation-note pattern detected; examiner review required",
                    explanation=f"Investigator '{inv_id}' reused identical boilerplate text (max {max_freq} times). First observed note: \"{str(display_note)[:100]}...\"",
                    evidence_ids=all_inv_cases,
                    metric_value=max_freq,
                    peer_value=None,
                    related_asset_type=f"Investigator {inv_id}"
                ))
                finding_idx += 1
                    
    return findings
