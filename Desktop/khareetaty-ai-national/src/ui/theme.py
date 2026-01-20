"""
Khareetaty AI — Theme Module
Applies custom CSS styling for Kuwait National Intelligence Platform
"""

import streamlit as st

def apply_theme():
    """Apply custom CSS theme to the Streamlit app"""
    
    st.markdown("""
    <style>
    /* Kuwait National Theme - Executive Dark Palette */
    
    /* Main background */
    .stApp {
        background: linear-gradient(180deg, #0a0e27 0%, #16213e 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16213e 0%, #0f3460 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00d4ff !important;
        font-weight: 600;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00d4ff;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a0a0a0;
        font-weight: 500;
    }
    
    /* Cards and containers */
    .element-container {
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #0f3460 0%, #16213e 100%);
        color: white;
        border: 1px solid #00d4ff;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #16213e 0%, #0f3460 100%);
        border-color: #00ffff;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: rgba(22, 33, 62, 0.5);
        border-radius: 6px;
        border-left: 3px solid #00d4ff;
    }
    
    /* Tables */
    .dataframe {
        border: 1px solid #00d4ff;
        border-radius: 6px;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 6px;
        border-left: 4px solid #00d4ff;
    }
    
    /* Links */
    a {
        color: #00d4ff !important;
    }
    
    a:hover {
        color: #00ffff !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(22, 33, 62, 0.5);
        border-radius: 6px 6px 0 0;
        color: #a0a0a0;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(180deg, #0f3460 0%, #16213e 100%);
        color: #00d4ff !important;
        border-bottom: 3px solid #00d4ff;
    }
    
    /* Selectbox and inputs */
    .stSelectbox, .stTextInput, .stNumberInput {
        border-radius: 6px;
    }
    
    /* Charts */
    .vega-embed {
        border-radius: 8px;
    }
    
    /* Footer */
    footer {
        visibility: hidden;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #16213e;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #00d4ff;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #00ffff;
    }
    </style>
    """, unsafe_allow_html=True)