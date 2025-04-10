import pickle
import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from gtts import gTTS
from googletrans import Translator
import pygame
import os
import requests

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Load the trained model
with open('C:/Users/Subhobroto Sasmal/Downloads/DeafTech---SignLanguageDetector-main/DeafTech---SignLanguageDetector-main/Backend/model.p', 'rb') as f:
    model_dict = pickle.load(f)

model = model_dict['model']

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

# Initialize translator
translator = Translator()
translated_text = ""  # Store translated text
translated_lang_code = ""

# Initialize suggestions list
suggestions = []
suggestion_buttons = []

# Function to speak recognized text or translated text
def speak_text():
    global translated_text, recognized_text
    text_to_speak = translated_text if translated_text else recognized_text
    lang = 'en' if not translated_text else translated_lang_code  # Use translated language

    if text_to_speak:
        file_name = "temp.mp3"
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

            if os.path.exists(file_name):
                os.remove(file_name)

            tts = gTTS(text=text_to_speak, lang=lang)
            tts.save(file_name)

            pygame.mixer.music.load(file_name)
            pygame.mixer.music.play()

        except Exception as e:
            print(f"Error in speak_text: {e}")

# Function to translate recognized text
def translate_text():
    global translated_text, translated_lang_code
    languages = {
        'Hindi': 'hi',
        'Bengali': 'bn',
        'Telugu': 'te',
        'Marathi': 'mr',
        'Tamil': 'ta',
        'Gujarati': 'gu',
        'Malayalam': 'ml',
        'Kannada': 'kn',
        'Punjabi': 'pa',
        'Urdu': 'ur'
    }

    def on_language_select(lang_code):
        global translated_text, translated_lang_code
        try:
            translated = translator.translate(recognized_text, dest=lang_code)
            translated_text = translated.text
            translated_lang_code = lang_code
            translator_label.config(text=f"Translated: {translated_text}")
            speak_text()
        except Exception as e:
            print(f"Translation Error: {e}")
            translated_text = ""
            translated_lang_code = ''
        finally:
            lang_window.destroy()

    lang_window = tk.Toplevel(root)
    lang_window.title("Select Language")
    lang_window.geometry("300x470")

    tk.Label(lang_window, text="Select a language:", font=language_font).pack(pady=10)

    for lang_name, lang_code in languages.items():
        tk.Button(lang_window, text=lang_name, command=lambda code=lang_code: on_language_select(code), font=language_font).pack(pady=5)

# Intellisense suggestion functionality using Datamuse API
def get_word_suggestions(word):
    url = f"https://api.datamuse.com/words?sp={word}*&max=1000"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            suggestions = [word['word'].upper() for word in response.json()]
            return suggestions
        else:
            print(f"Error fetching suggestions: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error in fetching word suggestions: {e}")
        return []

def clear_suggestions():
    for button in suggestion_buttons:
        button.config(text="", state=tk.DISABLED)

def show_suggestions():
    global suggestions
    suggestions = get_word_suggestions(recognized_text)
    # Handle case when no suggestions are found
    if suggestions:
        for i, suggestion in enumerate(suggestions[:5]):  # Limit the number of suggestions shown
            suggestion_buttons[i].config(text=suggestion, state=tk.NORMAL)
    else:
        print("No suggestions available.")

# Function to append the selected suggestion to the recognized text
def select_suggestion(index):
    global recognized_text
    recognized_text += suggestion_buttons[index].cget('text')[len(recognized_text):]
    text_display.config(text=f"Sentence: {recognized_text}")
    clear_suggestions()
    show_suggestions()

# Button functions
def on_next():
    global recognized_text, current_character
    if current_character:
        recognized_text += current_character
        current_character = ""
    display_text = f"Sentence: {recognized_text}"
    text_display.config(text=display_text)
    clear_suggestions()
    show_suggestions()

def on_space():
    global recognized_text
    recognized_text += ' '
    display_text = f"Sentence: {recognized_text}"
    text_display.config(text=display_text)
    clear_suggestions()

def on_backspace():
    global recognized_text
    recognized_text = recognized_text[:-1]
    display_text = f"Sentence: {recognized_text}"
    text_display.config(text=display_text)
    clear_suggestions()
    show_suggestions()

def on_clear():
    global recognized_text, translated_text
    recognized_text = ""
    translated_text = ""
    display_text = "Sentence: "
    text_display.config(text=display_text)
    translator_label.config(text="")
    clear_suggestions()

def on_translate():
    translate_text()
    clear_suggestions()

def on_speak():
    speak_text()
    clear_suggestions()

def on_quit():
    pygame.mixer.music.stop()
    root.quit()

# Create the main window
root = tk.Tk()
root.title("Sign Language Recognition")
root.configure(bg='#f7f7f7')
root.attributes('-fullscreen', True)

# Define fonts
heading_font = ('Helvetica', 30, 'bold')
text_font = ('Helvetica', 24)
translator_font = ('Helvetica', 20)
button_font = ('Helvetica', 16)
language_font = ('Helvetica', 12)

# Create a frame to add a border effect
border_frame = ttk.Frame(root, padding=20)
border_frame.pack(fill=tk.BOTH, expand=True)

# Create a heading
heading = tk.Label(border_frame, text="Sign Language to Text & Speech Translator - DeafTech©", font=heading_font)
heading.pack(pady=20)

# Create a frame inside the border frame for content
content_frame = tk.Frame(border_frame, bg='#f7f7f7')
content_frame.pack(fill=tk.BOTH, expand=True)

# Display recognized text
text_display = tk.Label(content_frame, text="Sentence: ", bg='#f7f7f7', font=text_font)
text_display.pack(pady=20, anchor='w', padx=20)

# Display translated text
translator_label = tk.Label(content_frame, text="", bg='#f7f7f7', font=translator_font)
translator_label.pack(pady=10, anchor='w', padx=20)

# Buttons for suggestions
for _ in range(5):
    button = tk.Button(content_frame, text="", state=tk.DISABLED, font=button_font, command=lambda i=_: select_suggestion(i))
    button.pack(pady=5)
    suggestion_buttons.append(button)

# Run the Tkinter event loop
root.mainloop()