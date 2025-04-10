import pickle
import cv2
import mediapipe as mp
import numpy as np
import pyttsx3

# Load the trained model
with open('model.p', 'rb') as f:
    model_dict = pickle.load(f)
model = model_dict['model']

# Initialize text-to-speech engine
engine = pyttsx3.init()

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Update the labels dictionary as per your classes
labels_dict = {str(i): str(i) for i in range(10)}  # 0-9
labels_dict.update({chr(i): chr(i) for i in range(65, 91)})  # A-Z

recognized_text = ""
gesture_detected = False
last_character = ""
current_character = ""

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        break

    H, W, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            data_aux = []
            x_, y_ = [], []

            for lm in hand_landmarks.landmark:
                x_.append(lm.x)
                y_.append(lm.y)

            for lm in hand_landmarks.landmark:
                data_aux.append(lm.x - min(x_))
                data_aux.append(lm.y - min(y_))

            # Predict the character
            prediction = model.predict([np.asarray(data_aux)])
            predicted_label = prediction[0]

            # Check if the predicted label is in the dictionary
            if predicted_label in labels_dict:
                predicted_character = labels_dict[predicted_label]

                # Detect gesture
                if not gesture_detected:
                    if predicted_character != last_character:  # Check if it's different from the last character
                        current_character = predicted_character
                        last_character = predicted_character
                        gesture_detected = True
                else:
                    if predicted_character != last_character:  # Check if it's different from the last character
                        current_character = predicted_character
                        last_character = predicted_character

                x1 = int(min(x_) * W) - 10
                y1 = int(min(y_) * H) - 10
                x2 = int(max(x_) * W) + 10
                y2 = int(max(y_) * H) + 10

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    else:
        # Reset detection when no hand is detected
        if gesture_detected:
            gesture_detected = False

    # Handle key presses
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # Quit
        break
    elif key == 13:  # Enter key
        if current_character:  # Append current character to recognized text
            recognized_text += current_character
            current_character = ""  # Clear current character
        display_text = recognized_text  # Update the display text
    elif key == ord(' '):  # Space bar
        recognized_text += ' '  # Add a space to recognized text
        display_text = recognized_text  # Update the display text

    # Display current character or recognized text on the frame
    display_text = current_character if gesture_detected else recognized_text
    cv2.putText(frame, display_text, (10, H - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow('Sign Language Recognition', frame)

# Speak the recognized text
if recognized_text:
    print(f'Recognized text: {recognized_text}')
    engine.say(recognized_text)
    engine.runAndWait()

cap.release()
cv2.destroyAllWindows()
