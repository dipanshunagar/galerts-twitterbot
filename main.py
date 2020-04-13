import feedparser
import tweepy
import requests
import urllib
import re
import random
from time import sleep

from flask import Flask, jsonify

app = Flask(__name__)

# Twitter dev app details
consumer_key = "xxxxxxxxxx"
consumer_secret = "xxxxxxxxxx"
access_token = "xxxxxxxxxx"
access_token_secret = "xxxxxxxxxx"

# Login to the twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
me = api.me()

tweet_mode = True
print("Tweet mode is", tweet_mode)

galerts_rss = ""  # Your google alert RSS feed URL
banned_words = ["stock", "image", "photo"]  # If either of these appears in a URL, that URL will not be posted


def working(url):
    """Checks whether the URL returns with a 200 status code"""
    return requests.get(url).status_code == 200


def already_posted(url):
    """Checks if the exact same url has already been posted in a previous run"""
    tweets = api.user_timeline(api.me().id_str)  # Brings the last 20 tweets
    base_domain = url.split("/")[2]
    for t in tweets:
        try:
            if url == t.entities['urls'][0]["expanded_url"]:
                return True
            # You may not need this check, but it was relevant to my use case:
            if base_domain in t.entities['urls'][0]["expanded_url"]:
                return True
        except IndexError:  # In case an old tweet doesn't have a URL, can occur if you tweet manually too.
            pass
    return False


@app.route("/news/autotweet")
def do_the_stuff():
    rss = feedparser.parse(galerts_rss)
    entries = rss["entries"]

    #  Some additional filtering, because not all GAlerts links are good
    entries = filter(
        lambda entry: (
            entry["title"].count(" ") > 3
            and
            set(entry["title"].lower().replace("<b>", "").replace("</b>", "").split()).intersection(["open", "access"])
            and
            not any([w in entry["link"] for w in banned_words])
        ),
        entries
    )
    tweet_count = 0
    for entry in entries:
        actual_url = re.findall(r"(?<=url=).*(?=&ct)", entry["link"])[0]
        if not working(actual_url) or len(actual_url) < 25:
            print("NOT WORKING:", actual_url, "\n")
            continue
        if already_posted(actual_url):
            print("Already posted:", actual_url, "\n")
            continue
        if not actual_url.startswith("http"):
            actual_url = "http://"+actual_url
        print("Going to tweet:", entry["title"])
        print(actual_url)
        if tweet_mode:
            api.update_status("#OpenScience "+actual_url)
            tweet_count += 1
            sleep_duration = random.randint(10, 30)
            print(f"Sleeping for {sleep_duration} seconds.")
            sleep(sleep_duration)
        print()
    return jsonify({"status": "finished", "tweets_posted": tweet_count})


if __name__ == "__main__":
    app.run("0.0.0.0")
