from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import easyocr
import os
from ultralytics import YOLO
import time
import cv2
import numpy as np

# import mysql.connector

app = Flask(__name__)

# Required
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ocr_db"

mysql = MySQL(app)


# Initialize EasyOCR reader
reader = easyocr.Reader(['id'], gpu=False)
print("EasyOCR initialized successfully.")

# load model yolo
model = YOLO("models/best.pt")
print("succes load model")

# Directory to save uploaded images
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# endpoind home
@app.route('/')
def home():
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT * from ocr_results""")
    rv = cursor.fetchall()
    return {
        "status": "succes",
        "data": rv
    }





# end2
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save uploaded image
    image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(image_path)

    # Perform YOLOv8 detection
    try:
        results = model(image_path)  # Perform detection
        detections = results[0].boxes.xyxy.cpu().numpy()  # Get bounding boxes
        detection_results = [] # array untuk menmpung hasil deteksi
        
        # Iterate over detected boxes
        for box in detections:
            if len(box) == 4:  # Handle case with no confidence score
                x1, y1, x2, y2 = box
                detection_results.append({
                    "x1": int(x1),
                    "y1": int(y1),
                    "x2": int(x2),
                    "y2": int(y2),
                    "confidence": None  # No confidence available
                })
            elif len(box) >= 5:  # Handle case with confidence score
                x1, y1, x2, y2, conf = box[:5]
                detection_results.append({
                    "x1": int(x1),
                    "y1": int(y1),
                    "x2": int(x2),
                    "y2": int(y2),
                    "confidence": float(conf)
                })

        # Jika ada hasil deteksi, crop image  untuk OCR
        if len(detection_results) > 0:
            first_box = detection_results[0]
            from PIL import Image
            image = Image.open(image_path)
            cropped_image = image.crop((first_box["x1"], first_box["y1"], first_box["x2"], first_box["y2"]))
            # convert image to cv2 
            cropped_image_cv = np.array(cropped_image)
            cropped_image_cv = cv2.cvtColor(cropped_image_cv, cv2.COLOR_RGB2BGR)  # PIL to OpenCV (RGB to BGR)

            # grayscaling dan tresholding
            gray_image = cv2.cvtColor(cropped_image_cv, cv2.COLOR_BGR2GRAY) # konversi ke grayscale
            # _, threshold_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) # tresholding

            # cropped_path = os.path.join(UPLOAD_FOLDER, f"cropped_{int(time.time())}.png")
            unique_filename = f"cropped_{int(time.time())}.png"
            cropped_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            cv2.imwrite(cropped_path, gray_image)
            # cropped_image.save(cropped_path)

            # Perform OCR gambar hasil tresholding
            ocr_result = reader.readtext(cropped_path, detail=0)  # Extract text only
            ocr_text = " ".join(ocr_result)
        else:
            ocr_text = "No KTP detected."

        # Save to database
        cursor = mysql.connection.cursor()
        sql = "INSERT INTO ocr_results (image_name, ocr_text) VALUES (%s, %s)"
        val = (file.filename, ocr_text)
        cursor.execute(sql, val)
        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "message": "OCR result already save to db",
            "detections": detection_results,
            "text": ocr_text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
