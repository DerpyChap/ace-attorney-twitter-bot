import tweepy
import os
import redis
import time
import dill
import threading
from reddit_bot import anim
from collections import Counter

db = redis.Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'), db=0)

auth = tweepy.OAuthHandler(os.environ.get('API_KEY'), os.environ.get('API_KEY_SECRET'))
auth.set_access_token(os.environ.get('ACCESS_TOKEN'), os.environ.get('ACCESS_TOKEN_SECRET'))

api = tweepy.API(auth, wait_on_rate_limit=True)
me = api.me()
me_mention = f'@{me.screen_name}'


def reply_thread():
    while True:
        r_out = db.lpop('reply_queue')
        if r_out:
            r_tweet = dill.loads(r_out)
            file = api.media_upload(f'video_cache/{r_tweet.id}.mp4')
            api.update_status(f'@{r_tweet.user.screen_name}', in_reply_to_status_id=r_tweet.id, media_ids=[file.media_id_string])
            os.remove(f'video_cache/{r_tweet.id}.mp4')
            time.sleep(36)
        time.sleep(0.01)


t = threading.Thread(target=reply_thread)
t.start()


while True:
    out = db.lpop('video_queue')
    if out:
        tweet, authors, tweets = dill.loads(out)

        most_common = [t[0] for t in Counter(authors).most_common()]
        output_filename = f'{tweet.id}.mp4'
        characters = anim.get_characters(most_common)
        anim.comments_to_scene(tweets, characters, output_filename=output_filename)
        if not os.path.exists('video_cache'):
            os.makedirs('video_cache')
        os.replace(output_filename, f'video_cache/{output_filename}')
        db.rpush('reply_queue', dill.dumps(tweet))
