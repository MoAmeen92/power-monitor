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

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

# Path to store historical data
DATA_FILE = os.path.join('data', 'history.csv')

# Initialize the CSV file with headers if it doesn't exist
if not os.path.exists(DATA_FILE):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'p1', 'p2', 'p3', 'irms1', 'irms2', 'irms3', 'vrms1', 'vrms2', 'vrms3'])

def background_thread():
    for data in read_serial_data():
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
                data.get('irms1', ''),
                data.get('irms2', ''),
                data.get('irms3', ''),
                data.get('vrms1', ''),
                data.get('vrms2', ''),
                data.get('vrms3', '')
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
