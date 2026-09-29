import streamlit as st

if "nav_radio" not in st.session_state:
    st.session_state.nav_radio = "Home"

if "nav" in st.query_params:
    nav = st.query_params["nav"]
    if nav == "Home":
        st.session_state.nav_radio = "Home"
    elif nav == "Settings":
        st.session_state.nav_radio = "Settings"
    st.query_params.clear()

st.radio("Nav", ["Home", "Settings"], key="nav_radio")

st.markdown('<a href="?nav=Settings" target="_self">Go to Settings</a>', unsafe_allow_html=True)
