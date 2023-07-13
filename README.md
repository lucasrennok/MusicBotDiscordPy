# Music Bot

A bot made to play songs in a discord server.

## Requirements

- Python
- FFMPEG

## Step by Step

After downloading Python and FFMPEG (be aware that you have to configure it path at Environment Variables in your computer), download the repository and create a file called '.env' to place your bot credentials there.

You will find that credentials at:
https://discord.com/developers/applications

To get them you will have to create an Application and get the Application ID and the Token.
OBS.: Swipe all the Privileged Gateway Intents, that's important, so your bot can play the songs.

### Example of .env

You will find an example at .env.example, but it is also filled like this:

DISCORD_TOKEN = YOUR TOKEN HERE
BOT_ID = YOUR Application ID HERE

### Pip install

With an open terminal install with pip all the following packages.

- discord.py
- discord.py[voice]
- python-dotenv
- PyNaCl
- https://github.com/ytdl-org/youtube-dl/archive/refs/heads/master.zip
- ffmpeg

After that you will be able to run the application and wake up your bot.

_Run the following command:_ py -3 main.py --verbose

OBS.: If you receive package errors you will need just to install them with pip and try to run it again, if youtube-dl is the problem so you have to unninstall it and install again this package: https://github.com/ytdl-org/youtube-dl/archive/refs/heads/master.zip
