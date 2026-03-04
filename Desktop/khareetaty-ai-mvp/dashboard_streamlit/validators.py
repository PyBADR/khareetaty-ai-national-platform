"""
Data Validators for Streamlit-Only Mode
Ensures data quality and integrity
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple
import streamlit as st

def validate_csv_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate incidents CSV schema
    
    Args:
        df: DataFrame to validate
    
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    # Required columns
    required_columns = ['timestamp', 'incident_type', 'lat', 'lon']
    
    for col in required_columns:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
    
    if errors:
        return False, errors
    
    # Validate data types
    try:
        pd.to_datetime(df['timestamp'], errors='coerce')
    except Exception as e:
        errors.append(f"Invalid timestamp format: {e}")
    
    # Validate coordinates
    if not pd.api.types.is_numeric_dtype(df['lat']):
        errors.append("Latitude must be numeric")
    
    if not pd.api.types.is_numeric_dtype(df['lon']):
        errors.append("Longitude must be numeric")
    
    # Validate coordinate ranges (Kuwait bounds)
    if 'lat' in df.columns and pd.api.types.is_numeric_dtype(df['lat']):
        invalid_lat = df[(df['lat'] < 28.5) | (df['lat'] > 30.5)]
        if len(invalid_lat) > 0:
            errors.append(f"Warning: {len(invalid_lat)} records with latitude outside Kuwait bounds (28.5-30.5)")
    
    if 'lon' in df.columns and pd.api.types.is_numeric_dtype(df['lon']):
        invalid_lon = df[(df['lon'] < 46.5) | (df['lon'] > 49.0)]
        if len(invalid_lon) > 0:
            errors.append(f"Warning: {len(invalid_lon)} records with longitude outside Kuwait bounds (46.5-49.0)")
    
    # Check for empty DataFrame
    if len(df) == 0:
        errors.append("CSV file is empty")
    
    return len(errors) == 0, errors

def validate_geojson(geojson_data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate GeoJSON structure
    
    Args:
        geojson_data: GeoJSON dict to validate
    
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    # Check type
    if 'type' not in geojson_data:
        errors.append("Missing 'type' field")
        return False, errors
    
    if geojson_data['type'] not in ['FeatureCollection', 'Feature']:
        errors.append(f"Invalid type: {geojson_data['type']}. Expected 'FeatureCollection' or 'Feature'")
    
    # Check features
    if geojson_data['type'] == 'FeatureCollection':
        if 'features' not in geojson_data:
            errors.append("Missing 'features' array in FeatureCollection")
            return False, errors
        
        if not isinstance(geojson_data['features'], list):
            errors.append("'features' must be an array")
            return False, errors
        
        if len(geojson_data['features']) == 0:
            errors.append("Warning: FeatureCollection has no features")
        
        # Validate each feature
        for i, feature in enumerate(geojson_data['features'][:10]):  # Check first 10
            if 'type' not in feature or feature['type'] != 'Feature':
                errors.append(f"Feature {i}: Invalid or missing type")
            
            if 'geometry' not in feature:
                errors.append(f"Feature {i}: Missing geometry")
            
            if 'properties' not in feature:
                errors.append(f"Feature {i}: Missing properties")
    
    return len(errors) == 0, errors

def check_data_completeness(df: pd.DataFrame) -> Dict[str, float]:
    """
    Check data completeness percentages
    
    Args:
        df: DataFrame to check
    
    Returns:
        Dict with completeness percentages per column
    """
    if df.empty:
        return {}
    
    completeness = {}
    
    for col in df.columns:
        non_null = df[col].notna().sum()
        total = len(df)
        completeness[col] = round((non_null / total) * 100, 1)
    
    return completeness

def check_data_freshness(file_path: Path) -> Dict[str, str]:
    """
    Check when data file was last modified
    
    Args:
        file_path: Path to data file
    
    Returns:
        Dict with freshness info
    """
    from datetime import datetime
    
    if not file_path.exists():
        return {
            'status': 'missing',
            'message': 'File not found',
            'last_modified': 'N/A'
        }
    
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    age_hours = (datetime.now() - mtime).total_seconds() / 3600
    
    if age_hours < 24:
        status = 'fresh'
        message = f'Updated {int(age_hours)} hours ago'
    elif age_hours < 168:  # 7 days
        status = 'recent'
        message = f'Updated {int(age_hours/24)} days ago'
    else:
        status = 'stale'
        message = f'Updated {int(age_hours/24)} days ago (may be outdated)'
    
    return {
        'status': status,
        'message': message,
        'last_modified': mtime.strftime('%Y-%m-%d %H:%M:%S')
    }

def validate_all_data() -> Dict[str, Dict]:
    """
    Validate all data files
    
    Returns:
        Dict with validation results for each file
    """
    from pathlib import Path
    
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    GEO_DIR = DATA_DIR / "geo" / "kuwait"
    
    results = {}
    
    # Validate incidents CSV
    incidents_file = DATA_DIR / "incidents.csv"
    if incidents_file.exists():
        try:
            df = pd.read_csv(incidents_file)
            is_valid, errors = validate_csv_schema(df)
            completeness = check_data_completeness(df)
            freshness = check_data_freshness(incidents_file)
            
            results['incidents'] = {
                'valid': is_valid,
                'errors': errors,
                'completeness': completeness,
                'freshness': freshness,
                'record_count': len(df)
            }
        except Exception as e:
            results['incidents'] = {
                'valid': False,
                'errors': [f"Failed to load: {e}"],
                'completeness': {},
                'freshness': {'status': 'error', 'message': str(e)},
                'record_count': 0
            }
    else:
        results['incidents'] = {
            'valid': False,
            'errors': ['File not found'],
            'completeness': {},
            'freshness': {'status': 'missing', 'message': 'File not found'},
            'record_count': 0
        }
    
    # Validate GeoJSON files
    for layer in ['governorates', 'districts', 'police_zones', 'blocks']:
        geojson_file = GEO_DIR / f"{layer}.geojson"
        
        if geojson_file.exists():
            try:
                with open(geojson_file, 'r', encoding='utf-8') as f:
                    geojson_data = json.load(f)
                
                is_valid, errors = validate_geojson(geojson_data)
                freshness = check_data_freshness(geojson_file)
                
                feature_count = len(geojson_data.get('features', [])) if geojson_data.get('type') == 'FeatureCollection' else 1
                
                results[layer] = {
                    'valid': is_valid,
                    'errors': errors,
                    'freshness': freshness,
                    'feature_count': feature_count
                }
            except Exception as e:
                results[layer] = {
                    'valid': False,
                    'errors': [f"Failed to load: {e}"],
                    'freshness': {'status': 'error', 'message': str(e)},
                    'feature_count': 0
                }
        else:
            results[layer] = {
                'valid': False,
                'errors': ['File not found'],
                'freshness': {'status': 'missing', 'message': 'File not found'},
                'feature_count': 0
            }
    
    return results
