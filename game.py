import cv2
import mediapipe as mp

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

print("Hand tracking started. Press Q or close window to quit.")

while True:

    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame.")
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            index_tip = hand_landmarks.landmark[8]

            finger_y = index_tip.y
            frame_height = frame.shape[0]

            pixel_y = int(finger_y * frame_height)

            print(f"Finger Y: {finger_y:.3f} | Pixel Y: {pixel_y}")

            finger_x = index_tip.x
            pixel_x = int(finger_x * frame.shape[1])
            cv2.circle(frame, (pixel_x, pixel_y), 10, (0, 255, 0), cv2.FILLED)

    cv2.imshow("Finger Tracking", frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    
    if cv2.getWindowProperty("Finger Tracking", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
print("Camera closed cleanly.")