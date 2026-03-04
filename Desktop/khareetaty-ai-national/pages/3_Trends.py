"""Trends Analysis Page"""
import streamlit as st
from ui import branding
from core import data_loader as loader
from core import analytics
import config
import pandas as pd

st.set_page_config(page_title="Trends", page_icon="📈", layout="wide")

branding.render_page_header("Trend Analysis", "📈")

st.info("🚧 Trend analysis coming soon. This page will show 7-day and 30-day trends.")

# Load data
try:
    df = loader.load_incidents()
    if df is not None and not df.empty:
        st.success(f"Analyzing trends for {len(df):,} incidents")
        
        # Simple time-based chart
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df_sorted = df.sort_values('timestamp')
            
            st.markdown("### Incident Timeline")
            st.line_chart(df_sorted.set_index('timestamp').resample('D').size())
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
