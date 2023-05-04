import random
import timeit

import pandas as pd
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from sklearn.preprocessing import StandardScaler
#from numpy import argmax
import pickle
from os import getenv
from dotenv import load_dotenv

load_dotenv(".env")

def cleanDuplicates(tracks):
    grouped = tracks.groupby(
        ['artist_name', 'track_name'], as_index=True).size()
    grouped[grouped > 1].count()
    tracks.drop_duplicates(subset=['artist_name', 'track_name'], inplace=True)


def dropColumns(df_audio_features):
    columns_to_drop = ['analysis_url', 'track_href',
                       'type', 'key', 'mode', 'time_signature', 'uri']
    df_audio_features.drop(columns_to_drop, axis=1, inplace=True)

    df_audio_features.rename(columns={'id': 'track_id'}, inplace=True)

    return df_audio_features.shape


def mergeDataframes(df_tracks, df_audio_features):
    # merge both dataframes
    # the 'inner' method will make sure that we only keep track IDs present in both datasets
    df = pd.merge(df_tracks, df_audio_features, on='track_id', how='inner')

    return df


def getRandomSearch():
    # A list of all characters that can be chosen.
    characters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                  'u', 'v', 'w', 'x', 'y', 'z']

    # Gets a random character from the characters string.
    randomCharacter = characters[random.randint(0, 25)]

    # Places the wildcard character at the beginning, or both beginning and end, randomly.
    switcher = random.randint(0, 1)
    if switcher == 0:
        randomSearch = randomCharacter + '%'
    else:
        randomSearch = '%' + randomCharacter + '%'

    return randomSearch


class MusicMoodClassifier:
    def __init__(self):
        self.cid = getenv("SPOTIFY_CLIENT_ID", None) #"a006ea8174bc4689b4eb39c47b5449a1"
        self.secret = getenv("SPOTIFY_CLIENT_SECRET", None) #"1cca3d1fff6145fdaee72ba822e8b586"
        self.playlist_id = getenv("SPOTIFY_PLAYLIST_ID", "6FDF6e5kvOAm7Jm4kh31OZ") #"6FDF6e5kvOAm7Jm4kh31OZ"
        self.scope = 'user-read-private user-read-playback-state user-modify-playback-state user-top-read playlist-modify-private playlist-modify-public'
        self.token = util.prompt_for_user_token(
                                client_id=self.cid,
                                client_secret=self.secret,
                                redirect_uri='http://localhost:'+ getenv('PORT', '7483'),
                                scope=self.scope
                            )

        self.sp = spotipy.Spotify(self.token)
        self.estimator = pickle.load(open('data/music_model_knn_new.pkl', 'rb'))

    def getTracks(self, number):
        start = timeit.default_timer()

        # create empty lists where the results are going to be stored
        tracks = {
            'artist_name': [],
            'track_name': [],
            'popularity': [],
            'track_id': []
        }

        for i in range(0, number, 10):

            track_results = self.sp.search(
                q=getRandomSearch(), type='track', limit=10, offset=i)
            for i, t in enumerate(track_results['tracks']['items']):
                tracks['artist_name'].append(t['artists'][0]['name'])
                tracks['track_name'].append(t['name'])
                tracks['track_id'].append(t['id'])
                tracks['popularity'].append(t['popularity'])

        stop = timeit.default_timer()
        print(f'Time to run this code (getTracks - {number}): {stop - start}')
        return pd.DataFrame(tracks)

    def getAudioFeatures(self, tracks):
        # again measuring the time
        start = timeit.default_timer()

        # empty list, batchsize and the counter for None results
        rows = []
        batchsize = 100
        none_counter = 0

        for i in range(0, len(tracks['track_id']), batchsize):
            batch = tracks['track_id'][i:i + batchsize]
            feature_results = self.sp.audio_features(batch)
            for i, t in enumerate(feature_results):
                if t == None:
                    none_counter = none_counter + 1
                    # rows.append(t)
                else:
                    rows.append(t)

        if none_counter:
            print(
                'Number of tracks where no audio features were available:', none_counter)

        stop = timeit.default_timer()
        print(
            f'Time to run this code (getAudioFeatures - { len(rows) }): {stop - start}')
        df_audio_features = pd.DataFrame.from_dict(rows, orient='columns')
        return df_audio_features

    def getTypicalTracks(self, typicalMood):
        test = self.getTracks(100 if typicalMood == 0 else 50)
        cleanDuplicates(test)
        test_features = self.getAudioFeatures(test)
        dropColumns(test_features)
        df_test = mergeDataframes(test, test_features)
        test_col_features = df_test.columns[4:13]
        df_test_features = df_test[test_col_features]

        df_test_features = StandardScaler().fit_transform(df_test_features)
        mood_preds_test = self.estimator.predict(df_test_features)
        IDs = list(test['track_id'])

        # Filter predictions with required mood
        results = [IDs[x] for x, mood in enumerate(mood_preds_test) if mood == typicalMood]

        # retry if there are no no songs with required mood
        if not results:
            return self.getTypicalTracks(typicalMood)
        
        # print(len(results), results)
        # playlist = ['6vN77lE9LK6HP2DewaN6HZ', '3AJwUDP919kvQ9QcozQPxg', '2UikqkwBv7aIvlixeVXHWt', '7zwn1eykZtZ5LODrf7c0tS', '0xaFw2zDYf1rIJWl2dXiSF', '6tB01QHgH9YuVA8TomAzni', '3d8y0t70g7hw2FOWl9Z4Fm', '7t2bFihaDvhIrd2gn2CWJO', '0WrIAsGJOei2FGeakvpTDU', '40riOy7x9W7GXjyGp4pjAv', '1bDbXMyjaUIooNwFE9wn0N', '7oDd86yk8itslrA9HRP2ki', '59nOXPmaKlBfGMDeOVGrIK', '73zawW1ttszLRgT9By826D', '7fveJ3pk1eSfxBdVkzdXZ0', '2Ch7LmS7r2Gy2kc64wv3Bz', '1Y3LN4zO1Edc2EluIoSPJN', '2aw1aEAxMe05MZIS5XiK8U', '5XeFesFbtLpXzIVDNQP22n']

        self.sp.playlist_replace_items(self.playlist_id, results)

        return "https://open.spotify.com/playlist/" + self.playlist_id       

        # result = self.sp.track(results[0])
        # ResponseResult = [result['name'], "https://open.spotify.com/track/" +
        #                   result['id'], result['album']['images'][0]['url']]
        # return ResponseResult


if __name__ == "__main__":
    abc = MusicMoodClassifier()
    print(abc.getTypicalTracks(3))
