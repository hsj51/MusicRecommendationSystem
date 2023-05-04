import cv2
import numpy as np

from spotify import MusicMoodClassifier

from tensorflow.keras.applications import vgg16
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Sequential, model_from_json
from tensorflow.keras.preprocessing.image import img_to_array


def getVGG16():
    """
    build the model architecture and load the saved model weights
    """

    emotion_map = {0: 'Angry', 1: 'Digust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}

    model = Sequential()
    pretrained_model = vgg16.VGG16(include_top=False, 
                                            input_shape=(48, 48, 3),classes=7,
                                            weights='data/VGG16/vgg16_weights_tf_dim_ordering_tf_kernels_notop.h5')

    # add pretrained model layer to the model
    model.add(pretrained_model)

    #model.add(Flatten())
    model.add(GlobalAveragePooling2D())
    model.add(Dropout(0.2))

    # Output layer
    model.add(Dense(7, activation='softmax'))

    # load the saved model weights
    model.load_weights('data/VGG16.h5')

    return model, emotion_map

model, emotion_map = getVGG16()

# load model architecture
# model = model_from_json(open("data/model_v2.json", "r").read())
# load the saved model weights
# model.load_weights('data/model_v2.h5')
# emotion_map = {0: 'Angry', 1: 'Digust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}


face_haar_cascade = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
font = cv2.FONT_HERSHEY_SIMPLEX

class RecommendationSystem:
    def __init__(self):

        # initialize the music recommendation system
        self.music_classifier = MusicMoodClassifier()
    
    def recommend_song(self, emotion):
        """
        get song recommendations for the expression
        """
        # song mood labels
        labels = {0:'Calm', 1:'Energitic', 2:'Happy', 3:'Sad'}

        # emotion_map = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

        #  map for facial expression to song mood
        mood_to_song_map = [0,0,0,2,3,1,0]

        # get label of the mood
        song_mood = mood_to_song_map[emotion]

        # get song recommendation
        songs = self.music_classifier.getTypicalTracks(song_mood)

        return labels[song_mood], songs

    def detect_emotion(self, ret, frame):
        """
        detect the emotion of person from the image
        """
        # convert color image to black and white
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detect faces from image
        faces = face_haar_cascade.detectMultiScale(gray_image)

        try:
            # loop through all the faces
            for (x,y, w, h) in faces:

                cv2.rectangle(frame, pt1 = (x,y),pt2 = (x+w, y+h), color = (255,0,0),thickness =  2)

                # crop the face from image
                roi_gray = gray_image[y-5:y+h+5,x-5:x+w+5]

                # resize the image to 48*48 pixels
                roi_gray=cv2.resize(roi_gray,(48, 48))
                # roi_gray=cv2.resize(roi_gray,(64,64))

                #convert 1 channel image to 3 channel ( gray to color )
                roi_gray = cv2.merge((roi_gray, roi_gray, roi_gray))

                # convert image pixels to numpy array and apply transformations
                image_pixels = img_to_array(roi_gray)
                image_pixels = np.expand_dims(image_pixels, axis = 0)
                image_pixels /= 255

                # predict the expression
                predictions = model.predict(image_pixels)
                max_index = np.argmax(predictions[0])
                
                # emotion_detection = ('Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral')
                emotion_prediction = emotion_map[max_index]

                # put expression label on the frame
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