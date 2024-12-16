from flask import Flask, request, jsonify
import easyocr
import os

app = Flask(__name__)

php_server_url = "http://localhost/esp-project-ocr/save_ocr.php"

# Initialize EasyOCR reader
reader = easyocr.Reader(['id'], gpu=False)

@app.route('/')
def home():
    return "Hello OCR with EasyOCR and Flask"

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save uploaded image
    image_path = os.path.join("uploads", file.filename)
    file.save(image_path)

    # Perform OCR
    try:
        result = reader.readtext(image_path, detail=0)
        return jsonify({"text": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
