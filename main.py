import mediapipe as mp
from mediapipe.python.solutions.pose import PoseLandmark
from mediapipe.python.solutions.drawing_utils import DrawingSpec
import cv2 as cv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema


mpPose = mp.solutions.pose
pose = mpPose.Pose()
mpDraw = mp.solutions.drawing_utils
mpStyles = mp.solutions.drawing_styles
points = mpPose.PoseLandmark

custom_style = mpStyles.get_default_pose_landmarks_style()
custom_connections = list(mpPose.POSE_CONNECTIONS)

excluded_landmarks = [
    PoseLandmark.LEFT_EYE_INNER, 
    PoseLandmark.RIGHT_EYE_INNER, 
    PoseLandmark.LEFT_EAR,
    PoseLandmark.RIGHT_EAR,
    PoseLandmark.LEFT_EYE_OUTER,
    PoseLandmark.RIGHT_EYE_OUTER,
    PoseLandmark.MOUTH_LEFT,
    PoseLandmark.MOUTH_RIGHT ]

for landmark in excluded_landmarks:
    # we change the way the excluded landmarks are drawn
    custom_style[landmark] = DrawingSpec(color=(255,255,0), thickness=None) 
    # we remove all connections which contain these landmarks
    custom_connections = [connection_tuple for connection_tuple in custom_connections 
                            if landmark.value not in connection_tuple]

vidfile = "videos/swing1.MOV"
vid = cv.VideoCapture(vidfile)

wrist_x = []
wrist_y = []
time = []
frames = []
i = 0
while True:
    frame = vid.read()
    frame = frame[1]
    if frame is None:
        break
    
    imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    black = np.zeros(frame.shape)
    width = frame.shape[0]
    height = frame.shape[1]
    results = pose.process(imgRGB)

    if results.pose_landmarks:
        mpDraw.draw_landmarks(black, results.pose_landmarks, connections=custom_connections, landmark_drawing_spec=custom_style)
        mpDraw.draw_landmarks(frame, results.pose_landmarks, landmark_drawing_spec=custom_style)

        keypoints = [0, 11, 12, 15, 16, 23, 24, 25, 26, 27, 28]

        wrist_x.append(results.pose_landmarks.landmark[15].x)
        wrist_y.append(results.pose_landmarks.landmark[15].y)
        time.append(i)
        
    #cv.imshow("Video", frame)
    cv.imshow('outline', black)
    key = cv.waitKey(1)
    if key == ord('q'):
        break

    frames.append(frame)
    i+=1


grads = np.gradient(wrist_y)
second_grads = np.gradient(grads)

# mins = argrelextrema(np.array(wrist_y), np.less)
# maxes = argrelextrema(np.array(wrist_y), np.greater)

# for ex in mins[0]:
#     cv.imshow("Minimums", frames[ex])
#     cv.waitKey(0)

# for ex in maxes[0]:
#     cv.imshow('Maximums', frames[ex])
#     cv.waitKey(0)


mins = argrelextrema(np.array(wrist_x), np.less)
maxes = argrelextrema(np.array(wrist_x), np.greater)

for ex in mins[0]:
    cv.imshow("Minimums", frames[ex])
    cv.waitKey(0)

for ex in maxes[0]:
    cv.imshow('Maximums', frames[ex])
    cv.waitKey(0)

