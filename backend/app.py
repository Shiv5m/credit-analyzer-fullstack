from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import defaultdict

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['file']
    # Simulated parsed output
    summary = {
        "Food": 3200,
        "Travel": 1500,
        "Utilities": 2000,
        "Shopping": 4500,
        "Others": 800
    }
    transactions = [
        {"date": "04-Jun", "merchant": "Swiggy", "amount": 578, "category": "Food"},
        {"date": "05-Jun", "merchant": "Amazon", "amount": 1200, "category": "Shopping"},
        {"date": "07-Jun", "merchant": "Uber", "amount": 320, "category": "Travel"},
    ]
    return jsonify({"summary": summary, "transactions": transactions})
