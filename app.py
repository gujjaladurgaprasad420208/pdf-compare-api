from flask import Flask, jsonify, request
from PyPDF2 import PdfReader
from flask_cors import CORS
import difflib
import os
import io

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        "message": "🚀 PDF Comparison API is live and running on Render (Text Diff Mode)"
    })

@app.route('/compare', methods=['POST'])
def compare_pdfs():
    try:
        # Ensure both files are uploaded
        if 'pdf1' not in request.files or 'pdf2' not in request.files:
            return jsonify({"error": "Missing PDF files"}), 400

        pdf1 = request.files['pdf1']
        pdf2 = request.files['pdf2']

        # Extract text from both PDFs
        text1 = extract_text_from_pdf(pdf1)
        text2 = extract_text_from_pdf(pdf2)

        # Compare text using difflib
        diff = list(difflib.ndiff(text1.splitlines(), text2.splitlines()))
        changes = []
        for line in diff:
            if line.startswith('- '):
                changes.append({"status": "removed", "text": line[2:]})
            elif line.startswith('+ '):
                changes.append({"status": "added", "text": line[2:]})
            elif line.startswith('? '):
                changes.append({"status": "modified", "text": line[2:]})

        result_summary = (
            "No differences found" if not changes else f"{len(changes)} differences detected"
        )

        return jsonify({
            "status": "success",
            "summary": result_summary,
            "differences": changes
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def extract_text_from_pdf(file):
    """Extract all text from a PDF using PyPDF2"""
    reader = PdfReader(io.BytesIO(file.read()))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

