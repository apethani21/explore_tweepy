import smtplib
import ssl
import string
import json
import sys
import os
import tweepy
import tweepy_utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def create_tweet_html_body(time, tweet):
    body = f"""\
    <html>
      <body>
        <p>
        <b> {time} </b><br>
        {tweet} <br>
        </p>
      </body>
    </html>
    """
    return body


def get_email_credentials():
    home = os.path.expanduser('~')
    with open(f"{home}/sender_config.json", "r") as f:
        config = json.loads(f.read())
    return config


def send_myself_message(message):
    email_credentials = get_email_credentials()
    receiver_email = email_credentials["receiver_email"]
    sender_email = email_credentials["sender_email"]
    if type(message) is MIMEMultipart:
        message["From"] = sender_email
        message["To"] = receiver_email
    password = email_credentials["sender_password"]
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com",
                          port=465,
                          context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
    return


def email_me_latest_tweets(handle='northernline', n=3):
    tweepy_auth = tweepy_utils.set_tweepy_account()
    api = tweepy.API(tweepy_auth)
    tweets = tweepy_utils.get_tweets(handle, n, api)
    message = MIMEMultipart("alternative")
    message["Subject"] = f"{handle} latest tweets"
    text = f"\n{tweets}"
    html = "".join([create_tweet_html_body(time, tweet)
                    for time, tweet in tweets.items()])
    plain_backup = MIMEText(text, "plain")
    html_main = MIMEText(html, "html")
    message.attach(plain_backup)
    message.attach(html_main)
    send_myself_message(message.as_string())
    return


if __name__ == "__main__":
    args = sys.argv[1:]
    args = dict([arg.split('=') for arg in args])
    handle = args.get('handle', 'northernline')
    number_of_tweets = int(args.get('n', 2))
    email_me_latest_tweets(handle, number_of_tweets)
