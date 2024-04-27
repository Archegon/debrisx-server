import cv2
from ultralytics import YOLO

model = YOLO("models/yolo/yolov8n.pt")

def predict_image(image):
    img = image
    results = model.predict(img)

    font_scale = 0.7

    # Iterate over detections
    for result in results:
        for box in result.boxes:
            # Get bounding box coordinates
            cords = box.xyxy[0].tolist()
            cords = [round(x) for x in cords]

            # Get class and confidence
            class_id = result.names[box.cls[0].item()]
            conf = round(box.conf[0].item(), 2)
            label = f"{class_id}: {conf*100}%"

            # Calculate text width and height
            (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)

            # Set up the background rectangle for better readability
            background_tl = (cords[0], cords[1] - text_height - 10)
            background_br = (cords[0] + text_width, cords[1])
            cv2.rectangle(img, background_tl, background_br, (255, 255, 255), -1)  # White background

            # Draw rectangle and label on the image
            cv2.rectangle(img, (cords[0], cords[1]), (cords[2], cords[3]), (255, 0, 0), 2)
            cv2.putText(img, label, (cords[0], cords[1]-10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), 2)
    
    return img