# SpotifyTelegramBot
A python based Telegram bot for the management of Spotify account.

This Bot is based on Spotipy and python-telegram-bot, in order to use it you must register to Spotify developer program and obtain your access credentials.

## Functions
The principle function of this bot is the playlist randomizer, i decided to implement it because i noticed that the spotify's shuffle doesn't work correctly, with this implementation you can randomize your personal playlists before playing them and always listen all the different songs your playlist contains.

The bot currently supports three functions:
  * **/start** = shows some lists of your favourite songs (short-term, mid-term and long-term)
  * **/playlists** = shows your playlists with their names and ids
  * **/randomize <playlist_id>** = randomizes the songs in the playlist you provide
  
More functions will probably be added later.

## Heroku Deploy
This repository has all the needed files to deploy it on Heroku, the only thing you must add are these environment variables:
  * **BOT_TOKEN** = the telegram bot token
  * **SPOTIPY_CLIENT_ID**
  * **SPOTIPY_CLIENT_SECRET**
  * **HEROKU_APP_NAME**
  * **SONGS_TO_SHOW** = needed to the /start function, it's the number of songs spotipy will get (personally i keep it to 30)
  * **SPOTIPY_CACHE** = the authorization cache spotipy needs to work, more information about it above
  * **ADMIN** = your telegram user id
  * **PORT** = the port for the telegram webhook (currently telegram supports 443, 80, 88, 8443)
  * **USER** = your spotify username
  
### Obtain Spotipy Cache
In order to make spotipy work, spotify needs to authorize you with a browser authentication (more informations here: [Spotify Authorization Guide](https://developer.spotify.com/documentation/general/guides/authorization-guide/)); this authentication, once done, is saved by spotipy in a hidden file called **.cache-YourSpotifyUsername**.

Since heroku cannot provide a web browser for you to authenticate you must do as follows:
1. Write a simple Spotipy action on a Python code
1. Run it and obtain browser authorization link
1. Once you authorized your device open the **.cache-YourSpotifyUsername** file that was created and copy the content
1. Paste the content into the **SPOTIPY_CACHE** environment variable on Heroku, my Python script will do the other tasks to make things work.

I'll link [here](https://spotipy.readthedocs.io/en/latest/#) spotipy docs for you to better understand how to make things work.
