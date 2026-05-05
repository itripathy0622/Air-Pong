Airpong is a gesture-controlled Pong game that uses your webcam and real-time finger tracking to control the paddle. Simply hold your index finger up in front of your camera and move it up and down to play.

Built with Python, the game uses Google's MediaPipe library to detect and track 21 hand landmarks in real time, extracting the position of your index fingertip and translating it directly into paddle movement. The game itself is rendered using Pygame, with a background thread continuously pulling from the webcam so the game runs smoothly at 60fps.

- Real-time finger tracking via webcam
- Automatic pause when your hand leaves the camera view
- Rally-based scoring with a persistent high score
- AI opponent that adapts to the ball position
- No external hardware required: just your built-in webcam

Tech Stack
- Python 3.10
- MediaPipe
- OpenCV
- Pygame

How to Run
1. Clone the repo
2. Create and activate a Conda environment with Python 3.10
3. Run pip install opencv-python mediapipe pygame numpy
4. Run python3 pong.py
