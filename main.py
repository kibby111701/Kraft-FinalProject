import mediapipe as mp
import cv2 as cv
import pandas as pd
import numpy as np

mpPose = mp.solutions.pose
pose = mpPose.Pose()
mpDraw = mp.solutions.drawing_utils
points = mpPose.PoseLandmark

vidfile = "videos/swing1.MOV"
vid = cv.VideoCapture(vidfile)

while True:
    frame = vid.read()
    frame = frame[1]
    if frame is None:
        break

    imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    black = np.zeros(frame.shape)
    results = pose.process(imgRGB)

    if results.pose_landmarks:
        mpDraw.draw_landmarks(black, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
        mpDraw.draw_landmarks(frame, results.pose_landmarks, mpPose.POSE_CONNECTIONS)

    cv.imshow("Video", frame)
    #cv.imshow('outline', black)
    cv.waitKey(1)

