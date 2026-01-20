"""
Khareetaty-AI National Intelligence Dashboard
Streamlit-Only | File-Based Analytics | No Backend Required

Version: 1.0 (Standalone)
Last Updated: 2026-01-17
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dashboard_streamlit.data_loader import (
    load_incidents, load_geojson, get_geo_options, filter_incidents,
    get_data_freshness, get_data_quality_metrics
)
from dashboard_streamlit.analytics import (
    calculate_hotspots, calculate_trends, calculate_summary_stats,
    calculate_time_distribution, calculate_risk_score
)
from dashboard_streamlit.validators import validate_all_data

# Page configuration
st.set_page_config(
    page_title="Khareetaty-AI National Intelligence",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .architecture-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1.5rem;
        font-size: 1.1rem;
    }
    .kpi-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .kpi-label {
        font-size: 1rem;
        color: #666;
    }
    .quality-indicator {
        background-color: #e8f4f8;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.3rem;
    }
    .executive-summary {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 0.3rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🚨 Khareetaty AI - National Intelligence Platform</div>', unsafe_allow_html=True)

# Architecture Banner
st.markdown("""
    <div class="architecture-banner">
        📊 Streamlit-Only | 📁 File-Based Analytics | ⚡ No Backend Required | 🇰🇼 Kuwait National Intelligence
    </div>
