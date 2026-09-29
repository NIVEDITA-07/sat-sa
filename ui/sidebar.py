"""
SAT-SA Sidebar Component.
Renders brand header, navigation controls, and offline status indicators.
"""

import streamlit as st
from ui.styles import render_html

def render_sidebar() -> str:
    """
    Renders the custom compact sidebar and returns the selected page.
    """
    with st.sidebar:
        # Top Logo & Identity
        render_html("""
        <div class="sat-sidebar-logo">
            <div class="sat-logo-icon">🛡️</div>
            <div>
                <div class="sat-logo-text">SAT-SA</div>
                <div class="sat-logo-sub">Supervisory Analytics Tool for SOC Assessment</div>
            </div>
        </div>
        """)
        
        # Navigation
        pages = [
            "1. Overview",
            "2. CSE Assessment",
            "3. Review Queue",
            "4. Data & Validation"
        ]
        
        if "nav_radio" not in st.session_state:
            st.session_state["nav_radio"] = pages[0]
            
        selected_page = st.radio(
            "Navigation",
            options=pages,
            label_visibility="collapsed",
            key="nav_radio"
        )
        
        # Spacer
        st.markdown("<div style='height: 140px;'></div>", unsafe_allow_html=True)
        
        # Bottom Status & Agency Branding
        render_html("""
        <div class="sat-sidebar-footer">
            <div class="sat-offline-badge">
                <span style="font-size: 8px;">●</span> OFFLINE / LOCAL
            </div>
            <div style="font-size: 11px; color: #636A84; margin-bottom: 8px;">No external network calls</div>
            <div class="sat-agency-badge">
                <strong>NCIIPC</strong><br>
                National Critical Information<br>
                Infrastructure Protection Centre
            </div>
        </div>
        """)
        
    return selected_page
