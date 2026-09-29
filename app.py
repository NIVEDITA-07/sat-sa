"""
SAT-SA — Supervisory Analytics Tool for SOC Assessment
SIH26157 | NCIIPC | Cybersecurity / Software
Single-page Streamlit Enterprise Dashboard Entrypoint.
"""

import streamlit as st
from ui.styles import get_custom_css, render_html
from ui.sidebar import render_sidebar
from engine.bootstrap import load_and_run_pipeline
from ui.overview import render_overview
from ui.cse_detail import render_cse_detail
from ui.review_queue import render_review_queue
from ui.data_validation import render_data_validation

# Set Streamlit Page Configuration (Desktop-first, wide layout)
st.set_page_config(
    page_title="SAT-SA | Supervisory Analytics Tool",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Inject Master Design System CSS
    render_html(get_custom_css())
    
    # Initialize Session State Dataset if not already loaded
    if "dataset" not in st.session_state:
        st.session_state["dataset"] = load_and_run_pipeline()
        
    dataset = st.session_state["dataset"]

    # Handle Query Parameters for Deep Linking
    if "nav" in st.query_params:
        nav = st.query_params["nav"]
        if nav == "queue":
            st.session_state["nav_radio"] = "3. Review Queue"
        elif nav == "cse":
            st.session_state["nav_radio"] = "2. CSE Assessment"
            
        if "rule" in st.query_params:
            st.session_state["q_rule_filter"] = st.query_params["rule"]
        if "cse_id" in st.query_params:
            st.session_state["cse_detail_selector"] = st.query_params["cse_id"]
            
        # Clear query params after consuming them so they don't persist on refresh
        st.query_params.clear()

    # Render Sidebar and retrieve active page selection
    active_page = render_sidebar()

    # Route to selected view
    if active_page == "1. Overview":
        render_overview(dataset)
    elif active_page == "2. CSE Assessment":
        render_cse_detail(dataset)
    elif active_page == "3. Review Queue":
        render_review_queue(dataset)
    elif active_page == "4. Data & Validation":
        render_data_validation(dataset)
    else:
        render_overview(dataset)

if __name__ == "__main__":
    main()
