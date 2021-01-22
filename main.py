import tweepy
import os
import time
from reddit_bot import anim
from collections import Counter


# Original script expects a praw.models.Comment model, so let's give it something close enough
class DummyComment():
    def __init__(self, t):
        self.body = t.text
        self.score = 0
        self.author = DummyAuthor(t.user)


class DummyAuthor():
    def __init__(self, user):
        self.name = f'@{user.screen_name}'


auth = tweepy.OAuthHandler(os.environ.get('API_KEY'), os.environ.get('API_KEY_SECRET'))
auth.set_access_token(os.environ.get('ACCESS_TOKEN'), os.environ.get('ACCESS_TOKEN_SECRET'))

api = tweepy.API(auth, wait_on_rate_limit=True)
me = api.me()
try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

since_id = 1
while True:
    print("Fetching mentions")
    for tweet in tweepy.Cursor(api.mentions_timeline, since_id=since_id).items():
        print(tweet)
        since_id = tweet.id
        if not tweet.in_reply_to_status_id:
            continue
        if f'@{me.screen_name}' not in tweet.text:
            continue
        if tweet.user.id == me.id:
            continue
        tweets = []
        last_tweet = api.get_status(tweet.in_reply_to_status_id)
        print('Iterating over thread...')
        for x in range(0, 50):
            print(tweet)
            tweets.append(last_tweet)
            if not last_tweet.in_reply_to_status_id:
                break
            try:
                last_tweet = api.get_status(last_tweet.in_reply_to_status_id)
            except:
                print('Failed to get last_tweet')
                break
        tweets.reverse()
        tweets = [DummyComment(t) for t in tweets]
        authors = [tweet.author.name for tweet in tweets]
        most_common = [t[0] for t in Counter(authors).most_common()]
        if len(most_common) <= 1:
            continue
        print(tweets)
        # Generate video
        print('Generating video')
        output_filename = f"{tweet.id}.mp4"
        characters = anim.get_characters(most_common)
        anim.comments_to_scene(tweets, characters, output_filename=output_filename)

        file = api.media_upload(output_filename)
        api.update_status(in_reply_to_status_id=tweet.id, media_ids=[file.media_id_string])

    time.sleep(30)
