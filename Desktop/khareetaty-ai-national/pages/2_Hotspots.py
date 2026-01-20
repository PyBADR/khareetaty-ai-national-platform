"""Hotspots Analysis Page"""
import streamlit as st
from ui import branding
from core import data_loader as loader
from core import analytics
from core import geo
import config

st.set_page_config(page_title="Hotspots", page_icon="🔥", layout="wide")

branding.render_page_header("Hotspot Analysis", "🔥")

st.info("🚧 Hotspot detection coming soon. This page will identify high-risk zones using DBSCAN clustering.")

# Load data
try:
    df = loader.load_incidents()
    if df is not None and not df.empty:
        df_kuwait = geo.filter_incidents_by_bbox(df)
        st.success(f"Analyzing {len(df_kuwait):,} incidents for hotspots")
        
        # Placeholder for hotspot analysis
        st.markdown("### Risk Zones")
        st.markdown("- High Risk: TBD")
        st.markdown("- Medium Risk: TBD")
        st.markdown("- Low Risk: TBD")
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
