from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import re

app = Flask(__name__)
CORS(app)

def parse_axis_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    lines = text.splitlines()
    txns = []
    txn_pattern = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([A-Z ]+?)\s+([\d,]+\.\d{2})\s+Dr")

    for line in lines:
        match = txn_pattern.match(line.strip())
        if match:
            date, merchant, category, amount = match.groups()
            txns.append({
                "date": date,
                "merchant": merchant.strip(),
                "category": category.strip().title(),
                "amount": float(amount.replace(",", ""))
            })

    summary = {}
    for txn in txns:
        summary[txn["category"]] = summary.get(txn["category"], 0) + txn["amount"]

    return {"summary": summary, "transactions": txns}

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    result = parse_axis_pdf(file)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
