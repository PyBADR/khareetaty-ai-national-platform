"""
Khareetaty AI — Analytics Engine
Hotspot Detection, Trend Analysis, and Risk Assessment

Version: 5.0 (Phase-5 Kuwait National)
Architecture: Streamlit-Only | File-Based | No External Dependencies
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.cluster import DBSCAN
from collections import Counter

import config


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HOTSPOT DETECTION (DBSCAN CLUSTERING)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def detect_hotspots(
    df: pd.DataFrame,
    eps_km: float = 2.0,
    min_samples: int = 3
) -> pd.DataFrame:
    """
    Detect incident hotspots using DBSCAN clustering.
    
    Args:
        df: DataFrame with latitude, longitude columns
        eps_km: Maximum distance between points in a cluster (kilometers)
        min_samples: Minimum number of points to form a cluster
        
    Returns:
        DataFrame with cluster assignments and risk levels
    """
    if df.empty or len(df) < min_samples:
        df['cluster'] = -1
        df['risk_level'] = 'Low'
        return df
    
    # Prepare coordinates
    coords = df[['latitude', 'longitude']].values
    
    # Convert km to approximate degrees (rough approximation for Kuwait region)
    # 1 degree ≈ 111 km at equator, adjust for latitude ~29°
    eps_degrees = eps_km / (111 * np.cos(np.radians(29.3)))
    
    # Run DBSCAN
    clustering = DBSCAN(eps=eps_degrees, min_samples=min_samples, metric='euclidean')
    df['cluster'] = clustering.fit_predict(coords)
    
    # Calculate risk levels based on cluster size
    cluster_sizes = df[df['cluster'] != -1]['cluster'].value_counts()
    
    def assign_risk(row):
        if row['cluster'] == -1:
            return 'Low'
        size = cluster_sizes.get(row['cluster'], 0)
        if size >= 10:
            return 'High'
        elif size >= 5:
            return 'Medium'
        else:
            return 'Low'
    
    df['risk_level'] = df.apply(assign_risk, axis=1)
    
    return df


def get_hotspot_summary(df: pd.DataFrame) -> Dict:
    """
    Generate summary statistics for hotspots.
    
    Returns:
        Dictionary with hotspot metrics
    """
    if df.empty:
        return {
            'total_clusters': 0,
            'high_risk_zones': 0,
            'medium_risk_zones': 0,
            'low_risk_zones': 0,
            'isolated_incidents': 0
        }
    
    clusters = df[df['cluster'] != -1]
    isolated = df[df['cluster'] == -1]
    
    risk_counts = df['risk_level'].value_counts().to_dict()
    
    return {
        'total_clusters': len(clusters['cluster'].unique()) if not clusters.empty else 0,
        'high_risk_zones': risk_counts.get('High', 0),
        'medium_risk_zones': risk_counts.get('Medium', 0),
        'low_risk_zones': risk_counts.get('Low', 0),
        'isolated_incidents': len(isolated)
    }


def get_top_zones(df: pd.DataFrame, top_n: int = 5) -> List[Dict]:
    """
    Get top risk zones with details.
    
    Returns:
        List of zone dictionaries with cluster info
    """
    if df.empty or 'cluster' not in df.columns:
        return []
    
    clusters = df[df['cluster'] != -1].groupby('cluster').agg({
        'incident_id': 'count',
        'latitude': 'mean',
        'longitude': 'mean',
        'severity': lambda x: x.mode()[0] if len(x) > 0 else 'Unknown',
        'risk_level': lambda x: x.mode()[0] if len(x) > 0 else 'Low'
    }).reset_index()
    
    clusters.columns = ['cluster', 'incident_count', 'lat', 'lon', 'severity', 'risk_level']
    clusters = clusters.sort_values('incident_count', ascending=False).head(top_n)
    
    zones = []
    for _, row in clusters.iterrows():
        zones.append({
            'zone_id': f"ZONE-{int(row['cluster']):03d}",
            'incident_count': int(row['incident_count']),
            'center_lat': float(row['lat']),
            'center_lon': float(row['lon']),
            'severity': row['severity'],
            'risk_level': row['risk_level']
        })
    
    return zones


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TREND ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze_trends(
    df: pd.DataFrame,
    days_7: bool = True,
    days_30: bool = True
) -> Dict:
    """
    Analyze incident trends over time periods.
    
    Args:
        df: DataFrame with timestamp column
        days_7: Include 7-day analysis
        days_30: Include 30-day analysis
        
    Returns:
        Dictionary with trend metrics
    """
    if df.empty or 'timestamp' not in df.columns:
        return {
            'last_7_days': {'total': 0, 'daily_avg': 0, 'trend': 'stable'},
            'last_30_days': {'total': 0, 'daily_avg': 0, 'trend': 'stable'}
        }
    
    # Ensure timestamp is datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    now = datetime.now()
    
    results = {}
    
    if days_7:
        df_7d = df[df['timestamp'] >= (now - timedelta(days=7))]
        total_7d = len(df_7d)
        avg_7d = total_7d / 7
        
        # Calculate trend (compare first half vs second half)
        mid_point = now - timedelta(days=3.5)
        first_half = len(df_7d[df_7d['timestamp'] < mid_point])
        second_half = len(df_7d[df_7d['timestamp'] >= mid_point])
        
        if first_half == 0:
            trend_7d = 'stable'
        else:
            change = ((second_half - first_half) / first_half) * 100
            if change > 20:
                trend_7d = 'increasing'
            elif change < -20:
                trend_7d = 'decreasing'
            else:
                trend_7d = 'stable'
        
        results['last_7_days'] = {
            'total': total_7d,
            'daily_avg': round(avg_7d, 1),
            'trend': trend_7d,
            'change_pct': round(change, 1) if first_half > 0 else 0
        }
    
    if days_30:
        df_30d = df[df['timestamp'] >= (now - timedelta(days=30))]
        total_30d = len(df_30d)
        avg_30d = total_30d / 30
        
        # Calculate trend
        mid_point = now - timedelta(days=15)
        first_half = len(df_30d[df_30d['timestamp'] < mid_point])
        second_half = len(df_30d[df_30d['timestamp'] >= mid_point])
        
        if first_half == 0:
            trend_30d = 'stable'
        else:
            change = ((second_half - first_half) / first_half) * 100
            if change > 20:
                trend_30d = 'increasing'
            elif change < -20:
                trend_30d = 'decreasing'
            else:
                trend_30d = 'stable'
        
        results['last_30_days'] = {
            'total': total_30d,
            'daily_avg': round(avg_30d, 1),
            'trend': trend_30d,
            'change_pct': round(change, 1) if first_half > 0 else 0
        }
    
    return results


def get_category_breakdown(df: pd.DataFrame) -> Dict[str, int]:
    """
    Get incident counts by category.
    
    Returns:
        Dictionary mapping category to count
    """
    if df.empty or 'category' not in df.columns:
        return {}
    
    return df['category'].value_counts().to_dict()


def get_severity_breakdown(df: pd.DataFrame) -> Dict[str, int]:
    """
    Get incident counts by severity.
    
    Returns:
        Dictionary mapping severity to count
    """
    if df.empty or 'severity' not in df.columns:
        return {}
    
    return df['severity'].value_counts().to_dict()


def get_hourly_pattern(df: pd.DataFrame) -> Dict[int, int]:
    """
    Get incident counts by hour of day.
    
    Returns:
        Dictionary mapping hour (0-23) to count
    """
    if df.empty or 'timestamp' not in df.columns:
        return {}
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    
    return df['hour'].value_counts().sort_index().to_dict()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ALERT GENERATION (SIMULATED - NO SMS)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_simulated_alerts(df: pd.DataFrame, threshold: str = 'High') -> List[Dict]:
    """
    Generate simulated alert messages for high-priority incidents.
    
    NOTE: This is SIMULATION ONLY for Phase-5.
    Real SMS/OTP workflows are deferred to Phase-2 to preserve
    Streamlit-only architecture and national security boundaries.
    
    Args:
        df: DataFrame with incidents
        threshold: Severity threshold ('High', 'Medium', 'Low')
        
    Returns:
        List of alert dictionaries
    """
    if df.empty:
        return []
    
    # Filter by severity
    severity_order = {'High': 3, 'Medium': 2, 'Low': 1}
    min_severity = severity_order.get(threshold, 3)
    
    alerts_df = df[df['severity'].map(lambda x: severity_order.get(x, 0)) >= min_severity]
    
    alerts = []
    for _, row in alerts_df.head(10).iterrows():  # Limit to 10 most recent
        alert = {
            'alert_id': f"ALERT-{row['incident_id']}",
            'incident_id': row['incident_id'],
            'timestamp': row['timestamp'],
            'severity': row['severity'],
            'category': row['category'],
            'location': f"({row['latitude']:.4f}, {row['longitude']:.4f})",
            'message': f"[{row['severity']}] {row['category']} incident at {row['description'][:50]}",
            'status': 'SIMULATED',
            'recipient': '+965 6663 3387 (Executive Contact)'
        }
        alerts.append(alert)
    
    return alerts


def get_alert_summary(alerts: List[Dict]) -> Dict:
    """
    Generate summary statistics for alerts.
    
    Returns:
        Dictionary with alert metrics
    """
    if not alerts:
        return {
            'total_alerts': 0,
            'high_priority': 0,
            'medium_priority': 0,
            'low_priority': 0
        }
    
    severity_counts = Counter([a['severity'] for a in alerts])
    
    return {
        'total_alerts': len(alerts),
        'high_priority': severity_counts.get('High', 0),
        'medium_priority': severity_counts.get('Medium', 0),
        'low_priority': severity_counts.get('Low', 0)
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPREHENSIVE ANALYTICS REPORT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_comprehensive_report(df: pd.DataFrame) -> Dict:
    """
    Generate a comprehensive analytics report.
    
    Returns:
        Dictionary with all analytics metrics
    """
    if df.empty:
        return {
            'status': 'no_data',
            'message': 'No incident data available for analysis'
        }
    
    # Run all analytics
    df_with_clusters = detect_hotspots(df)
    hotspot_summary = get_hotspot_summary(df_with_clusters)
    top_zones = get_top_zones(df_with_clusters)
    trends = analyze_trends(df)
    category_breakdown = get_category_breakdown(df)
    severity_breakdown = get_severity_breakdown(df)
    hourly_pattern = get_hourly_pattern(df)
    alerts = generate_simulated_alerts(df)
    alert_summary = get_alert_summary(alerts)
    
    return {
        'status': 'success',
        'total_incidents': len(df),
        'hotspots': hotspot_summary,
        'top_zones': top_zones,
        'trends': trends,
        'category_breakdown': category_breakdown,
        'severity_breakdown': severity_breakdown,
        'hourly_pattern': hourly_pattern,
        'alerts': alerts,
        'alert_summary': alert_summary,
        'data_with_clusters': df_with_clusters
    }
