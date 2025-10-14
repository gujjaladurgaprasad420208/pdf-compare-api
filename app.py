from flask import Flask, jsonify, request
from PyPDF2 import PdfReader
from flask_cors import CORS
import difflib
import os
import io

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
    print("=== Incoming Request ===")
    print("Headers:", dict(request.headers))
    print("Form keys:", list(request.form.keys()))
    print("Files keys:", list(request.files.keys()))

    if 'pdf1' not in request.files or 'pdf2' not in request.files:
        return jsonify({
            "error": "Missing PDF content",
            "received_keys": list(request.files.keys()),
            "note": "Expected 'pdf1' and 'pdf2'"
        }), 400

    file1 = request.files['pdf1']
    file2 = request.files['pdf2']

    print("File1 name:", file1.filename)
    print("File2 name:", file2.filename)

    return jsonify({
        "status": "success",
        "file1": file1.filename,
        "file2": file2.filename
    })


def extract_text_from_pdf(file):
    reader = PdfReader(io.BytesIO(file.read()))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)



