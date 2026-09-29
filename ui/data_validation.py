import streamlit as st
import pandas as pd
from engine.bootstrap import load_and_run_pipeline
from ui.styles import render_html

def render_data_validation(data: dict):
    render_html("""
    <div class="sat-header-wrapper">
        <div>
            <h1 class="sat-header-title">Data Ingestion & Validation</h1>
            <div class="sat-header-subtitle">Heterogeneous SOC evidence normalization and completeness check</div>
        </div>
        <div class="sat-meta-pill-group">
            <div class="sat-meta-pill">
                <span>Validation Mode:</span> <strong>Deterministic Strict</strong>
            </div>
            <div class="sat-meta-pill">
                <span>Network Status:</span> <strong>Air-Gapped Local</strong>
            </div>
        </div>
    </div>
    """)

    st.markdown("### Step 1: Select Source Profile")
    mode = st.radio("Data Mode", ["Controlled Demo", "Public SOC Sample", "CSE Submission"], label_visibility="collapsed")
    
    profile_key = "CONTROLLED_DEMO"
    desc = "Deterministic synthetic dataset used to demonstrate and validate SAT-SA rules."
    if mode == "Public SOC Sample":
        profile_key = "PUBLIC_SOC"
        desc = "Public cybersecurity research data normalized for demonstration."
    elif mode == "CSE Submission":
        profile_key = "CSE_SUBMISSION"
        desc = "Upload SOC/CSE evidence for assessment."
        
    st.caption(desc)
    st.markdown("<hr style='margin:1rem 0; border:none; border-top:1px solid #E3E4EC;'/>", unsafe_allow_html=True)
    
    if mode == "CSE Submission":
        st.markdown("### Step 2: Upload Source Files")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.file_uploader("CSE Profiles", type=["csv"], key="up_p")
        with c2: st.file_uploader("Alerts Export", type=["csv"], key="up_a")
        with c3: st.file_uploader("Asset Inventory", type=["csv"], key="up_b")
        with c4: st.file_uploader("Cases Export", type=["csv"], key="up_c")
        
        st.button("Run Deterministic Verification", type="primary")
        st.info("In this demo, selecting 'CSE Submission' is a placeholder. Please use 'Controlled Demo'.")
        return

    st.markdown("### Step 2: Extract & Map Schema")
    ingestion_meta = data.get("ingestion_meta", {})
    provenance = ingestion_meta.get("provenance", {})
    mappings = ingestion_meta.get("schema_mapping", [])
    
    c_map, c_cov, c_prov = st.columns([2, 2, 1])
    
    with c_map:
        st.markdown("#### Step 3: Source Normalization")
        map_html = '<div style="height: 250px; overflow-y: auto; border: 1px solid #E5E7F0; border-radius: 6px; padding: 10px; background-color: #F8F9FC;"><table style="width: 100%; text-align: left; border-collapse: collapse;">'
        map_html += '<tr style="border-bottom: 2px solid #E5E7F0;"><th style="padding-bottom: 6px; font-size: 11px; color: #7A819B;">SOURCE FIELD</th><th style="padding-bottom: 6px; font-size: 11px; color: #7A819B;">CANONICAL FIELD</th><th style="padding-bottom: 6px; font-size: 11px; color: #7A819B;">STATUS</th></tr>'
        for m in mappings:
            color = "#31966B" if m["status"] == "Mapped" else "#D64545"
            map_html += f'<tr><td style="font-family:monospace; font-size:12px;">{m["source_field"]}</td><td style="font-family:monospace; font-size:12px;">{m["sat_sa_field"]}</td><td style="color:{color}; font-weight:600;">{m["status"]}</td></tr>'
        map_html += '</table></div>'
        render_html(map_html)
        
    with c_cov:
        st.markdown("#### Step 4: Evidence Coverage (Per CSE)")
        coverage_info = data.get("coverage", {})
        
        if not coverage_info:
            st.info("No coverage data available.")
        else:
            selected_cse = st.selectbox("View coverage for:", list(coverage_info.keys()), label_visibility="collapsed")
            cse_cov = coverage_info[selected_cse]["coverage_summary"]
            warnings = coverage_info[selected_cse]["warnings"]
            
            cov_html = '<div class="sat-card" style="border-top: 3px solid var(--brand-600); height: 195px; overflow-y: auto;">'
            for k, v in cse_cov.items():
                color = "#31966B" if v == "Available" else ("#D99A27" if v == "Partial" else "#D64545")
                cov_html += f'<div style="margin-bottom:8px; font-size:13px; font-family:monospace; display:flex; justify-content:space-between; align-items:center;"><span>{k}</span><span style="color:{color}; font-weight: 600;">{v}</span></div>'
            cov_html += '</div>'
            render_html(cov_html)
            
            for w in warnings:
                st.warning(w, icon="⚠️")

    with c_prov:
        st.markdown("#### Step 5: Data Provenance")
        prov_html = f"""
        <div class="sat-card" style="height: 250px;">
            <div style="font-size:11px; color:#7A819B; text-transform:uppercase; margin-bottom:4px;">Source:</div>
            <div style="font-size:13.5px; font-weight:600; color:var(--brand-950); margin-bottom:14px;">{provenance.get("source_name", "-")}</div>
            
            <div style="font-size:11px; color:#7A819B; text-transform:uppercase; margin-bottom:4px;">Type:</div>
            <div style="font-size:13.5px; font-weight:600; color:var(--brand-950); margin-bottom:14px;">{provenance.get("type", "-")}</div>
            
            <div style="font-size:11px; color:#7A819B; text-transform:uppercase; margin-bottom:4px;">Records:</div>
            <div style="font-size:13.5px; font-weight:600; color:var(--brand-950); margin-bottom:14px;">{provenance.get("records", "-")}</div>
            
            <div style="font-size:11px; color:#7A819B; text-transform:uppercase; margin-bottom:4px;">Processing:</div>
            <div style="font-size:13.5px; font-weight:600; color:var(--brand-950); margin-bottom:14px;">Local / Offline</div>
        </div>
        """
        render_html(prov_html)

    val_metrics = data.get("validation_metrics", {})
    if val_metrics and val_metrics.get("status") != "No Ground Truth Found":
        st.markdown("<hr style='margin:1rem 0; border:none; border-top:1px solid #E3E4EC;'/>", unsafe_allow_html=True)
        st.markdown("### Ground Truth Validation Engine")
        
        summary = val_metrics.get("summary", {})
        tot = summary.get("expected_total", 0)
        detected = summary.get("detected", 0)
        not_detected = summary.get("not_detected", 0)
        unexpected = summary.get("unexpected_detections", 0)
        
        val_html = f"""
        <div class="sat-card" style="display:flex; justify-content: space-around; text-align: center; margin-bottom: 20px;">
            <div><div style="font-size:11px; color:#7A819B; text-transform:uppercase;">Ground-truth scenarios</div><div style="font-size:24px; font-weight:700;">{tot}</div></div>
            <div><div style="font-size:11px; color:#7A819B; text-transform:uppercase;">Detected</div><div style="font-size:24px; font-weight:700; color:var(--alert-low);">{detected}</div></div>
            <div><div style="font-size:11px; color:#7A819B; text-transform:uppercase;">Not detected</div><div style="font-size:24px; font-weight:700; color:var(--alert-high);">{not_detected}</div></div>
            <div><div style="font-size:11px; color:#7A819B; text-transform:uppercase;">Unexpected detections</div><div style="font-size:24px; font-weight:700; color:var(--alert-med);">{unexpected}</div></div>
        </div>
        """
        render_html(val_html)
        
        results = val_metrics.get("results", [])
        if results:
            df_results = pd.DataFrame(results)
            st.dataframe(df_results, use_container_width=True, hide_index=True)
