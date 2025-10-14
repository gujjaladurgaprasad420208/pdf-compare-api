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
def compare_pdfs():
    try:
        # Log what Salesforce is actually sending
        print("⚡ Received headers:", dict(request.headers))
        print("⚡ Form fields:", request.form)
        print("⚡ Files:", request.files)
        print("⚡ Content length:", request.content_length)

        pdf1 = request.files.get('pdf1')
        pdf2 = request.files.get('pdf2')

        if not pdf1 or not pdf2:
            return jsonify({
                "error": "Missing PDF content",
                "received_files": list(request.files.keys()),
                "content_length": request.content_length,
                "headers": dict(request.headers)
            }), 400

        # Continue your comparison logic
        return jsonify({"status": "success", "summary": "PDFs received!"})

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


