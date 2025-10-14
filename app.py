from flask import Flask, jsonify, request
from pdf_diff import diff
from PyPDF2 import PdfReader
import tempfile
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "🚀 PDF Comparison API is live and running on Render!"
    })

@app.route('/compare', methods=['POST'])
def compare_pdfs():
    try:
        if 'pdf1' not in request.files or 'pdf2' not in request.files:
            return jsonify({"error": "Missing PDF files"}), 400

        pdf1 = request.files['pdf1']
        pdf2 = request.files['pdf2']

        # Save PDFs temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp1, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp2:
            pdf1.save(tmp1.name)
            pdf2.save(tmp2.name)

            # Perform PDF text diff
            report = diff(tmp1.name, tmp2.name)

        # Clean up
        os.unlink(tmp1.name)
        os.unlink(tmp2.name)

        return jsonify({
            "status": "success",
            "differences": report,
            "summary": f"Found {len(report)} differences" if report else "No differences found"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
