"""Alerts Page (Simulated)"""
import streamlit as st
from ui import branding, phone_auth
from core import data_loader as loader
import config

st.set_page_config(page_title="Alerts", page_icon="🚨", layout="wide")

branding.render_page_header("Alert System (Simulated)", "🚨")

st.warning("⚠️ This is a SIMULATED alert system. No actual SMS/OTP functionality is implemented in Phase-5.")

st.markdown("### Alert Configuration")
st.markdown(f"**Primary Contact:** {phone_auth.NATIONAL_CONTACT}")
st.markdown(f"**Owner:** {phone_auth.EXECUTIVE_OWNER}")
st.markdown(f"**Status:** {phone_auth.STATUS}")

st.markdown("---")

st.markdown("### Simulated Alert Log")
st.info("Live SMS alerts will be implemented in Phase-2 with proper OTP/SMS gateway integration.")

# Placeholder alert log
alert_data = [
    {"timestamp": "2026-01-17 10:30", "type": "High Risk Zone", "message": "Cluster detected in Capital governorate", "status": "Simulated"},
    {"timestamp": "2026-01-17 09:15", "type": "Trend Alert", "message": "30% increase in incidents", "status": "Simulated"},
    {"timestamp": "2026-01-17 08:00", "type": "System", "message": "Daily report generated", "status": "Simulated"},
]

import pandas as pd
st.dataframe(pd.DataFrame(alert_data), use_container_width=True)
