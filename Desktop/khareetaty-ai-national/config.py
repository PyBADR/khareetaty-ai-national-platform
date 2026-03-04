"""
Khareetaty AI - National Intelligence Platform
Configuration and Constants

Version: 2.0 (Production)
Architecture: Streamlit-Only | File-Based | Government-Grade
Last Updated: 2026-01-17
"""

from pathlib import Path
from typing import List, Dict

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PROJECT METADATA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT_NAME = "Khareetaty AI"
PROJECT_TITLE = "Kuwait National Intelligence Platform"
VERSION = "5.0.0"
LAST_UPDATED = "2026-01-17"

ARCHITECTURE_BANNER = "🏛️ Streamlit-Only | 📊 File-Based Analytics | ⚡ No Backend Required | 🇰🇼 Kuwait National Intelligence"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PATHS (Portable - Use Pathlib)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
GEO_DIR = BASE_DIR / "geo"
SRC_DIR = BASE_DIR / "src"

# Data files
INCIDENTS_FILE = DATA_DIR / "incidents.csv"

# Geographic files
GEO_GOVERNORATES = GEO_DIR / "kuwait_governorates.geojson"
GEO_DISTRICTS = GEO_DIR / "kuwait_districts.geojson"
GEO_POLICE_ZONES = GEO_DIR / "kuwait_police_zones.geojson"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA SCHEMA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INCIDENT_SCHEMA: Dict[str, str] = {
    "incident_type": "string",
    "governorate": "string",
    "zone": "string",
    "lat": "float",
    "lon": "float",
    "timestamp": "datetime"
}

REQUIRED_COLUMNS: List[str] = [
    "incident_type",
    "governorate",
    "zone",
    "lat",
    "lon",
    "timestamp"
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONTROLLED VOCABULARIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Kuwait Governorates (Official)
GOVERNORATES: List[str] = [
    "Capital",
    "Hawalli",
    "Farwaniya",
    "Mubarak Al-Kabeer",
    "Ahmadi",
    "Jahra"
]

# Incident Types (Controlled Taxonomy)
INCIDENT_TYPES: List[str] = [
    "assault",
    "theft",
    "vandalism",
    "traffic_accident",
    "medical_emergency",
    "fire",
    "domestic_dispute",
    "suspicious_activity",
    "other"
]

# Severity Levels
SEVERITY_LEVELS: Dict[int, str] = {
    1: "Minor",
    2: "Low",
    3: "Medium",
    4: "High",
    5: "Critical"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GEOGRAPHIC BOUNDARIES (Kuwait)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Kuwait Bounding Box (min_lon, min_lat, max_lon, max_lat)
KUWAIT_BBOX = (46.2, 28.4, 48.6, 30.2)

KUWAIT_BOUNDS = {
    "lat_min": 28.4,
    "lat_max": 30.2,
    "lon_min": 46.2,
    "lon_max": 48.6
}

KUWAIT_CENTER = {
    "lat": 29.3759,
    "lon": 47.9774
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ANALYTICS PARAMETERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Hotspot Detection (DBSCAN)
HOTSPOT_CONFIG = {
    "eps_km": 0.5,  # 500 meters radius
    "min_samples": 5,  # Minimum incidents to form cluster
    "metric": "haversine"
}

# Trend Analysis
TREND_CONFIG = {
    "short_window": 7,  # 7 days
    "long_window": 30,  # 30 days
    "forecast_periods": 7  # Forecast 7 days ahead
}

# Quality Thresholds
QUALITY_THRESHOLDS = {
    "completeness_min": 0.90,  # 90% non-null
    "validity_min": 0.95,  # 95% valid values
    "freshness_max_hours": 24  # Data should be < 24h old
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# UI CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Page Configuration
PAGE_CONFIG = {
    "page_title": f"{PROJECT_NAME} - {PROJECT_TITLE}",
    "page_icon": "🚨",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Navigation Pages
PAGES = [
    "Executive Summary",
    "Map View",
    "Hotspots",
    "Trends",
    "Analytics",
    "Data Quality & Governance"
]

# Color Scheme
COLORS = {
    "primary": "#FF4B4B",
    "secondary": "#0068C9",
    "success": "#09AB3B",
    "warning": "#FFA500",
    "danger": "#FF4B4B",
    "info": "#00C0F2"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECURITY & GOVERNANCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Disclaimer
DISCLAIMER = """
⚠️ **INTERNAL USE ONLY**  
This platform is for authorized government personnel only.  
All data is aggregated and anonymized. No personally identifiable information (PII) is displayed.  
For official use in national intelligence and operational planning.
"""

# Data Provenance
DATA_PROVENANCE = {
    "source": "Kuwait National Intelligence Database",
    "update_frequency": "Real-time (simulated with static dataset)",
    "quality_standard": "Insurance-Grade",
    "governance": "Government-Approved"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CACHING CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CACHE_TTL = 3600  # 1 hour in seconds

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
