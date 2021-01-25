import tweepy
import os
import time
import redis
import dill

db = redis.Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'), db=0)


auth = tweepy.OAuthHandler(os.environ.get('API_KEY'), os.environ.get('API_KEY_SECRET'))
auth.set_access_token(os.environ.get('ACCESS_TOKEN'), os.environ.get('ACCESS_TOKEN_SECRET'))

api = tweepy.API(auth, wait_on_rate_limit=True)
me = api.me()
me_mention = f'@{me.screen_name}'

# noinspection PyBroadException
try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

if not db.get('since_id'):
    # noinspection PyBroadException
    try:
        tweet_id = tweepy.Cursor(api.mentions_timeline, count=1).items()[0].id
    except:
        tweet_id = 1
    db.set('since_id', tweet_id)

while True:
    # Rate limit for mentions timeline: once very 12 seconds
    # Rate limit for updates GET: once every second
    try:
        for tweet in tweepy.Cursor(api.mentions_timeline, since_id=int(db.get('since_id')), count=200).items():
            db.set('since_id', tweet.id)
            if not tweet.in_reply_to_status_id:
                continue
            if me_mention not in tweet.text:
                continue
            if tweet.user.id == me.id:
                continue
            for mention in tweet.entities['user_mentions']:
                if mention['screen_name'] != me.screen_name:
                    tweet.text = tweet.text.replace(f'@{mention["screen_name"]}', '')

            if tweet.text.strip() != me_mention:
                continue
            db.rpush('tweet_queue', dill.dumps(tweet))
    except Exception as e:
        print('Something fucked up: ' + str(e))
    time.sleep(15)
