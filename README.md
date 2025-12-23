# 🌍 AtmoSight: Weather Data Processing & Analysis  
### NASA Space Apps Challenge 2025 — *Will It Rain on My Parade?*

**AtmoSight** is a data-centric analytical prototype developed as part of the **NASA Space Apps Challenge 2025**.  
This repository focuses specifically on the **backend logic, data retrieval, statistical processing, and insight generation** using **NASA POWER historical weather data**.

> ⚠️ This repository **does not include the complete frontend** used during the final submission.  
> The full system (frontend + backend) is available in the project repository linked below.

---

## Overview

This repository demonstrates **how raw NASA climate data is transformed into interpretable insights**, rather than how the final user interface was designed.

The implementation is intentionally kept minimal on the UI side (Streamlit) to clearly showcase:

- Data acquisition logic  
- Temporal filtering strategies  
- Statistical analysis  
- Trend and risk interpretation  

---

## Scope of This Repository

**This repository is concerned with:**

- Fetching daily historical data from the **NASA POWER API**
- Geocoding user-defined locations
- Day-of-year based climatological analysis
- Statistical modeling of long-term trends
- Quantifying variability and extreme-event likelihood
- Generating interpretable visual and numerical outputs

**This repository does NOT focus on:**

- Full production frontend
- UI/UX used in the final competition demo
- System-level deployment architecture

---

## NASA Space Apps Context

- **Challenge:** Will It Rain on My Parade?
- **NASA Project Page:**  
  [Explore our team](https://www.spaceappschallenge.org/2025/find-a-team/explorers12/) 

- **Complete Project Repository (Frontend + Backend):**  
  https://github.com/hurairaali/Rain-Parade-NASA_Challange

---

## Technical Highlights

- Historical analysis of a **specific calendar day across decades**
- Trend detection using linear regression
- Extreme-event probability estimation (μ + 2σ)
- Distribution modeling for uncertainty visualization
- Exportable datasets and figures for further analysis

---

## Author Contribution

My contribution focused on:

- Designing the **data processing pipeline**
- Implementing statistical analysis and trend detection
- Structuring how insights are derived from raw climate data
- Developing a simplified analytical interface to demonstrate the logic

---

## Technology Stack

- Python  
- Streamlit  
- Pandas, NumPy  
- SciPy  
- Matplotlib  
- NASA POWER API  
- Geopy (Nominatim)

---

## ▶️ Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py


## 🔗 Demo
- Live Demo of this project deployed through streamlit can be found here: [Demo-Link](https://atmosight-weather-insight-dashboard.streamlit.app/)
