import cv2
import logging
from ultralytics import YOLO

logging.getLogger('ultralytics').setLevel(logging.WARNING)
LAPTOP_MODEL_PATH = "models/yolo/yolov8n.onnx"
DESKTOP_MODEL_PATH = "models/yolo/yolov8n.pt"
model = YOLO(DESKTOP_MODEL_PATH, task="detect")

def predict_image(image, postprocess=True, stream=False):
    img = image
    results = model.predict(img, conf=0.5, stream=stream)

    if not postprocess:
        return results, img

    font_scale = 0.7
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Iterate over detections
    for result in results:
        for box in result.boxes:
            conf = round(box.conf[0].item(), 2)
            
            # Adjust coordinates for the offset and ensure they are integers
            cords = [int(x) for x in box.xyxy[0].tolist()]

            # Get class and update label with confidence percentage
            class_id = result.names[box.cls[0].item()]
            label = f"{class_id}: {round(conf * 100)}%"

            # Calculate text width and height for label background
            (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, 2)
            text_width, text_height = int(text_width), int(text_height)

            # Set up the background rectangle for better readability
            background_tl = (cords[0], max(cords[1] - text_height - 10, 0))
            background_br = (cords[0] + text_width, cords[1])
            cv2.rectangle(img, background_tl, background_br, (255, 255, 255), -1)  # White background

            # Draw rectangle and label on the image
            cv2.rectangle(img, (cords[0], cords[1]), (cords[2], cords[3]), (255, 0, 0), 2)
            cv2.putText(img, label, (cords[0], cords[1]-10), font, font_scale, (255, 0, 0), 2)
    return results, img

if __name__ == "__main__":
    logging.getLogger('ultralytics').setLevel(logging.INFO)
    test_img_path = "test.jpeg"
    img = cv2.imread(test_img_path)
    _, result = predict_image(img)
    cv2.imshow("Processed", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()