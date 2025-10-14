from flask import Flask, request, jsonify
import io
from PyPDF2 import PdfReader
import difflib

app = Flask(__name__)

# ✅ Simple health check
@app.route('/')
def home():
    return "✅ Flask PDF Comparison API is Running"

# ✅ Main compare route
@app.route('/compare', methods=['POST'])
def compare_pdfs():
    try:
        # Ensure both files exist in the request
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({"error": "Both PDF files are required."}), 400

        # Read files from the request
        file1 = request.files['file1']
        file2 = request.files['file2']

        # Convert to text
        text1 = extract_text_from_pdf(file1)
        text2 = extract_text_from_pdf(file2)

        # Compare line by line
        comparison = compare_texts(text1, text2)

        # Return as JSON
        return jsonify({
            "comparison": comparison,
            "status": "ok"
        }), 200

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500


# ✅ Helper: Extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    reader = PdfReader(io.BytesIO(file.read()))
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()


# ✅ Helper: Compare line by line
def compare_texts(text1, text2):
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    diff = difflib.ndiff(lines1, lines2)

    result = []
    for i, line in enumerate(diff):
        # line starts with '  ' (same), '- ' (removed), '+ ' (added)
        if line.startswith('  '):
            result.append({"text1": line[2:], "text2": line[2:], "status": "match"})
        elif line.startswith('- '):
            result.append({"text1": line[2:], "text2": "", "status": "diff"})
        elif line.startswith('+ '):
            result.append({"text1": "", "text2": line[2:], "status": "diff"})
    return result


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # Render provides PORT automatically
    app.run(host="0.0.0.0", port=port)


