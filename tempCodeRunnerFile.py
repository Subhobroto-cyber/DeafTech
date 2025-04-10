import pickle
import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import tkinter as tk
from PIL import Image, ImageTk

# Load the trained model
with open('model.p', 'rb') as f:
    model_dict = pickle.load(f)
model = model_dict['model']

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize webcam
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

# Function to speak recognized text
def speak_text():
    if recognized_text:
        engine.say(recognized_text)
        engine.runAndWait()

# Create the main window
root = tk.Tk()
root.title("Sign Language Recognition")
root.configure(bg='white')
root.attributes('-fullscreen', True)

# Create and place the widgets
text_display = tk.Label(root, text="Sentence: ", bg='white', font=('Helvetica', 24))
text_display.pack(pady=20, anchor='w', padx=20)  # Place below gesture box

# Button functions
def on_next():
    global recognized_text, current_character
    if current_character:
        recognized_text += current_character
        current_character = ""
    display_text = f"Sentence: {recognized_text}"
    text_display.config(text=display_text)

def on_space():
    global recognized_text
    recognized_text += ' '
    display_text = f"Sentence: {recognized_text}"
    text_display.config(text=display_text)

def on_quit():
    root.quit()

def on_speak():
    speak_text()

def on_clear():
    global recognized_text
    recognized_text = ""
    display_text = "Sentence: "
    text_display.config(text=display_text)

# Create buttons
button_font = ('Helvetica', 18)
button_frame = tk.Frame(root, bg='white')

enter_button = tk.Button(button_frame, text="Next", command=on_next, font=button_font, height=2, width=10)
enter_button.pack(side=tk.TOP, padx=20, pady=10)

space_button = tk.Button(button_frame, text="Space", command=on_space, font=button_font, height=2, width=10)
space_button.pack(side=tk.TOP, padx=20, pady=10)

speak_button = tk.Button(button_frame, text="Speak", command=on_speak, font=button_font, height=2, width=10)
speak_button.pack(side=tk.TOP, padx=20, pady=10)

quit_button = tk.Button(button_frame, text="Quit", command=on_quit, font=button_font, height=2, width=10)
quit_button.pack(side=tk.TOP, padx=20, pady=10)

clear_button = tk.Button(button_frame, text="Clear", command=on_clear, font=button_font, height=2, width=10)
clear_button.pack(side=tk.TOP, padx=20, pady=10)

button_frame.pack(side=tk.RIGHT, padx=20, pady=20)

# Start the video capture and update loop
def update_frame():
    global recognized_text, gesture_detected, last_character, current_character

    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        root.quit()
        return

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

                # Draw a rectangle with a border around the detected gesture area
                x1 = int(min(x_) * W) - 10
                y1 = int(min(y_) * H) - 10
                x2 = int(max(x_) * W) + 10
                y2 = int(max(y_) * H) + 10

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Border color

                # Display the current character in the middle of the gesture box
                cv2.putText(frame, predicted_character, (x1 + (x2 - x1) // 4, y1 + (y2 - y1) // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    else:
        # Reset detection when no hand is detected
        if gesture_detected:
            gesture_detected = False

    # Convert the frame to RGB for Tkinter
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
    image_label.config(image=img)
    image_label.image = img

    # Update the frame every 30 ms
    root.after(30, update_frame)

# Create label to display the webcam feed
image_label = tk.Label(root, bg='white')
image_label.pack(side=tk.LEFT, padx=20, pady=20)

# Start the Tkinter event loop
update_frame()
root.mainloop()

cap.release()
cv2.destroyAllWindows()
