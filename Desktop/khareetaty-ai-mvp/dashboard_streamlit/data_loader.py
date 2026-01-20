"""
File-Based Data Loader for Streamlit-Only Mode
No Backend Required | Pure File-Based Analytics
"""

import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import streamlit as st
from typing import Optional, Dict, List, Tuple

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
GEO_DIR = DATA_DIR / "geo" / "kuwait"

@st.cache_data(ttl=300)
def load_incidents(limit: int = 10000) -> pd.DataFrame:
    """
    Load incidents from CSV file
    
    Returns:
        DataFrame with columns: timestamp, incident_type, lat, lon, 
        governorate, district, police_zone, block, description
    """
    incidents_file = DATA_DIR / "incidents.csv"
    
    if not incidents_file.exists():
        st.warning(f"⚠️ Incidents file not found: {incidents_file}")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(incidents_file)
        
        # Ensure required columns exist
        required_cols = ['timestamp', 'incident_type', 'lat', 'lon']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"❌ Missing required columns: {missing_cols}")
            return pd.DataFrame()
        
        # Parse timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Fill missing geographic fields
        for col in ['governorate', 'district', 'police_zone', 'block', 'description']:
            if col not in df.columns:
                df[col] = 'Unknown'
        
        # Sort by timestamp descending
        df = df.sort_values('timestamp', ascending=False)
        
        # Limit records
        if len(df) > limit:
            df = df.head(limit)
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error loading incidents: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_geojson(layer: str) -> Optional[Dict]:
    """
    Load GeoJSON file for a specific layer
    
    Args:
        layer: One of 'governorates', 'districts', 'blocks', 'police_zones'
    
    Returns:
        GeoJSON dict or None if not found
    """
    geojson_file = GEO_DIR / f"{layer}.geojson"
    
    if not geojson_file.exists():
        st.warning(f"⚠️ GeoJSON file not found: {geojson_file}")
        return None
    
    try:
        with open(geojson_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ Error loading GeoJSON {layer}: {e}")
        return None

@st.cache_data(ttl=600)
def get_geo_options() -> Dict[str, List[Dict]]:
    """
    Extract geographic options from GeoJSON files
    
    Returns:
        Dict with keys: governorates, districts, police_zones, blocks
    """
    options = {
        "governorates": [],
        "districts": [],
        "police_zones": [],
        "blocks": []
    }
    
    # Load governorates
    gov_geojson = load_geojson("governorates")
    if gov_geojson and "features" in gov_geojson:
        for feature in gov_geojson["features"]:
            props = feature.get("properties", {})
            options["governorates"].append({
                "name_en": props.get("name_en", props.get("name", "Unknown")),
                "name_ar": props.get("name_ar", ""),
                "code": props.get("code", "")
            })
    
    # Load districts
    dist_geojson = load_geojson("districts")
    if dist_geojson and "features" in dist_geojson:
        for feature in dist_geojson["features"]:
            props = feature.get("properties", {})
            options["districts"].append({
                "name_en": props.get("name_en", props.get("name", "Unknown")),
                "name_ar": props.get("name_ar", ""),
                "governorate_code": props.get("governorate_code", ""),
                "code": props.get("code", "")
            })
    
    # Load police zones
    police_geojson = load_geojson("police_zones")
    if police_geojson and "features" in police_geojson:
        for feature in police_geojson["features"]:
            props = feature.get("properties", {})
            options["police_zones"].append({
                "name_en": props.get("name_en", props.get("name", "Unknown")),
                "name_ar": props.get("name_ar", ""),
                "code": props.get("code", "")
            })
    
    # Load blocks
    blocks_geojson = load_geojson("blocks")
    if blocks_geojson and "features" in blocks_geojson:
        for feature in blocks_geojson["features"]:
            props = feature.get("properties", {})
            options["blocks"].append({
                "name_en": props.get("name_en", props.get("name", "Unknown")),
                "name_ar": props.get("name_ar", ""),
                "district_code": props.get("district_code", ""),
                "code": props.get("code", "")
            })
    
    return options

def filter_incidents(
    df: pd.DataFrame,
    governorate: Optional[str] = None,
    district: Optional[str] = None,
    police_zone: Optional[str] = None,
    block: Optional[str] = None
) -> pd.DataFrame:
    """
    Filter incidents DataFrame by geographic criteria
    
    Args:
        df: Incidents DataFrame
        governorate: Governorate name filter
        district: District name filter
        police_zone: Police zone name filter
        block: Block name filter
    
    Returns:
        Filtered DataFrame
    """
    filtered = df.copy()
    
    if governorate:
        filtered = filtered[filtered['governorate'] == governorate]
    
    if district:
        filtered = filtered[filtered['district'] == district]
    
    if police_zone:
        filtered = filtered[filtered['police_zone'] == police_zone]
    
    if block:
        filtered = filtered[filtered['block'] == block]
    
    return filtered

def get_data_freshness() -> Dict[str, str]:
    """
    Get data freshness information
    
    Returns:
        Dict with file modification times
    """
    freshness = {}
    
    incidents_file = DATA_DIR / "incidents.csv"
    if incidents_file.exists():
        mtime = datetime.fromtimestamp(incidents_file.stat().st_mtime)
        freshness["incidents"] = mtime.strftime("%Y-%m-%d %H:%M:%S")
    else:
        freshness["incidents"] = "Not available"
    
    for layer in ["governorates", "districts", "police_zones", "blocks"]:
        geojson_file = GEO_DIR / f"{layer}.geojson"
        if geojson_file.exists():
            mtime = datetime.fromtimestamp(geojson_file.stat().st_mtime)
            freshness[layer] = mtime.strftime("%Y-%m-%d %H:%M:%S")
        else:
            freshness[layer] = "Not available"
    
    return freshness

def get_data_quality_metrics(df: pd.DataFrame) -> Dict[str, any]:
    """
    Calculate data quality metrics
    
    Args:
        df: Incidents DataFrame
    
    Returns:
        Dict with quality metrics
    """
    if df.empty:
        return {
            "total_records": 0,
            "completeness": 0.0,
            "date_range": "N/A",
            "missing_coords": 0,
            "missing_geo": 0
        }
    
    total = len(df)
    
    # Check for missing coordinates
    missing_coords = df[['lat', 'lon']].isna().any(axis=1).sum()
    
    # Check for missing geographic info
    missing_geo = df[['governorate', 'district']].isna().any(axis=1).sum()
    
    # Date range
    if 'timestamp' in df.columns and not df['timestamp'].isna().all():
        min_date = df['timestamp'].min()
        max_date = df['timestamp'].max()
        date_range = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
    else:
        date_range = "N/A"
    
    # Completeness score
    completeness = ((total - missing_coords - missing_geo) / total * 100) if total > 0 else 0
    
    return {
        "total_records": total,
        "completeness": round(completeness, 1),
        "date_range": date_range,
        "missing_coords": missing_coords,
        "missing_geo": missing_geo
    }
