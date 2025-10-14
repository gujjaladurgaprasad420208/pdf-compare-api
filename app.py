from flask import Flask, request, jsonify
import io
import requests
from PyPDF2 import PdfReader
import difflib
import base64
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Flask PDF Comparison API is Running"

@app.route('/compare', methods=['POST'])
def compare_pdfs():
    try:
        # If Salesforce sends JSON with file IDs
        if request.is_json:
            data = request.get_json()
            file1_id = data.get("file1Id")
            file2_id = data.get("file2Id")
            if not file1_id or not file2_id:
                return jsonify({"error": "Missing file IDs"}), 400

            # 🔹 Replace this with your actual Salesforce file download logic (for local test, skip)
            # For now, just respond with dummy comparison
            comparison = [
                {"text1": "Address: 123 Main St", "text2": "Address: 123 Main Street", "status": "diff"},
                {"text1": "Product: Chemical A", "text2": "Product: Chemical B", "status": "diff"},
                {"text1": "Shipment Date: 2025-10-14", "text2": "Shipment Date: 2025-10-14", "status": "match"}
            ]
            return jsonify({"status": "ok", "comparison": comparison}), 200

        # If Postman or another client uploads files directly
        elif 'file1' in request.files and 'file2' in request.files:
            file1 = request.files['file1']
            file2 = request.files['file2']
            text1 = extract_text_from_pdf(file1)
            text2 = extract_text_from_pdf(file2)
            comparison = compare_texts(text1, text2)
            return jsonify({"status": "ok", "comparison": comparison}), 200

        else:
            return jsonify({"error": "No valid files or JSON received"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def extract_text_from_pdf(file):
    text = ""
    reader = PdfReader(io.BytesIO(file.read()))
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

def compare_texts(text1, text2):
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    diff = difflib.ndiff(lines1, lines2)
    result = []
    for line in diff:
        if line.startswith('  '):
            result.append({"text1": line[2:], "text2": line[2:], "status": "match"})
        elif line.startswith('- '):
            result.append({"text1": line[2:], "text2": "", "status": "diff"})
        elif line.startswith('+ '):
            result.append({"text1": "", "text2": line[2:], "status": "diff"})
    return result

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
