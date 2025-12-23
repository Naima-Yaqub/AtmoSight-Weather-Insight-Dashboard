import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from geopy.geocoders import Nominatim
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import io
import zipfile

# Page config
st.set_page_config(
    layout="wide",
    page_title="NASA Weather Insight Dashboard",
    page_icon="🌍"
)

# Custom CSS
st.markdown("""
<style>
.stApp {
    background-color: #f6f8fb;
}

/* Hero */
.main-title {
    font-size: 42px;
    font-weight: 700;
    color: #1f2937;
}
.subtitle {
    font-size: 17px;
    color: #4b5563;
    margin-bottom: 2em;
}

/* Cards */
.section-card {
    background: #ffffff;
    padding: 24px 28px;
    border-radius: 16px;
    box-shadow: 0 10px 22px rgba(0,0,0,0.06);
    margin-bottom: 26px;
}

/* Weather Insight */
.insight-card {
    background: linear-gradient(135deg, #ecfeff, #f0f9ff);
    padding: 26px 30px;
    border-radius: 18px;
    box-shadow: 0 12px 26px rgba(0,0,0,0.08);
    margin-bottom: 34px;
}
.insight-card h3 {
    color: #0f172a;
    margin-bottom: 10px;
}

/* Metrics */
.metric-box {
    background: linear-gradient(135deg, #eef2ff, #f8fafc);
    padding: 18px;
    border-radius: 14px;
    text-align: center;
    box-shadow: 0 6px 16px rgba(0,0,0,0.06);
}
.metric-box h4 {
    color: #475569;
    margin-bottom: 6px;
}
.metric-box h2 {
    color: #1e3a8a;
    margin: 0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0f172a;
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb;
}
section[data-testid="stSidebar"] input {
    background-color: #ffffff;
    color: #000000 !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] * {
    color: #000000 !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    border-radius: 14px;
    padding: 0.7em 1.5em;
    font-size: 15px;
    border: none;
}

/* Download buttons */
.stDownloadButton>button {
    background: linear-gradient(135deg, #22c55e, #16a34a);
    color: white;
    border-radius: 14px;
    padding: 0.7em 1.4em;
    font-size: 15px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# Custom CSS for headings
st.markdown("""
<style>
.hero-main {
    font-size: 48px;       /* Main heading size */
    font-weight: 700;
    color: #1f2937;
    text-align: center;
    margin-bottom: 0.2em;
}
.hero-sub {
    font-size: 24px;       /* Smaller subheading size */
    font-weight: 500;
    color: #4b5563;
    text-align: center;
    margin-top: 0;
    margin-bottom: 1em;
}
</style>
""", unsafe_allow_html=True)

# Hero header
st.markdown('<div class="hero-main">🌍 AtmoSight</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">NASA Weather Insight Dashboard</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="subtitle">'
    'Explore how weather behaves over decades using NASA POWER historical data. '
    'Designed to reveal patterns, trends, and climate risk — not short-term forecasts.'
    '</div>',
    unsafe_allow_html=True
)


# Sidebar Inputs
with st.sidebar:
    st.header("⚙️ Analysis Settings")

    location_input = st.text_input("City or Location", "Faisalabad")

    VAR_INFO = {
        "Temperature (T2M)": {"code": "T2M", "unit": "°C"},
        "Rainfall (PRECTOTCORR)": {"code": "PRECTOTCORR", "unit": "mm/day"},
        "Wind Speed (WS2M)": {"code": "WS2M", "unit": "m/s"},
        "Relative Humidity (RH2M)": {"code": "RH2M", "unit": "%"},
        "Solar Radiation (ALLSKY_SFC_SW_DWN)": {"code": "ALLSKY_SFC_SW_DWN", "unit": "kWh/m²/day"},
    }

    var_choice = st.selectbox("Weather Variable", list(VAR_INFO.keys()))
    var = VAR_INFO[var_choice]["code"]
    unit = VAR_INFO[var_choice]["unit"]

    date_in = st.date_input("Day of Year", datetime.today())
    run = st.button("Run Weather Analysis")

# Intro screen
if not run:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📌 What does this dashboard help you understand?")
    st.markdown("""
- How a **specific day of the year** behaves across decades  
- Whether conditions are becoming **more extreme or stable**  
- How often **rare events** have occurred historically  

Use it to build **intuition and risk awareness**, not daily forecasts.
""")
    st.info("Select a location, choose a variable, and run the analysis to begin.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Geocoding
@st.cache_data
def geocode_location(city):
    geolocator = Nominatim(user_agent="nasa_weather_app")
    loc = geolocator.geocode(city, timeout=10)
    if loc:
        return loc.latitude, loc.longitude
    return 24.8607, 67.0011

lat, lon = geocode_location(location_input)

# NASA POWER Data Fetcher
@st.cache_data(show_spinner=False)
def fetch_power_point(lat, lon, start_year, end_year, parameter):
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": parameter,
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "start": f"{start_year}0101",
        "end": f"{end_year}1231",
        "format": "JSON",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def build_dataframe(json_resp, parameter):
    data = json_resp.get("properties", {}).get("parameter", {}).get(parameter, {})
    records = [{"date": pd.to_datetime(k), parameter: v} for k, v in data.items()]
    return pd.DataFrame(records).sort_values("date").reset_index(drop=True)

# Analysis
year_start = 1991
year_end = datetime.today().year

json_data = fetch_power_point(lat, lon, year_start, year_end, var)
df = build_dataframe(json_data, var)

df["doy"] = df["date"].dt.dayofyear
selected = df[df["doy"] == date_in.timetuple().tm_yday]

values = selected[var].dropna()
mean_val = values.mean()
std_val = values.std(ddof=0)
max_val = values.max()
min_val = values.min()

prob_extreme = (values > mean_val + 2 * std_val).mean()
slope = np.polyfit(selected["date"].dt.year, selected[var], 1)[0]
trend_text = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"


# Weather Insight (Main Highlight)
st.markdown('<div class="insight-card">', unsafe_allow_html=True)
st.markdown(f"""
### 🌤️ Weather Insight for {location_input}

On **{date_in.strftime('%B %d')}**, **{var_choice.lower()}** has shown a **{trend_text} pattern** over the last three decades.

• Typical value: **{mean_val:.2f} {unit}**  
• Rare extremes occurred in **~{prob_extreme*100:.1f}%** of years  

This means the selected day is **historically {'more volatile' if prob_extreme > 0.15 else 'generally stable'}**, based on NASA observations.
""")
st.markdown('</div>', unsafe_allow_html=True)

# Metrics
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("📊 Key Statistics")

c1, c2, c3 = st.columns(3)
c1.markdown(f"<div class='metric-box'><h4>Average</h4><h2>{mean_val:.2f} {unit}</h2></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='metric-box'><h4>Maximum</h4><h2>{max_val:.2f} {unit}</h2></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='metric-box'><h4>Minimum</h4><h2>{min_val:.2f} {unit}</h2></div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# Visualizations 
colA, colB = st.columns(2)

with colA:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📈 Long-term Trend")
    fig, ax = plt.subplots(figsize=(4.2, 2.6))
    ax.plot(selected["date"].dt.year, selected[var], marker="o")
    ax.axhline(mean_val, linestyle="--")
    ax.set_xlabel("Year")
    ax.set_ylabel(unit)
    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)

with colB:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("🔔 Probability Distribution")
    x = np.linspace(mean_val - 4 * std_val, mean_val + 4 * std_val, 200)
    y = norm.pdf(x, mean_val, std_val)
    fig2, ax2 = plt.subplots(figsize=(4.2, 2.6))
    ax2.plot(x, y)
    ax2.axvline(mean_val, linestyle="--")
    ax2.fill_between(x, y, alpha=0.3)
    ax2.set_xlabel(unit)
    st.pyplot(fig2)
    st.markdown('</div>', unsafe_allow_html=True)

# Historical Data
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("📄 Historical Values")
selected["date"] = selected["date"].dt.strftime("%Y-%m-%d")
table_df = selected[["date", var]].rename(columns={var: f"{var_choice} [{unit}]"})
st.dataframe(table_df, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Downloadables
csv_data = table_df.to_csv(index=False)

trend_buf = io.BytesIO()
fig.savefig(trend_buf, format="png", dpi=150, bbox_inches="tight")
trend_buf.seek(0)

bell_buf = io.BytesIO()
fig2.savefig(bell_buf, format="png", dpi=150, bbox_inches="tight")
bell_buf.seek(0)

zip_buf = io.BytesIO()
with zipfile.ZipFile(zip_buf, "w") as z:
    z.writestr("historical_data.csv", csv_data)
    z.writestr("trend.png", trend_buf.getvalue())
    z.writestr("distribution.png", bell_buf.getvalue())
zip_buf.seek(0)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("📦 Export Results")

d1, d2 = st.columns(2)
d1.download_button("📥 Download CSV Data", csv_data, "nasa_weather_data.csv")
d2.download_button("🖼️ Download Charts (ZIP)", zip_buf, "nasa_weather_visuals.zip")
st.markdown('</div>', unsafe_allow_html=True)
