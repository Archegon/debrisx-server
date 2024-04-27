import cv2
import numpy as np
import tensorflow as tf

MODEL_PATH = "models\\1.tflite"
LABEL_PATH = "models\\coco-labels-2014_2017.txt"

def load_labels(filename):
    with open(filename, 'r') as file:
        labels = [line.strip() for line in file.readlines()]
    return labels

def load_tflite_model(model_path):
    # Load TFLite model and allocate tensors using TensorFlow
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter

def preprocess_image(frame, input_size):
    frame = cv2.resize(frame, input_size)
    frame = frame.astype(np.float32) / 255.0
    frame = np.expand_dims(frame, axis=0)  # Add batch dimension.
    return frame

def detect_objects(frame, model_path):
    interpreter = load_tflite_model(model_path)
    labels = load_labels(LABEL_PATH)

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    height, width = frame.shape[:2]
    input_data = preprocess_image(frame, (input_details[0]['shape'][2], input_details[0]['shape'][1]))

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])[0]  # Remove batch dimension

    detections = []
    for detection in output_data:
        x, y, w, h, conf = detection[:5]
        class_probs = detection[5:]
        class_id = np.argmax(class_probs)
        class_score = class_probs[class_id]

        if conf * class_score > 0.5:  # Threshold can be adjusted
            label = labels[class_id]
            x_center = x * width
            y_center = y * height
            box_width = w * width
            box_height = h * height

            x_min = int(x_center - (box_width / 2))
            y_min = int(y_center - (box_height / 2))
            x_max = int(x_center + (box_width / 2))
            y_max = int(y_center + (box_height / 2))

            detections.append((label, class_id, conf * class_score, (x_min, y_min, x_max - x_min, y_max - y_min)))

    return detections

def apply_nms(detections):
    boxes = [det[3] for det in detections]  # Extract bounding boxes
    scores = [det[2] for det in detections]  # Extract scores

    # Convert lists to numpy arrays for OpenCV
    boxes = np.array(boxes)
    scores = np.array(scores)

    # Apply Non-Maximum Suppression
    indices = cv2.dnn.NMSBoxes(boxes.tolist(), scores.tolist(), 0.5, 0.4)

    # Properly check if indices is not empty and handle the data
    if indices is not None and len(indices) > 0:
        # Flatten the array to handle both single and multiple results correctly
        indices = np.array(indices).flatten()
    else:
        return []  # Return an empty list if no indices or indices are empty

    # Filter detections based on NMS indices
    filtered_detections = [detections[i] for i in indices]
    return filtered_detections

def process_image(image): 
    model = MODEL_PATH  # Replace with your model
    
    # Detect objects in the image
    detections = detect_objects(image, model)
    filtered_detections = apply_nms(detections)
    
    # Draw bounding boxes on the image
    for label, _, score, (x, y, w, h) in filtered_detections:
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 1)
        label_text = f"{label}: {score:.2f}"
        cv2.putText(image, label_text, (int(x), int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    return image
