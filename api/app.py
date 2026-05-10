import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

# ---------------- LOAD ENV ----------------
# Try Streamlit Cloud first
API_KEY = st.secrets.get("API_KEY", None)

# Fallback for local system
if not API_KEY:
    load_dotenv()
    API_KEY = os.getenv("API_KEY")

# Stop only if truly missing
if not API_KEY:
    st.error("❌ API Key missing. Please add it in Streamlit Secrets or .env file.")
    st.stop()

# ---------------- DEBUG CHECK ----------------
if not API_KEY:
    st.error("❌ API Key not found! Check your .env file")
    st.stop()

BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

# ---------------- UI ----------------
st.set_page_config(page_title="Weather Dashboard", layout="wide")

st.title("🌦️ Weather Forecast & Alert Dashboard")

# ---------------- CITY SELECTION ----------------
cities = ["Hyderabad", "Bangalore", "Chennai", "Delhi", "Mumbai"]
city = st.selectbox("📍 Select City", cities)

# ---------------- API FUNCTION ----------------
def get_weather(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(BASE_URL, params=params)

        # DEBUG INFO (very important for you)
        st.write("Status Code:", response.status_code)

        data = response.json()

        if response.status_code != 200:
            st.error(f"API Error: {data.get('message', 'Unknown error')}")
            return None

        return data

    except Exception as e:
        st.error(f"Request failed: {e}")
        return None


# ---------------- FETCH DATA ----------------
data = get_weather(city)

if data:

    records = []
    alerts = []

    for item in data["list"][:8]:

        # THE ONLY CHANGE: Swapped 'temp' to 'feels_like' to match terminal accuracy
        temp = item["main"]["feels_like"] 
        humidity = item["main"]["humidity"]
        rain = item.get("rain", {}).get("3h", 0)
        time = item["dt_txt"]

        records.append({
            "Time": time,
            "Temperature": temp,
            "Humidity": humidity,
            "Rainfall": rain
        })

        # ALERT LOGIC
        if temp > 40:
            alerts.append("🔥 High Temperature Alert")
        if humidity > 85:
            alerts.append("💧 High Humidity Alert")
        if rain > 5:
            alerts.append("🌧️ Heavy Rain Alert")

    df = pd.DataFrame(records)

    # ---------------- KPI ----------------
    col1, col2, col3 = st.columns(3)

    col1.metric("🌡️ Temp", f"{df['Temperature'].iloc[0]:.2f} °C")
    col2.metric("💧 Humidity", f"{df['Humidity'].iloc[0]:.2f} %")
    col3.metric("🌧️ Rain", f"{df['Rainfall'].iloc[0]:.2f} mm")

    st.divider()

    # ---------------- ALERTS ----------------
    st.subheader("🚨 Alerts")

    if alerts:
        for a in set(alerts):
            st.error(a)
    else:
        st.success("No alerts")

    st.divider()

    # ---------------- CHARTS ----------------
    chart = st.radio("Select Chart", ["Temperature", "Humidity", "Rainfall"])

    if chart == "Temperature":
        fig = px.line(df, x="Time", y="Temperature", markers=True)
    elif chart == "Humidity":
        fig = px.bar(df, x="Time", y="Humidity")
    else:
        fig = px.area(df, x="Time", y="Rainfall")

    st.plotly_chart(fig, use_container_width=True)

    # ---------------- DATA ----------------
    with st.expander("📊 Raw Data"):
        st.dataframe(df)