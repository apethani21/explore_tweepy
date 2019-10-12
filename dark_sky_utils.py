import os
import time
import requests


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
    with open(f"{home}/dark_sky_key", "r") as f:
        dark_sky_key = f.read().rstrip("\n")
    return dark_sky_key


def get_weather(latitude=51.583017, longitude=-0.226472):
    api_key = get_dark_sky_key()
    url = f"https://api.darksky.net/forecast/{api_key}/{latitude},{longitude}"
    r = requests.get(url, params={"exclude": "currently,flags"})
    r.raise_for_status()
    return r.json()


def get_today_hour_minute(hour, minute):
    now = int(time.time())
    midnight = now - (now % 86400)
    return midnight + hour*3600 + minute*60


def get_weather_hour_minute(area, hour, minute=None):
    latitude_longitude = location[area]
    weather_data = get_weather(**latitude_longitude)
    if minute is None:
        minute = 0
    timestamp = get_today_hour_minute(hour, minute)
    data_block = weather_data["minutely"]
    overview = {
        "summary": data_block["summary"],
        "icon": data_block["icon"]
    }
    for datapoint in data_block["data"]:
        if datapoint["time"] == timestamp:
            minute_datapoint = datapoint
    return {"area": area, **minute_datapoint, **overview}


if __name__ == "__main__":
    pass
