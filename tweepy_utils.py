import os
import time
from pprint import pprint
from twilio.rest import Client
import tweepy

def get_tweepy_auth():
    home = os.path.expanduser('~')
    with open(f"{home}/twitter_key", 'r') as f:
        twitter_key = f.read().rstrip('\n')
    with open(f"{home}/twitter_secret_key", 'r') as f:
        twitter_secret_key = f.read().rstrip('\n')
    with open(f"{home}/twitter_access_token", 'r') as f:
        twitter_access_token = f.read().rstrip('\n')
    with open(f"{home}/twitter_secret_access_token", 'r') as f:
        twitter_secret_access_token = f.read().rstrip('\n')
    return {
        "twitter_key": twitter_key,
        "twitter_secret_key": twitter_secret_key,
        "twitter_access_token": twitter_access_token,
        "twitter_secret_access_token": twitter_secret_access_token
    }

def set_tweepy_account():
    credentials = get_tweepy_auth()
    auth = tweepy.OAuthHandler(credentials["twitter_key"],
                               credentials["twitter_secret_key"])
    auth.set_access_token(credentials["twitter_access_token"],
                          credentials["twitter_secret_access_token"])
    return auth

def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            print("Rate Limited. Sleeping.")
            time.sleep(60)
            
def get_tweets(screen_name, tweet_count):
    counter = tweet_count
    timeline_obj = []
    while len(timeline_obj) < tweet_count:
        timeline_obj = api.user_timeline(
                                    screen_name=screen_name,
                                    count=counter,
                                    exclude_replies=True,
                                    tweet_mode="extended"
                            )
        counter += 5
    tweets = {twt.created_at.strftime("%d-%m-%y %H:%H:%S"): 
              twt.full_text.replace('\n', ' ')
              for twt in timeline_obj}
    return dict((list(tweets.items())[:tweet_count]))


if __name__ == "__main__":
    tweepy_auth = set_tweepy_account()
    api = tweepy.API(tweepy_auth)
    pprint(get_tweets('northernline', 3))