""", unsafe_allow_html=True)

# Load data
with st.spinner('🔄 Loading intelligence data...'):
    df_incidents = load_incidents(limit=10000)
    geo_options = get_geo_options()
    data_freshness = get_data_freshness()

# Executive Summary Section
if not df_incidents.empty:
    st.markdown('<div class="executive-summary">', unsafe_allow_html=True)
    st.markdown("### 🎯 Executive Intelligence Summary")
    
    summary_stats = calculate_summary_stats(df_incidents)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📈 What is happening?**")
        st.write(f"- {summary_stats['total_incidents']:,} total incidents recorded")
        st.write(f"- {summary_stats['incidents_24h']} incidents in last 24 hours")
        st.write(f"- {summary_stats['avg_daily']} average daily incidents")
    
    with col2:
        st.markdown("**⚠️ Why it matters?**")
        st.write(f"- Primary threat: {summary_stats['top_incident_type']}")
        st.write(f"- Highest risk zone: {summary_stats['top_district']}")
        st.write(f"- Trend: {'Increasing' if summary_stats['incidents_24h'] > summary_stats['avg_daily'] else 'Stable'}")
    
    with col3:
        st.markdown("**🎯 Recommended Actions**")
        if summary_stats['incidents_24h'] > summary_stats['avg_daily'] * 1.5:
            st.write("⚠️ Increase patrol presence")
            st.write("🚨 Activate rapid response teams")
        else:
            st.write("✅ Maintain current operations")
            st.write("🔍 Continue monitoring hotspots")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Data Quality Insurance Panel
with st.expander("🛡️ Data Quality & Governance", expanded=False):
    st.markdown("### Insurance-Grade Quality Indicators")
    
    quality_metrics = get_data_quality_metrics(df_incidents)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", f"{quality_metrics['total_records']:,}")
    
    with col2:
        completeness = quality_metrics['completeness']
        st.metric("Data Completeness", f"{completeness}%", 
                 delta="Excellent" if completeness > 90 else "Good" if completeness > 70 else "Fair")
    
    with col3:
        st.metric("Missing Coordinates", quality_metrics['missing_coords'])
    
    with col4:
        st.metric("Missing Geography", quality_metrics['missing_geo'])
    
    st.markdown("---")
    
    st.markdown("**📅 Data Freshness**")
    freshness_col1, freshness_col2 = st.columns(2)
    
    with freshness_col1:
        st.write(f"**Incidents Data:** {data_freshness.get('incidents', 'Unknown')}")
    
    with freshness_col2:
        st.write(f"**Date Range:** {quality_metrics['date_range']}")
    
    st.markdown("---")
    
    st.markdown("**⚠️ Known Limitations**")
    st.write("• Data is file-based and requires manual updates")
    st.write("• Hotspot calculations use DBSCAN clustering (0.5km radius, min 5 incidents)")
    st.write("• Forecasts are simple trend projections (not ML-based predictions)")
    st.write("• Real-time alerting is not available in standalone mode")
    
    st.markdown("---")
    
    st.markdown("**📊 Confidence Levels**")
    st.write("• Geographic accuracy: High (based on GPS coordinates)")
    st.write("• Hotspot detection: Medium-High (statistical clustering)")
    st.write("• Trend analysis: Medium (historical patterns)")
    st.write("• Risk scoring: Medium (simplified algorithm)")

# Sidebar - Geographic Filters
st.sidebar.title("🔍 Geographic Filters")

if geo_options:
    # Governorate filter
    governorates = ["All"] + sorted([g["name_en"] for g in geo_options.get("governorates", [])])
    selected_governorate = st.sidebar.selectbox("Governorate", governorates, key="gov_filter")
    
    # District filter
    districts = ["All"]
    if selected_governorate != "All":
        # Filter districts by governorate (simplified - would need governorate_code matching)
        districts.extend(sorted([d["name_en"] for d in geo_options.get("districts", [])]))
    else:
        districts.extend(sorted([d["name_en"] for d in geo_options.get("districts", [])]))
    
    selected_district = st.sidebar.selectbox("District", districts, key="dist_filter")
    
    # Police Zone filter
    police_zones = ["All"] + sorted([z["name_en"] for z in geo_options.get("police_zones", [])])
    selected_police_zone = st.sidebar.selectbox("Police Zone", police_zones, key="police_filter")
else:
    st.sidebar.warning("⚠️ Geographic data not available")
    selected_governorate = "All"
    selected_district = "All"
    selected_police_zone = "All"

# Convert "All" to None for filtering
gov_filter = None if selected_governorate == "All" else selected_governorate
dist_filter = None if selected_district == "All" else selected_district
police_filter = None if selected_police_zone == "All" else selected_police_zone

st.sidebar.markdown("---")

# System Information
st.sidebar.title("📊 System Status")
st.sidebar.success("✅ System Operational")

if not df_incidents.empty:
    st.sidebar.metric("📋 Total Incidents", f"{len(df_incidents):,}")
    st.sidebar.metric("🔥 Last 24h", calculate_summary_stats(df_incidents)['incidents_24h'])
    st.sidebar.metric("📅 Last 7d", calculate_summary_stats(df_incidents)['incidents_7d'])

st.sidebar.markdown("---")
st.sidebar.markdown("**💾 Data Source:** Local Files")
st.sidebar.markdown("**🔄 Last Refresh:** " + datetime.now().strftime("%H:%M:%S"))

# Filter incidents
df_filtered = filter_incidents(df_incidents, gov_filter, dist_filter, police_filter)

# Main Dashboard Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Map View", "🔥 Hotspots", "📈 Trends", "📊 Analytics"])

# TAB 1: Map View
with tab1:
    st.header("🗺️ Geographic Intelligence Map")
    
    if not df_filtered.empty:
        # Calculate hotspots for overlay
        hotspots = calculate_hotspots(df_filtered, eps_km=0.5, min_samples=5)
        
        # Create map
        df_filtered['marker_size'] = 8
        
        fig = px.scatter_mapbox(
            df_filtered.head(1000),  # Limit for performance
            lat="lat",
            lon="lon",
            color="incident_type",
            size="marker_size",
            hover_data=["district", "police_zone", "timestamp"],
            zoom=10,
            height=650,
            title=f"Incident Map ({len(df_filtered):,} incidents)"
        )
        
        # Add hotspot overlays
        if hotspots:
            for hotspot in hotspots[:10]:  # Top 10 hotspots
                fig.add_scattermapbox(
                    lat=[hotspot["lat"]],
                    lon=[hotspot["lon"]],
                    mode="markers",
                    marker=dict(size=hotspot["score"]/2, color="red", opacity=0.6),
                    name=f"Hotspot: {hotspot['zone']} (Score: {hotspot['score']})",
                    showlegend=False
                )
        
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Incident breakdown
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📊 By Type")
            type_counts = df_filtered["incident_type"].value_counts().head(5)
            fig_pie = px.pie(values=type_counts.values, names=type_counts.index)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("🏛️ By District")
            district_counts = df_filtered["district"].value_counts().head(10)
            fig_bar = px.bar(x=district_counts.index, y=district_counts.values)
            fig_bar.update_layout(xaxis_title="District", yaxis_title="Count")
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col3:
            st.subheader("⏰ By Hour")
            time_dist = calculate_time_distribution(df_filtered)
            hourly_data = pd.DataFrame(time_dist['hourly'])
            fig_hour = px.line(hourly_data, x="hour", y="count")
            fig_hour.update_layout(xaxis_title="Hour of Day", yaxis_title="Incidents")
            st.plotly_chart(fig_hour, use_container_width=True)
    else:
        st.info("📊 No incidents found for selected filters")

# TAB 2: Hotspots
with tab2:
    st.header("🔥 Active Hotspots Analysis")
    
    if not df_filtered.empty:
        hotspots = calculate_hotspots(df_filtered, eps_km=0.5, min_samples=5)
        
        if hotspots:
            # KPI Cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{len(hotspots)}</div><div class='kpi-label'>Total Hotspots</div></div>", unsafe_allow_html=True)
            
            with col2:
                most_dangerous = hotspots[0]['district'] if hotspots else "N/A"
                st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{most_dangerous}</div><div class='kpi-label'>Highest Risk Zone</div></div>", unsafe_allow_html=True)
            
            with col3:
                total_forecast = sum(h['forecast'] for h in hotspots)
                st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{total_forecast}</div><div class='kpi-label'>24h Forecast</div></div>", unsafe_allow_html=True)
            
            with col4:
                max_score = hotspots[0]['score'] if hotspots else 0
                st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{max_score}</div><div class='kpi-label'>Max Hotspot Score</div></div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Narrative annotation
            st.markdown("**📝 Intelligence Assessment:**")
            if len(hotspots) > 5:
                st.warning(f"⚠️ High concentration of {len(hotspots)} hotspots detected. Recommend increased patrol allocation.")
            else:
                st.info(f"ℹ️ {len(hotspots)} hotspots identified. Situation within normal parameters.")
            
            # Hotspot table
            st.subheader("📋 Hotspot Details")
            
            df_hotspots = pd.DataFrame(hotspots)
            display_df = df_hotspots[["zone", "governorate", "district", "police_zone", "score", "forecast", "last_seen"]]
            display_df = display_df.sort_values("score", ascending=False)
            
            st.dataframe(display_df, use_container_width=True, height=400)
            
            # Methodology explanation
            with st.expander("🔍 How are hotspots calculated?"):
                st.markdown("""
                **Methodology: DBSCAN Clustering**
                
                1. **Algorithm:** Density-Based Spatial Clustering (DBSCAN)
                2. **Parameters:** 
                   - Radius: 0.5 km
                   - Minimum incidents: 5
                3. **Process:**
                   - Groups incidents within 0.5km of each other
                   - Requires at least 5 incidents to form a hotspot
                   - Calculates center point and risk score
                4. **Score:** Number of incidents in cluster
                5. **Forecast:** Recent trend × 1.2 (simple projection)
                
                **Confidence Level:** Medium-High (statistical method)
                """)
        else:
            st.info("📊 No hotspots detected with current parameters (min 5 incidents within 0.5km)")
    else:
        st.info("📊 No incidents available for hotspot analysis")

# TAB 3: Trends
with tab3:
    st.header("📈 Trend Analysis")
    
    if not df_filtered.empty:
        # Time range selector
        col1, col2 = st.columns([1, 3])
        
        with col1:
            time_range = st.selectbox("Time Range", ["7 days", "30 days", "90 days"])
            days = int(time_range.split()[0])
        
        with col2:
            zone_type = st.selectbox("Zone Type", ["district", "governorate", "police_zone"])
        
        # Calculate trends
        trends = calculate_trends(df_filtered, zone_type, days)
        
        if trends:
            df_trends = pd.DataFrame(trends)
            
            # Narrative annotation
            st.markdown("**📝 Trend Assessment:**")
            recent_total = df_filtered[df_filtered['timestamp'] > (datetime.now() - timedelta(days=7))].shape[0]
            older_total = df_filtered[
                (df_filtered['timestamp'] > (datetime.now() - timedelta(days=14))) &
                (df_filtered['timestamp'] <= (datetime.now() - timedelta(days=7)))
            ].shape[0]
            
            if recent_total > older_total * 1.2:
                st.warning("⚠️ Incidents increasing. Trend shows 20%+ growth in recent period.")
            elif recent_total < older_total * 0.8:
                st.success("✅ Incidents decreasing. Trend shows 20%+ reduction in recent period.")
            else:
                st.info("ℹ️ Incidents stable. No significant trend change detected.")
            
            # Line chart
            fig_line = px.line(
                df_trends,
                x="date",
                y="count",
                color="zone",
                title=f"Incidents Over Time by {zone_type.title()}",
                labels={"count": "Incident Count", "date": "Date"}
            )
            st.plotly_chart(fig_line, use_container_width=True)
            
            # Stacked area chart
            pivot_df = df_trends.pivot(index="date", columns="zone", values="count").fillna(0)
            
            fig_area = go.Figure()
            for zone in pivot_df.columns:
                fig_area.add_trace(go.Scatter(
                    x=pivot_df.index,
                    y=pivot_df[zone],
                    mode="lines",
                    stackgroup="one",
                    name=zone
                ))
            
            fig_area.update_layout(
                title=f"Stacked Incidents by {zone_type.title()}",
                xaxis_title="Date",
                yaxis_title="Incident Count"
            )
            st.plotly_chart(fig_area, use_container_width=True)
        else:
            st.info("📊 No trend data available for selected period")
    else:
        st.info("📊 No incidents available for trend analysis")

# TAB 4: Analytics
with tab4:
    st.header("📊 Advanced Analytics")
    
    if not df_incidents.empty:
        # Summary statistics
        summary = calculate_summary_stats(df_incidents)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Incidents", f"{summary['total_incidents']:,}")
            st.metric("Last 24 Hours", summary['incidents_24h'])
        
        with col2:
            st.metric("Last 7 Days", summary['incidents_7d'])
            st.metric("Daily Average", summary['avg_daily'])
        
        with col3:
            st.metric("Top Incident Type", summary['top_incident_type'])
            st.metric("Top District", summary['top_district'])
        
        st.markdown("---")
        
        # Time distribution
        st.subheader("⏰ Temporal Patterns")
        
        time_dist = calculate_time_distribution(df_incidents)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Hourly Distribution**")
            hourly_df = pd.DataFrame(time_dist['hourly'])
            fig_hourly = px.bar(hourly_df, x="hour", y="count")
            fig_hourly.update_layout(xaxis_title="Hour of Day", yaxis_title="Incidents")
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        with col2:
            st.markdown("**Daily Distribution**")
            daily_df = pd.DataFrame(time_dist['daily'])
            fig_daily = px.bar(daily_df, x="day", y="count")
            fig_daily.update_layout(xaxis_title="Day of Week", yaxis_title="Incidents")
            st.plotly_chart(fig_daily, use_container_width=True)
        
        st.markdown("---")
        
        # Data validation results
        st.subheader("🛡️ Data Validation Report")
        
        with st.spinner("Running validation checks..."):
            validation_results = validate_all_data()
        
        for data_type, results in validation_results.items():
            with st.expander(f"📄 {data_type.title()}", expanded=False):
                if results['valid']:
                    st.success(f"✅ {data_type.title()} data is valid")
                else:
                    st.error(f"❌ {data_type.title()} data has issues")
                
                if results.get('errors'):
                    st.markdown("**Issues:**")
                    for error in results['errors']:
                        st.write(f"- {error}")
                
                if 'record_count' in results:
                    st.metric("Records", f"{results['record_count']:,}")
                
                if 'feature_count' in results:
                    st.metric("Features", results['feature_count'])
                
                if 'freshness' in results:
                    freshness = results['freshness']
                    st.write(f"**Last Modified:** {freshness.get('last_modified', 'Unknown')}")
                    st.write(f"**Status:** {freshness.get('message', 'Unknown')}")
    else:
        st.warning("⚠️ No data available for analytics")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <strong>Khareetaty-AI v1.0 Standalone</strong> | 
        Streamlit-Only | File-Based Analytics | No Backend Required<br>
        🇰🇼 National Intelligence Platform | © 2026
    </div>
""", unsafe_allow_html=True)
