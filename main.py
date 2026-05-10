import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# 1. Load your .env file (Make sure API_KEY=your_key is in there)
load_dotenv()
API_KEY = os.getenv("API_KEY")

# 2. CURRENT Weather URL (More accurate than Forecast for 'right now')
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    # Using exact coordinates for Hyderabad City Center to avoid the cooler airport station
    if city.lower() == "hyderabad":
        params = {"lat": 17.3850, "lon": 78.4867, "appid": API_KEY, "units": "metric"}
    else:
        params = {"q": city, "appid": API_KEY, "units": "metric"}

    try:
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

def main():
    print("--- Exact Weather System ---")
    city = input("Enter city name (e.g., Hyderabad): ")
    
    data = get_weather(city)
    
    if data:
        # 'feels_like' captures the urban heat—this matches your phone!
        actual_temp = data["main"]["temp"]
        phone_match_temp = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        condition = data["weather"][0]["description"]

        print(f"\n📍 Weather in {city.capitalize()}:")
        print(f"   Temperature (Phone Match): {phone_match_temp}°C")
        print(f"   Actual Station Air Temp: {actual_temp}°C")
        print(f"   Humidity: {humidity}%")
        print(f"   Condition: {condition.capitalize()}")

        # Save the report automatically
        os.makedirs("reports", exist_ok=True)
        report_df = pd.DataFrame([{
            "Time": datetime.now().strftime("%H:%M"),
            "Temp": phone_match_temp,
            "Humidity": humidity
        }])
        report_df.to_csv("reports/latest_report.csv", index=False)
        print("\n✅ Report saved to reports/latest_report.csv")
    else:
        print("❌ Could not fetch data. Check your API key in the .env file.")

if __name__ == "__main__":
    main()