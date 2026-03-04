"""
Local Analytics Engine for Streamlit-Only Mode
Calculates hotspots, trends, and forecasts without backend
"""

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from datetime import datetime, timedelta
import streamlit as st
from typing import List, Dict, Tuple

@st.cache_data(ttl=300)
def calculate_hotspots(
    df: pd.DataFrame,
    eps_km: float = 0.5,
    min_samples: int = 5
) -> List[Dict]:
    """
    Calculate crime hotspots using DBSCAN clustering
    
    Args:
        df: Incidents DataFrame with lat, lon columns
        eps_km: Maximum distance between points in km (default 0.5km)
        min_samples: Minimum points to form a cluster
    
    Returns:
        List of hotspot dicts with location, score, zone info
    """
    if df.empty or len(df) < min_samples:
        return []
    
    # Filter valid coordinates
    valid_df = df.dropna(subset=['lat', 'lon'])
    
    if len(valid_df) < min_samples:
        return []
    
    try:
        # Prepare coordinates (lat, lon)
        coords = valid_df[['lat', 'lon']].values
        
        # Convert km to degrees (approximate: 1 degree ≈ 111 km)
        eps_degrees = eps_km / 111.0
        
        # Run DBSCAN clustering
        clustering = DBSCAN(eps=eps_degrees, min_samples=min_samples, metric='euclidean')
        valid_df = valid_df.copy()
        valid_df['cluster'] = clustering.fit_predict(coords)
        
        # Extract hotspots (exclude noise points with cluster=-1)
        hotspots = []
        
        for cluster_id in valid_df['cluster'].unique():
            if cluster_id == -1:  # Skip noise
                continue
            
            cluster_data = valid_df[valid_df['cluster'] == cluster_id]
            
            # Calculate hotspot center
            center_lat = cluster_data['lat'].mean()
            center_lon = cluster_data['lon'].mean()
            
            # Calculate score (number of incidents in cluster)
            score = len(cluster_data)
            
            # Get most common zone info
            governorate = cluster_data['governorate'].mode()[0] if 'governorate' in cluster_data.columns and not cluster_data['governorate'].empty else 'Unknown'
            district = cluster_data['district'].mode()[0] if 'district' in cluster_data.columns and not cluster_data['district'].empty else 'Unknown'
            police_zone = cluster_data['police_zone'].mode()[0] if 'police_zone' in cluster_data.columns and not cluster_data['police_zone'].empty else 'Unknown'
            
            # Get most common incident type
            incident_type = cluster_data['incident_type'].mode()[0] if not cluster_data['incident_type'].empty else 'Unknown'
            
            # Calculate forecast (simple: recent trend * 1.2)
            recent_incidents = cluster_data[cluster_data['timestamp'] > (datetime.now() - timedelta(days=7))]
            forecast = int(len(recent_incidents) * 1.2)
            
            # Last seen
            last_seen = cluster_data['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S') if 'timestamp' in cluster_data.columns else 'Unknown'
            
            hotspots.append({
                'cluster_id': int(cluster_id),
                'lat': float(center_lat),
                'lon': float(center_lon),
                'score': int(score),
                'forecast': forecast,
                'governorate': governorate,
                'district': district,
                'police_zone': police_zone,
                'zone': f"{district}, {governorate}",
                'incident_type': incident_type,
                'last_seen': last_seen
            })
        
        # Sort by score descending
        hotspots.sort(key=lambda x: x['score'], reverse=True)
        
        return hotspots
    
    except Exception as e:
        st.error(f"❌ Error calculating hotspots: {e}")
        return []

@st.cache_data(ttl=300)
def calculate_trends(
    df: pd.DataFrame,
    zone_type: str = 'district',
    days: int = 30
) -> List[Dict]:
    """
    Calculate incident trends by zone over time
    
    Args:
        df: Incidents DataFrame
        zone_type: 'district', 'governorate', or 'police_zone'
        days: Number of days to analyze
    
    Returns:
        List of trend dicts with date, zone, count
    """
    if df.empty:
        return []
    
    try:
        # Filter to date range
        cutoff_date = datetime.now() - timedelta(days=days)
        df_filtered = df[df['timestamp'] >= cutoff_date].copy()
        
        if df_filtered.empty:
            return []
        
        # Ensure zone_type column exists
        if zone_type not in df_filtered.columns:
            st.warning(f"⚠️ Column '{zone_type}' not found in data")
            return []
        
        # Extract date
        df_filtered['date'] = df_filtered['timestamp'].dt.date
        
        # Group by date and zone
        trends = df_filtered.groupby(['date', zone_type]).size().reset_index(name='count')
        trends.columns = ['date', 'zone', 'count']
        
        # Convert to list of dicts
        return trends.to_dict('records')
    
    except Exception as e:
        st.error(f"❌ Error calculating trends: {e}")
        return []

