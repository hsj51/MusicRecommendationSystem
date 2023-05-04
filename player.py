from dotenv import load_dotenv
from os import getenv
import customtkinter as ctk

# Spotify API Library
import spotipy
import spotipy.util as util

# Image library
#import imageio
from PIL import Image

import requests
from urllib.request import urlopen

from io import BytesIO

import webbrowser
# controller = webbrowser.Chrome
# controller = webbrowser.get('firefox')


load_dotenv(".env")

# Spotify API ID and Key
# CLIENT_ID = "2c63ae3585d34835b04b34971282a731"
# CLIENT_SECRET = "ed953ad432654ed796e9083db7174639"

CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", None)

class SpotifyFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):

        super().__init__(master, **kwargs)

        # get variables from .env file
        self.cid = getenv("SPOTIFY_CLIENT_ID", None) #"a006ea8174bc4689b4eb39c47b5449a1"
        self.secret = getenv("SPOTIFY_CLIENT_SECRET", None) #"1cca3d1fff6145fdaee72ba822e8b586"
        self.scope = 'user-read-private user-read-playback-state user-modify-playback-state user-top-read playlist-modify-private playlist-modify-public'
        self.token = util.prompt_for_user_token(
                                client_id=self.cid,
                                client_secret=self.secret,
                                redirect_uri='http://localhost:'+ getenv('PORT', '7483'),
                                scope=self.scope
                            )
        # initialize the spotify client
        self.sp = spotipy.Spotify(self.token)

        self.sp.trace = False

        # Class member variables
        self.playlistID = getenv("SPOTIFY_PLAYLIST_ID", "6FDF6e5kvOAm7Jm4kh31OZ") #"6FDF6e5kvOAm7Jm4kh31OZ"
        self.playingNow = False
        self.volume = 0
        self.currentTrackID = 0
        self.songs_label = []

        # Connect UI components to methods
        # self.pausePlay.clicked.connect(self.pausePlayPressed)
        # self.nextPB.clicked.connect(self.nextPressed)
        # self.prevPB.clicked.connect(self.prevPressed)
        # self.volSlider.valueChanged.connect(self.volSliderMoved)
        # self.changeDeviceCombo.currentIndexChanged.connect(self.deviceComboIndexChanged)
        # self.searchEdit.textEdited.connect(self.searching)

        # Device options QComboBox

        # self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.checkForSongChange)
        # self.timer.start(2000) #trigger every 2 secs

        img = Image.open(
            urlopen('https://i.scdn.co/image/ab67616d00001e02004e1366643f4549ce81dfd0'))
        sp_img = ctk.CTkImage(img, size=(300, 300))

        # add widgets onto the frame...
        # self.label = ctk.CTkLabel(self, text='Spotify')
        # self.label.grid(row=0, =0, padx=10, sticky=ctk.N)

        self.playlist_image_label = ctk.CTkLabel(self, text='', image=sp_img)
        self.playlist_image_label.grid(
            row=0, column=0, columnspan=3, padx=10, pady=10)

        self.playlist_btn = ctk.CTkButton(
            self, text="Open Playlist", command=self.open_playlist, width=100)
        self.playlist_btn.grid(row=1, column=0, padx=5, pady=5)

        # self.play_pause_btn = ctk.CTkButton(self, text="Play/Pause", width=100, command=self.pausePlayPressed)
        # self.play_pause_btn.grid(row=1, column=1, padx=0, pady=0)

        self.device_combo = ctk.CTkComboBox(self, command=self.deviceComboChanged, width=200)
        self.device_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        # self.device_combo.set(self.devices.values()[0])

        self.play_pause_btn = ctk.CTkButton(self, text="Prev Song", width=100, command=self.prevPressed)
        self.play_pause_btn.grid(row=2, column=0, padx=0, pady=0)

        self.play_pause_btn = ctk.CTkButton(self, text="Play/Pause", width=100, command=self.pausePlayPressed)
        self.play_pause_btn.grid(row=2, column=1, padx=0, pady=0)

        self.play_pause_btn = ctk.CTkButton(self, text="Next Song", width=100, command=self.nextPressed)
        self.play_pause_btn.grid(row=2, column=2, padx=0, pady=0)
        # self.emotion_label = ctk.CTkLabel(self, text="Place Holder")
        # self.emotion_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Add a scrollable frame for song list
        self.songs_frame = ctk.CTkScrollableFrame(self, height=100, width=300)
        self.songs_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        self.populateDeviceComboboxes()
        self.updatePlaylistTracks()
        self.updateCurrentTrack()

    def checkForSongChange(self):
        """
        check if user is playing the playlist created by the recommendation system
        """
        curr = self.sp.currently_playing()
        if(curr["item"]["id"] != self.currentTrackID):
            self.updateCurrentTrack()

    def volSliderMoved(self):
        """
        event handler for volume slider
        """
        self.volume = int(self.volSlider.value())
        self.sp.volume(self.volume)
        return

    def nextPressed(self):
        """
        event handler for playing next song
        """
        self.sp.next_track()
        self.updateCurrentTrack()
        return

    def prevPressed(self):
        """
        event handler for playing previous song
        """
        self.sp.previous_track()
        self.updateCurrentTrack()
        return

    def populateDeviceComboboxes(self):
        """
        Update active devices list
        """
        allDevices = self.sp.devices()
        devices = {d["id"]: d["name"] for d in allDevices["devices"]}

        self.device_combo.configure(values=devices.values())

        for device in allDevices["devices"]:
            if device["is_active"] == True:
                self.device_combo.set(device["name"])
                self.currentDeviceID = device["id"]
                return True
        else:
            # if devices are available but none are active
            if devices:
                for id, name in devices.items():
                    self.sp.transfer_playback(id)
                    self.device_combo.set(name)
                    self.currentDeviceID = id
                    return True

        return False

    def deviceComboChanged(self, choice):
        """
        event handler for changing active device
        """
        allDevices = self.sp.devices()
        for device in allDevices["devices"]:
            if device["name"] == choice:
                self.currentDeviceID = device["id"]
                break
        self.sp.transfer_playback(self.currentDeviceID)
        return True

    def updateCurrentTrack(self):
        """
        get the track the user is playing currently
        """
        currentData = self.sp.currently_playing()
        if currentData is not None:
            self.playingNow = currentData["is_playing"]
            self.currentTrack = (currentData["item"]["name"],
                                 currentData["item"]["album"]["artists"][0]["name"])
            albumArtURL = currentData["item"]["album"]["images"][0]["url"]
            self.currentTrackID = currentData["item"]["id"]
            response = requests.get(albumArtURL)
            img = Image.open(BytesIO(response.content))
            tk_img = ctk.CTkImage(img, size=(200, 200))
            #imageio.imwrite('albumArtPhoto.png', img)
            #pixmap = QPixmap("albumArtPhoto.png")
            #self.albumArtLabel.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.FastTransformation))
            # self.trackTitleLabel.setText(self.currentTrack[0])
            # self.trackArtistLabel.setText(self.currentTrack[1])

    def pausePlayPressed(self):
        """
        event handler for play/pause button
        """
        self.populateDeviceComboboxes()
        if self.currentDeviceID:
            currentData = self.sp.currently_playing()
            uri=None
            if (currentData is None
                or currentData["context"] is None
                or self.playlistID not in currentData["context"]["uri"]
                or currentData['item']['id'] not in self.tracks):

                    uri = 'spotify:playlist:' + self.playlistID

            self.playingNow = currentData["is_playing"]

            if self.playingNow == True:
                self.sp.pause_playback()
                self.playingNow = False
            else:
                self.sp.start_playback( context_uri = uri )
                self.playingNow = True
            return True
        else:
            print("No active device for playback")
            return False

    def updatePlaylistTracks(self):
        """
        update the music player frame with current playist tracks
        """
        # Delete existing labels
        [x.destroy() for x in self.songs_label]
        self.songs_label = []

        playlist = self.sp.playlist(self.playlistID)
        for image in playlist['images']:
            if image['height'] == 300:
                img = self.getCTkImage(image['url'], size=(300, 300))
                self.playlist_image_label.configure(image=img)
                break

        self.tracks = {}
        for i, track in enumerate(playlist['tracks']['items']):
            id = track['track']['id']
            name = track['track']['name']
            self.tracks[id] = {'name': track['track']['name'],
                            'uri': track['track']['uri'],
                            'duration_ms': track['track']['duration_ms'],
                            'poster': [img['url'] for img in track['track']['album']['images'] if img['height'] == 64][0]
                            }

            img = self.getCTkImage(self.tracks[id]['poster'], size=(50, 50))
            song_label = ctk.CTkLabel(self.songs_frame,
                            text=f"  {name}\n   { round(self.tracks[id]['duration_ms']/1000,2) }s",
                            image=img, compound='left', anchor=ctk.NW, justify='left')
            song_label.bind("<Button-1>", lambda event, uri= self.tracks[id]['uri']: self.playTrackWithID(event, uri ))
            song_label.grid(row=i, padx=5, pady=5, sticky=ctk.NW)
            self.songs_label.append(song_label)

        # TODO: Uncomment when Spotify Premium is available
        # if self.currentDeviceID:
        #     self.sp.start_playback(context_uri='spotify:playlist:'+ self.playlistID )
        #     self.sp.pause_playback()

    
    def playTrackWithID(self, event, uri):
        """
        play song when user clicks on a song label
        """
        self.sp.start_playback( context_uri = 'spotify:playlist:' + self.playlistID, offset = { "uri": uri})

    def searching(self):
        """
        search songs using spotify api"""
        query = self.searchEdit.text()
        results = self.sp.search(query, limit=3, offset=0, type='track')
        for i in results["tracks"]["items"]:
            print(i["name"])

    def open_playlist(self):
        """
        callback function to open the playlist url
        """
        url = "https://open.spotify.com/playlist/" + self.playlistID
        webbrowser.open(url = url, new = 2)

    def getCTkImage(self, url, size=(200, 200)):
        return ctk.CTkImage(Image.open(urlopen(url)), size=size)
