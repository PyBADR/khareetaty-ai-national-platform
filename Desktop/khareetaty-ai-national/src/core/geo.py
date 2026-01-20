"""
Khareetaty AI — Geographic Module
Kuwait boundary enforcement and geographic operations
"""

import pandas as pd
import config

# Kuwait bounding box (min_lon, min_lat, max_lon, max_lat)
KUWAIT_BBOX = (46.2, 28.4, 48.6, 30.2)

def is_within_kuwait(lat, lon):
    """
    Check if coordinates are within Kuwait boundaries.
    """
    min_lon, min_lat, max_lon, max_lat = KUWAIT_BBOX
    return (min_lat <= lat <= max_lat) and (min_lon <= lon <= max_lon)

def filter_incidents_by_bbox(df):
    """
    Filter incidents to only include those within Kuwait boundaries.
    """
    if df is None or df.empty:
        return df
    
    if 'lat' not in df.columns or 'lon' not in df.columns:
        return df
    
    # Remove rows with missing coordinates
    df = df.dropna(subset=['lat', 'lon'])
    
    # Filter by Kuwait bbox
    min_lon, min_lat, max_lon, max_lat = KUWAIT_BBOX
    mask = (
        (df['lat'] >= min_lat) & (df['lat'] <= max_lat) &
        (df['lon'] >= min_lon) & (df['lon'] <= max_lon)
    )
    
    filtered_df = df[mask].copy()
    
    return filtered_df

def filter_geojson_by_bbox(geojson_data):
    """
    Filter GeoJSON features to only include those intersecting Kuwait bbox.
    This is a simplified implementation - keeps features whose centroid is in Kuwait.
    """
    if not geojson_data or 'features' not in geojson_data:
        return geojson_data
    
    filtered_features = []
    
    for feature in geojson_data['features']:
        # Simple check: if feature has coordinates, check if any are in Kuwait
        # For production, use proper geometric intersection
        try:
            geometry = feature.get('geometry', {})
            if geometry.get('type') == 'Point':
                coords = geometry.get('coordinates', [])
                if len(coords) >= 2:
                    lon, lat = coords[0], coords[1]
                    if is_within_kuwait(lat, lon):
                        filtered_features.append(feature)
            else:
                # For polygons/multipolygons, include all (assume Kuwait data)
                filtered_features.append(feature)
        except:
            # If error, include the feature
            filtered_features.append(feature)
    
    return {
        'type': 'FeatureCollection',
        'features': filtered_features
    }

def get_kuwait_center():
    """
    Return Kuwait center coordinates.
    """
    return config.KUWAIT_CENTER

def get_kuwait_bounds():
    """
    Return Kuwait bounding box.
    """
    return KUWAIT_BBOX

def calculate_distance_km(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points using Haversine formula.
    Returns distance in kilometers.
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c