import tweepy
import os
import time
import redis
from reddit_bot import anim
from collections import Counter

db = redis.Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'), db=0)


# Original script expects a praw.models.Comment model, so let's give it something close enough
class DummyComment:
    def __init__(self, t):
        self.body = t.full_text
        self.score = 0
        self.author = DummyAuthor(t.user)


class DummyAuthor:
    def __init__(self, user):
        self.name = f'@{user.screen_name}'


auth = tweepy.OAuthHandler(os.environ.get('API_KEY'), os.environ.get('API_KEY_SECRET'))
auth.set_access_token(os.environ.get('ACCESS_TOKEN'), os.environ.get('ACCESS_TOKEN_SECRET'))

api = tweepy.API(auth, wait_on_rate_limit=True)
me = api.me()
me_mention = f'@{me.screen_name}'

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

if not db.get('since_id'):
    db.set('since_id', 1)

while True:
    print("Fetching mentions")
    # Rate limit for mentions timeline: once very 12 seconds
    # Rate limit for updates GET: once every second
    for tweet in tweepy.Cursor(api.mentions_timeline, since_id=int(db.get('since_id'))).items():
        # TODO: Create database for completed requests
        # TODO: Use threading or something to cache latest mentions into a database
        # TODO: Use threading or something to process tweet threads for video generation
        # TODO: Use threading or something to create worker threads for generating the videos
        # TODO: Use threading or something to post the videos
        # TODO: Properly set source device metadata
        # TODO: Convert potentially troublesome characters into standard letters where applicable
        # TODO: Language filter
        # TODO: Better error handling

        print(tweet)
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
        tweets = []
        # try:
        last_tweet = api.get_status(tweet.in_reply_to_status_id, tweet_mode='extended')
        # except:
        #     continue
        print('Iterating over thread...')
        for x in range(0, 50):
            print(last_tweet)
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
        api.update_status(f'@{tweet.user.screen_name}', in_reply_to_status_id=tweet.id, media_ids=[file.media_id_string])

    time.sleep(30)
