# scripts/read_data.py

import serial
import time

def read_serial_data(serial_port='/dev/ttyAMA0', baud_rate=38400):
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        time.sleep(2)  # Wait for the serial connection to initialize

        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').rstrip()
                if line:
                    # Split the line by spaces
                    parts = line.split()
                    print(f"Received line: {line}")  # Debugging

                    try:
                        # Convert each part to float, handling 'nan'
                        data_values = []
                        for part in parts:
                            try:
                                value = float(part)
                            except ValueError:
                                value = 0.0  # Handle 'nan' or invalid values as 0
                            data_values.append(value)
                        
                        # Log the parsed data for debugging
                        print(f"Parsed data_values: {data_values}")  # Debugging

                        # Extract relevant data points based on position
                        # Ensure that the list has enough elements
                        if len(data_values) < 23:
                            print("Incomplete data, skipping")
                            continue

                        # Extracting based on correct positions
                        p1 = data_values[1] if data_values[1] is not None else 0.0  # Active Power
                        p2 = data_values[2] if data_values[2] is not None else 0.0  # Active Power
                        p3 = data_values[3] if data_values[3] is not None else 0.0  # Active Power
                        irms1 = data_values[10] if data_values[10] is not None else 0.0  # Current RMS
                        irms2 = data_values[11] if data_values[11] is not None else 0.0  # Current RMS for CT2
                        irms3 = data_values[12] if data_values[12] is not None else 0.0  # Current RMS for CT3
                        vrms1 = data_values[13] if data_values[13] is not None else 0.0  # Voltage RMS
                        vrms2 = data_values[14] if data_values[14] is not None else 0.0  # Voltage RMS
                        vrms3 = data_values[15] if data_values[15] is not None else 0.0  # Voltage RMS

                        # Set voltage to 0 if negative
                        vrms1 = vrms1 if vrms1 >=0 else 0.0
                        vrms2 = vrms2 if vrms2 >=0 else 0.0
                        vrms3 = vrms3 if vrms3 >=0 else 0.0

                        # Create a data dictionary
                        data = {
                            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                            'p1': p1,
                            'p2': p2,
                            'p3': p3,
                            'irms1': irms1,
                            'irms2': irms2,
                            'irms3': irms3,
                            'vrms1': vrms1,
                            'vrms2': vrms2,
                            'vrms3': vrms3
                        }

                        # Log the data dictionary
                        print(f"Yielding data: {data}")  # Debugging

                        yield data

                    except Exception as e:
                        print(f"Error processing line: {line}")
                        print(e)
            time.sleep(1)  # Adjust the reading frequency as needed
    except serial.SerialException as e:
        print(f"Serial exception: {e}")
