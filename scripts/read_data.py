# scripts/read_data.py

import serial
import time
import math  # Import math for NaN checking

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
                                if math.isnan(value):
                                    value = 0.0  # Replace NaN with 0.0
                            except ValueError:
                                value = 0.0  # Handle invalid values as 0.0
                            data_values.append(value)
                        
                        # Log the parsed data for debugging
                        print(f"Parsed data_values: {data_values}")  # Debugging

                        # Extract relevant data points based on position
                        # Ensure that the list has enough elements
                        if len(data_values) < 22:
                            print("Incomplete data, skipping")
                            continue

                        # Extracting based on correct positions
                        p1 = data_values[1] if data_values[1] is not None else 0.0  # Active Power CT1
                        p2 = data_values[2] if data_values[2] is not None else 0.0  # Active Power CT2
                        p3 = data_values[3] if data_values[3] is not None else 0.0  # Active Power CT3

                        s1 = data_values[4] if data_values[4] is not None else 0.0  # S (VA) CT1
                        s2 = data_values[5] if data_values[5] is not None else 0.0  # S (VA) CT2
                        s3 = data_values[6] if data_values[6] is not None else 0.0  # S (VA) CT3

                        q1 = data_values[7] if data_values[7] is not None else 0.0  # Q (VAR) CT1
                        q2 = data_values[8] if data_values[8] is not None else 0.0  # Q (VAR) CT2
                        q3 = data_values[9] if data_values[9] is not None else 0.0  # Q (VAR) CT3

                        irms1 = data_values[10] if data_values[10] is not None else 0.0  # Current RMS CT1
                        irms2 = data_values[11] if data_values[11] is not None else 0.0  # Current RMS CT2
                        irms3 = data_values[12] if data_values[12] is not None else 0.0  # Current RMS CT3

                        vrms1 = data_values[13] if data_values[13] is not None else 0.0  # Voltage RMS CT1
                        vrms2 = data_values[14] if data_values[14] is not None else 0.0  # Voltage RMS CT2
                        vrms3 = data_values[15] if data_values[15] is not None else 0.0  # Voltage RMS CT3

                        f1 = data_values[16] if data_values[16] is not None else 0.0  # Frequency CT1
                        f2 = data_values[17] if data_values[17] is not None else 0.0  # Frequency CT2
                        f3 = data_values[18] if data_values[18] is not None else 0.0  # Frequency CT3

                        pf1 = data_values[19] if data_values[19] is not None else 0.0  # Power Factor CT1
                        pf2 = data_values[20] if data_values[20] is not None else 0.0  # Power Factor CT2
                        pf3 = data_values[21] if data_values[21] is not None else 0.0  # Power Factor CT3

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
                            's1': s1,
                            's2': s2,
                            's3': s3,
                            'q1': q1,
                            'q2': q2,
                            'q3': q3,
                            'irms1': irms1,
                            'irms2': irms2,
                            'irms3': irms3,
                            'vrms1': vrms1,
                            'vrms2': vrms2,
                            'vrms3': vrms3,
                            'f1': f1,
                            'f2': f2,
                            'f3': f3,
                            'pf1': pf1,
                            'pf2': pf2,
                            'pf3': pf3
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
