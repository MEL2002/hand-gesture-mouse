import mediapipe as mp
import math

mpHands = mp.solutions.hands

# Configuration for the hand detection model
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    max_num_hands=1
)

def get_distance(p1, p2):
    """Calculates Euclidean distance between two points."""
    x1, y1 = p1
    x2, y2 = p2
    return math.hypot(x2 - x1, y2 - y1)

def fingers_up(lm_list):
    """
    Checks which fingers are extended. Returns a list [T, I, M, R, P].
    1 = finger is up, 0 = finger is down.
    The check is relative to the PIP joint (knuckle before the tip).
    """
    fingers = []
    if len(lm_list) == 0:
        return []

    # Thumb check (Thumb tip x-coordinate vs MCP joint x-coordinate)
    # This check is sensitive to hand orientation (right/left)
    if lm_list[4][0] > lm_list[3][0]: 
        fingers.append(1)  # Thumb is up (simple check)
    else:
        fingers.append(0)

    # Four Fingers (Index, Middle, Ring, Pinky)
    # Check if tip y-coordinate (lm_list[tip_id][1]) is above the PIP y-coordinate (lm_list[tip_id - 2][1])
    tip_ids = [8, 12, 16, 20]
    for id in tip_ids:
        if lm_list[id][1] < lm_list[id - 2][1]:
            fingers.append(1)
        else:
            fingers.append(0)
            
    return fingers