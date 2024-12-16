from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return {
        "status":"succes",
        "message":"service dah jalan"
    }, 200

app.run(debug=True)