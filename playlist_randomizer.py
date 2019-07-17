from functools import wraps
import spotipy
import telegram
from spotipy import util
import random
import os
from telegram.ext import Updater, CommandHandler

BOT_TOKEN = os.environ.get('BOT_TOKEN')
SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.environ.get('SPOTIPY_REDIRECT_URI')
HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME")
SONGS_TO_SHOW = os.getenv("SONGS_TO_SHOW")
ADMIN = os.getenv("ADMIN")
PORT = os.environ.get('PORT','8443')
user = os.environ.get('USER')
cache = os.environ.get('SPOTIPY_CACHE')
scope = 'user-library-read playlist-modify-public playlist-modify-private user-top-read'

#Save spotipy cache
f = open(".cache-{}".format(user), "w+")
f.write(cache)
f.close()

spotify_token = util.prompt_for_user_token(user, scope, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI)

#SPOTIFY FUNCTIONS

def get_tracks_uri(tracks):
    uris = []
    for track in tracks:
        uris.append(track['track']['uri'])
    return uris

def get_playlists(spotify_token):
    if spotify_token:
        sp = spotipy.Spotify(auth=spotify_token)
        sp.trace = False
        playlists = sp.current_user_playlists()
        result = []
        for playlist in playlists['items']:
            result.append((playlist['id'],playlist['name']))
        return result

def get_playlist_tracks(spotify_token,playlist_id):
    if spotify_token:
        sp = spotipy.Spotify(auth=spotify_token)
        results = sp.user_playlist_tracks(user,playlist_id)
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        return tracks

def randomize_tracks(spotify_token,playlist_id,tracks):
    if spotify_token:
        sp = spotipy.Spotify(auth=spotify_token)
        random.shuffle(tracks)
        sp.user_playlist_remove_all_occurrences_of_tracks(user,playlist_id,tracks)
        sp.user_playlist_add_tracks(user,playlist_id,tracks)
        return True

def info(spotify_token):
    if spotify_token:
        sp = spotipy.Spotify(auth=spotify_token)
        long_term = sp.current_user_top_tracks(limit=int(SONGS_TO_SHOW), time_range="long_term")
        medium_term = sp.current_user_top_tracks(limit=int(SONGS_TO_SHOW), time_range="medium_term")
        short_term = sp.current_user_top_tracks(limit=int(SONGS_TO_SHOW), time_range="short_term")
        return long_term['items'], medium_term['items'], short_term['items']

#TELEGRAM BOT

def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = context.message.from_user.id
        if str(user_id) != str(ADMIN):
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped

def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu

@restricted
def get_playlists_handler(bot, update):
    playlists = get_playlists(spotify_token)
    answer = "Write /randomize <playlist_id>\nChoose between these playlists:"
    update.message.reply_text("Write /randomize <playlist_id> "
                              "Choose between these playlists:")
    for playlist in playlists:
        update.message.reply_text(playlist[1] + " [" + playlist[0] + "]",parse_mode=telegram.ParseMode.MARKDOWN)

@restricted
def randomize_playlist_handler(bot, update):
    if (len(update.message.text.split(" ")) == 2):
        playlist_id = update.message.text.split(" ")[1]
        tracks = get_tracks_uri(get_playlist_tracks(spotify_token,playlist_id))
        random.shuffle(tracks)
        chunks = [tracks[x:x + 10] for x in range(0, len(tracks), 10)]
        for chunk in chunks:
            randomize_tracks(spotify_token,playlist_id,chunk)
        update.message.reply_text("Playlist randomized")
    else:
        update.message.reply_text("Wrong parameters number")

@restricted
def start_handler(bot, update):
    lms = info(spotify_token)
    answer = "*Your long term {} favourite songs:*\n".format(SONGS_TO_SHOW)
    for idx,song in enumerate(lms[0]):
        answer += str(idx+1) + ". " + song['name'] + ' - ' + song['artists'][0]['name'] + '\n'
    answer += "\n"
    answer += "*Your mid term {} favourite songs:*\n".format(SONGS_TO_SHOW)
    for idx,song in enumerate(lms[1]):
        answer += str(idx+1) + ". " + song['name'] + ' - ' + song['artists'][0]['name'] + '\n'
    answer += "\n"
    answer += "*Your short term {} favourite songs:*\n".format(SONGS_TO_SHOW)
    for idx,song in enumerate(lms[2]):
        answer += str(idx+1) + ". " + song['name'] + ' - ' + song['artists'][0]['name'] + '\n'
    answer += "\n"
    update.message.reply_text(answer,parse_mode=telegram.ParseMode.MARKDOWN)

if __name__ == '__main__':
    print("Starting the bot")
    updater = Updater(BOT_TOKEN)
    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.dispatcher.add_handler(CommandHandler("playlists", get_playlists_handler))
    updater.dispatcher.add_handler(CommandHandler("randomize", randomize_playlist_handler))
    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=BOT_TOKEN)
    updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, BOT_TOKEN))