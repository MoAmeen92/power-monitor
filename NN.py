# NN.py

import csv
import serial
import time
import joblib

# Load the saved scaler and model
scaler = joblib.load('scaler.pkl')
mlp = joblib.load('mlp_model.pkl')

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
            data = line.split()

            # Ensure that there are enough data points
            expected_length = 22  # Adjust based on your actual data format
            if len(data) < expected_length:
                print(f"Incomplete data received: {data}")
                continue

            # Extract measurements for each CT sensor
            measurements = {
                'CT1': [
                    float(data[1]) if data[1].lower() != 'nan' else 0.0,
                    float(data[4]) if data[4].lower() != 'nan' else 0.0,
                    float(data[7]) if data[7].lower() != 'nan' else 0.0,
                    float(data[10]) if data[10].lower() != 'nan' else 0.0,
                    float(data[13]) if data[13].lower() != 'nan' else 0.0,
                    float(data[19]) if data[19].lower() != 'nan' else 0.0,
                    float(data[16]) if data[16].lower() != 'nan' else 0.0
                ],
                'CT2': [
                    float(data[2]) if data[2].lower() != 'nan' else 0.0,
                    float(data[5]) if data[5].lower() != 'nan' else 0.0,
                    float(data[8]) if data[8].lower() != 'nan' else 0.0,
                    float(data[11]) if data[11].lower() != 'nan' else 0.0,
                    float(data[14]) if data[14].lower() != 'nan' else 0.0,
                    float(data[20]) if data[20].lower() != 'nan' else 0.0,
                    float(data[16]) if data[16].lower() != 'nan' else 0.0
                ],
                'CT3': [
                    float(data[3]) if data[3].lower() != 'nan' else 0.0,
                    float(data[6]) if data[6].lower() != 'nan' else 0.0,
                    float(data[9]) if data[9].lower() != 'nan' else 0.0,
                    float(data[12]) if data[12].lower() != 'nan' else 0.0,
                    float(data[15]) if data[15].lower() != 'nan' else 0.0,
                    float(data[21]) if data[21].lower() != 'nan' else 0.0,
                    float(data[16]) if data[16].lower() != 'nan' else 0.0
                ]
            }

            # Predict and print appliances for each CT sensor
            for ct, input_data in measurements.items():
                appliance = predict_appliance(input_data, scaler, mlp)
                print(f"{ct} - Detected Appliance: {appliance}")

        except (IndexError, ValueError) as e:
            print(f"Error parsing data: {e}")

    time.sleep(1)  # Adjust according to your sampling rate
