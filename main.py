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


def already_posted(url, title=""):
    """Checks if the same url/title has already been posted in a previous run"""

    tweets = api.user_timeline(me.id_str)  # Brings the last 20 tweets
    base_domain = url.split("/")[2]
    title = title.lower().replace("<b>", "").replace("</b>", "")
    title_words = set(title.split())
    for t in tweets:
        try:
            if url == t.entities['urls'][0]["expanded_url"]:
                return True
            if base_domain in t.entities['urls'][0]["expanded_url"]:
                return True
            text2 = t.text.replace("#OpenScience ", "")
            text2 = text2[:text2.index("https")].lower().replace("<b>", "").replace("</b>", "")
            if title != "" and len((title_words.intersection(text2.split()))) > 0.6*len(title_words):
                return True
        except IndexError:
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
            # Use this one only if google alerts gives you irrelevant results:
            # and
            # set(entry["title"].lower().replace("<b>", "").replace("</b>", "").split()).intersection([your keywords here])
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
        if already_posted(actual_url, entry["title"]):
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
