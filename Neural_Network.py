import csv
import serial
import random
import time
import math
import json
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss

# Load and Encode CSV Data with normalization
def load_data(filename):
    data = []
    labels = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        header = next(reader, None)  # Skip header
        for line in reader:
            # Ensure row has the correct number of columns
            if len(line) < 9:  # Adjust based on your actual data format
                print(f"Skipping incomplete row: {line}")
                continue

            # Extract numeric values, skipping timestamp and keeping label as is
            try:
                numeric_values = [float(value) for value in line[1:-1]]
                label = line[-1]
                data.append(numeric_values)
                labels.append(label)
            except ValueError as e:
                print(f"Skipping row with invalid data: {line}, Error: {e}")
                continue

    if not data:
        print("No valid data found in the CSV file.")
        exit()

    # Normalize data using Min-Max Scaling
    scaler = MinMaxScaler()
    data_normalized = scaler.fit_transform(data)

    return data_normalized, labels, scaler

# Load Data
filename = 'appliance_data.csv'
X, y, scaler = load_data(filename)

# Split Data into Training and Test Sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and Train MLPClassifier
mlp = MLPClassifier(hidden_layer_sizes=(64, 32), activation='relu', solver='adam', max_iter=1000, random_state=42)
mlp.fit(X_train, y_train)

# Evaluate the Model
y_pred = mlp.predict(X_test)
y_prob = mlp.predict_proba(X_test)
accuracy = accuracy_score(y_test, y_pred)
loss = log_loss(y_test, y_prob)
print(f"Test Loss: {loss:.4f}, Accuracy: {accuracy * 100:.2f}%")

# Save the Scaler and Model for Future Use
import joblib
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(mlp, 'mlp_model.pkl')

# Real-time Prediction Function with threshold logic
def predict_appliance(input_data, scaler, model):
    # Normalize input data
    input_normalized = scaler.transform([input_data])

    # Check threshold for "No Appliance Connected"
    # Assuming P (W) is the first feature in the input data
    p_w = input_data[0]
    if p_w < 2.0:
        return "No Appliance Connected"

    # Predict appliance
    prediction = model.predict(input_normalized)[0]
    return prediction

# Load the saved scaler and model
scaler = joblib.load('scaler.pkl')
mlp = joblib.load('mlp_model.pkl')

# Open Serial Port and Read Real-Time Data
serial_port = '/dev/ttyAMA0'  # Adjust if necessary
baud_rate = 38400
try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print("Serial connection established.")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit()

while True:
    if ser.in_waiting > 0:
        try:
            line = ser.readline().decode('utf-8').strip()
            # If data is space-separated, use split()
            data = line.split()  # Changed from split(',')

            # Ensure that there are enough data points
            expected_length = 22  # Adjust based on your actual data format
            if len(data) < expected_length:
                print(f"Incomplete data received: {data}")
                continue

            # Extract measurements for each CT sensor
            measurements = {
                'CT1': {
                    'P (W)': float(data[1]) if data[1].lower() != 'nan' else 0.0,
                    'S (VA)': float(data[4]) if data[4].lower() != 'nan' else 0.0,
                    'Q (VAR)': float(data[7]) if data[7].lower() != 'nan' else 0.0,
                    'Irms (A)': float(data[10]) if data[10].lower() != 'nan' else 0.0,
                    'Vrms (V)': float(data[13]) if data[13].lower() != 'nan' else 0.0,
                    'Pf': float(data[19]) if data[19].lower() != 'nan' else 0.0,
                    'F (Hz)': float(data[16]) if data[16].lower() != 'nan' else 0.0
                },
                'CT2': {
                    'P (W)': float(data[2]) if data[2].lower() != 'nan' else 0.0,
                    'S (VA)': float(data[5]) if data[5].lower() != 'nan' else 0.0,
                    'Q (VAR)': float(data[8]) if data[8].lower() != 'nan' else 0.0,
                    'Irms (A)': float(data[11]) if data[11].lower() != 'nan' else 0.0,
                    'Vrms (V)': float(data[14]) if data[14].lower() != 'nan' else 0.0,
                    'Pf': float(data[20]) if data[20].lower() != 'nan' else 0.0,
                    'F (Hz)': float(data[16]) if data[16].lower() != 'nan' else 0.0
                },
                'CT3': {
                    'P (W)': float(data[3]) if data[3].lower() != 'nan' else 0.0,
                    'S (VA)': float(data[6]) if data[6].lower() != 'nan' else 0.0,
                    'Q (VAR)': float(data[9]) if data[9].lower() != 'nan' else 0.0,
                    'Irms (A)': float(data[12]) if data[12].lower() != 'nan' else 0.0,
                    'Vrms (V)': float(data[15]) if data[15].lower() != 'nan' else 0.0,
                    'Pf': float(data[21]) if data[21].lower() != 'nan' else 0.0,
                    'F (Hz)': float(data[16]) if data[16].lower() != 'nan' else 0.0
                }
            }

            # Aggregate CT1, CT2, CT3 data
            # Depending on your requirements, you might want to predict per CT or collectively
            # Here, we'll predict for each CT separately
            for ct, values in measurements.items():
                input_data = [
                    values['P (W)'], values['S (VA)'], values['Q (VAR)'],
                    values['Irms (A)'], values['Vrms (V)'], values['Pf'], values['F (Hz)']
                ]
                appliance = predict_appliance(input_data, scaler, mlp)
                print(f"{ct} - Detected Appliance: {appliance}")

        except (IndexError, ValueError) as e:
            print(f"Error parsing data: {e}")

        time.sleep(3)  # Adjust according to your sampling rate
