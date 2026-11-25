import cv2
import mediapipe as mp
import numpy as np
import os
import tracker as logic 
import Hand_detector as hd # Import the new detector file

# --- CONFIGURATION (Move from original code) ---
brushThickness = 25
eraserThickness = 100
drawColor = (255, 0, 255) # Default Pink

# --- LOAD HEADER IMAGES ---
# **IMPORTANT:** Create a folder named 'Header' with your four color selection images.
folderPath = "Header"
overlayList = []
try:
    myList = os.listdir(folderPath)
    for imPath in myList:
        image = cv2.imread(f'{folderPath}/{imPath}')
        overlayList.append(image)
    if not overlayList:
        raise Exception("Header folder is empty.")
    header = overlayList[0]
except Exception as e:
    print(f"Warning: Failed to load headers ({e}). Using black placeholder.")
    header = np.zeros((125, 1280, 3), np.uint8) 
    overlayList = [header, header, header, header]


# --- STATE VARIABLES ---
imgCanvas = np.zeros((720, 1280, 3), np.uint8)
xp, yp = 0, 0 # Previous draw coordinates
mode = "mouse" # Initial mode is mouse

def main():
    global xp, yp, drawColor, header, mode, imgCanvas

    cap = cv2.VideoCapture(0)
    cap.set(3, 1280) # Set width
    cap.set(4, 720)  # Set height

    draw = mp.solutions.drawing_utils

    print("\n--- Application Ready ---")
    print("Press 'm' to toggle between MOUSE mode and PAINT mode.")
    print("Press 'c' to CLEAR the canvas.")
    print("Press 'q' to QUIT.\n")

    try:
        while cap.isOpened():
            ret, img = cap.read()
            if not ret: break

            img = cv2.flip(img, 1) # Flip image horizontally

            # 1. Process Hand Landmarks
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            processed = hd.hands.process(imgRGB) 
            
            landmark_list = []
            if processed.multi_hand_landmarks:
                hand_landmarks = processed.multi_hand_landmarks[0]
                draw.draw_landmarks(img, hand_landmarks, hd.mpHands.HAND_CONNECTIONS)
                
                h, w, c = img.shape
                for lm in hand_landmarks.landmark:
                    px, py = int(lm.x * w), int(lm.y * h)
                    landmark_list.append([px, py])
                
                # --- MODE SWITCHING LOGIC ---
                if mode == "mouse":
                    logic.run_mouse_logic(img, landmark_list)
                    cv2.putText(img, "MODE: MOUSE", (10, 700), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

                elif mode == "paint":
                    # Run the painter logic and update persistent state variables
                    imgCanvas, xp, yp, drawColor, header = logic.run_painter_logic(
                        img, imgCanvas, landmark_list, xp, yp, drawColor, 
                        overlayList, brushThickness, eraserThickness
                    )
                    cv2.putText(img, "MODE: PAINT", (10, 700), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
            
            # 2. Combine Camera Feed and Canvas (Only needed in Paint Mode)
            if mode == "paint":
                # This is the complex blending logic from your original painter code
                imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
                # Create an inverted mask where the drawing is white and background is black
                _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
                imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
                
                # Black out the drawn area on the live camera feed
                img = cv2.bitwise_and(img, imgInv)
                # Add the colored drawing from the canvas
                img = cv2.bitwise_or(img, imgCanvas)

            # 3. Add Header and Display
            img[0:125, 0:1280] = header # Overlay header
            cv2.imshow("Hand Controller", img)
            
            # --- Key Press Controls ---
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            
            # Toggle Mode
            elif key == ord('m'):
                mode = "paint" if mode == "mouse" else "mouse"
                xp, yp = 0, 0 # Reset drawing state on mode change
                print(f"Switched to {mode.upper()} Mode.")
            
            # Clear Canvas (Only in Paint Mode)
            elif key == ord('c') and mode == "paint":
                imgCanvas = np.zeros((720, 1280, 3), np.uint8)
                print("Canvas cleared.")
                

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()