"""
Khareetaty AI — Kuwait National Branding Module
Provides consistent Kuwait-focused branding across the platform
"""

import streamlit as st
import config

def render_header():
    """Render the main header with Kuwait branding"""
    
    # Hero banner with gradient (no external images)
    st.markdown("""
    <style>
    .hero-banner {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border-left: 5px solid #00d4ff;
    }
    .hero-title {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .hero-subtitle {
        color: #00d4ff;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    .sovereignty-line {
        color: #a0a0a0;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        font-style: italic;
    }
    </style>
    
    <div class="hero-banner">
        <div class="hero-title">🇰🇼 Khareetaty AI — Kuwait National Intelligence Platform</div>
        <div class="hero-subtitle">Streamlit-Only | File-Based Analytics | No Backend Required</div>
        <div class="sovereignty-line">State of Kuwait — National Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

def render_page_header(title: str, icon: str = "📊"):
    """Render a consistent page header"""
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #16213e 0%, #0f3460 100%); 
                padding: 1.5rem; 
                border-radius: 8px; 
                margin-bottom: 1.5rem;
                border-left: 4px solid #00d4ff;">
        <h1 style="color: white; margin: 0; font-size: 2rem;">
            {icon} {title}
        </h1>
        <p style="color: #00d4ff; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
            🇰🇼 Kuwait National Intelligence Platform
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_kuwait_flag():
    """Render Kuwait flag emoji"""
    return "🇰🇼"

def get_kuwait_colors():
    """Return Kuwait-inspired color palette"""
    return {
        "primary": "#00d4ff",      # Bright blue (inspired by Kuwait waters)
        "secondary": "#16213e",    # Deep navy (night sky)
        "accent": "#0f3460",       # Ocean blue
        "success": "#00c853",      # Green
        "warning": "#ffa726",      # Orange
        "danger": "#ef5350",       # Red
        "text": "#ffffff",         # White
        "background": "#1a1a2e"    # Dark background
    }
