"""
Khareetaty AI — Data Loader Module
Handles loading of CSV and GeoJSON data with caching
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
import config

@st.cache_data(ttl=config.CACHE_TTL)
def load_incidents():
    """
    Load incidents data from CSV file.
    Returns None if file doesn't exist or is empty.
    """
    try:
        if not config.INCIDENTS_FILE.exists():
            st.warning(f"Data file not found: {config.INCIDENTS_FILE}")
            return None
        
        df = pd.read_csv(config.INCIDENTS_FILE)
        
        if df.empty:
            st.warning("Data file is empty")
            return None
        
        # Parse timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Ensure numeric lat/lon
        if 'lat' in df.columns:
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        if 'lon' in df.columns:
            df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        
        return df
    
    except Exception as e:
        st.error(f"Error loading incidents data: {str(e)}")
        return None

@st.cache_data(ttl=config.CACHE_TTL)
def load_geo_layers():
    """
    Load all GeoJSON layers.
    Returns dictionary of layer_name: geojson_data
    """
    layers = {}
    
    geo_files = {
        'governorates': config.GEO_GOVERNORATES,
        'districts': config.GEO_DISTRICTS,
        'police_zones': config.GEO_POLICE_ZONES
    }
    
    for name, filepath in geo_files.items():
        try:
            if filepath.exists():
                with open(filepath, 'r') as f:
                    layers[name] = json.load(f)
        except Exception as e:
            st.warning(f"Could not load {name} layer: {str(e)}")
    
    return layers if layers else None

@st.cache_data(ttl=config.CACHE_TTL)
def load_governorate_geojson():
    """Load governorate boundaries"""
    try:
        if config.GEO_GOVERNORATES.exists():
            with open(config.GEO_GOVERNORATES, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.warning(f"Could not load governorate boundaries: {str(e)}")
    return None

def get_data_summary(df):
    """
    Get summary statistics for the dataset.
    """
    if df is None or df.empty:
        return None
    
    summary = {
        'total_records': len(df),
        'date_range': {
            'start': df['timestamp'].min() if 'timestamp' in df.columns else None,
            'end': df['timestamp'].max() if 'timestamp' in df.columns else None
        },
        'governorates': df['governorate'].nunique() if 'governorate' in df.columns else 0,
        'incident_types': df['incident_type'].nunique() if 'incident_type' in df.columns else 0,
        'columns': list(df.columns),
        'missing_values': df.isnull().sum().to_dict()
    }
    
    return summary