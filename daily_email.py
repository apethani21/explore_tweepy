import os
import sys
import ssl
import json
import smtplib
import tweepy
import tweepy_utils
import dark_sky_utils
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_email_credentials():
    home = os.path.expanduser('~')
    with open(f"{home}/sender_config.json", "r") as f:
        config = json.loads(f.read())
    return config


def create_tweet_html_body(time, tweet):
    body = f"""\
        <b> {time} </b><br>
        {tweet} <br>
    """
    return body


def create_weather_html_body(weather_info):
    area = weather_info["area"].split('_')
    area_clean = ' '.join([word.capitalize() for word in area])
    ts = weather_info["time"]
    time_clean = datetime.fromtimestamp(ts).strftime("%d %b %H:%M:%S")
    body = f"""\
        <b>Time</b>: {time_clean} -- <b>{area_clean}</b> <br>
        <b>Summary</b>: {weather_info["summary"]} <br>
    """
    if "precipType" in weather_info:
        body += f"""
        <b>Chance of {weather_info["precipType"]}</b>: {weather_info["precipProbability"]} <br>
        <b>Intensity of {weather_info["precipType"]}</b>: {weather_info["precipIntensity"]} inch/hour <br>
        """
    return body


def get_raw_content(twitter_args={'screen_name': 'northernline',
                                  'tweet_count': 3},
                    dark_sky_args=[{'area': 'hendon_central',
                                    'hour': 7,
                                    'minute': 35},
                                   {'area': 'goodge_street',
                                    'hour': 8,
                                    'minute': 30}]):
    tweepy_auth = tweepy_utils.set_tweepy_account()
    api = tweepy.API(tweepy_auth)
    tweets = tweepy_utils.get_tweets(**twitter_args, api=api)
    print('tweets obtained')
    weather_updates = [dark_sky_utils.get_weather_hour_minute(**arg)
                       for arg in dark_sky_args]
    print('weather updates obtained')
    return {
        'twitter': tweets,
        'weather': weather_updates
    }


def create_email_body(raw_content):
    tweets = raw_content['twitter']
    twitter_text = f"\n{tweets}"
    twitter_html = "<br>".join([create_tweet_html_body(time, tweet)
                            for time, tweet in tweets.items()])
    weather_updates = raw_content['weather']
    weather_text = '\n'.join([str(update) for update in weather_updates])
    weather_html = "<br>".join([create_weather_html_body(update)
                            for update in weather_updates])
    html = f"""
        <html>
          <body>
            <p style="color:black;">
              <h2>Weather</h2> <br>
              {weather_html} <br>
              <hr>
              <h2>Travel</h2> <br>
              {twitter_html} <br>
            </p>
          </body>
        </html>
    """
    return {
        'text': '\n'.join([weather_text, twitter_text]),
        'html': html
    }


def send_myself_email(raw_content):
    email_credentials = get_email_credentials()
    receiver_email = email_credentials["receiver_email"]
    sender_email = email_credentials["sender_email"]
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Morning update"
    text = raw_content.get('text', 'FAILED TO GET TEXT')
    html = raw_content['html']
    plain_backup = MIMEText(text, "plain")
    html_main = MIMEText(html, "html")
    message["From"] = sender_email
    message["To"] = receiver_email
    message.attach(plain_backup)
    message.attach(html_main)
    password = email_credentials["sender_password"]
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com",
                          port=465,
                          context=context) as server:
        server.login(sender_email, password)
        print('sending message..')
        server.send_message(message, sender_email, receiver_email)
    return


def main(config):
    raw_content = get_raw_content(config)
    email_body = create_email_body(raw_content)
    send_myself_email(email_body)
    print('message sent')
    return


if __name__ == "__main__":
    args = sys.argv[1:]
    args = dict([arg.split('=') for arg in args])
    config_name = args['config']
    print(f"config: {config_name}")
    with open(f'./configs/{config_name}', 'r') as f:
        config = json.loads(f.read())
    main(**config)
