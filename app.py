# app.py

import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, send_file
from flask_socketio import SocketIO
import threading
import csv
import os
import time
from scripts.read_data import read_serial_data
import joblib

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

# Paths
DATA_FILE = os.path.join('data', 'history.csv')
MODEL_DIR = 'models'
SCALER_FILE = os.path.join(MODEL_DIR, 'scaler.pkl')
MODEL_FILE = os.path.join(MODEL_DIR, 'mlp_model.pkl')

# Initialize the CSV file with headers if it doesn't exist
if not os.path.exists(DATA_FILE):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'timestamp', 'p1', 'p2', 'p3',
            's1', 's2', 's3',
            'q1', 'q2', 'q3',
            'irms1', 'irms2', 'irms3',
            'vrms1', 'vrms2', 'vrms3',
            'f1', 'f2', 'f3',
            'pf1', 'pf2', 'pf3',
            'prediction_ct1', 'prediction_ct2', 'prediction_ct3'
        ])

# Ensure the models directory exists
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

# Check if scaler and model exist
if not os.path.exists(SCALER_FILE) or not os.path.exists(MODEL_FILE):
    print("Scaler or model file not found. Please ensure 'scaler.pkl' and 'mlp_model.pkl' are in the 'models' directory.")
    exit()

# Load scaler and model
scaler = joblib.load(SCALER_FILE)
model = joblib.load(MODEL_FILE)

def background_thread():
    for data in read_serial_data():
        # Prepare input data for predictions
        predictions = {}
        for ct in ['ct1', 'ct2', 'ct3']:
            try:
                input_features = [
                    data.get(f'p{ct[-1]}', 0.0),  # P (W)
                    data.get(f's{ct[-1]}', 0.0),  # S (VA)
                    data.get(f'q{ct[-1]}', 0.0),  # Q (VAR)
                    data.get(f'irms{ct[-1]}', 0.0),  # Irms (A)
                    data.get(f'vrms{ct[-1]}', 0.0),  # Vrms (V)
                    data.get(f'pf{ct[-1]}', 0.0),    # Pf
                    data.get(f'f{ct[-1]}', 0.0)      # F (Hz)
                ]
                # Normalize input data
                input_normalized = scaler.transform([input_features])
                # Make prediction
                prediction = model.predict(input_normalized)[0]
                predictions[ct] = prediction
            except Exception as e:
                print(f"Error making prediction for {ct}: {e}")
                predictions[ct] = "Prediction Error"

        # Add predictions to data
        data['prediction_ct1'] = predictions.get('ct1', 'Unknown')
        data['prediction_ct2'] = predictions.get('ct2', 'Unknown')
        data['prediction_ct3'] = predictions.get('ct3', 'Unknown')

        # Emit data to frontend
        socketio.emit('update', data)

        # Save data to CSV
        with open(DATA_FILE, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                data.get('timestamp', ''),
                data.get('p1', ''),
                data.get('p2', ''),
                data.get('p3', ''),
                data.get('s1', ''),
                data.get('s2', ''),
                data.get('s3', ''),
                data.get('q1', ''),
                data.get('q2', ''),
                data.get('q3', ''),
                data.get('irms1', ''),
                data.get('irms2', ''),
                data.get('irms3', ''),
                data.get('vrms1', ''),
                data.get('vrms2', ''),
                data.get('vrms3', ''),
                data.get('f1', ''),
                data.get('f2', ''),
                data.get('f3', ''),
                data.get('pf1', ''),
                data.get('pf2', ''),
                data.get('pf3', ''),
                data.get('prediction_ct1', ''),
                data.get('prediction_ct2', ''),
                data.get('prediction_ct3', '')
            ])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download')
def download_data():
    return send_file(DATA_FILE, as_attachment=True)

if __name__ == '__main__':
    thread = threading.Thread(target=background_thread)
    thread.daemon = True
    thread.start()
    socketio.run(app, host='0.0.0.0', port=5000)
