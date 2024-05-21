import mediapipe as mp
from mediapipe.python.solutions.pose import PoseLandmark
from mediapipe.python.solutions.drawing_utils import DrawingSpec
import cv2 as cv
import pandas as pd
import numpy as np
import metrics

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

lwrist_x = []
lwrist_y = []
head_y = []

y_coords = {}
x_coords = {}

body_parts = {
    'head': 0,
    'lshoulder': 11,
    'rshoulder': 12,
    'lwrist': 15,
    'rwrist': 16,
    'lhip': 23,
    'rhip': 24,
    'lknee': 25,
    'rknee': 26,
    'lfoot': 27,
    'rfoot': 28
}

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

        for part in body_parts.keys():
            keypoint = body_parts[part]
            if not y_coords.get(part):
                y_coords[part] = []
            y_coords[part].append(results.pose_landmarks.landmark[keypoint].y)

            if not x_coords.get(part):
                x_coords[part] = []
            x_coords[part].append(results.pose_landmarks.landmark[keypoint].x)
        
        
    #cv.imshow("Video", frame)
    cv.imshow('outline', black)
    key = cv.waitKey(1)
    if key == ord('q'):
        break

    frames.append(frame)

lwrist_x = x_coords['lwrist']
lwrist_y = y_coords['lwrist']
head_y = y_coords['head']
lhip_x = x_coords['lhip']
rhip_x = x_coords['rhip']
lshoulder_y = y_coords['lshoulder']
rshoulder_y = y_coords['rshoulder']

address, backswing, follow, finish, impact = metrics.identify_phases(lwrist_y,lwrist_x)
cv.imshow('Address', frames[address])
cv.waitKey(0)
cv.imshow('Backswing', frames[backswing])
cv.waitKey(0)
cv.imshow('Impact', frames[impact])
cv.waitKey(0)
cv.imshow('Followthrough', frames[follow])
cv.waitKey(0)
cv.imshow('Finish', frames[finish])
cv.waitKey(0)
start = metrics.find_swing_start(address, lwrist_x, 0.01)
tempo = metrics.calculate_tempo(start, backswing, impact)
print("Swing tempo (ratio of backswing frames to impact frames)" + tempo)
print("Backswing head movement" + str(metrics.head_movement_up(head_y, start, backswing)))
print("Downswing head movement" + str(metrics.head_movement_down(head_y, backswing, impact)))
print("Head movement (as a fraction of image size)" + str(metrics.head_movement_total(head_y, start, impact)))
print("Hip shift" + str(metrics.hip_shift(lhip_x, rhip_x, start, impact)))
print("Shoulder dip/lift" + str(metrics.shoulder_dip(lshoulder_y, rshoulder_y, impact)))