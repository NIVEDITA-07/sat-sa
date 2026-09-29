"""
SAT-SA UI Styling & Design System
Strictly follows the Indigo/Violet Brand Palette and Enterprise Cybersecurity theme.
"""

def get_custom_css() -> str:
    return """
<style>
/* -------------------------------------------------------------------------
   SAT-SA ENTERPRISE DESIGN SYSTEM (VISUAL POLISH PASS)
   Brand Primary: Indigo / Violet (#5B50B5)
   Backgrounds: #F2F3F8 (canvas), #F7F7FA (secondary), #FCFCFE (cards)
   Alerts: #D64545 (High), #D99A27 (Medium), #31966B (Low)
------------------------------------------------------------------------- */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --brand-950: #40378C;
    --brand-900: #5B50B5;
    --brand-800: #5247A6;
    --brand-700: #655BC7;
    --brand-600: #665BC7;
    --brand-500: #8279D8;
    --brand-100: #E9E6FF;
    --brand-50:  #F3F1FF;
    
    --bg-main: #F2F3F8;
    --bg-surface: #F7F7FA;
    --bg-card: #FCFCFE;
    --bg-sidebar: #EBECF1;
    --border-color: #E3E4EC;
    
    --alert-high: #D64545;
    --alert-high-bg: #FDF2F2;
    --alert-high-border: #F9D2D2;
    
    --alert-med: #D99A27;
    --alert-med-bg: #FEF9E7;
    --alert-med-border: #FDE8C7;
    
    --alert-low: #31966B;
    --alert-low-bg: #EAF7F1;
    --alert-low-border: #D1E7DD;
    
    --shadow-soft: 0 4px 18px rgba(54, 47, 110, 0.06);
    --shadow-hover: 0 6px 20px rgba(54, 47, 110, 0.09);
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-pill: 9999px;
}

/* Global Container & Typography */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    background-color: var(--bg-main) !important;
    color: #1E202B !important;
}

/* Header & Main Padding */
.main .block-container {
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 1440px !important;
}

/* Sidebar Customization */
section[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-color) !important;
    width: 260px !important;
}

section[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}

/* Radio button (Sidebar Navigation) hover styling */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
    padding: 6px 12px;
    border-radius: 8px;
    transition: background-color 0.15s ease;
}
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
    background-color: var(--brand-50);
}

/* Hide default streamlit top header line & menu */
#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {
    display: none !important;
}
[data-testid="stToolbar"] {
    display: none !important;
}

/* Top Navigation Bar / Breadcrumb Header */
.sat-header-wrapper {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 1.25rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid var(--border-color);
}

.sat-header-title {
    font-size: 26px;
    font-weight: 700;
    color: var(--brand-950);
    margin: 0;
    line-height: 1.2;
}

.sat-header-subtitle {
    font-size: 13px;
    color: #636A84;
    margin-top: 4px;
    font-weight: 500;
}

.sat-meta-pill-group {
    display: flex;
    gap: 8px;
    align-items: center;
}

.sat-meta-pill {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    padding: 6px 12px;
    border-radius: var(--radius-pill);
    font-size: 12px;
    font-weight: 500;
    color: #4A5168;
    display: flex;
    align-items: center;
    gap: 6px;
}

.sat-meta-pill strong {
    color: var(--brand-900);
}

/* Card Components */
.sat-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 1.25rem;
    box-shadow: var(--shadow-soft);
    margin-bottom: 1rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.sat-card:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
}

.sat-card-gradient {
    background: linear-gradient(135deg, var(--brand-600), var(--brand-500)) !important;
    border: 1px solid var(--brand-600) !important;
    color: #FFFFFF !important;
}

.sat-card-gradient .sat-kpi-label {
    color: var(--brand-50) !important;
}

.sat-card-gradient .sat-kpi-val {
    color: #FFFFFF !important;
}

/* KPI Card specifics */
.sat-kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 1.1rem 1.25rem;
    box-shadow: var(--shadow-soft);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.sat-kpi-card:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
}

.sat-kpi-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.sat-kpi-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #636A84;
}

.sat-indicator-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}

.sat-dot-high { background-color: var(--alert-high); }
.sat-dot-med { background-color: var(--alert-med); }
.sat-dot-low { background-color: var(--alert-low); }

.sat-kpi-val {
    font-size: 28px;
    font-weight: 700;
    color: var(--brand-950);
    line-height: 1.1;
}

.sat-kpi-sub {
    font-size: 12px;
    color: #7A819B;
    margin-top: 4px;
}

/* Supervisory Sector-wide Signal Banner */
.sat-sector-banner {
    background: linear-gradient(135deg, var(--brand-50) 0%, var(--brand-100) 100%);
    border: 1px solid var(--brand-100);
    border-left: 4px solid var(--brand-600);
    border-radius: var(--radius-md);
    padding: 1rem 1.25rem;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: var(--shadow-soft);
}

.sat-banner-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.sat-banner-icon {
    background-color: transparent;
    color: var(--brand-700);
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
}

.sat-banner-title {
    font-size: 14px;
    font-weight: 700;
    color: var(--brand-950);
    margin: 0;
}

.sat-banner-desc {
    font-size: 12.5px;
    color: var(--brand-950);
    margin-top: 2px;
}

/* Badges */
.sat-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 8px;
    border-radius: var(--radius-pill);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

.sat-badge-high {
    background-color: var(--alert-high-bg);
    color: var(--alert-high);
    border: 1px solid var(--alert-high-border);
}

.sat-badge-med {
    background-color: var(--alert-med-bg);
    color: var(--alert-med);
    border: 1px solid var(--alert-med-border);
}

.sat-badge-low {
    background-color: var(--alert-low-bg);
    color: var(--alert-low);
    border: 1px solid var(--alert-low-border);
}

.sat-badge-neutral {
    background-color: var(--brand-50);
    color: var(--brand-700);
    border: 1px solid var(--brand-100);
}

/* Tables & Lists */
.sat-table-wrapper {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    overflow: hidden;
    box-shadow: var(--shadow-soft);
}

.sat-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    text-align: left;
}

.sat-table th {
    background-color: var(--bg-surface);
    color: #636A84;
    font-weight: 600;
    font-size: 11.5px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 12px 14px;
    border-bottom: 1px solid var(--border-color);
}

.sat-table td {
    padding: 12px 14px;
    border-bottom: 1px solid var(--border-color);
    color: #2D3142;
    vertical-align: middle;
    transition: background-color 0.15s ease;
}

.sat-table tr:hover td {
    background-color: var(--brand-50);
}

/* Expected vs Observed Workflow Card */
.sat-workflow-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 1.25rem;
    box-shadow: var(--shadow-soft);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.sat-workflow-card:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
}

.sat-workflow-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 1rem;
    margin-bottom: 1rem;
}

.sat-flow-col {
    border-radius: 8px;
    padding: 12px;
}

.sat-flow-expected {
    background-color: var(--brand-50);
    border: 1px solid var(--brand-100);
}

.sat-flow-observed {
    background-color: var(--bg-surface);
    border: 1px solid var(--border-color);
}

.sat-flow-header {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 10px;
    text-align: center;
}

.sat-flow-step {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 12px;
    font-weight: 500;
    color: #33384F;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.sat-step-missing {
    background-color: var(--alert-high-bg) !important;
    border: 1px solid var(--alert-high-border) !important;
    color: var(--alert-high) !important;
    font-weight: 600 !important;
}

.sat-arrow {
    text-align: center;
    color: #9AA0B4;
    font-size: 12px;
    margin: -4px 0 4px 0;
}

/* Operational Evidence Cards */
.sat-op-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 1rem 1.1rem;
    box-shadow: var(--shadow-soft);
    border-top: 3px solid var(--brand-600);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.sat-op-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-hover);
}

.sat-op-rule {
    font-size: 11px;
    font-weight: 700;
    color: var(--brand-700);
    background-color: var(--brand-50);
    padding: 3px 8px;
    border-radius: 6px;
    display: inline-block;
    margin-bottom: 8px;
}

.sat-op-title {
    font-size: 13.5px;
    font-weight: 600;
    color: var(--brand-950);
    line-height: 1.3;
    margin-bottom: 8px;
}

.sat-op-count {
    font-size: 18px;
    font-weight: 700;
    color: #1E202B;
}

.sat-op-sub {
    font-size: 11.5px;
    color: #7A819B;
}

/* Streamlit Native Element Overrides */
div[data-testid="stExpander"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
}

/* ---- FIX NATIVE INPUTS (Selectbox, TextInput, FileUploader) ---- */
div[data-baseweb="select"] > div, 
div[data-baseweb="base-input"],
div[data-testid="stFileUploaderDropzone"] {
    background-color: #FFFFFF !important;
    border: 1px solid var(--border-color) !important;
    color: #1E202B !important;
}

input, textarea {
    color: #1E202B !important;
    background-color: #FFFFFF !important;
}

input::placeholder {
    color: #636A84 !important;
}

/* ---- FIX STREAMLIT NATIVE TYPOGRAPHY (Defeat Dark Mode) ---- */
/* Target ONLY direct children of markdown containers to spare custom HTML */
div[data-testid="stMarkdownContainer"] > p,
div[data-testid="stMarkdownContainer"] > h1,
div[data-testid="stMarkdownContainer"] > h2,
div[data-testid="stMarkdownContainer"] > h3,
div[data-testid="stMarkdownContainer"] > h4,
div[data-testid="stMarkdownContainer"] > h5,
div[data-testid="stMarkdownContainer"] > h6 {
    color: #1E202B !important;
}

/* Force sidebar text to be dark */
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] > p {
    color: #1E202B !important;
}

/* Fix radio buttons */
div[role="radiogroup"] label p {
    color: #1E202B !important;
}
div[role="radiogroup"] label {
    background-color: transparent !important;
}

/* Fix widget labels */
label[data-testid="stWidgetLabel"] p {
    color: #1E202B !important;
    font-weight: 600 !important;
}

/* Keep the logo icon white */
.sat-logo-icon {
    color: #FFFFFF !important;
}

.stButton > button {
    background-color: var(--brand-700) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.45rem 1rem !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    transition: background-color 0.2s ease, transform 0.15s ease !important;
}

.stButton > button:hover {
    background-color: var(--brand-800) !important;
    transform: translateY(-1px) !important;
}

.stButton > button:active {
    background-color: var(--brand-950) !important;
    transform: translateY(0px) !important;
}

/* Secondary Button */
.sat-sec-btn > button {
    background-color: var(--bg-card) !important;
    color: var(--brand-700) !important;
    border: 1px solid var(--brand-500) !important;
}

.sat-sec-btn > button:hover {
    background-color: var(--brand-50) !important;
}

/* Sidebar Branding & Nav */
.sat-sidebar-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 1.25rem;
    margin-bottom: 1.25rem;
    border-bottom: 1px solid var(--border-color);
}

.sat-logo-icon {
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, var(--brand-900), var(--brand-700));
    color: #FFFFFF;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: bold;
    box-shadow: 0 2px 8px rgba(91, 80, 181, 0.25);
}

.sat-logo-text {
    font-size: 18px;
    font-weight: 700;
    color: var(--brand-950);
    letter-spacing: -0.02em;
    line-height: 1.1;
}

.sat-logo-sub {
    font-size: 10.5px;
    font-weight: 500;
    color: #636A84;
}

.sat-sidebar-footer {
    position: fixed;
    bottom: 15px;
    left: 15px;
    width: 230px;
    padding-top: 15px;
    border-top: 1px solid var(--border-color);
    background-color: var(--bg-sidebar);
}

.sat-offline-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 600;
    color: var(--alert-low) !important;
    background-color: var(--alert-low-bg) !important;
    border: 1px solid var(--alert-low-border);
    padding: 4px 10px;
    border-radius: var(--radius-pill);
    margin-bottom: 8px;
}

.sat-agency-badge {
    font-size: 10.5px;
    color: #7A819B !important;
    line-height: 1.4;
}

.sat-agency-badge strong {
    color: var(--brand-900) !important;
}
</style>
"""

import streamlit as st

def render_html(html_content: str):
    """
    Renders raw HTML safely in Streamlit without risk of markdown indented code block formatting.
    Strips leading/trailing whitespace per line so no line starts with >=4 spaces.
    """
    clean = "\n".join(line.strip() for line in html_content.strip().split("\n") if line.strip())
    st.markdown(clean, unsafe_allow_html=True)
