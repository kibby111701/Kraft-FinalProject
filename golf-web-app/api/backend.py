from flask import Flask, request
from werkzeug.utils import secure_filename
import mediapipe as mp
from mediapipe.python.solutions.pose import PoseLandmark
from mediapipe.python.solutions.drawing_utils import DrawingSpec
import cv2 as cv
import pandas as pd
import numpy as np
import metrics

ALLOWED_EXTENSIONS = set(['mov'])
UPLOAD_FOLDER = '../public/static/videos/'

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

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowedFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_extn(filename):
    return filename.rsplit('.', 1)[1].lower()


@app.route('/')
def hello():
    return 'Hello!'

@app.route('/test')
def test():
    return {'Name': "Chris",
            "Age": "22",
            "Understanding": "Absolutely none"}

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print('here')
        f = request.files['file']
        filename = secure_filename(f.filename)
        if allowedFile(filename):
            savepath = UPLOAD_FOLDER+'base.'+get_extn(f.filename)
            f.save(savepath)
            return {'filename': filename, 'status': 'success'}
        else:
            return {'status': 'failed'}
    except Exception as e:
        print(e)
        return {'status': 'failed'}


@app.route('/generate', methods=['GET'])
def generate_statistics():
    try:
        vidfile = UPLOAD_FOLDER + "base.mov"
        vid = cv.VideoCapture(vidfile)
    except:
        return {'status': 'failed', 'error': 'no video file found'}
    
    y_coords = {}
    x_coords = {}

    frames = []
    i = 0
    while True:
        frame = vid.read()
        frame = frame[1]
        if frame is None:
            break
        
        imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = pose.process(imgRGB)

        if results.pose_landmarks:
            mpDraw.draw_landmarks(frame, results.pose_landmarks, landmark_drawing_spec=custom_style)

            for part in body_parts.keys():
                keypoint = body_parts[part]
                if not y_coords.get(part):
                    y_coords[part] = []
                y_coords[part].append(results.pose_landmarks.landmark[keypoint].y)

                if not x_coords.get(part):
                    x_coords[part] = []
                x_coords[part].append(results.pose_landmarks.landmark[keypoint].x)


    lwrist_x = x_coords['lwrist']
    lwrist_y = y_coords['lwrist']
    head_y = y_coords['head']
    lhip_x = x_coords['lhip']
    rhip_x = x_coords['rhip']
    lshoulder_y = y_coords['lshoulder']
    rshoulder_y = y_coords['rshoulder']
    rfoot_y = y_coords['rfoot']

    try:
        address, backswing, follow, finish, impact = metrics.identify_phases(lwrist_y,lwrist_x)
    except Exception as e:
        return {'status': 'failed', 'error': 'Failed to identify phases: ' + str(e)}

    start = metrics.find_swing_start(address, lwrist_x, 0.01)
    tempo = metrics.calculate_tempo(start, backswing, impact)
    height = metrics.get_height(start, head_y, rfoot_y)   
    stats = {}
    stats["Swing tempo (ratio of backswing frames to impact frames)"] = tempo
    stats["Backswing head movement"] = str(metrics.head_movement_up(head_y, start, backswing, height=height))
    stats["Downswing head movement"] = str(metrics.head_movement_down(head_y, backswing, impact, height=height))
    stats["Head movement"] = str(metrics.head_movement_total(head_y, start, impact, height=height))
    stats["Hip shift"] = str(metrics.hip_shift(lhip_x, rhip_x, start, impact, height=height))
    stats["Shoulder dip/lift"] = str(metrics.shoulder_dip(lshoulder_y, rshoulder_y, impact, height=height))
    resp = {"status": 'success', 'data': stats}
    return resp


if __name__ == "__main__":
    app.run(debug=True)