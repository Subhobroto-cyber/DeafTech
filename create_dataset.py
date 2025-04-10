import os
import pickle
import mediapipe as mp
import cv2
import zipfile
import kaggle

# Set up directories
DATA_DIR = './data/Indian'
EXTRACT_DIR = './data'

# Ensure the directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Kaggle API credentials (put this in ~/.kaggle/kaggle.json or set them here directly)
# If you don't have your API key, follow the instructions at: https://www.kaggle.com/docs/api

# Step 1: Download the dataset from Kaggle
kaggle.api.dataset_download_files('prathumarikeri/indian-sign-language-isl', path=EXTRACT_DIR, unzip=True)

# Dataset directory path (assumes the dataset unzipped into this folder)
dataset_path = os.path.join(EXTRACT_DIR, 'Indian')

# Step 2: Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

data = []
labels = []

# Step 3: Organize images from the dataset
for dir_ in os.listdir(dataset_path):
    class_dir = os.path.join(dataset_path, dir_)
    if os.path.isdir(class_dir):  # Ensure we only process directories (class folders)
        for img_path in os.listdir(class_dir):
            data_aux = []
            x_, y_ = [], []

            # Read the image
            img = cv2.imread(os.path.join(class_dir, img_path))
            if img is None:
                continue  # If an image is corrupted or cannot be opened, skip it.

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Step 4: Process each image using MediaPipe Hands
            results = hands.process(img_rgb)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    for lm in hand_landmarks.landmark:
                        x_.append(lm.x)
                        y_.append(lm.y)

                    # Normalize the landmarks
                    for lm in hand_landmarks.landmark:
                        data_aux.append(lm.x - min(x_))
                        data_aux.append(lm.y - min(y_))

                # Append the data and label for the current image
                data.append(data_aux)
                labels.append(dir_)

# Step 5: Save the processed dataset (features and labels) to a pickle file
with open('data.pickle', 'wb') as f:
    pickle.dump({'data': data, 'labels': labels}, f)

print(f'Dataset created with {len(data)} samples.')