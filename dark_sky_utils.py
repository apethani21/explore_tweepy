import os
import time
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_me_tweets import send_myself_message


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
    midnight = datetime.utcfromtimestamp(now - (now % 86400))
    morning = midnight + timedelta(hours=hour, minutes=minute)
    return int(morning.strftime("%s"))


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


def create_weather_html_body(weather_info):
    area = weather_info["area"].split('_')
    area_clean = ' '.join([word.capitalize() for word in area])
    ts = weather_info["time"]
    time_clean = datetime.fromtimestamp(ts).strftime("%d %b %H:%M:%S")
    body = f"""\
    <html>
      <body>
        <p>
        <b>Time</b>: {time_clean} -- <b>{area_clean}</b> <br>
        <b>Summary</b>: {weather_info["summary"]} <br>
        <b>Chance of {weather_info["precipType"]}</b>: {weather_info["precipProbability"]} <br>
        <b>Intensity of {weather_info["precipType"]}</b>: {weather_info["precipIntensity"]} inch/hour <br>
        </p>
      </body>
    </html>
    """
    return body


def email_me_latest_weather(weather_updates):
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Weather update"
    text = '\n'.join([str(update) for update in weather_updates])
    html = "".join([create_weather_html_body(update) for update in weather_updates])
    plain_backup = MIMEText(text, "plain")
    html_main = MIMEText(html, "html")
    message.attach(plain_backup)
    message.attach(html_main)
    send_myself_message(message.as_string())
    return


if __name__ == "__main__":
    hendon_weather_update = get_weather_hour_minute("hendon_central", 16, 15)
    fitzrovia_weather_update = get_weather_hour_minute("goodge_street", 16, 30)
    email_me_latest_weather([hendon_weather_update, fitzrovia_weather_update])
