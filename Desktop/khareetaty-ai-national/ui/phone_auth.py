"""
Khareetaty AI — Phone Authentication Module
Executive Acknowledgment Panel (UI-Level Only, No OTP/SMS)
"""

import streamlit as st

# Executive ownership constants
EXECUTIVE_OWNER = "Bader Alabdadan"
NATIONAL_CONTACT = "+965 6663 3387"
AUTH_MODE = "Executive Acknowledgment"
STATUS = "Verified — Phase-5"

def render_executive_panel():
    """
    Render executive ownership and authentication panel.
    This is UI-level only with no actual OTP/SMS functionality.
    """
    
    # First render the CSS
    st.markdown("""
    <style>
    .exec-panel {
        background: linear-gradient(135deg, rgb(22, 33, 62) 0%, rgb(15, 52, 96) 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #00d4ff;
        margin: 1rem 0;
    }
    .exec-title {
        color: #00d4ff;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .exec-field {
        margin: 0.8rem 0;
    }
    .exec-label {
        color: #a0a0a0;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .exec-value {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 0.2rem;
    }
    .exec-status {
        background: rgba(0, 212, 255, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 6px;
        border-left: 4px solid #00d4ff;
        margin-top: 1rem;
    }
    .exec-note {
        color: #a0a0a0;
        font-size: 0.9rem;
        font-style: italic;
        margin-top: 1rem;
        padding: 1rem;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 6px;
        border-left: 3px solid #ffa726;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Then render the panel with f-string
    panel_html = f"""
    <div class="exec-panel">
        <div class="exec-title">🔐 Executive Ownership Verified</div>
        
        <div class="exec-field">
            <div class="exec-label">Owner</div>
            <div class="exec-value">{EXECUTIVE_OWNER}</div>
        </div>
        
        <div class="exec-field">
            <div class="exec-label">Primary National Contact</div>
            <div class="exec-value">🇰🇼 {NATIONAL_CONTACT}</div>
        </div>
        
        <div class="exec-field">
            <div class="exec-label">Authentication Mode</div>
            <div class="exec-value">{AUTH_MODE}</div>
        </div>
        
        <div class="exec-status">
            <strong>Status:</strong> ✅ {STATUS}
        </div>
        
        <div class="exec-note">
            <strong>Executive Ownership Verified.</strong><br>
            This platform operates under executive acknowledgment and national ownership.
            Live OTP/SMS workflows are deferred to Phase-2 to preserve Streamlit-only architecture,
            cloud isolation, and national security boundaries.
        </div>
    </div>
    """
    
    st.markdown(panel_html, unsafe_allow_html=True)

def render_operations_auth():
    """
    Render authentication panel for Operations page.
    Simplified version for page-level display.
    """
    
    st.info(f"""
    **🔐 Executive Authentication**
    
    - **Owner:** {EXECUTIVE_OWNER}
    - **Contact:** 🇰🇼 {NATIONAL_CONTACT}
    - **Mode:** {AUTH_MODE}
    - **Status:** ✅ {STATUS}
    
    *Live OTP/SMS deferred to Phase-2 for Streamlit-only architecture.*
    """)

def get_executive_info():
    """Return executive information as dictionary"""
    return {
        "owner": EXECUTIVE_OWNER,
        "contact": NATIONAL_CONTACT,
        "auth_mode": AUTH_MODE,
        "status": STATUS
    }