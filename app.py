from flask import Flask, request, jsonify
import io
from PyPDF2 import PdfReader
import difflib
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Flask PDF Comparison API is Running"


@app.route('/compare', methods=['POST'])
def compare_pdfs():
    try:
        # Log request details for debugging
        print("📩 Received /compare request")
        print("Headers:", dict(request.headers))

        # Salesforce sends files as multipart/form-data
        if 'file1' not in request.files or 'file2' not in request.files:
            print("❌ Missing files in request")
            return jsonify({"error": "Missing PDF files in multipart form-data"}), 400

        file1 = request.files['file1']
        file2 = request.files['file2']

        print(f"📄 Received files: {file1.filename}, {file2.filename}")

        # Extract text from both PDFs
        text1 = extract_text_from_pdf(file1)
        text2 = extract_text_from_pdf(file2)

        # Compare text differences
        comparison = compare_texts(text1, text2)

        print(f"✅ Comparison complete: {len(comparison)} lines compared")

        return jsonify({"status": "ok", "comparison": comparison}), 200

    except Exception as e:
        print("🔥 Error:", e)
        return jsonify({"error": str(e)}), 500


def extract_text_from_pdf(file):
    """Extract all visible text from a PDF file object"""
    text = ""
    reader = PdfReader(io.BytesIO(file.read()))
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def compare_texts(text1, text2):
    """Compare two texts line-by-line"""
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
