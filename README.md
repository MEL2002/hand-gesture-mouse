# Hand Gesture Mouse

Control your computer with your hand through a webcam. No mouse, no touchpad.

The program tracks 21 points on your hand in real time and turns simple gestures into mouse actions. It also has a paint mode where you can draw in the air and see your drawing on top of the camera feed.

## What it does

**Mouse mode**
- Raise only your index finger to move the cursor
- Pinch your thumb and index finger together to click

**Paint mode**
- Raise your index finger to draw
- Raise your index and middle fingers to stop drawing and pick a color from the top bar (pink, blue, green or eraser)

**Keyboard shortcuts**
- `m` switch between mouse mode and paint mode
- `c` clear the drawing (paint mode)
- `q` quit

## How it works

1. OpenCV reads the webcam feed.
2. MediaPipe Hands detects the hand and returns 21 landmarks (fingertips, knuckles, wrist).
3. `Hand_detector.py` checks which fingers are up and measures the distance between fingertips.
4. `tracker.py` turns those gestures into actions: it maps the index fingertip position to screen coordinates to move the cursor, and treats a short thumb-to-index distance as a click. In paint mode it draws lines on a separate canvas that is blended with the camera image.
5. `main.py` runs the loop, handles the mode switch and displays the result.

## Project structure

```
main.py            main loop, mode switching, display
tracker.py         mouse logic and paint logic
Hand_detector.py   MediaPipe setup, finger detection, distance helper
Header/            optional color bar images for paint mode
requirements.txt   Python dependencies
```

## Run it

Requires Python 3.10 to 3.12 and a webcam.

```bash
git clone https://github.com/MEL2002/hand-gesture-mouse.git
cd hand-gesture-mouse
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
python main.py
```

For paint mode, you can put four 1280x125 images in the `Header` folder (one per color). If the folder is empty, the program shows a plain black bar and still works.

## Built with

Python, OpenCV, MediaPipe, NumPy, PyAutoGUI, pynput

## What I learned

- Working with real-time computer vision and landmark detection
- Turning noisy hand positions into stable controls (mapping a smaller active zone of the camera to the full screen)
- Keeping a drawing layer separate from the live video and merging the two with masks

## Next steps

- Smooth the cursor movement to remove jitter
- Add right click, double click and scroll gestures
- Add a short delay after a click so a single pinch does not trigger several clicks

## Author

Moïra Lamarre, [github.com/MEL2002](https://github.com/MEL2002)
