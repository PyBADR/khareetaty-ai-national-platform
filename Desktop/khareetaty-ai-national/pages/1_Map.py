"""Map View Page"""
import streamlit as st
from ui import branding
from core import data_loader as loader
from core import geo
import config

st.set_page_config(page_title="Map View", page_icon="🗺️", layout="wide")

branding.render_page_header("Map View", "🗺️")

st.info("🚧 Map visualization coming soon. This page will display Kuwait-bounded incident map with geographic layers.")

# Load data
try:
    df = loader.load_incidents()
    if df is not None and not df.empty:
        # Filter to Kuwait bbox
        df_kuwait = geo.filter_incidents_by_bbox(df)
        st.success(f"Loaded {len(df_kuwait):,} incidents within Kuwait boundaries")
        
        # Show sample data
        with st.expander("Sample Data"):
            st.dataframe(df_kuwait.head(10))
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
