import math
import numpy as np
from scipy.signal import argrelextrema

def identify_phases(lwrist_y, lwrist_x, closeness_thresh = 0.02):
    """Returns phases of swings as frame numbers from the video"""
    y_mins = argrelextrema(np.array(lwrist_y), np.less)
    y_maxes = argrelextrema(np.array(lwrist_y), np.greater)

    candidates = []
    prev = None
    for ex in y_mins[0]:
        if prev:
            if abs(prev-lwrist_y[ex]) > closeness_thresh:
                candidates.append(ex)
        else:
            candidates.append(ex)
        prev = lwrist_y[ex]
    
    address, backswing, follow, finish = [candidates[i] for i in range(4)]

    impact_candidates = []
    for ex in y_maxes[0]:
        if ex > backswing and ex < follow:
            impact_candidates.append(ex)
    impact = np.max(impact_candidates)

    return address, backswing, follow, finish, impact
    

def find_swing_start(address, lwrist_x, closeness_thresh=0.01):
    prev = None
    for i in range(address, address+20):
        if prev:
            if abs(prev - lwrist_x[i]) > closeness_thresh:
                return i
            
        
        prev = lwrist_x[i]
    return address


def calculate_tempo(start, backswing, impact):
    tempo = (backswing - start) / (impact - backswing)
    tempo = str(tempo) + ':1'
    return tempo

def head_movement_up(head_y, start, backswing):
    return head_y[start] - head_y[backswing]

def head_movement_down(head_y, backswing, impact):
    return head_y[backswing] - head_y[impact]

def head_movement_total(head_y, start, impact):
    return head_y[start] - head_y[impact]

def hip_shift(lhip_x, rhip_x, start, impact):
    return ((lhip_x[impact] - lhip_x[start]) + (rhip_x[impact] - rhip_x[start])) / 2.0

def shoulder_dip(lshoulder_y, rshoulder_y, impact):
    return lshoulder_y[impact] - rshoulder_y[impact]