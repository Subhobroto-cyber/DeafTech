import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

# Load the dataset
with open('data.pickle', 'rb') as f:
    data_dict = pickle.load(f)

# Handling inhomogeneous data by padding or truncating (Example padding)
max_length = max([len(item) for item in data_dict['data']])
data_padded = [np.pad(item, (0, max_length - len(item)), 'constant') for item in data_dict['data']]
data = np.asarray(data_padded)
labels = np.asarray(data_dict['labels'])

# Split the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, shuffle=True, stratify=None)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(x_train, y_train)

# Evaluate the model
y_predict = model.predict(x_test)
accuracy = accuracy_score(y_test, y_predict)
print(f'Model accuracy: {accuracy * 100:.2f}%')

# Save the trained model
with open('model.p', 'wb') as f:
    pickle.dump({'model': model}, f)

print('Model saved successfully.')
