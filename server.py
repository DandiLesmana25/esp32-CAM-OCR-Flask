from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import easyocr
import os
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




# endpoind upload
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

    # Perform OCR
    try:
        # load model
        # path model
         # Perform OCR
        ocr_result = reader.readtext(image_path, detail=0)  # Extract text only
        ocr_text = " ".join(ocr_result)

        # save to db
        cursor = mysql.connection.cursor()
        sql = "INSERT INTO ocr_results (image_name, ocr_text) VALUES (%s, %s)"
        val = (file.filename, ocr_text)
        cursor.execute(sql, val)
        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "message": "OCR processing and save to db",
            "text": ocr_result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
