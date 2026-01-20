"""
Khareetaty AI — Data Quality Validator
Insurance-grade quality checks and validation
"""

import streamlit as st
import pandas as pd
import config
from src.core import geo

def validate_data(df):
    """
    Perform comprehensive data quality validation.
    Returns a quality report dictionary.
    """
    if df is None or df.empty:
        return {
            'status': 'error',
            'message': 'No data to validate'
        }
    
    report = {
        'status': 'success',
        'checks': {}
    }
    
    # 1. Schema validation
    report['checks']['schema'] = validate_schema(df)
    
    # 2. Completeness check
    report['checks']['completeness'] = check_completeness(df)
    
    # 3. Timestamp validation
    report['checks']['timestamps'] = validate_timestamps(df)
    
    # 4. Geographic validation
    report['checks']['geography'] = validate_geography(df)
    
    # 5. Duplicate check
    report['checks']['duplicates'] = check_duplicates(df)
    
    # 6. Anomaly detection
    report['checks']['anomalies'] = detect_anomalies(df)
    
    # Calculate overall score
    report['overall_score'] = calculate_quality_score(report['checks'])
    
    return report

def validate_schema(df):
    """
    Validate that required columns exist.
    """
    missing_cols = [col for col in config.REQUIRED_COLUMNS if col not in df.columns]
    
    return {
        'passed': len(missing_cols) == 0,
        'missing_columns': missing_cols,
        'message': 'All required columns present' if not missing_cols else f'Missing: {missing_cols}'
    }

def check_completeness(df):
    """
    Check for null values and completeness.
    """
    null_counts = df.isnull().sum()
    null_percentages = (null_counts / len(df) * 100).round(2)
    
    completeness = 100 - null_percentages.mean()
    passed = completeness >= (config.QUALITY_THRESHOLDS['completeness_min'] * 100)
    
    return {
        'passed': passed,
        'completeness_pct': round(completeness, 2),
        'null_counts': null_counts.to_dict(),
        'message': f'Completeness: {completeness:.2f}%'
    }

def validate_timestamps(df):
    """
    Validate timestamp column.
    """
    if 'timestamp' not in df.columns:
        return {'passed': False, 'message': 'No timestamp column'}
    
    # Check for null timestamps
    null_count = df['timestamp'].isnull().sum()
    
    # Check for future dates
    future_dates = 0
    try:
        future_dates = (df['timestamp'] > pd.Timestamp.now()).sum()
    except:
        pass
    
    passed = (null_count == 0) and (future_dates == 0)
    
    return {
        'passed': passed,
        'null_count': int(null_count),
        'future_dates': int(future_dates),
        'message': f'Valid timestamps: {len(df) - null_count - future_dates}/{len(df)}'
    }

def validate_geography(df):
    """
    Validate lat/lon coordinates are within Kuwait boundaries.
    """
    if 'lat' not in df.columns or 'lon' not in df.columns:
        return {'passed': False, 'message': 'Missing lat/lon columns'}
    
    # Check for null coordinates
    null_coords = df[['lat', 'lon']].isnull().any(axis=1).sum()
    
    # Check for coordinates outside Kuwait
    valid_df = df.dropna(subset=['lat', 'lon'])
    outside_kuwait = 0
    
    for _, row in valid_df.iterrows():
        if not geo.is_within_kuwait(row['lat'], row['lon']):
            outside_kuwait += 1
    
    passed = (null_coords == 0) and (outside_kuwait == 0)
    
    return {
        'passed': passed,
        'null_coordinates': int(null_coords),
        'outside_kuwait': int(outside_kuwait),
        'message': f'Valid coordinates: {len(valid_df) - outside_kuwait}/{len(df)}'
    }

def check_duplicates(df):
    """
    Check for duplicate records.
    """
    duplicate_count = df.duplicated().sum()
    passed = duplicate_count == 0
    
    return {
        'passed': passed,
        'duplicate_count': int(duplicate_count),
        'message': f'Duplicates: {duplicate_count}'
    }

def detect_anomalies(df):
    """
    Detect basic anomalies in the data.
    """
    anomalies = []
    
    # Check for unusual incident types
    if 'incident_type' in df.columns:
        unknown_types = df[~df['incident_type'].isin(config.INCIDENT_TYPES)]
        if len(unknown_types) > 0:
            anomalies.append(f'{len(unknown_types)} unknown incident types')
    
    # Check for unusual governorates
    if 'governorate' in df.columns:
        unknown_govs = df[~df['governorate'].isin(config.GOVERNORATES)]
        if len(unknown_govs) > 0:
            anomalies.append(f'{len(unknown_govs)} unknown governorates')
    
    passed = len(anomalies) == 0
    
    return {
        'passed': passed,
        'anomalies': anomalies,
        'message': 'No anomalies detected' if passed else f'{len(anomalies)} anomaly types found'
    }

def calculate_quality_score(checks):
    """
    Calculate overall quality score (0-100).
    """
    passed_checks = sum(1 for check in checks.values() if check.get('passed', False))
    total_checks = len(checks)
    
    if total_checks == 0:
        return 0
    
    return round((passed_checks / total_checks) * 100, 2)

def render_quality_report(report):
    """
    Render quality report in Streamlit.
    """
    if report.get('status') == 'error':
        st.error(report.get('message', 'Validation error'))
        return
    
    # Overall score
    score = report.get('overall_score', 0)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Quality Score", f"{score}%")
    
    with col2:
        checks = report.get('checks', {})
        passed = sum(1 for c in checks.values() if c.get('passed', False))
        st.metric("Checks Passed", f"{passed}/{len(checks)}")
    
    with col3:
        status = "✅ Excellent" if score >= 90 else "⚠️ Needs Attention" if score >= 70 else "❌ Critical"
        st.metric("Status", status)
    
    # Detailed checks
    st.markdown("### Detailed Quality Checks")
    
    for check_name, check_result in report.get('checks', {}).items():
        passed = check_result.get('passed', False)
        message = check_result.get('message', '')
        
        icon = "✅" if passed else "❌"
        
        with st.expander(f"{icon} {check_name.title()}", expanded=not passed):
            st.write(message)
            
            # Show additional details
            for key, value in check_result.items():
                if key not in ['passed', 'message']:
                    st.write(f"**{key}:** {value}")