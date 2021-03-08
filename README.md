# ace-attorney-twitter-bot

# No longer maintained. I recommend looking at https://github.com/LuisMayo/ace-attorney-twitter-bot instead

A port of the [Ace Attorney reddit bot](https://github.com/micah5/ace-attorney-reddit-bot) by [micah5](https://github.com/micah5) to Twitter.

Summon the bot by replying [@Objection_Bot_](https://twitter.com/Objection_Bot_/) to any Twitter thread involving two or more people.

This is still somewhat experimental and a bit of a hack job, so expect bugs and issues.

## Running
You'll need to clone the repository with `--recurse-submodules`. For example:
```
git clone --recurse-submodules git@github.com:DerpyChap/ace-attorney-twitter-bot.git
```

You'll also need the relevant game assets used for generating videos, which are not distributed with the repository as they're owned by Capcom. These should be put in a new folder called `./assets/`.

Docker and Docker Compose are needed for running the bot yourself. You'll also need an API key, a token and their secrets from the Twitter Developer Dashboard. Duplicate `.env.example` to `.env` and paste the keys there.

## Contributing
If you want to contribute improvements to the video generation, then you should do so at micah5's repo. I have a submodule set up pointing to it so any changes or improvements to that project can be easily brought over here.

Any other contributions are more than welcome. A quick rundown of the function of each Docker container:

 - `mentions_fetch` - Periodically pulls the latest @mentions to the bot and runs some simple checks to ensure it's a valid request, and then adds it to the queue in the database to be processed.
 - `thread_scraper` - Reads the `mentions_fetch` queue and scrapes the full thread up to the last 25 tweets, and does some simple filtering and normalising. These are then passed to another queue for video processing.
 - `video_processing` - Where the magic happens. Converts the threads queued up into their final video form, and runs a separate thread for sending out the replies.

The database used for this is Redis due to its speed and simplicity, making it ideal for caching data like this.
