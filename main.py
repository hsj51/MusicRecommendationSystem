import customtkinter as ctk
from PIL import Image, ImageTk
#from urllib.request import urlopen

from camera import VideoCamera
from player import SpotifyFrame
from prediction import RecommendationSystem

ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")


class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source

        # open video source (by default this will try to open the computer webcam)
        self.vid = VideoCamera(self.video_source)

        # Creater Lable
        self.creater_label=ctk.CTkLabel(window, text='', justify='left', anchor=ctk.W, width=200)
        self.creater_label.grid(row=2, column=0, padx=10, pady=10)

        self.label1=ctk.CTkLabel(window, text='Camera')
        self.label1.grid(row=0, column=1, padx=10, pady=10)

        # create a canvas that can fit the above video source size
        self.canvas = ctk.CTkCanvas(window, width = self.vid.width, height = self.vid.height)
        self.canvas.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        
        # create a button that calls the snapshot method when pressed
        self.btn_snapshot = ctk.CTkButton(window, text="Recommend Song", width=140, command=self.snapshot)
        self.btn_snapshot.grid(row=2, column=1, padx=10, pady=10)

        self.emotion_label=ctk.CTkLabel(window, text='', justify='right', anchor=ctk.E, height=50, width=200)
        self.emotion_label.grid(row=2, column=2, padx=10, pady=10)

        # bind the left mouse button click event to the canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.spotify_frame = SpotifyFrame(master=self.window)
        self.spotify_frame.grid(row=1, rowspan=2, column=3, padx=10, pady=10)

        self.label2=ctk.CTkLabel(window, text='Spotify')
        self.label2.grid(row=0, column=3, padx=10, pady=10)

        self.recommender = RecommendationSystem()

        # after starting the GUI loop, call the update() method periodically to update the video stream
        self.delay = 10
        self.update()

        self.window.mainloop()

    def on_canvas_click(self, event):
        print("Canvas clicked at", event.x, event.y)

    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        prediction = self.recommender.detect_emotion(ret, frame)
        if prediction:
            song = self.recommender.recommend_song(prediction[0])

            # Done # ------------ TODO: Update Spotify Frame Code ---------------#
            self.emotion_label.configure(text=f"\nEmotion: {prediction[1]}\nSong Mood: {song[0]}")
            print(self.emotion_label.cget("width"))

            self.spotify_frame.grid(row=1, column=3, padx=10, pady=10)
            self.label2.grid(row=0, column=3, padx=10, pady=10)
            print(f"\nEmotion: {prediction[1]} | Song Mood: {song[0]}\nSong: {song[1]}\n")
            self.spotify_frame.updatePlaylistTracks()

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.recommender.detect_emotion(ret, frame)
            self.photo = ImageTk.PhotoImage(image = Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = ctk.NW)

        self.window.after(self.delay, self.update)

# try:
    # Create a window and pass it to the Application object
    # App(ctk.CTk(), "Music Recommendation System", 'http://192.168.1.103:8080/video')
App(ctk.CTk(), "Music Recommendation System")

# except Exception as e:
#     print('E:', e)