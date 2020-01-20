import os
import time
import requests
from datetime import datetime, timedelta


location = {
    "hendon_central": {
        "latitude": 51.583017,
        "longitude": -0.226472
    },
    "goodge_street": {
        "latitude": 51.520581,
        "longitude": -0.134331
    }
}


def get_dark_sky_key():
    home = os.path.expanduser('~')
    with open(f"{home}/keys/dark_sky/dark_sky_key", "r") as f:
        dark_sky_key = f.read().rstrip("\n")
    return dark_sky_key


def get_weather(latitude, longitude):
    api_key = get_dark_sky_key()
    url = f"https://api.darksky.net/forecast/{api_key}/{latitude},{longitude}"
    r = requests.get(url, params={"exclude": "currently,flags"})
    r.raise_for_status()
    return r.json()


def get_today_hour_minute(hour, minute):
    now = int(time.time())
    midnight = now - (now % 86400)
    midnight = datetime.utcfromtimestamp(midnight)
    day = midnight + timedelta(hours=hour, minutes=minute)
    return int(day.strftime("%s"))


def get_weather_hour_minute(area, hour, minute=None):
    latitude_longitude = location[area]
    weather_data = get_weather(**latitude_longitude)
    if minute is None:
        minute = 0
    timestamp = get_today_hour_minute(hour, minute)
    overview = {
        "day_summary": weather_data["hourly"].get("summary"),
        "summary": weather_data["minutely"]["summary"],
        "icon": weather_data["minutely"]["icon"],
    }
    for datapoint in weather_data["minutely"]["data"]:
        if datapoint["time"] == timestamp:
            minute_datapoint = datapoint
    return {"area": area, **minute_datapoint, **overview}
