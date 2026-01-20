# 🇰🇼 Khareetaty AI — Kuwait National Intelligence Platform

**Version:** 5.0.0 (Phase-5 Kuwait National)  
**Architecture:** Streamlit-Only | File-Based Analytics | No Backend Required  
**Status:** Executive-Ready | Ministerial-Ready | Streamlit Cloud Deployable

---

## 🎯 Overview

Khareetaty AI is a sovereign national intelligence platform for the State of Kuwait, designed for executive-level operational intelligence and risk analysis. Built with a Streamlit-only architecture, it requires no backend services, databases, or external dependencies.

### Key Characteristics

✅ **Streamlit-Only** — No backend services required  
✅ **File-Based Analytics** — CSV + GeoJSON inside repository  
✅ **No Database** — No PostgreSQL, no external databases  
✅ **No SMS Gateway** — No Twilio, no OTP (deferred to Phase-2)  
✅ **No Secrets** — No API keys, no credentials  
✅ **Streamlit Cloud Ready** — Zero external service dependencies  
✅ **Kuwait National Boundary** — Geographic enforcement active

---

## 🏗️ Architecture

```
khareetaty-ai-national/
├── app.py                      # Main Streamlit entry point
├── config.py                   # Configuration and constants
├── pages/                      # Streamlit multi-page app
│   ├── 1_Map.py               # Map visualization
│   ├── 2_Hotspots.py          # Hotspot detection
│   ├── 3_Trends.py            # Trend analysis
│   ├── 4_Alerts.py            # Alert system (simulated)
│   └── 5_Operations.py        # Operations & executive control
├── ui/                         # UI components
│   ├── branding.py            # Kuwait branding
│   ├── theme.py               # CSS theme
│   └── phone_auth.py          # Executive acknowledgment panel
├── core/                       # Core business logic
│   ├── data_loader.py         # Data loading with caching
│   ├── geo.py                 # Geographic operations & Kuwait bbox
│   ├── analytics.py           # Analytics engine
│   └── quality.py             # Data quality validation
├── data/                       # Data files
│   └── incidents.csv          # Incident data
├── geo/                        # Geographic layers
│   ├── kuwait_governorates.geojson
│   ├── kuwait_districts.geojson
│   └── kuwait_police_zones.geojson
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Python version
└── Makefile                    # Development commands
```

---

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/PyBADR/khareetaty-ai-national-platform.git
   cd khareetaty-ai-national-platform
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   # OR
   make run
   ```

4. **Open in browser**
   ```
   http://localhost:8501
   ```

---

## ☁️ Streamlit Cloud Deployment

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at [streamlit.io/cloud](https://streamlit.io/cloud))

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repository: `PyBADR/khareetaty-ai-national-platform`
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Verify Deployment**
   - App should load with zero errors
   - All pages should be accessible
   - Kuwait branding should be visible
   - No localhost references

---

## 📊 Features

### Executive Summary (app.py)
- System status dashboard
- Key metrics and insights
- Executive ownership panel
- Data quality scorecard

### Map View (pages/1_Map.py)
- Kuwait-bounded incident visualization
- Geographic layers (governorates, districts, police zones)
- Real-time filtering

### Hotspot Analysis (pages/2_Hotspots.py)
- DBSCAN clustering for risk zones
- High/Medium/Low risk classification
- Zone-level insights

### Trend Analysis (pages/3_Trends.py)
- 7-day and 30-day trend views
- Time-series visualization
- Incident type breakdown

### Alert System (pages/4_Alerts.py)
- **SIMULATED ONLY** (Phase-5)
- Alert log and configuration
- Live SMS/OTP deferred to Phase-2

### Operations (pages/5_Operations.py)
- Executive ownership verification
- Data quality governance
- System information

---

## 🔐 Executive Ownership

**Owner:** Bader Alabdadan  
**Primary National Contact:** +965 6663 3387  
**Authentication Mode:** Executive Acknowledgment  
**Status:** Verified — Phase-5

### Sovereignty Statement

🇰🇼 **State of Kuwait — National Intelligence Platform**

This platform operates under executive acknowledgment and national ownership. Live OTP/SMS workflows are deferred to Phase-2 to preserve Streamlit-only architecture, cloud isolation, and national security boundaries.

---

## 🛡️ Constraints & Boundaries

### Hard Constraints (Non-Negotiable)

✅ Streamlit-only  
✅ File-based analytics (CSV + GeoJSON) inside repo  
✅ No backend (no FastAPI)  
✅ No database (no Postgres)  
✅ No SMS gateway (no Twilio)  
✅ No OTP  
✅ No secrets  
✅ Must work on Streamlit Cloud with zero external services  
✅ Must not reference localhost anywhere

### Geographic Boundaries

**Kuwait Bounding Box:** `(46.2, 28.4, 48.6, 30.2)` (min_lon, min_lat, max_lon, max_lat)

All incident data and geographic features are filtered to Kuwait boundaries. The platform enforces national sovereignty at the data layer.

---

## 🧪 Development

### Linting
```bash
make lint
# OR
ruff check .
```

### Testing
```bash
make test
# OR
pytest tests/ -v
```

### Cleaning
```bash
make clean
```

---

## 📦 Dependencies

**Minimal dependencies for Streamlit Cloud compatibility:**

- `streamlit>=1.30.0` — Web framework
- `pandas>=2.0.0` — Data manipulation
- `numpy>=1.24.0` — Numerical operations
- `scikit-learn>=1.3.0` — Clustering (DBSCAN)

**No heavy dependencies. No external APIs. No secrets.**

---

## 🗺️ Roadmap

### Phase-5 (Current) ✅
- Streamlit-only architecture
- File-based analytics
- Kuwait boundary enforcement
- Executive acknowledgment panel
- Simulated alerts

### Phase-2 (Future)
- Live OTP/SMS integration
- Real-time data ingestion
- Advanced predictive models
- Multi-user authentication

---

## ⚠️ Disclaimer

**INTERNAL USE ONLY**

This platform is for authorized government personnel only. All data is aggregated and anonymized. No personally identifiable information (PII) is displayed. For official use in national intelligence and operational planning.

---

## 📄 License

Proprietary — State of Kuwait National Intelligence Platform

---

## 📞 Contact

**Executive Owner:** Bader Alabdadan  
**National Contact:** +965 6663 3387  
**Platform:** Khareetaty AI v5.0.0

---

🇰🇼 **State of Kuwait — National Intelligence Platform**
