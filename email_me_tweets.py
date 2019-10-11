import smtplib
import ssl
import string
import json
import sys
import os
import tweepy
import tweepy_utils


def get_email_credentials():
    home = os.path.expanduser('~')
    with open(f"{home}/sender_config.json", "r") as f:
        config = json.loads(f.read())
    return config


def send_myself_message(message):
    email_credentials = get_email_credentials()
    receiver_email_address = email_credentials["receiver_email"]
    sender_email_address = email_credentials["sender_email"]
    password = email_credentials["sender_password"]
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com",
                          port=465,
                          context=context) as server:
        server.login(sender_email_address, password)
        server.sendmail(sender_email_address, receiver_email_address, message)
    return


def email_me_latest_tweets(handle='northernline', n=3):
    tweepy_auth = tweepy_utils.set_tweepy_account()
    api = tweepy.API(tweepy_auth)
    tweets = tweepy_utils.get_tweets(handle, n, api)
    printable = set(string.printable)
    clean_tweets = ''.join(filter(lambda x: x in printable, str(tweets)))
    send_myself_message(f"\n{clean_tweets}")
    return


if __name__ == "__main__":
    args = sys.argv[1:]
    args = dict([arg.split('=') for arg in args])
    email_me_latest_tweets(**args)
