import cv2
import numpy as np

from spotify import MusicMoodClassifier

from tensorflow.keras.applications import vgg16
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Sequential, model_from_json
from tensorflow.keras.preprocessing.image import img_to_array


def getVGG16():
    emotion_map = {0: 'Angry', 1: 'Digust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}
    model = Sequential()

    pretrained_model = vgg16.VGG16(include_top=False, 
                                            input_shape=(48, 48, 3),classes=7,
                                            weights='data/VGG16/vgg16_weights_tf_dim_ordering_tf_kernels_notop.h5')
    #for layer in pretrained_model.layers:
    #        layer.trainable=False

    model.add(pretrained_model)
    #model.add(Flatten())
    model.add(GlobalAveragePooling2D())
    model.add(Dropout(0.2))
    # Output layer
    model.add(Dense(7, activation='softmax'))

    model.load_weights('data/VGG16.h5')

    return model, emotion_map

model, emotion_map = getVGG16()

# model = model_from_json(open("data/model_v2.json", "r").read())
# model.load_weights('data/model_v2.h5')
# emotion_map = {0: 'Angry', 1: 'Digust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}


face_haar_cascade = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
font = cv2.FONT_HERSHEY_SIMPLEX

class RecommendationSystem:
    def __init__(self):
        self.music_classifier = MusicMoodClassifier()
    
    def recommend_song(self, emotion):
        labels = ['Calm', 'Energitic', 'Happy', 'Sad']
        # emotion_map = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        mood_to_song_map = [0,0,0,2,3,1,0]
        song_mood = mood_to_song_map[emotion]
        return labels[song_mood], self.music_classifier.getTypicalTracks(song_mood)

    def detect_emotion(self, ret, frame):
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_haar_cascade.detectMultiScale(gray_image)
        try:
            for (x,y, w, h) in faces:
                cv2.rectangle(frame, pt1 = (x,y),pt2 = (x+w, y+h), color = (255,0,0),thickness =  2)
                roi_gray = gray_image[y-5:y+h+5,x-5:x+w+5]
                roi_gray=cv2.resize(roi_gray,(48, 48))
                # roi_gray=cv2.resize(roi_gray,(64,64))

                #convert 1 channel image to 3 channel
                roi_gray = cv2.merge((roi_gray, roi_gray, roi_gray))

                image_pixels = img_to_array(roi_gray)
                image_pixels = np.expand_dims(image_pixels, axis = 0)
                image_pixels /= 255
                predictions = model.predict(image_pixels)
                max_index = np.argmax(predictions[0])
                
                # emotion_detection = ('Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral')
                emotion_prediction = emotion_map[max_index]
                cv2.putText(frame, emotion_prediction, (x, y), font, 1, (0, 255, 255), 2)
                # print(emotion_prediction)
                # cv2.putText(ret, "Sentiment: {}".format(emotion_prediction), (0,textY+22+5), FONT,0.7, lable_color,2)
                # lable_violation = 'Confidence: {}'.format(str(np.round(np.max(predictions[0])*100,1))+ "%")
                # violation_text_dimension = cv2.getTextSize(lable_violation,FONT,FONT_SCALE,FONT_THICKNESS )[0]
                # violation_x_axis = int(ret.shape[1]- violation_text_dimension[0])
                # cv2.putText(ret, lable_violation, (violation_x_axis,textY+22+5), FONT,0.7, lable_color,2)
                return (max_index, emotion_prediction)
            else:
                pass
                #print("\n---------- No face detected -----------\n")
        except Exception as e:
            print("\nError\n", e)
        # frame[0:int(height/6),0:int(width)] = ret
        # cv2.imshow('frame', frame)