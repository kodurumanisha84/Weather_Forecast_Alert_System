import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dotenv import load_dotenv
import os
import shutil

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"


# -------------------- GET WEATHER --------------------
def get_weather(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(BASE_URL, params=params)

        if response.status_code != 200:
            print("Status Code:", response.status_code)
            print(response.text)
            return None

        return response.json()

    except Exception as e:
        print("Error:", e)
        return None


# -------------------- ANALYZE WEATHER --------------------
def analyze_weather(data):
    alerts = []
    records = []

    forecast_list = data["list"]

    for item in forecast_list[:8]:

        temp = item["main"]["temp"]
        humidity = item["main"]["humidity"]
        rain = item.get("rain", {}).get("3h", 0)
        dt_txt = item["dt_txt"]

        records.append({
            "Datetime": dt_txt,
            "Temperature": temp,
            "Humidity": humidity,
            "Rainfall": rain
        })

        # Alerts
        if temp > 40:
            alerts.append(f"🔥 High Temperature Alert at {dt_txt}")

        if humidity > 85:
            alerts.append(f"💧 High Humidity Alert at {dt_txt}")

        if rain > 5:
            alerts.append(f"🌧️ Heavy Rain Alert at {dt_txt}")

    return records, alerts


# -------------------- SAVE REPORT --------------------
def save_report(records):

    df = pd.DataFrame(records)

    os.makedirs("reports", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"reports/weather_report_{timestamp}.csv"

    df.to_csv(filename, index=False)

    # ✅ FIXED LINE (correct variable name)
    shutil.copy(filename, "reports/latest_report.csv")

    print(f"\nReport saved: {filename}")

    return df


# -------------------- VISUALIZATION --------------------
def visualize(df, city):

    os.makedirs("outputs", exist_ok=True)

    plt.figure(figsize=(10, 5))

    plt.plot(df["Datetime"], df["Temperature"], marker='o')

    plt.xticks(rotation=45)

    plt.title(f"Temperature Forecast - {city}")

    plt.xlabel("Datetime")

    plt.ylabel("Temperature °C")

    plt.tight_layout()

    image_path = f"outputs/{city}_temperature.png"

    plt.savefig(image_path)

    print(f"Chart saved: {image_path}")


# -------------------- MAIN --------------------
def main():

    city = input("Enter city name: ")

    data = get_weather(city)

    if not data:
        print("Weather data not available")
        return

    records, alerts = analyze_weather(data)

    df = save_report(records)

    visualize(df, city)

    print("\nCurrent Forecast:\n")

    for record in records:
        print(record)

    print("\nGenerated Alerts:\n")

    if alerts:
        for alert in alerts:
            print(alert)
    else:
        print("No alerts generated")


if __name__ == "__main__":
    main()