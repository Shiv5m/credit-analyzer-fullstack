from flask import Flask, request, jsonify
from flask_cors import CORS
from io import BytesIO
from parser import analyze_pdf

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return {"status": "Backend running with pdfplumber ✅"}

@app.route("/analyze", methods=["POST"])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    try:
        file_bytes = BytesIO(file.read())
        result = analyze_pdf(file_bytes)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
