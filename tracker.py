import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from pynput.mouse import Button, Controller
import Hand_detector as hd # Use the new detector file
import math

mouse = Controller()
screen_width, screen_height = pyautogui.size()

# --- MOUSE LOGIC ---
def run_mouse_logic(frame, landmark_list):
    if not landmark_list: return

    # Get index finger tip coordinates
    index_x, index_y = landmark_list[8]
    
    # Distance between Index (8) and Thumb (4)
    thumb_index_dist = hd.get_distance(landmark_list[4], landmark_list[8])

    # Check which fingers are up using the new module
    fingers = hd.fingers_up(landmark_list)

    # 1. MOVEMENT: Only Index is up (Fingers [1, 1, 0, 0, 0])
    if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
        # Map camera coordinates (0-1280, 0-720) to screen coordinates
        screen_x = np.interp(index_x, (100, 1180), (0, screen_width))
        screen_y = np.interp(index_y, (100, 620), (0, screen_height))
        
        # Smooth movement for better control
        pyautogui.moveTo(screen_x, screen_y, duration=0.01)
        cv2.circle(frame, (index_x, index_y), 15, (255, 0, 255), cv2.FILLED)

    # 2. CLICK: Pinch gesture (Index and Thumb close)
    if thumb_index_dist < 40:
        cv2.circle(frame, (index_x, index_y), 15, (0, 255, 0), cv2.FILLED)
        mouse.click(Button.left, 1) # Single click
        cv2.putText(frame, "CLICK", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


# --- PAINTER LOGIC ---
def run_painter_logic(img, imgCanvas, landmark_list, xp, yp, drawColor, overlayList, brushThickness, eraserThickness):
    x1, y1 = landmark_list[8]  # Index Tip
    x2, y2 = landmark_list[12] # Middle Tip
    
    fingers = hd.fingers_up(landmark_list)

    new_xp, new_yp = xp, yp
    new_drawColor = drawColor
    new_header = overlayList[0] # Default header

    # A. SELECTION MODE (Index and Middle fingers up)
    if fingers[1] and fingers[2]:
        new_xp, new_yp = 0, 0 # Reset drawing path
        
        # Highlight selection area on the main camera image
        cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)
        
        # Color/Tool selection is in the header area (y < 125)
        if y1 < 125:
            if 250 < x1 < 450:
                new_header = overlayList[0]
                new_drawColor = (255, 0, 255) # Pink
            elif 550 < x1 < 750:
                new_header = overlayList[1]
                new_drawColor = (255, 0, 0)   # Blue
            elif 800 < x1 < 950:
                new_header = overlayList[2]
                new_drawColor = (0, 255, 0)   # Green
            elif 1050 < x1 < 1200:
                new_header = overlayList[3]
                new_drawColor = (0, 0, 0)     # Eraser (Black)

    # B. DRAWING MODE (Only Index finger up)
    elif fingers[1] and not fingers[2]:
        cv2.circle(img, (x1, y1), brushThickness, drawColor, cv2.FILLED)
        
        # Initialize previous point if starting a new stroke
        if xp == 0 and yp == 0:
            new_xp, new_yp = x1, y1

        # Determine brush size (Eraser is black)
        current_thickness = eraserThickness if drawColor == (0, 0, 0) else brushThickness
        
        # Draw on the main camera image (for visual feedback)
        cv2.line(img, (xp, yp), (x1, y1), drawColor, current_thickness)
        
        # Draw on the persistent canvas (imgCanvas)
        cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, current_thickness)

        new_xp, new_yp = x1, y1 # Update previous point

    # C. NO FINGERS (or other gestures)
    else:
        new_xp, new_yp = 0, 0 # Reset drawing path if hand is idle

    # Return updated state variables
    return imgCanvas, new_xp, new_yp, new_drawColor, new_header