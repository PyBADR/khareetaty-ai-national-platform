"""
Khareetaty AI — Kuwait National Intelligence Platform
Main Streamlit Application Entry Point

Version: 5.0 (Phase-5 Kuwait National)
Architecture: Streamlit-Only | File-Based | No Backend | No Database
Owner: Bader Alabdadan
Contact: +965 6663 3387
"""

import streamlit as st
from pathlib import Path

import config
from ui import branding, theme, phone_auth
from core import data_loader as loader
from core import quality as validator
from core import analytics as engine

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.set_page_config(**config.PAGE_CONFIG)

# Apply theme
theme.apply_theme()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HEADER & BRANDING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

branding.render_header()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SYSTEM STATUS PANEL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("---")
st.subheader("🔧 System Status")

col1, col2, col3, col4, col5 = st.columns(5)

# Load data
try:
    df = loader.load_incidents()
    data_loaded = df is not None and len(df) > 0
except Exception as e:
    data_loaded = False
    df = None

# Check geo
try:
    geo_data = loader.load_geo_layers()
    geo_loaded = geo_data is not None and len(geo_data) > 0
except Exception as e:
    geo_loaded = False
    geo_data = None

# Analytics ready
analytics_ready = data_loaded

with col1:
    st.metric("Data Loaded", "✅ Yes" if data_loaded else "❌ No")
    if data_loaded and df is not None:
        st.caption(f"{len(df):,} incidents")

with col2:
    st.metric("Geo Loaded", "✅ Yes" if geo_loaded else "❌ No")
    if geo_loaded and geo_data is not None:
        st.caption(f"{len(geo_data)} layers")

with col3:
    st.metric("Analytics Ready", "✅ Yes" if analytics_ready else "❌ No")

with col4:
    st.metric("No Backend Required", "✅ Always True")
    st.caption("Streamlit-Only")

with col5:
    st.metric("National Boundary", "🇰🇼 Kuwait-Only")
    st.caption("Enforced")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUTIVE SUMMARY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("---")
st.header("📊 Executive Summary")

if data_loaded and df is not None:
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Incidents", f"{len(df):,}")
    
    with col2:
        # Recent incidents (last 7 days)
        try:
            import pandas as pd
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            recent = df[df['timestamp'] >= pd.Timestamp.now() - pd.Timedelta(days=7)]
            st.metric("Last 7 Days", f"{len(recent):,}")
        except:
            st.metric("Last 7 Days", "N/A")
    
    with col3:
        # Top incident type
        try:
            top_type = df['incident_type'].value_counts().index[0]
            st.metric("Top Incident Type", top_type.replace("_", " ").title())
        except:
            st.metric("Top Incident Type", "N/A")
    
    with col4:
        # Top governorate
        try:
            top_gov = df['governorate'].value_counts().index[0]
            st.metric("Top Governorate", top_gov)
        except:
            st.metric("Top Governorate", "N/A")
    
    # Quick charts
    st.markdown("### 📈 Quick Insights")
    
    tab1, tab2 = st.tabs(["Incident Types", "Governorates"])
    
    with tab1:
        try:
            incident_counts = df['incident_type'].value_counts()
            st.bar_chart(incident_counts)
        except Exception as e:
            st.warning("Unable to display incident type chart")
    
    with tab2:
        try:
            gov_counts = df['governorate'].value_counts()
            st.bar_chart(gov_counts)
        except Exception as e:
            st.warning("Unable to display governorate chart")

else:
    st.warning("⚠️ No data loaded. Please ensure data files are present in the `data/` folder.")
    st.info("Expected file: `data/incidents.csv`")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUTIVE OWNERSHIP & AUTHENTICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("---")
st.header("🔐 Executive Ownership & Authentication")

phone_auth.render_executive_panel()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA QUALITY & GOVERNANCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("---")

with st.expander("📋 Executive Data Quality & Governance", expanded=False):
    if data_loaded and df is not None:
        quality_report = validator.validate_data(df)
        validator.render_quality_report(quality_report)
    else:
        st.warning("No data available for quality assessment")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ABOUT & DISCLAIMER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("---")

with st.expander("ℹ️ About This Platform", expanded=False):
    st.markdown(f"""
    ### {config.PROJECT_NAME} — {config.PROJECT_TITLE}
    
    **Version:** {config.VERSION}  
    **Last Updated:** {config.LAST_UPDATED}  
    **Architecture:** {config.ARCHITECTURE_BANNER}
    
    #### Executive Ownership
    - **Owner:** Bader Alabdadan
    - **Primary National Contact:** +965 6663 3387
    - **Authentication Mode:** Executive Acknowledgment
    - **Status:** Verified — Phase-5
    
    #### Platform Characteristics
    - ✅ **Streamlit-Only:** No backend services required
    - ✅ **File-Based Analytics:** CSV + GeoJSON inside repository
    - ✅ **No Database:** No PostgreSQL, no external databases
    - ✅ **No SMS Gateway:** No Twilio, no OTP (deferred to Phase-2)
    - ✅ **No Secrets:** No API keys, no credentials
    - ✅ **Streamlit Cloud Ready:** Zero external service dependencies
    - ✅ **Kuwait National Boundary:** Geographic enforcement active
    
    #### Sovereignty Statement
    🇰🇼 **State of Kuwait — National Intelligence Platform**
    
    This platform operates under executive acknowledgment and national ownership.
    Live OTP/SMS workflows are deferred to Phase-2 to preserve Streamlit-only architecture,
    cloud isolation, and national security boundaries.
    
    {config.DISCLAIMER}
    """)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FOOTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("---")
st.caption(f"🇰🇼 {config.PROJECT_NAME} v{config.VERSION} | State of Kuwait — National Intelligence Platform")