def calculate_summary_stats(df: pd.DataFrame) -> Dict:
    """
    Calculate summary statistics for incidents
    
    Args:
        df: Incidents DataFrame
    
    Returns:
        Dict with summary statistics
    """
    if df.empty:
        return {
            'total_incidents': 0,
            'incidents_24h': 0,
            'incidents_7d': 0,
            'top_incident_type': 'N/A',
            'top_district': 'N/A',
            'avg_daily': 0
        }
    
    now = datetime.now()
    
    # Total incidents
    total = len(df)
    
    # Last 24 hours
    incidents_24h = len(df[df['timestamp'] > (now - timedelta(hours=24))])
    
    # Last 7 days
    incidents_7d = len(df[df['timestamp'] > (now - timedelta(days=7))])
    
    # Top incident type
    top_type = df['incident_type'].mode()[0] if not df['incident_type'].empty else 'N/A'
    
    # Top district
    top_district = df['district'].mode()[0] if 'district' in df.columns and not df['district'].empty else 'N/A'
    
    # Average daily incidents (last 30 days)
    df_30d = df[df['timestamp'] > (now - timedelta(days=30))]
    avg_daily = len(df_30d) / 30 if not df_30d.empty else 0
    
    return {
        'total_incidents': total,
        'incidents_24h': incidents_24h,
        'incidents_7d': incidents_7d,
        'top_incident_type': top_type,
        'top_district': top_district,
        'avg_daily': round(avg_daily, 1)
    }

def calculate_time_distribution(df: pd.DataFrame) -> Dict[str, List]:
    """
    Calculate incident distribution by time of day and day of week
    
    Args:
        df: Incidents DataFrame
    
    Returns:
        Dict with hourly and daily distributions
    """
    if df.empty or 'timestamp' not in df.columns:
        return {'hourly': [], 'daily': []}
    
    df = df.copy()
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.day_name()
    
    # Hourly distribution
    hourly = df['hour'].value_counts().sort_index().to_dict()
    hourly_list = [{'hour': h, 'count': hourly.get(h, 0)} for h in range(24)]
    
    # Daily distribution
    daily = df['day_of_week'].value_counts().to_dict()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_list = [{'day': d, 'count': daily.get(d, 0)} for d in day_order]
    
    return {
        'hourly': hourly_list,
        'daily': daily_list
    }

def calculate_risk_score(df: pd.DataFrame, zone: str, zone_type: str = 'district') -> float:
    """
    Calculate risk score for a specific zone
    
    Args:
        df: Incidents DataFrame
        zone: Zone name
        zone_type: Type of zone (district, governorate, police_zone)
    
    Returns:
        Risk score (0-100)
    """
    if df.empty or zone_type not in df.columns:
        return 0.0
    
    # Filter to zone
    zone_df = df[df[zone_type] == zone]
    
    if zone_df.empty:
        return 0.0
    
    # Calculate factors
    now = datetime.now()
    
    # Recent incidents (last 7 days)
    recent = len(zone_df[zone_df['timestamp'] > (now - timedelta(days=7))])
    
    # Incident density (incidents per day)
    days_span = (zone_df['timestamp'].max() - zone_df['timestamp'].min()).days + 1
    density = len(zone_df) / days_span if days_span > 0 else 0
    
    # Severity (based on incident types - simplified)
    severity_weights = {
        'assault': 3,
        'robbery': 3,
        'burglary': 2,
        'theft': 2,
        'vandalism': 1,
        'other': 1
    }
    
    avg_severity = zone_df['incident_type'].map(
        lambda x: severity_weights.get(x.lower(), 1)
    ).mean()
    
    # Calculate risk score (0-100)
    risk_score = min(100, (recent * 2) + (density * 10) + (avg_severity * 5))
    
    return round(risk_score, 1)
