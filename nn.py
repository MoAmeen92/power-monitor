import csv
import serial
import random
import time
import math
import json

# Simple Softmax Activation with numerical stability
def softmax(x):
    max_x = max(x)
    exps = [math.exp(xi - max_x) if not math.isinf(xi - max_x) and not math.isnan(xi - max_x) else 0.0 for xi in x]
    sum_exps = sum(exps)
    if sum_exps == 0:
        # Avoid division by zero; return uniform probabilities
        return [1.0 / len(x) for _ in x]
    return [exp_i / sum_exps for exp_i in exps]

# Forward Propagation
def forward_propagation(inputs, weights, biases):
    weighted_sums = []
    for weight_set, bias in zip(weights, biases):
        sum_w = sum(i * w for i, w in zip(inputs, weight_set)) + bias
        weighted_sums.append(sum_w)
    return softmax(weighted_sums)

# Cross-Entropy Loss
def cross_entropy_loss(predicted, actual):
    return -sum(a * math.log(p) for p, a in zip(predicted, actual) if p > 0)

# Load and Encode CSV Data with normalization
def load_data(filename):
    data = []
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
                data.append(numeric_values + [label])
            except ValueError as e:
                print(f"Skipping row with invalid data: {line}, Error: {e}")
                continue

    if not data:
        print("No valid data found in the CSV file.")
        exit()

    # Compute min and max for each feature
    num_features = len(data[0]) - 1
    min_values = [float('inf')] * num_features
    max_values = [float('-inf')] * num_features

    for row in data:
        for i in range(num_features):
            value = row[i]
            if value < min_values[i]:
                min_values[i] = value
            if value > max_values[i]:
                max_values[i] = value

    # Normalize data
    for row in data:
        for i in range(num_features):
            if max_values[i] - min_values[i] == 0:
                row[i] = 0.0  # Avoid division by zero
            else:
                row[i] = (row[i] - min_values[i]) / (max_values[i] - min_values[i])

    # Map appliance labels to one-hot vectors
    appliances = sorted(list(set(row[-1] for row in data)))
    label_map = {appliance: i for i, appliance in enumerate(appliances)}
    one_hot_labels = {label: [1 if i == j else 0 for j in range(len(appliances))] for label, i in label_map.items()}

    # Replace label with one-hot encoded vector
    for row in data:
        row[-1] = one_hot_labels[row[-1]]

    # Save normalization parameters for future use (real-time predictions)
    with open('normalization.json', 'w') as f:
        json.dump({'min': min_values, 'max': max_values}, f)

    return data, label_map, min_values, max_values

# Initialize Weights and Biases
def initialize_network(input_size, output_size):
    weights = [[random.uniform(-0.1, 0.1) for _ in range(input_size)] for _ in range(output_size)]
    biases = [random.uniform(-0.1, 0.1) for _ in range(output_size)]
    return weights, biases

# Train the Neural Network
def train_network(data, weights, biases, learning_rate=0.01, epochs=1000):
    num_inputs = len(data[0]) - 1
    for epoch in range(epochs):
        total_loss = 0
        for row in data:
            # Inputs are already normalized floats, excluding the label
            inputs = row[:-1]
            target = row[-1]

            # Forward pass
            predicted = forward_propagation(inputs, weights, biases)
            loss = cross_entropy_loss(predicted, target)
            total_loss += loss

            # Backpropagation
            for i in range(len(biases)):
                for j in range(num_inputs):
                    weights[i][j] -= learning_rate * (predicted[i] - target[i]) * inputs[j]
                biases[i] -= learning_rate * (predicted[i] - target[i])

        if epoch % 100 == 0:
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss:.4f}")

# Evaluate the Neural Network
def evaluate_model(test_data, weights, biases, label_map):
    total_loss = 0
    correct = 0
    for row in test_data:
        inputs = row[:-1]
        target = row[-1]
        predicted = forward_propagation(inputs, weights, biases)
        loss = cross_entropy_loss(predicted, target)
        total_loss += loss

        predicted_label = predicted.index(max(predicted))
        true_label = target.index(1)
        if predicted_label == true_label:
            correct += 1

    accuracy = (correct / len(test_data)) * 100
    print(f"Test Loss: {total_loss:.4f}, Accuracy: {accuracy:.2f}%")

# Real-time Prediction Function with normalization
def predict_appliance(inputs, weights, biases, label_map, min_values, max_values):
    # Normalize inputs using min and max
    normalized_inputs = []
    for i in range(len(inputs)):
        if max_values[i] - min_values[i] == 0:
            normalized = 0.0
        else:
            normalized = (inputs[i] - min_values[i]) / (max_values[i] - min_values[i])
        # Clamp normalized values to [0,1] to handle any out-of-range values
        normalized = max(0.0, min(1.0, normalized))
        normalized_inputs.append(normalized)

    # Check for any 'nan' or 'inf' in normalized inputs
    if any(math.isnan(x) or math.isinf(x) for x in normalized_inputs):
        return "Invalid Data"

    predicted = forward_propagation(normalized_inputs, weights, biases)
    predicted_label = predicted.index(max(predicted))
    for appliance, index in label_map.items():
        if index == predicted_label:
            return appliance

    return "Unknown"

# Load and Train the Network
filename = 'appliance_data.csv'
data, label_map, min_values, max_values = load_data(filename)
random.shuffle(data)
split_index = int(0.8 * len(data))
train_data = data[:split_index]
test_data = data[split_index:]

input_size = len(train_data[0]) - 1
output_size = len(label_map)

weights, biases = initialize_network(input_size, output_size)
train_network(train_data, weights, biases)

# Evaluate the model
evaluate_model(test_data, weights, biases, label_map)

# Open Serial Port and Read Real-Time Data
serial_port = '/dev/ttyAMA0'
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

            for ct, values in measurements.items():
                # Prepare input for prediction
                input_data = [
                    values['P (W)'], values['S (VA)'], values['Q (VAR)'],
                    values['Irms (A)'], values['Vrms (V)'], values['Pf'], values['F (Hz)']
                ]
                appliance = predict_appliance(input_data, weights, biases, label_map, min_values, max_values)
                print(f"{ct} - Detected Appliance: {appliance}")

        except (IndexError, ValueError) as e:
            print(f"Error parsing data: {e}")

        time.sleep(3)  # Adjust according to your sampling rate
