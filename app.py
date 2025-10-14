from flask import Flask, jsonify, request
from PyPDF2 import PdfReader
from flask_cors import CORS
import difflib
import os
import io
import base64

app = Flask(__name__)

# ✅ Allow Salesforce Lightning origins and FormData uploads
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route("/")
def home():
    return jsonify({
        "message": "🚀 PDF Comparison API is live and running on Render (Text Diff Mode)"
    })


@app.route('/compare', methods=['POST'])
def compare():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        pdf1_name = data.get('pdf1_name')
        pdf2_name = data.get('pdf2_name')
        pdf1_data = data.get('pdf1_data')
        pdf2_data = data.get('pdf2_data')

        if not pdf1_data or not pdf2_data:
            return jsonify({
                "error": "Missing PDF content",
                "received_keys": list(data.keys())
            }), 400

        # Decode base64 to binary
        pdf1_bytes = base64.b64decode(pdf1_data)
        pdf2_bytes = base64.b64decode(pdf2_data)

        # For testing: save locally (optional)
        with open(pdf1_name, 'wb') as f1:
            f1.write(pdf1_bytes)
        with open(pdf2_name, 'wb') as f2:
            f2.write(pdf2_bytes)

        print(f"✅ Received and saved {pdf1_name} & {pdf2_name}")
        return jsonify({
            "status": "success",
            "pdf1_name": pdf1_name,
            "pdf2_name": pdf2_name
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_text_from_pdf(file):
    reader = PdfReader(io.BytesIO(file.read()))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)





