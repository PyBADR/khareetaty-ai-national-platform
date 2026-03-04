"""Operations & Executive Control Page"""
import streamlit as st
from ui import branding, phone_auth
from core import data_loader as loader
from core import quality as validator
import config

st.set_page_config(page_title="Operations", page_icon="⚙️", layout="wide")

branding.render_page_header("Operations & Executive Control", "⚙️")

# Executive Ownership Panel
st.markdown("## 🔐 Executive Ownership & Authentication")
phone_auth.render_executive_panel()

st.markdown("---")

# Data Quality Panel
st.markdown("## 📋 Data Quality & Governance")

try:
    df = loader.load_incidents()
    if df is not None and not df.empty:
        quality_report = validator.validate_data(df)
        validator.render_quality_report(quality_report)
    else:
        st.warning("No data available for quality assessment")
except Exception as e:
    st.error(f"Error loading data quality report: {str(e)}")

st.markdown("---")

# System Information
st.markdown("## 🔧 System Information")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Platform Details")
    st.markdown(f"**Version:** {config.VERSION}")
    st.markdown(f"**Last Updated:** {config.LAST_UPDATED}")
    st.markdown(f"**Architecture:** Streamlit-Only")
    st.markdown(f"**Data Source:** File-Based (CSV + GeoJSON)")

with col2:
    st.markdown("### Constraints")
    st.markdown("✅ No Backend Required")
    st.markdown("✅ No Database")
    st.markdown("✅ No SMS Gateway (Phase-5)")
    st.markdown("✅ No Secrets/API Keys")
    st.markdown("✅ Streamlit Cloud Ready")

st.markdown("---")

# About
with st.expander("ℹ️ About This Platform"):
    st.markdown(f"""
    ### {config.PROJECT_NAME} — {config.PROJECT_TITLE}
    
    {config.ARCHITECTURE_BANNER}
    
    #### Sovereignty Statement
    🇰🇼 **State of Kuwait — National Intelligence Platform**
    
    This platform operates under executive acknowledgment and national ownership.
    Live OTP/SMS workflows are deferred to Phase-2 to preserve Streamlit-only architecture,
    cloud isolation, and national security boundaries.
    
    {config.DISCLAIMER}
    """)
