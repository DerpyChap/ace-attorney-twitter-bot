import tweepy
import os
import redis
import time
import dill
from collections import Counter


# Original script expects a praw.models.Comment model, so let's give it something close enough
class DummyComment:
    def __init__(self, t):
        self.body = t.full_text
        self.score = 0
        self.author = DummyAuthor(t.user)


class DummyAuthor:
    def __init__(self, user):
        self.name = f'@{user.screen_name}'


db = redis.Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'), db=0)

auth = tweepy.OAuthHandler(os.environ.get('API_KEY'), os.environ.get('API_KEY_SECRET'))
auth.set_access_token(os.environ.get('ACCESS_TOKEN'), os.environ.get('ACCESS_TOKEN_SECRET'))

api = tweepy.API(auth, wait_on_rate_limit=True)
me = api.me()
me_mention = f'@{me.screen_name}'

while True:
    out = db.lpop('tweet_queue')
    if out:
        tweet = dill.loads(out)
        try:
            last_tweet = api.get_status(tweet.in_reply_to_status_id, tweet_mode='extended')
        except:
            continue

        tweets = []
        print('Iterating over thread...')
        for x in range(0, 50):
            # I think there should be a better solution for stripping mentions and URLs than this but oh well
            for mention in last_tweet.entities['user_mentions']:
                if not last_tweet.full_text.startswith('@'):
                    break
                last_tweet.full_text.replace(f'@{mention["screen_name"]}', '')
                last_tweet.full_text = last_tweet.full_text.replace(f'@{mention["screen_name"]}', '').lstrip()
            for url in last_tweet.entities['urls']:
                last_tweet.full_text = last_tweet.full_text.replace(url['url'], '[link]')
            last_tweet.full_text = last_tweet.full_text.strip()
            if not last_tweet.full_text:
                last_tweet.full_text = '...'
            tweets.append(last_tweet)
            if not last_tweet.in_reply_to_status_id:
                break
            try:
                last_tweet = api.get_status(last_tweet.in_reply_to_status_id, tweet_mode='extended')
            except:
                print('Failed to get last_tweet')
                break
        if tweets:
            tweets.reverse()
            tweets = [DummyComment(t) for t in tweets]
            authors = [tweet.author.name for tweet in tweets]
            if len(authors) <= 1:
                continue
            db.rpush('video_queue', dill.dumps((tweet, authors, tweets)))
    time.sleep(0.01)